# Phase 1 実装ガイド - タスク管理層

**目的**: cmwをClaude Codeと統合するための基盤を構築  
**推定時間**: 3-4時間  
**前提**: Phase 0（基盤構築）が完了していること

---

## 🎯 Phase 1の目標

Claude Codeが以下のことをできるようにする:

```python
# 1. 次のタスクを取得
task = cmw.get_next_task()

# 2. タスクのコンテキストを取得
context = cmw.get_task_context(task.id)

# 3. Claude Codeがコーディング（自身の能力）

# 4. 完了報告
cmw.mark_completed(task.id, ["backend/auth.py"])
```

---

## 📋 実装する3つのコンポーネント

### 1. TaskProvider（2時間）⭐ 最優先
- タスク情報の提供
- コンテキスト構築
- 状態更新

### 2. StateManager（1時間）
- 永続化
- ロック機構
- セッション管理

### 3. ParallelExecutor（1-2時間）
- 並列実行判定
- ファイル競合検出

---

## 🔨 Phase 1.1: TaskProvider実装

### ファイル: `src/cmw/task_provider.py`

```python
"""
TaskProvider - Claude Codeにタスク情報を提供

役割:
- 次に実行すべきタスクを選択
- タスク実行に必要な全情報を提供
- タスク完了/失敗の記録
"""
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import json

from .models import Task, TaskStatus
from .coordinator import Coordinator


class TaskProvider:
    """Claude Codeへのタスク情報提供"""
    
    def __init__(self, project_path: Path):
        """
        Args:
            project_path: プロジェクトのルートパス
        """
        self.project_path = Path(project_path)
        self.coordinator = Coordinator(project_path)
        self.progress_file = project_path / "shared/coordination/progress.json"
        
        # 進捗情報を読み込み
        self._load_progress()
    
    def get_next_task(self) -> Optional[Task]:
        """
        次に実行すべきタスクを取得
        
        依存関係を考慮し、実行可能なタスクの中から
        優先度の高いものを返す
        
        Returns:
            実行可能なタスク、なければNone
        """
        # 実行可能なタスクを取得（依存関係チェック済み）
        ready_tasks = self._get_ready_tasks()
        
        if not ready_tasks:
            return None
        
        # 優先度でソート
        ready_tasks.sort(key=lambda t: (
            t.priority == "high",    # 高優先度を先に
            t.priority == "medium",
            -len(t.dependencies)     # 依存が少ないものを先に
        ), reverse=True)
        
        return ready_tasks[0]
    
    def get_task_context(self, task_id: str) -> Dict:
        """
        タスク実行に必要な全コンテキストを構築
        
        Args:
            task_id: タスクID
            
        Returns:
            タスク実行に必要な情報を含む辞書
        """
        task = self.coordinator.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        return {
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "target_files": task.target_files,
                "acceptance_criteria": task.acceptance_criteria
            },
            "requirements": self._load_requirements_section(task),
            "api_spec": self._load_api_spec(task),
            "related_files": self._get_related_files(task),
            "dependencies_artifacts": self._get_dependency_artifacts(task),
            "project_structure": self._get_project_structure()
        }
    
    def mark_started(self, task_id: str):
        """
        タスク開始を記録
        
        Args:
            task_id: タスクID
        """
        task = self.coordinator.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now().isoformat()
        
        self._save_progress()
    
    def mark_completed(self, task_id: str, artifacts: List[str]):
        """
        タスク完了を記録
        
        Args:
            task_id: タスクID
            artifacts: 生成されたファイルのリスト
        """
        task = self.coordinator.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now().isoformat()
        task.artifacts = artifacts
        
        self._save_progress()
        
        # 依存タスクのブロックを解除
        self._unblock_dependent_tasks(task_id)
    
    def mark_failed(self, task_id: str, error: str):
        """
        タスク失敗を記録
        
        Args:
            task_id: タスクID
            error: エラーメッセージ
        """
        task = self.coordinator.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        task.status = TaskStatus.FAILED
        task.error = error
        task.failed_at = datetime.now().isoformat()
        
        self._save_progress()
        
        # 依存タスクをブロック状態に
        self._block_dependent_tasks(task_id)
    
    # === プライベートメソッド ===
    
    def _get_ready_tasks(self) -> List[Task]:
        """依存関係を満たした実行可能なタスクを取得"""
        ready = []
        
        for task in self.coordinator.tasks.values():
            # 既に完了済みはスキップ
            if task.status == TaskStatus.COMPLETED:
                continue
            
            # ブロックされているタスクはスキップ
            if task.status == TaskStatus.BLOCKED:
                continue
            
            # 依存関係をチェック
            if self._are_dependencies_met(task):
                ready.append(task)
        
        return ready
    
    def _are_dependencies_met(self, task: Task) -> bool:
        """タスクの依存関係が満たされているか"""
        for dep_id in task.dependencies:
            dep_task = self.coordinator.get_task(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    def _load_requirements_section(self, task: Task) -> str:
        """requirements.mdから関連セクションを読み込み"""
        req_file = self.project_path / "shared/docs/requirements.md"
        if not req_file.exists():
            return ""
        
        content = req_file.read_text(encoding='utf-8')
        
        # タスクに関連するセクションを抽出
        # （簡易実装: 将来的にはセクションマッピングを使用）
        return content
    
    def _load_api_spec(self, task: Task) -> str:
        """API仕様から関連部分を読み込み"""
        api_file = self.project_path / "shared/docs/api-spec.md"
        if not api_file.exists():
            return ""
        
        return api_file.read_text(encoding='utf-8')
    
    def _get_related_files(self, task: Task) -> List[str]:
        """タスクに関連する既存ファイルを取得"""
        related = []
        artifacts_dir = self.project_path / "shared/artifacts"
        
        # target_filesに関連するファイルを探す
        for target in task.target_files:
            target_path = artifacts_dir / target
            if target_path.exists():
                related.append({
                    "path": target,
                    "content": target_path.read_text(encoding='utf-8')
                })
        
        return related
    
    def _get_dependency_artifacts(self, task: Task) -> List[Dict]:
        """依存タスクの成果物を取得"""
        artifacts = []
        
        for dep_id in task.dependencies:
            dep_task = self.coordinator.get_task(dep_id)
            if dep_task and dep_task.status == TaskStatus.COMPLETED:
                for artifact_path in dep_task.artifacts:
                    full_path = self.project_path / "shared/artifacts" / artifact_path
                    if full_path.exists():
                        artifacts.append({
                            "task_id": dep_id,
                            "path": artifact_path,
                            "content": full_path.read_text(encoding='utf-8')
                        })
        
        return artifacts
    
    def _get_project_structure(self) -> Dict:
        """プロジェクト構造の情報を取得"""
        return {
            "backend_dir": "shared/artifacts/backend",
            "frontend_dir": "shared/artifacts/frontend",
            "tests_dir": "shared/artifacts/tests"
        }
    
    def _unblock_dependent_tasks(self, completed_task_id: str):
        """依存タスクのブロックを解除"""
        for task in self.coordinator.tasks.values():
            if completed_task_id in task.dependencies:
                if self._are_dependencies_met(task):
                    if task.status == TaskStatus.BLOCKED:
                        task.status = TaskStatus.PENDING
    
    def _block_dependent_tasks(self, failed_task_id: str):
        """依存タスクをブロック状態に"""
        for task in self.coordinator.tasks.values():
            if failed_task_id in task.dependencies:
                task.status = TaskStatus.BLOCKED
    
    def _load_progress(self):
        """進捗情報を読み込み"""
        if not self.progress_file.exists():
            self._init_progress()
            return
        
        progress = json.loads(self.progress_file.read_text(encoding='utf-8'))
        
        # タスクの状態を復元
        for task_id, task_data in progress.get("tasks", {}).items():
            task = self.coordinator.get_task(task_id)
            if task:
                task.status = TaskStatus(task_data.get("status", "pending"))
                task.started_at = task_data.get("started_at")
                task.completed_at = task_data.get("completed_at")
                task.artifacts = task_data.get("artifacts", [])
                task.error = task_data.get("error")
    
    def _save_progress(self):
        """進捗情報を保存"""
        progress = {
            "updated_at": datetime.now().isoformat(),
            "tasks": {}
        }
        
        for task_id, task in self.coordinator.tasks.items():
            progress["tasks"][task_id] = {
                "id": task.id,
                "status": task.status.value,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "artifacts": task.artifacts,
                "error": task.error
            }
        
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        self.progress_file.write_text(
            json.dumps(progress, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    
    def _init_progress(self):
        """進捗情報を初期化"""
        progress = {
            "created_at": datetime.now().isoformat(),
            "tasks": {}
        }
        
        for task_id, task in self.coordinator.tasks.items():
            progress["tasks"][task_id] = {
                "id": task.id,
                "status": TaskStatus.PENDING.value,
                "started_at": None,
                "completed_at": None,
                "artifacts": [],
                "error": None
            }
        
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        self.progress_file.write_text(
            json.dumps(progress, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
```

