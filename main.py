#!/usr/bin/env python3
import argparse
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pools import DynamicRolePool, DynamicTaskPool, DynamicToolPool
from message_bus import MessageBus
from agent import AgentLifecycleManager
from coordinator import StepCoordinator


def main():
    parser = argparse.ArgumentParser(description="步长驱动无主并行多Agent系统")
    parser.add_argument("--agents", type=int, default=3, help="初始Agent数量 (默认: 3)")
    parser.add_argument("--max-steps", type=int, default=10, help="最大步数 (默认: 10)")
    parser.add_argument("--roles", type=str, default="roles.json", help="角色种子文件路径 (默认: roles.json)")
    parser.add_argument("--tasks", type=str, default="tasks.json", help="任务种子文件路径 (默认: tasks.json)")
    parser.add_argument("--model", type=str, default="deepseek-chat", help="模型名称 (默认: deepseek-chat)")

    args = parser.parse_args()

    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("错误: 请设置 DEEPSEEK_API_KEY 或 OPENAI_API_KEY 环境变量")
        return

    llm = ChatOpenAI(
        model=args.model,
        temperature=0.7,
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    role_pool = DynamicRolePool()
    task_pool = DynamicTaskPool()
    tool_pool = DynamicToolPool()
    message_bus = MessageBus()

    lifecycle_manager = AgentLifecycleManager(
        llm=llm,
        role_pool=role_pool,
        task_pool=task_pool,
        tool_pool=tool_pool,
        message_bus=message_bus
    )

    coordinator = StepCoordinator(
        llm=llm,
        role_pool=role_pool,
        task_pool=task_pool,
        tool_pool=tool_pool,
        message_bus=message_bus,
        lifecycle_manager=lifecycle_manager
    )

    coordinator.start_episode(
        max_step=args.max_steps,
        agent_count=args.agents,
        roles_seed_path=args.roles if os.path.exists(args.roles) else None,
        tasks_seed_path=args.tasks if os.path.exists(args.tasks) else None
    )

    try:
        while coordinator.advance_step():
            pass
    except KeyboardInterrupt:
        print("\n\n用户中断，系统正在停止...")
        coordinator.global_terminate()


if __name__ == "__main__":
    main()
