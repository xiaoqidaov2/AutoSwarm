"""测试动态池"""
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from autoswarm import (
    DynamicRolePool,
    DynamicTaskPool,
    DynamicToolPool,
    Role,
    Task,
    ToolInfo
)


def test_role_pool_basic():
    """测试角色池基本功能"""
    pool = DynamicRolePool()
    
    # 创建角色
    role = Role(
        name="测试角色",
        description="测试",
        system_prompt="测试"
    )
    
    # 添加角色
    success = pool.add_role(role, "agent_1")
    assert success is True
    
    # 列出角色
    roles = pool.list_roles()
    assert len(roles) == 1
    
    # 申领角色
    claim_success = pool.claim("agent_2", role.role_id)
    assert claim_success is True
    
    # 释放角色
    release_success = pool.release("agent_2", role.role_id)
    assert release_success is True
    
    # 删除角色
    delete_success = pool.delete_role(role.role_id, "agent_1")
    assert delete_success is True
    
    # 清空
    pool.clear_all()
    assert len(pool.list_roles()) == 0


def test_task_pool_basic():
    """测试任务池基本功能"""
    pool = DynamicTaskPool()
    
    task = Task(
        title="测试任务",
        description="测试",
        requirements="完成"
    )
    
    success = pool.add_task(task, "agent_1")
    assert success is True
    
    tasks = pool.list_tasks()
    assert len(tasks) == 1
    
    pool.clear_all()
    assert len(pool.list_tasks()) == 0


def test_tool_pool_basic():
    """测试工具池基本功能"""
    pool = DynamicToolPool()
    
    tool = ToolInfo(
        name="测试工具",
        description="测试工具",
        tool_type="custom"
    )
    
    success = pool.add_custom_tool(tool, "agent_1")
    assert success is True
    
    tools = pool.list_tools()
    assert len(tools) == 1
    
    pool.clear_all_custom_tools()
    assert len(pool.list_tools()) == 0
