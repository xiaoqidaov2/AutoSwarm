from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


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
