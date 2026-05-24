#!/usr/bin/env python3
"""
AutoSwarm 简单使用示例
展示如何在代码中使用 AutoSwarm 的 API
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from autoswarm import (
    AutoSwarmConfig,
    setup_logger,
    DynamicRolePool,
    DynamicTaskPool,
    DynamicToolPool,
    MessageBus,
    AgentLifecycleManager,
    StepCoordinator,
    Role,
    Task
)
from langchain_openai import ChatOpenAI


def simple_example():
    """简单使用示例"""
    print("=" * 60)
    print("AutoSwarm 简单使用示例")
    print("=" * 60)
    
    # 1. 加载配置
    config = AutoSwarmConfig.from_env()
    setup_logger(config)
    
    # 检查 API Key
    if not config.llm.api_key:
        print("错误: 请设置 DEEPSEEK_API_KEY 或 OPENAI_API_KEY 环境变量")
        return
    
    # 2. 初始化 LLM
    llm = ChatOpenAI(
        model=config.llm.model,
        temperature=config.agent.temperature,
        api_key=config.llm.api_key,
        base_url=config.llm.base_url
    )
    
    # 3. 初始化组件
    role_pool = DynamicRolePool()
    task_pool = DynamicTaskPool()
    tool_pool = DynamicToolPool()
    message_bus = MessageBus()
    
    # 4. 创建管理器和协调器
    lifecycle_manager = AgentLifecycleManager(
        llm=llm,
        role_pool=role_pool,
        task_pool=task_pool,
        tool_pool=tool_pool,
        message_bus=message_bus,
        max_token_limit=config.agent.max_token_limit
    )
    
    coordinator = StepCoordinator(
        llm=llm,
        role_pool=role_pool,
        task_pool=task_pool,
        tool_pool=tool_pool,
        message_bus=message_bus,
        lifecycle_manager=lifecycle_manager
    )
    
    # 5. 手动添加一些角色和任务（演示用）
    leader_role = Role(
        name="团队领导",
        description="负责协调团队工作",
        system_prompt="你是一个团队领导，负责协调工作"
    )
    role_pool.add_role(leader_role, "system")
    
    example_task = Task(
        title="简单演示任务",
        description="这是一个简单的演示任务",
        requirements="完成演示"
    )
    task_pool.add_task(example_task, "system")
    
    # 6. 启动系统（这里仅演示初始化，不实际运行，避免消耗 API）
    print("\n✅ 系统初始化成功！")
    print(f"   - 配置已加载")
    print(f"   - 组件已初始化")
    print(f"   - 角色池中有 {len(role_pool.list_roles())} 个角色")
    print(f"   - 任务池中有 {len(task_pool.list_tasks())} 个任务")
    print("\n要实际运行系统，请使用 CLI:")
    print("  autoswarm --agents 3 --max-steps 10")
    print("\n或使用 Python 运行:")
    print("  python main.py --agents 3 --max-steps 10")


if __name__ == "__main__":
    simple_example()
