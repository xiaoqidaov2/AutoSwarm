"""测试消息总线"""
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from autoswarm import MessageBus


def test_message_bus_basic():
    """测试消息总线基本功能"""
    bus = MessageBus()
    
    bus.set_current_step(1)
    
    # 发送消息
    msg_id = bus.send("agent_1", "agent_2", "你好", False)
    assert msg_id is not None
    
    # 接收消息
    messages = bus.receive("agent_2", 1)
    assert len(messages) == 1
    assert messages[0].content == "你好"
    
    # 发送广播
    broadcast_id = bus.send("agent_1", None, "大家好", True)
    messages2 = bus.receive("agent_3", 1)
    assert len(messages2) == 1
    
    # 清空当前步的消息
    bus.clear_step(1)
    
    # 清空所有
    bus.clear_all()
