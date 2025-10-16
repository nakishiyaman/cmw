"""
Claude Multi-Worker Framework

マルチワーカーアーキテクチャでソフトウェア開発を自動化するフレームワーク
"""

__version__ = "0.1.0"

from .models import Task, TaskStatus, Worker, ExecutionResult, Priority
from .coordinator import Coordinator, PromptGenerator
from .task_provider import TaskProvider

__all__ = [
    "Task",
    "TaskStatus",
    "Worker",
    "ExecutionResult",
    "Priority",
    "Coordinator",
    "PromptGenerator",
    "TaskProvider",
]