---

## 🔨 Phase 1.2: StateManager実装

### ファイル: `src/cmw/state_manager.py`

```python
"""
StateManager - 状態の永続化とセッション管理

役割:
- 複数セッション間での状態共有
- ロック機構による競合回避
- セッションの継続性保証
"""
from pathlib import Path
from typing import Optional
import json
import time
import os


class StateManager:
    """状態管理とロック機構"""
    
    LOCK_TIMEOUT = 300  # 5分
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.progress_file = project_path / "shared/coordination/progress.json"
        self.lock_file = project_path / "shared/coordination/.lock"
    
    def acquire_lock(self, timeout: int = 10) -> bool:
        """
        ロックを取得
        
        Args:
            timeout: タイムアウト秒数
            
        Returns:
            ロック取得成功ならTrue
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self._try_acquire_lock():
                return True
            time.sleep(0.1)
        
        return False
    
    def release_lock(self):
        """ロックを解放"""
        if self.lock_file.exists():
            try:
                self.lock_file.unlink()
            except FileNotFoundError:
                pass  # 既に削除済み
    
    def is_locked(self) -> bool:
        """ロックされているか確認"""
        if not self.lock_file.exists():
            return False
        
        lock_data = self._read_lock()
        if not lock_data:
            return False
        
        # タイムアウトチェック
        if time.time() - lock_data['timestamp'] > self.LOCK_TIMEOUT:
            # 古いロックは無効
            self.release_lock()
            return False
        
        return True
    
    def get_lock_info(self) -> Optional[dict]:
        """ロック情報を取得"""
        if not self.lock_file.exists():
            return None
        
        return self._read_lock()
    
    def _try_acquire_lock(self) -> bool:
        """ロック取得を試みる"""
        # 既にロックされているかチェック
        if self.is_locked():
            return False
        
        # ロックを作成
        lock_data = {
            'session_id': os.getpid(),
            'timestamp': time.time(),
            'hostname': os.uname().nodename if hasattr(os, 'uname') else 'unknown'
        }
        
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock_file.write_text(
            json.dumps(lock_data, indent=2),
            encoding='utf-8'
        )
        
        return True
    
    def _read_lock(self) -> Optional[dict]:
        """ロックファイルを読み込み"""
        try:
            return json.loads(self.lock_file.read_text(encoding='utf-8'))
        except (FileNotFoundError, json.JSONDecodeError):
            return None


class SessionContext:
    """
    セッション管理のコンテキストマネージャー
    
    使用例:
        with SessionContext(project_path) as session:
            # ロックを取得した状態で作業
            provider = TaskProvider(project_path)
            task = provider.get_next_task()
        # ロック自動解放
    """
    
    def __init__(self, project_path: Path):
        self.state_manager = StateManager(project_path)
    
    def __enter__(self):
        if not self.state_manager.acquire_lock():
            raise RuntimeError(
                "Could not acquire lock. "
                "Another session may be running."
            )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.state_manager.release_lock()
```

