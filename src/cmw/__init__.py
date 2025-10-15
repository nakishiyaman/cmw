"""
Claude Multi-Worker Framework
Document-Driven Multi-Agent Development Orchestration
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .coordinator import Coordinator
from .workers import WorkerInstance
from .models import (
    WorkerConfig,
    Task,
    WorkerProgress,
    ProjectProgress,
    Decision,
    WorkerType,
    WorkerStatus,
    TaskStatus,
    TaskPriority
)

__all__ = [
    "Coordinator",
    "WorkerInstance",
    "WorkerConfig",
    "Task",
    "WorkerProgress",
    "ProjectProgress",
    "Decision",
    "WorkerType",
    "WorkerStatus",
    "TaskStatus",
    "TaskPriority",
]
