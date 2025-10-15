"""
Claude Multi-Worker Framework

マルチワーカーアーキテクチャでソフトウェア開発を自動化するフレームワーク
"""

__version__ = "0.1.0"

from .models import Task, TaskStatus, Worker, ExecutionResult, Priority
from .api_client import ClaudeAPIClient
from .coordinator import Coordinator, PromptGenerator
from .executor import TaskExecutor

__all__ = [
    "Task",
    "TaskStatus",
    "Worker",
    "ExecutionResult",
    "Priority",
    "ClaudeAPIClient",
    "Coordinator",
    "PromptGenerator",
    "TaskExecutor",
]
