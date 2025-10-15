"""
Core data models for Claude Multi-Worker Framework
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class WorkerType(str, Enum):
    """ワーカータイプ"""
    ORCHESTRATOR = "orchestrator"
    IMPLEMENTATION = "implementation"
    QUALITY_ASSURANCE = "quality_assurance"
    INFRASTRUCTURE = "infrastructure"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    COMPLIANCE = "compliance"


class WorkerStatus(str, Enum):
    """ワーカーの状態"""
    IDLE = "idle"
    WORKING = "working"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ERROR = "error"


class TaskStatus(str, Enum):
    """タスクの状態"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class TaskPriority(str, Enum):
    """タスクの優先度"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class WorkerConfig(BaseModel):
    """ワーカー設定"""
    id: str
    role: str
    type: WorkerType
    skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    reads: List[str] = Field(default_factory=list)
    writes: List[str] = Field(default_factory=list)
    depends_on: List[str] = Field(default_factory=list)
    priority: str = "normal"
    output_format: List[str] = Field(default_factory=list)


class Task(BaseModel):
    """タスク"""
    task_id: str
    worker_id: str
    title: str
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    based_on: List[str] = Field(default_factory=list)
    instructions: Dict[str, Any] = Field(default_factory=dict)
    deliverables: List[str] = Field(default_factory=list)
    depends_on_tasks: List[str] = Field(default_factory=list)
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None


class Blocker(BaseModel):
    """ブロッカー"""
    reason: str
    waiting_for: str
    estimated_unblock: Optional[datetime] = None


class WorkerProgress(BaseModel):
    """ワーカーの進捗"""
    worker_id: str
    status: WorkerStatus
    completion: str  # "70%" など
    current_task: Optional[str] = None
    completed_tasks: List[str] = Field(default_factory=list)
    blockers: List[Blocker] = Field(default_factory=list)
    last_update: datetime = Field(default_factory=datetime.now)

class ProjectProgress(BaseModel):
    """プロジェクト全体の進捗"""
    project_name: str
    updated_at: datetime = Field(default_factory=datetime.now)
    overall_progress: str = "0%"
    workers: Dict[str, WorkerProgress] = Field(default_factory=dict)
    milestones: Dict[str, Any] = Field(default_factory=dict)

class Decision(BaseModel):
    """意思決定のログ"""
    id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    decision: str
    based_on: List[Dict[str, str]] = Field(default_factory=list)
    rationale: str
    instructions_sent: Optional[str] = None
    action: Optional[str] = None


class InconsistencyReport(BaseModel):
    """整合性チェックレポート"""
    check_type: str  # "api", "data_model", "security" など
    timestamp: datetime = Field(default_factory=datetime.now)
    inconsistencies: List[Dict[str, Any]] = Field(default_factory=list)
    severity: str  # "critical", "high", "medium", "low"
    recommended_actions: List[str] = Field(default_factory=list)


class ProjectConfig(BaseModel):
    """プロジェクト設定"""
    project_name: str
    description: Optional[str] = None
    version: str = "1.0"
    settings: Dict[str, Any] = Field(default_factory=dict)
    workers: List[WorkerConfig] = Field(default_factory=list)
    dependency_graph: Dict[str, Any] = Field(default_factory=dict)
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