---

## 🔨 Phase 1.3: ParallelExecutor実装

### ファイル: `src/cmw/parallel_executor.py`

```python
"""
ParallelExecutor - 並列実行の制御

役割:
- ファイル競合の検出
- 並列実行可能なタスクの判定
- 実行グループの管理
"""
from pathlib import Path
from typing import List, Set
from .models import Task
from .task_provider import TaskProvider


class ParallelExecutor:
    """並列実行の制御"""
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.provider = TaskProvider(project_path)
    
    def get_executable_tasks(self, max_parallel: int = 3) -> List[Task]:
        """
        並列実行可能なタスクを取得
        
        Args:
            max_parallel: 最大並列実行数
            
        Returns:
            並列実行可能なタスクのリスト
        """
        # 準備完了タスクを全て取得
        ready_tasks = self._get_all_ready_tasks()
        
        if not ready_tasks:
            return []
        
        # ファイル競合を考慮して選択
        executable = []
        used_files: Set[str] = set()
        
        for task in ready_tasks:
            if len(executable) >= max_parallel:
                break
            
            task_files = self._get_task_files(task)
            
            # 既に使用中のファイルと重複しないかチェック
            if not task_files & used_files:
                executable.append(task)
                used_files.update(task_files)
        
        return executable
    
    def can_run_parallel(self, task1: Task, task2: Task) -> bool:
        """
        2つのタスクが並列実行可能か判定
        
        Args:
            task1, task2: タスク
            
        Returns:
            並列実行可能ならTrue
        """
        files1 = self._get_task_files(task1)
        files2 = self._get_task_files(task2)
        
        # ファイルが重複していなければ並列実行可能
        return not (files1 & files2)
    
    def group_tasks_by_parallelism(self, tasks: List[Task]) -> List[List[Task]]:
        """
        タスクを並列実行可能なグループに分ける
        
        Args:
            tasks: タスクのリスト
            
        Returns:
            並列実行可能なグループのリスト
        """
        groups = []
        remaining = tasks.copy()
        
        while remaining:
            # 新しいグループを作成
            group = []
            used_files: Set[str] = set()
            
            # 並列実行可能なタスクをグループに追加
            for task in remaining[:]:
                task_files = self._get_task_files(task)
                
                if not task_files & used_files:
                    group.append(task)
                    used_files.update(task_files)
                    remaining.remove(task)
            
            if group:
                groups.append(group)
            else:
                # 無限ループ防止
                break
        
        return groups
    
    # === プライベートメソッド ===
    
    def _get_all_ready_tasks(self) -> List[Task]:
        """実行可能な全タスクを取得"""
        ready = []
        task = self.provider.get_next_task()
        
        # 次のタスクを順次取得
        while task:
            ready.append(task)
            # 一時的に実行中にマーク（競合チェック用）
            task.status = TaskStatus.IN_PROGRESS
            task = self.provider.get_next_task()
        
        # ステータスを戻す
        for t in ready:
            t.status = TaskStatus.PENDING
        
        return ready
    
    def _get_task_files(self, task: Task) -> Set[str]:
        """
        タスクが扱うファイルの集合を取得
        
        target_files と related_files の両方を含む
        """
        files = set(task.target_files)
        
        # 依存タスクの成果物も含める（読み取り専用だが念のため）
        for dep_id in task.dependencies:
            dep_task = self.provider.coordinator.get_task(dep_id)
            if dep_task and dep_task.artifacts:
                files.update(dep_task.artifacts)
        
        return files
```

