"""测试核心数据模型"""
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from autoswarm import Role, Task, ToolInfo, StepInfo, StepResult, Message


def test_role_creation():
    """测试 Role 创建"""
    role = Role(
        name="测试角色",
        description="这是一个测试角色",
        system_prompt="你是一个测试助手"
    )
    assert role.name == "测试角色"
    assert role.description == "这是一个测试角色"
    assert role.system_prompt == "你是一个测试助手"
    assert role.role_id is not None
    assert role.publisher_agent_id is None


def test_task_creation():
    """测试 Task 创建"""
    task = Task(
        title="测试任务",
        description="这是一个测试任务",
        requirements="完成测试"
    )
    assert task.title == "测试任务"
    assert task.description == "这是一个测试任务"
    assert task.requirements == "完成测试"
    assert task.task_id is not None


def test_message_creation():
    """测试 Message 创建"""
    msg = Message(
        sender_id="agent_123",
        content="你好",
        step=1,
        receiver_id="agent_456",
        broadcast=False
    )
    assert msg.sender_id == "agent_123"
    assert msg.content == "你好"
    assert msg.step == 1
    assert msg.receiver_id == "agent_456"
    assert msg.broadcast is False


def test_step_info():
    """测试 StepInfo"""
    step_info = StepInfo(current_step=5, max_step=10)
    assert step_info.current_step == 5
    assert step_info.max_step == 10
