from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Role:
    name: str
    description: str
    system_prompt: str
    role_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    publisher_agent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Task:
    title: str
    description: str
    requirements: str
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    publisher_agent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0  # 0.0 - 1.0
    assigned_agent_id: Optional[str] = None
    completed_at: Optional[datetime] = None
    parent_task_id: Optional[str] = None  # 支持子任务


@dataclass
class ToolInfo:
    name: str
    description: str
    tool_type: str
    tool_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    publisher_agent_id: Optional[str] = None
    code: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentMetadata:
    agent_id: str
    role_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_active_step: int = 0
    status: str = "active"  # active, paused, destroyed


@dataclass
class StepInfo:
    current_step: int
    max_step: int


@dataclass
class StepResult:
    agent_id: str
    completed: bool
    output: str
    tool_calls: List[Dict] = field(default_factory=list)


@dataclass
class Message:
    sender_id: str
    content: str
    step: int
    receiver_id: Optional[str] = None
    broadcast: bool = False
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    priority: int = 0  # 数字越大优先级越高
    ttl: int = 3  # 消息存活步数
    topic: Optional[str] = None
    read_by: List[str] = field(default_factory=list)
