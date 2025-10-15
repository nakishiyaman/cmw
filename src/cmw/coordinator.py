"""
Coordinator - オーケストレーションの中核
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import yaml

from .models import (
    WorkerConfig, Task, WorkerProgress, ProjectProgress,
    Decision, TaskStatus, WorkerStatus, TaskPriority, ProjectConfig
)
from .workers import WorkerInstance
from .utils import DocumentParser, ConsistencyChecker, Logger


class Coordinator:
    """
    プロジェクト全体を統括するCoordinator
    """
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.shared_path = project_path / "shared"
        self.docs_path = self.shared_path / "docs"
        self.coordination_path = self.shared_path / "coordination"
        self.artifacts_path = self.shared_path / "artifacts"
        
        self.logger = Logger(self.coordination_path / "coordinator.log")
        self.doc_parser = DocumentParser(self.docs_path)
        self.consistency_checker = ConsistencyChecker(
            self.docs_path, 
            self.artifacts_path
        )
        
        self.config: Optional[ProjectConfig] = None
        self.workers: Dict[str, WorkerInstance] = {}
        self.tasks: Dict[str, Task] = {}
        self.decisions: List[Decision] = []
        
        self._ensure_directories()
        self.load_configuration()
    
    def _ensure_directories(self):
        """必要なディレクトリを作成"""
        for path in [self.docs_path, self.coordination_path, self.artifacts_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def load_configuration(self):
        """設定ファイルを読み込み"""
        config_file = self.project_path / "workers-config.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {config_file}")
        
        with open(config_file) as f:
            config_data = yaml.safe_load(f)
        
        self.config = ProjectConfig(**config_data)
        self.logger.info(f"プロジェクト: {self.config.project_name}")
        self.logger.info(f"ワーカー数: {len(self.config.workers)}")
        
        self.initialize_workers()
        self.build_dependency_graph()
    
    def initialize_workers(self):
        """ワーカーを初期化"""
        if not self.config:
            raise RuntimeError("設定が読み込まれていません")
        
        for worker_config in self.config.workers:
            if worker_config.id == 'coordinator':
                continue  # 自分自身はスキップ
            
            worker = WorkerInstance(
                config=worker_config,
                shared_path=self.shared_path
            )
            self.workers[worker.id] = worker
            self.logger.info(f"✓ ワーカー初期化: {worker.id} ({worker.role})")
    
    def build_dependency_graph(self):
        """依存関係グラフを構築"""
        if not self.config:
            return
        
        if not self.config.dependency_graph:
            # 自動生成
            dep_graph = {}
            for worker_id, worker in self.workers.items():
                dep_graph[worker_id] = {
                    'depends_on': worker.depends_on,
                    'blocks': self._find_blocked_workers(worker_id)
                }
            self.config.dependency_graph = dep_graph
        
        self.logger.info("依存関係グラフを構築しました")
    
    def _find_blocked_workers(self, worker_id: str) -> List[str]:
        """このワーカーに依存している他のワーカーを検索"""
        blocked = []
        for other_id, other_worker in self.workers.items():
            if worker_id in other_worker.depends_on:
                blocked.append(other_id)
        return blocked
    
    def decompose_requirements(self) -> List[Task]:
        """要件を読み込んでタスクに分解（改善版）"""
        requirements_file = self.docs_path / "requirements.md"
        
        if not requirements_file.exists():
            self.logger.warning("requirements.md が見つかりません")
            return []
        
        # 要件を解析
        requirements = self.doc_parser.parse_requirements(requirements_file)
        
        # タスクに分解
        tasks = []
        task_counter = 1
        
        # セクションごとにタスクを生成
        for section in requirements.get('sections', []):
            # 機能要件のセクションのみを処理
            if self._is_feature_section(section):
                # このセクションから複数のタスクを生成することもある
                generated_tasks = self._generate_tasks_from_section(section, task_counter)
                tasks.extend(generated_tasks)
                task_counter += len(generated_tasks)
        
        # 依存関係を自動設定
        self._setup_task_dependencies(tasks)
        
        self.logger.info(f"{len(tasks)} 個のタスクを生成しました")
        return tasks
    
    def _is_feature_section(self, section: Dict[str, Any]) -> bool:
        """機能要件のセクションかどうかを判定"""
        title = section.get('title', '').lower()
        
        # 除外するセクション
        exclude_keywords = [
            'プロジェクト概要', '非機能要件', '技術スタック', 
            '画面一覧', '優先順位', 'phase'
        ]
        
        for keyword in exclude_keywords:
            if keyword.lower() in title:
                return False
        
        # 機能要件のキーワード
        include_keywords = ['機能', 'タスク', '管理', '認証', '検索', '表示']
        
        for keyword in include_keywords:
            if keyword in title:
                return True
        
        return False
    
    def _generate_tasks_from_section(self, section: Dict[str, Any], 
                                    start_counter: int) -> List[Task]:
        """セクションから複数のタスクを生成"""
        tasks = []
        title = section.get('title', '')
        
        # セクションの内容に応じてタスクを生成
        
        # 1. データベース関連タスク（最初に実行）
        if self._requires_database(section):
            task = Task(
                task_id=f"TASK-{start_counter:03d}",
                worker_id="database",
                title=f"データベース設計: {title}",
                priority=TaskPriority.HIGH,
                based_on=[f"/shared/docs/requirements.md#{section.get('id', '')}",
                         "/shared/docs/data-models.json"],
                instructions={
                    'section': title,
                    'description': '該当機能のデータモデルとマイグレーションを作成'
                },
                deliverables=[
                    "/shared/artifacts/database/migrations/",
                    "/shared/artifacts/database/models.py"
                ]
            )
            tasks.append(task)
            start_counter += 1
        
        # 2. バックエンドAPI タスク
        if self._requires_backend(section):
            task = Task(
                task_id=f"TASK-{start_counter:03d}",
                worker_id="backend",
                title=f"バックエンドAPI実装: {title}",
                priority=TaskPriority.HIGH,
                based_on=[f"/shared/docs/requirements.md#{section.get('id', '')}",
                         "/shared/docs/api-specification.yaml"],
                instructions={
                    'section': title,
                    'description': '該当機能のREST APIエンドポイントを実装'
                },
                deliverables=[
                    "/shared/artifacts/backend/routers/",
                    "/shared/artifacts/backend/crud/"
                ]
            )
            tasks.append(task)
            start_counter += 1
        
        # 3. フロントエンドUI タスク
        if self._requires_frontend(section):
            task = Task(
                task_id=f"TASK-{start_counter:03d}",
                worker_id="frontend",
                title=f"フロントエンドUI実装: {title}",
                priority=TaskPriority.NORMAL,
                based_on=[f"/shared/docs/requirements.md#{section.get('id', '')}",
                         "/shared/docs/api-specification.yaml"],
                instructions={
                    'section': title,
                    'description': '該当機能のUIコンポーネントを実装'
                },
                deliverables=[
                    "/shared/artifacts/frontend/src/pages/",
                    "/shared/artifacts/frontend/src/components/"
                ]
            )
            tasks.append(task)
            start_counter += 1
        
        return tasks
    
    def _requires_database(self, section: Dict[str, Any]) -> bool:
        """データベース設計が必要か判定"""
        title = section.get('title', '').lower()
        keywords = ['管理', '登録', '作成', '保存', 'crud', 'データ']
        return any(kw in title for kw in keywords)
    
    def _requires_backend(self, section: Dict[str, Any]) -> bool:
        """バックエンド実装が必要か判定"""
        # ほぼすべての機能要件でバックエンドが必要
        return True
    
    def _requires_frontend(self, section: Dict[str, Any]) -> bool:
        """フロントエンド実装が必要か判定"""
        title = section.get('title', '').lower()
        # 「画面」「表示」「UI」などがあればフロントエンド必要
        keywords = ['表示', '画面', 'ui', 'ユーザー', '一覧', '詳細', '編集', '作成']
        return any(kw in title for kw in keywords)
    
    def _setup_task_dependencies(self, tasks: List[Task]):
        """タスクの依存関係を自動設定"""
        # データベースタスクのID
        db_task_ids = [t.task_id for t in tasks if t.worker_id == "database"]
        
        # バックエンドタスクのID
        backend_task_ids = [t.task_id for t in tasks if t.worker_id == "backend"]
        
        for task in tasks:
            # バックエンドはデータベースに依存
            if task.worker_id == "backend" and db_task_ids:
                task.depends_on_tasks = db_task_ids.copy()
            
            # フロントエンドはバックエンドに依存
            elif task.worker_id == "frontend" and backend_task_ids:
                task.depends_on_tasks = backend_task_ids.copy()
            
            # テストはすべてに依存
            elif task.worker_id == "test":
                task.depends_on_tasks = [t.task_id for t in tasks 
                                        if t.worker_id != "test"]

    def _create_task_from_section(self, section: Dict[str, Any], counter: int) -> Optional[Task]:
        """要件セクションからタスクを生成"""
        # 適切なワーカーを見つける
        suitable_workers = self._find_suitable_workers_for_section(section)
        
        if not suitable_workers:
            return None
        
        worker_id = suitable_workers[0].id
        
        return Task(
            task_id=f"TASK-{counter:03d}",
            worker_id=worker_id,
            title=section.get('title', ''),
            priority=TaskPriority.NORMAL,
            based_on=[f"/shared/docs/requirements.md#{section.get('id', '')}"],
            instructions=section.get('content', {}),
            deliverables=[]
        )
    
    def _find_suitable_workers_for_section(self, section: Dict[str, Any]) -> List[WorkerInstance]:
        """セクションに適したワーカーを検索"""
        suitable = []
        keywords = section.get('keywords', [])
        
        for worker in self.workers.values():
            # キーワードと責任範囲のマッチング
            if any(kw in worker.responsibilities for kw in keywords):
                suitable.append(worker)
        
        return suitable
    
    def assign_tasks(self, tasks: List[Task]):
        """タスクをワーカーに割り当て"""
        for task in tasks:
            task.status = TaskStatus.ASSIGNED
            task.assigned_at = datetime.now()
            self.tasks[task.task_id] = task
            
            # ワーカーに通知
            worker = self.workers.get(task.worker_id)
            if worker:
                worker.assign_task(task)
                self.logger.info(f"✓ タスク割り当て: {task.title} → {task.worker_id}")
        
        # タスクファイルに保存
        self._save_tasks()
    
    def _save_tasks(self):
        """タスクをJSONファイルに保存"""
        tasks_file = self.coordination_path / "tasks.json"
        tasks_data = {
            "tasks": [task.model_dump(mode='json') for task in self.tasks.values()]
        }
        
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, indent=2, ensure_ascii=False, default=str)
    
    def check_progress(self) -> ProjectProgress:
        """全ワーカーの進捗をチェック"""
        progress = ProjectProgress(
            project_name=self.config.project_name if self.config else "Unknown",
            workers={}
        )
        
        for worker_id, worker in self.workers.items():
            worker_progress = worker.get_progress()
            progress.workers[worker_id] = worker_progress
        
        # 全体進捗を計算
        total_completion = sum(
            int(wp.completion.rstrip('%')) 
            for wp in progress.workers.values()
        )
        avg_completion = total_completion // len(progress.workers) if progress.workers else 0
        progress.overall_progress = f"{avg_completion}%"
        
        # 進捗ファイルに保存
        self._save_progress(progress)
        
        return progress
    
    def _save_progress(self, progress: ProjectProgress):
        """進捗をJSONファイルに保存"""
        progress_file = self.coordination_path / "progress.json"
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress.model_dump(mode='json'), f, indent=2, ensure_ascii=False, default=str)
    
    def identify_blockers(self) -> List[Dict[str, Any]]:
        """ブロッカーを特定"""
        blockers = []
        
        for worker_id, worker in self.workers.items():
            # 依存先の完了チェック
            for dep_worker_id in worker.depends_on:
                dep_worker = self.workers.get(dep_worker_id)
                if dep_worker and dep_worker.status != WorkerStatus.COMPLETED:
                    blockers.append({
                        'worker_id': worker_id,
                        'blocked_by': dep_worker_id,
                        'reason': f'{dep_worker_id} の作業が未完了'
                    })
        
        return blockers
    
    def check_consistency(self) -> Dict[str, Any]:
        """整合性をチェック"""
        self.logger.info("整合性チェックを開始")
        
        results = {
            'api': self.consistency_checker.check_api_consistency(),
            'data_models': self.consistency_checker.check_data_model_consistency(),
            'security': self.consistency_checker.check_security_compliance()
        }
        
        # 不一致があれば記録
        for check_type, inconsistencies in results.items():
            if inconsistencies:
                self.logger.warning(f"{check_type}: {len(inconsistencies)} 件の不一致")
        
        return results
    
    def make_decision(self, decision_text: str, based_on: List[Dict[str, str]], 
                     rationale: str) -> Decision:
        """意思決定を記録"""
        decision = Decision(
            id=f"DEC-{len(self.decisions) + 1:03d}",
            decision=decision_text,
            based_on=based_on,
            rationale=rationale
        )
        
        self.decisions.append(decision)
        self._save_decisions()
        
        return decision
    
    def _save_decisions(self):
        """意思決定ログを保存"""
        decisions_file = self.coordination_path / "decisions-log.json"
        decisions_data = {
            "decisions": [d.model_dump(mode='json') for d in self.decisions]
        }
        
        with open(decisions_file, 'w', encoding='utf-8') as f:
            json.dump(decisions_data, f, indent=2, ensure_ascii=False, default=str)
    
    def run(self, check_interval: int = 300):
        """Coordinatorのメインループ"""
        self.logger.info("Coordinator を起動します")
        
        # 初期タスク生成
        tasks = self.decompose_requirements()
        self.assign_tasks(tasks)
        
        try:
            while not self._all_completed():
                # 進捗確認
                progress = self.check_progress()
                self.logger.info(f"全体進捗: {progress.overall_progress}")
                
                # ブロッカー確認
                blockers = self.identify_blockers()
                if blockers:
                    self.logger.warning(f"{len(blockers)} 件のブロッカーを検出")
                    # TODO: ブロッカー解消ロジック
                
                # 整合性チェック
                consistency_results = self.check_consistency()
                
                # 待機
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            self.logger.info("Coordinator を停止します")
    
    def _all_completed(self) -> bool:
        """全タスクが完了したか"""
        return all(
            task.status == TaskStatus.COMPLETED 
            for task in self.tasks.values()
        )