---

## 🧪 テストコード

### ファイル: `tests/test_task_provider.py`

```python
"""
TaskProviderのユニットテスト
"""
import pytest
from pathlib import Path
import tempfile
import shutil
from cmw.task_provider import TaskProvider
from cmw.models import Task, TaskStatus


@pytest.fixture
def test_project():
    """テスト用プロジェクトを作成"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # ディレクトリ構造を作成
    (temp_dir / "shared/coordination").mkdir(parents=True)
    (temp_dir / "shared/docs").mkdir(parents=True)
    (temp_dir / "shared/artifacts").mkdir(parents=True)
    
    # tasks.jsonを作成
    tasks = {
        "tasks": [
            {
                "id": "TASK-001",
                "title": "タスク1",
                "description": "説明1",
                "dependencies": [],
                "target_files": ["file1.py"],
                "priority": "high"
            },
            {
                "id": "TASK-002",
                "title": "タスク2",
                "description": "説明2",
                "dependencies": ["TASK-001"],
                "target_files": ["file2.py"],
                "priority": "medium"
            }
        ]
    }
    
    import json
    (temp_dir / "shared/coordination/tasks.json").write_text(
        json.dumps(tasks, indent=2)
    )
    
    yield temp_dir
    
    # クリーンアップ
    shutil.rmtree(temp_dir)


def test_get_next_task_returns_independent_task_first(test_project):
    """依存関係のないタスクが先に返される"""
    provider = TaskProvider(test_project)
    
    task = provider.get_next_task()
    
    assert task is not None
    assert task.id == "TASK-001"
    assert len(task.dependencies) == 0


def test_get_next_task_respects_dependencies(test_project):
    """依存関係を尊重する"""
    provider = TaskProvider(test_project)
    
    # TASK-001を完了
    provider.mark_completed("TASK-001", ["file1.py"])
    
    # 次はTASK-002が返される
    task = provider.get_next_task()
    assert task.id == "TASK-002"


def test_mark_completed_updates_status(test_project):
    """完了マークでステータスが更新される"""
    provider = TaskProvider(test_project)
    
    task = provider.coordinator.get_task("TASK-001")
    assert task.status == TaskStatus.PENDING
    
    provider.mark_completed("TASK-001", ["file1.py"])
    
    assert task.status == TaskStatus.COMPLETED
    assert task.artifacts == ["file1.py"]
    assert task.completed_at is not None


def test_mark_failed_blocks_dependent_tasks(test_project):
    """失敗すると依存タスクがブロックされる"""
    provider = TaskProvider(test_project)
    
    provider.mark_failed("TASK-001", "テストエラー")
    
    task2 = provider.coordinator.get_task("TASK-002")
    assert task2.status == TaskStatus.BLOCKED
```

---

## ✅ 実装チェックリスト

### Phase 1.1: TaskProvider
- [ ] `src/cmw/task_provider.py` を作成
- [ ] `get_next_task()` 実装
- [ ] `get_task_context()` 実装
- [ ] `mark_completed()` 実装
- [ ] `mark_failed()` 実装
- [ ] ユニットテスト作成
- [ ] 動作確認

### Phase 1.2: StateManager
- [ ] `src/cmw/state_manager.py` を作成
- [ ] `acquire_lock()` 実装
- [ ] `release_lock()` 実装
- [ ] `SessionContext` 実装
- [ ] ユニットテスト作成
- [ ] 動作確認

### Phase 1.3: ParallelExecutor
- [ ] `src/cmw/parallel_executor.py` を作成
- [ ] `get_executable_tasks()` 実装
- [ ] `can_run_parallel()` 実装
- [ ] ユニットテスト作成
- [ ] 動作確認

---

## 🚀 次のステップ

Phase 1完了後:
1. GitHubにコミット
2. Phase 2.1（Claude Code統合）へ
3. エンドツーエンドテスト

---

**Phase 1を完成させて、Claude Codeとの統合準備を整えましょう！** 🎉
