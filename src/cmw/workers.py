"""
Worker Instance - 個々のワーカーの実装
"""
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .models import WorkerConfig, Task, WorkerProgress, WorkerStatus, TaskStatus


class WorkerInstance:
    """
    個々のワーカーのインスタンス
    """
    
    def __init__(self, config: WorkerConfig, shared_path: Path):
        self.id = config.id
        self.role = config.role
        self.type = config.type
        self.skills = config.skills
        self.responsibilities = config.responsibilities
        self.reads = config.reads
        self.writes = config.writes
        self.depends_on = config.depends_on
        self.priority = config.priority
        self.output_format = config.output_format
        
        self.shared_path = shared_path
        self.status = WorkerStatus.IDLE
        self.assigned_tasks: List[Task] = []
        self.completed_tasks: List[str] = []
        self.current_task: Optional[Task] = None
    
    def assign_task(self, task: Task):
        """タスクを割り当てる"""
        self.assigned_tasks.append(task)
        
        if self.status == WorkerStatus.IDLE:
            self._start_next_task()
    
    def _start_next_task(self):
        """次のタスクを開始"""
        if not self.assigned_tasks:
            self.status = WorkerStatus.IDLE
            return
        
        # 優先度順にソート
        self.assigned_tasks.sort(
            key=lambda t: (t.priority.value, t.assigned_at or datetime.now())
        )
        
        self.current_task = self.assigned_tasks[0]
        self.current_task.status = TaskStatus.IN_PROGRESS
        self.current_task.started_at = datetime.now()
        self.status = WorkerStatus.WORKING
    
    def complete_task(self, task_id: str):
        """タスクを完了としてマーク"""
        task = next((t for t in self.assigned_tasks if t.task_id == task_id), None)
        
        if task:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            self.assigned_tasks.remove(task)
            self.completed_tasks.append(task_id)
            
            if self.current_task and self.current_task.task_id == task_id:
                self.current_task = None
            
            # 次のタスクを開始
            self._start_next_task()
    
    def get_progress(self) -> WorkerProgress:
        """現在の進捗を取得"""
        total_tasks = len(self.assigned_tasks) + len(self.completed_tasks)
        completed_count = len(self.completed_tasks)
        
        if total_tasks == 0:
            completion = "0%"
        else:
            completion = f"{int(completed_count / total_tasks * 100)}%"
        
        return WorkerProgress(
            worker_id=self.id,
            status=self.status,
            completion=completion,
            current_task=self.current_task.title if self.current_task else None,
            completed_tasks=self.completed_tasks,
            blockers=[]
        )
    
    def is_ready(self) -> bool:
        """ワーカーが準備できているか（依存関係が解決されているか）"""
        # TODO: 依存先のワーカーの状態をチェック
        return True
    
    def can_handle(self, task: Task) -> bool:
        """このワーカーがタスクを処理できるか"""
        # スキルマッチング
        if hasattr(task, 'required_skills'):
            required_skills = task.required_skills
            if not any(skill in self.skills for skill in required_skills):
                return False
        
        # 責任範囲マッチング
        if hasattr(task, 'keywords'):
            keywords = task.keywords
            if any(kw in self.responsibilities for kw in keywords):
                return True
        
        return True
