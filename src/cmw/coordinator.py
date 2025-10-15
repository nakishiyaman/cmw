"""
コーディネーター機能

タスクの管理、依存関係の解決、プロンプト生成などを行います。
"""
import json
from pathlib import Path
from typing import Optional, List, Dict
from .models import Task, TaskStatus, Worker


class PromptGenerator:
    """タスク実行用のプロンプトを生成"""
    
    def __init__(self, project_path: Path):
        """
        プロンプトジェネレーターを初期化
        
        Args:
            project_path: プロジェクトのルートパス
        """
        self.project_path = project_path
        self.docs_path = project_path / "shared" / "docs"
        self.coordination_path = project_path / "shared" / "coordination"
        self.artifacts_path = project_path / "shared" / "artifacts"
    
    def generate_prompt(self, task: Task) -> str:
        """
        タスク実行用のプロンプトを生成
        
        Args:
            task: 実行するタスク
            
        Returns:
            生成されたプロンプト
        """
        # 関連ドキュメントを読み込む
        context = self._load_context(task)
        
        # プロンプトを構築
        prompt = f"""# タスク実行依頼

## タスク情報
- **ID**: {task.id}
- **タイトル**: {task.title}
- **説明**: {task.description}
- **担当ワーカー**: {task.assigned_to}
- **優先度**: {task.priority.value}

## 依存タスク
{self._format_dependencies(task)}

## プロジェクトコンテキスト
{context}

## 実装要件
{task.description}

## 指示
上記のタスク情報とコンテキストに基づいて、以下を実装してください：

1. **コードの実装**: 
   - タスクの要件を満たすコードを記述
   - ベストプラクティスに従う
   - 適切なエラーハンドリングを含める

2. **ファイル形式**:
   - コードブロックは ```python または ```typescript などの適切な言語指定を使用
   - 各ファイルには明確なファイルパスをコメントで記載

3. **成果物の配置**:
   - Backend: `shared/artifacts/backend/`
   - Frontend: `shared/artifacts/frontend/`
   - Database: `shared/artifacts/backend/core/`
   - Tests: `shared/artifacts/tests/`

実装を開始してください。
"""
        return prompt
    
    def _load_context(self, task: Task) -> str:
        """
        タスクに関連するコンテキスト情報を読み込む
        
        Args:
            task: タスク
            
        Returns:
            コンテキスト情報（文字列）
        """
        context_parts = []
        
        # requirements.md を読み込む
        requirements_file = self.docs_path / "requirements.md"
        if requirements_file.exists():
            with open(requirements_file, 'r', encoding='utf-8') as f:
                context_parts.append(f"### requirements.md\n{f.read()}\n")
        
        # API仕様書を読み込む
        api_spec_file = self.docs_path / "api-spec.md"
        if api_spec_file.exists():
            with open(api_spec_file, 'r', encoding='utf-8') as f:
                context_parts.append(f"### API仕様\n{f.read()}\n")
        
        return "\n".join(context_parts) if context_parts else "コンテキスト情報なし"
    
    def _format_dependencies(self, task: Task) -> str:
        """
        依存タスクをフォーマット
        
        Args:
            task: タスク
            
        Returns:
            フォーマットされた依存タスク情報
        """
        if not task.dependencies:
            return "依存タスクなし"
        
        return "\n".join([f"- {dep_id}" for dep_id in task.dependencies])


class Coordinator:
    """タスクの管理と調整を行うコーディネーター"""
    
    def __init__(self, project_path: Path):
        """
        コーディネーターを初期化
        
        Args:
            project_path: プロジェクトのルートパス
        """
        self.project_path = project_path
        self.tasks_file = project_path / "shared" / "coordination" / "tasks.json"
        self.progress_file = project_path / "shared" / "coordination" / "progress.json"
        self.tasks: Dict[str, Task] = {}
        self.workers: Dict[str, Worker] = {}
        
        # タスクとワーカーを読み込む
        self._load_tasks()
    
    def _load_tasks(self):
        """tasks.json からタスクを読み込む"""
        if not self.tasks_file.exists():
            return
        
        with open(self.tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # タスクを読み込む
            for task_data in data.get("tasks", []):
                task = Task.from_dict(task_data)
                self.tasks[task.id] = task
            
            # ワーカーを読み込む
            for worker_data in data.get("workers", []):
                worker = Worker(
                    id=worker_data["id"],
                    name=worker_data["name"],
                    description=worker_data["description"],
                    skills=worker_data.get("skills", []),
                    assigned_tasks=worker_data.get("assigned_tasks", [])
                )
                self.workers[worker.id] = worker
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        タスクを取得
        
        Args:
            task_id: タスクID
            
        Returns:
            タスク（存在しない場合はNone）
        """
        return self.tasks.get(task_id)
    
    def update_task_status(
        self, 
        task_id: str, 
        status: TaskStatus,
        error_message: Optional[str] = None,
        artifacts: Optional[List[str]] = None
    ):
        """
        タスクのステータスを更新
        
        Args:
            task_id: タスクID
            status: 新しいステータス
            error_message: エラーメッセージ（任意）
            artifacts: 生成されたファイルのリスト（任意）
        """
        task = self.tasks.get(task_id)
        if not task:
            return
        
        task.status = status
        task.error_message = error_message
        
        if artifacts:
            task.artifacts = artifacts
        
        if status == TaskStatus.COMPLETED:
            from datetime import datetime
            task.completed_at = datetime.now()
        
        # progress.json を更新
        self._save_progress()
    
    def _save_progress(self):
        """進捗状況を保存"""
        progress_data = {
            "tasks": [task.to_dict() for task in self.tasks.values()]
        }
        
        # ディレクトリが存在しない場合は作成
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, indent=2, ensure_ascii=False)
    
    def get_executable_tasks(self) -> List[Task]:
        """
        実行可能なタスクのリストを取得
        
        Returns:
            依存タスクが完了しており実行可能なタスクのリスト
        """
        executable = []
        
        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            
            # 依存タスクがすべて完了しているか確認
            dependencies_met = True
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    dependencies_met = False
                    break
            
            if dependencies_met:
                executable.append(task)
        
        return executable
