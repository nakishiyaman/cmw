"""
Claude Multi-Worker Framework

マルチワーカーアーキテクチャでソフトウェア開発を自動化するフレームワーク
"""

__version__ = "0.1.0"

from .models import Task, TaskStatus, Worker, ExecutionResult, Priority
from .coordinator import Coordinator
from .task_provider import TaskProvider
from .state_manager import StateManager, SessionContext
from .parallel_executor import ParallelExecutor
from .error_handler import ErrorHandler, TaskFailureAction
from .feedback import FeedbackManager
from .requirements_parser import RequirementsParser
from .conflict_detector import ConflictDetector, Conflict, ConflictType, ConflictSeverity
from .progress_tracker import ProgressTracker
from .dashboard import Dashboard

__all__ = [
    "Task",
    "TaskStatus",
    "Worker",
    "ExecutionResult",
    "Priority",
    "Coordinator",
    "TaskProvider",
    "StateManager",
    "SessionContext",
    "ParallelExecutor",
    "ErrorHandler",
    "TaskFailureAction",
    "FeedbackManager",
    "RequirementsParser",
    "ConflictDetector",
    "Conflict",
    "ConflictType",
    "ConflictSeverity",
    "ProgressTracker",
    "Dashboard",
]
