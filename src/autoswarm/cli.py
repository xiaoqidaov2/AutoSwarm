#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_openai import ChatOpenAI
from autoswarm import (
    AutoSwarmConfig,
    setup_logger,
    get_logger,
    DynamicRolePool,
    DynamicTaskPool,
    DynamicToolPool,
    MessageBus,
    AgentLifecycleManager,
    StepCoordinator
)


def main():
    parser = argparse.ArgumentParser(description="步长驱动无主并行多Agent系统 - AutoSwarm v0.0.2")
    parser.add_argument("--agents", type=int, default=3, help="初始Agent数量 (默认: 3)")
    parser.add_argument("--max-steps", type=int, default=10, help="最大步数 (默认: 10)")
    parser.add_argument("--roles", type=str, default="roles.json", help="角色种子文件路径 (默认: roles.json)")
    parser.add_argument("--tasks", type=str, default="tasks.json", help="任务种子文件路径 (默认: tasks.json)")
    parser.add_argument("--model", type=str, default="deepseek-chat", help="模型名称 (默认: deepseek-chat)")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="日志级别")
    parser.add_argument("--log-file", type=str, default="logs/autoswarm.log", help="日志文件路径")
    parser.add_argument("--enable-parallel", action="store_true", default=True, help="启用并行执行 (默认: 启用)")
    parser.add_argument("--disable-parallel", action="store_false", dest="enable_parallel", help="禁用并行执行")
    parser.add_argument("--max-parallel-workers", type=int, default=5, help="最大并行工作线程数 (默认: 5)")
    parser.add_argument("--enable-retries", action="store_true", default=True, help="启用LLM重试 (默认: 启用)")
    parser.add_argument("--disable-retries", action="store_false", dest="enable_retries", help="禁用LLM重试")
    parser.add_argument("--max-retries", type=int, default=3, help="最大重试次数 (默认: 3)")
    parser.add_argument("--retry-base-delay", type=float, default=1.0, help="重试基础延迟秒数 (默认: 1.0)")

    args = parser.parse_args()

    # Load config
    config = AutoSwarmConfig.from_env()
    
    # Override with CLI args
    config.llm.model = args.model
    config.llm.enable_retries = args.enable_retries
    config.llm.max_retries = args.max_retries
    config.llm.retry_base_delay = args.retry_base_delay
    config.execution.enable_parallel_execution = args.enable_parallel
    config.execution.max_parallel_workers = args.max_parallel_workers
    if args.log_level:
        config.logging.level = args.log_level
    if args.log_file:
        config.logging.log_file = args.log_file

    # Setup logging
    setup_logger(config)
    logger = get_logger(__name__)
    logger.info("=" * 60)
    logger.info("AutoSwarm v0.0.2 启动")
    logger.info("=" * 60)

    # Check API key
    if not config.llm.api_key:
        logger.error("错误: 请设置 DEEPSEEK_API_KEY 或 OPENAI_API_KEY 环境变量")
        print("错误: 请设置 DEEPSEEK_API_KEY 或 OPENAI_API_KEY 环境变量")
        return 1

    # Initialize LLM
    llm = ChatOpenAI(
        model=config.llm.model,
        temperature=config.agent.temperature,
        api_key=config.llm.api_key,
        base_url=config.llm.base_url
    )

    # Initialize components
    role_pool = DynamicRolePool()
    task_pool = DynamicTaskPool(role_pool=role_pool)
    tool_pool = DynamicToolPool()
    message_bus = MessageBus()

    lifecycle_manager = AgentLifecycleManager(
        llm=llm,
        role_pool=role_pool,
        task_pool=task_pool,
        tool_pool=tool_pool,
        message_bus=message_bus,
        max_token_limit=config.agent.max_token_limit,
        enable_retries=config.llm.enable_retries,
        max_retries=config.llm.max_retries,
        retry_base_delay=config.llm.retry_base_delay
    )

    coordinator = StepCoordinator(
        llm=llm,
        role_pool=role_pool,
        task_pool=task_pool,
        tool_pool=tool_pool,
        message_bus=message_bus,
        lifecycle_manager=lifecycle_manager,
        enable_parallel=config.execution.enable_parallel_execution,
        max_parallel_workers=config.execution.max_parallel_workers
    )

    # Check and resolve seed file paths
    def resolve_path(path: str) -> str:
        if os.path.exists(path):
            return path
        # Try in current dir or parent dir
        base_dirs = [".", ".."]
        for base_dir in base_dirs:
            check_path = os.path.join(base_dir, path)
            if os.path.exists(check_path):
                return check_path
        return path if os.path.exists(path) else None

    roles_path = resolve_path(args.roles)
    tasks_path = resolve_path(args.tasks)

    # Start episode
    coordinator.start_episode(
        max_step=args.max_steps,
        agent_count=args.agents,
        roles_seed_path=roles_path,
        tasks_seed_path=tasks_path
    )

    try:
        while coordinator.advance_step():
            pass
    except KeyboardInterrupt:
        logger.info("用户中断，系统正在停止...")
        print("\n\n用户中断，系统正在停止...")
        coordinator.global_terminate()

    logger.info("AutoSwarm 结束")
    return 0


if __name__ == "__main__":
    sys.exit(main())
