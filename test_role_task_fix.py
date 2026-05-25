#!/usr/bin/env python3
"""
测试任务申领的角色限制修复
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from autoswarm.core.pools import DynamicRolePool, DynamicTaskPool
from autoswarm.core.models import Role, Task


def test_task_claim_without_role():
    """测试没有角色时无法申领任务"""
    print("=" * 60)
    print("测试 1: 无角色时申领任务")
    print("=" * 60)
    
    role_pool = DynamicRolePool()
    task_pool = DynamicTaskPool(role_pool=role_pool)
    
    # 添加测试任务
    test_task = Task(
        task_id="task_test",
        title="测试任务",
        description="测试描述",
        requirements="测试需求"
    )
    task_pool.add_task(test_task, "agent_initial")
    
    # 尝试在没有角色的情况下申领任务 - 应该失败
    result = task_pool.claim("agent_123", "task_test")
    print(f"无角色时申领任务: {'失败' if not result else '成功'}")
    assert not result, "无角色时应该无法申领任务"
    print("✅ PASS: 无角色时无法申领任务")
    
    print()


def test_task_claim_with_role():
    """测试有角色时可以申领任务"""
    print("=" * 60)
    print("测试 2: 有角色时申领任务")
    print("=" * 60)
    
    role_pool = DynamicRolePool()
    task_pool = DynamicTaskPool(role_pool=role_pool)
    
    # 添加测试角色
    test_role = Role(
        role_id="role_developer",
        name="开发者",
        description="测试开发者",
        system_prompt="测试提示词"
    )
    role_pool.add_role(test_role, "agent_initial")
    
    # 添加测试任务
    test_task = Task(
        task_id="task_test",
        title="测试任务",
        description="测试描述",
        requirements="测试需求"
    )
    task_pool.add_task(test_task, "agent_initial")
    
    # 先申领角色
    role_result = role_pool.claim("agent_456", "role_developer")
    print(f"申领角色: {'成功' if role_result else '失败'}")
    assert role_result, "角色申领应该成功"
    
    # 然后申领任务 - 应该成功
    task_result = task_pool.claim("agent_456", "task_test")
    print(f"有角色时申领任务: {'成功' if task_result else '失败'}")
    assert task_result, "有角色时应该可以申领任务"
    print("✅ PASS: 有角色时可以正常申领任务")
    
    print()


def test_task_claim_by_other_agent():
    """测试任务已被其他Agent申领时的情况"""
    print("=" * 60)
    print("测试 3: 任务已被他人申领")
    print("=" * 60)
    
    role_pool = DynamicRolePool()
    task_pool = DynamicTaskPool(role_pool=role_pool)
    
    # 添加测试角色和任务
    role1 = Role(role_id="role1", name="角色1", description="测试", system_prompt="")
    role2 = Role(role_id="role2", name="角色2", description="测试", system_prompt="")
    role_pool.add_role(role1, "agent_initial")
    role_pool.add_role(role2, "agent_initial")
    
    task1 = Task(task_id="task1", title="任务1", description="", requirements="")
    task_pool.add_task(task1, "agent_initial")
    
    # Agent A 申领角色和任务
    role_pool.claim("agent_a", "role1")
    result_a = task_pool.claim("agent_a", "task1")
    assert result_a, "Agent A应该可以申领任务"
    print("Agent A 成功申领任务")
    
    # Agent B 也申领了角色，然后尝试申领同一个任务 - 应该失败
    role_pool.claim("agent_b", "role2")
    result_b = task_pool.claim("agent_b", "task1")
    print(f"Agent B 申领同一个任务: {'失败' if not result_b else '成功'}")
    assert not result_b, "Agent B应该无法申领已被A申领的任务"
    print("✅ PASS: 任务互斥机制正常")
    
    print()


def main():
    print()
    print("🎯 AutoSwarm 角色任务申领限制测试")
    print()
    
    try:
        test_task_claim_without_role()
        test_task_claim_with_role()
        test_task_claim_by_other_agent()
        
        print("=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
