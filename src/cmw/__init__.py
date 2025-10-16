"""
Claude Multi-Worker Framework

マルチワーカーアーキテクチャでソフトウェア開発を自動化するフレームワーク
"""

__version__ = "0.1.0"

from .models import Task, TaskStatus, Worker, ExecutionResult, Priority
from .coordinator import Coordinator, PromptGenerator
from .task_provider import TaskProvider
from .state_manager import StateManager, SessionContext
from .parallel_executor import ParallelExecutor
from .error_handler import ErrorHandler, TaskFailureAction

__all__ = [
    "Task",
    "TaskStatus",
    "Worker",
    "ExecutionResult",
    "Priority",
    "Coordinator",
    "PromptGenerator",
    "TaskProvider",
    "StateManager",
    "SessionContext",
    "ParallelExecutor",
    "ErrorHandler",
    "TaskFailureAction",
]
