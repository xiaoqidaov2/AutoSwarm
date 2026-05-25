from typing import Optional, List
from langchain_openai import ChatOpenAI
import logging
from .models import StepInfo, StepResult
from .pools import DynamicRolePool, DynamicTaskPool, DynamicToolPool
from .message_bus import MessageBus
from .agent import AgentLifecycleManager, Agent
from .executor import ParallelExecutor


logger = logging.getLogger(__name__)


class StepCoordinator:
    def __init__(
        self,
        llm: ChatOpenAI,
        role_pool: DynamicRolePool,
        task_pool: DynamicTaskPool,
        tool_pool: DynamicToolPool,
        message_bus: MessageBus,
        lifecycle_manager: AgentLifecycleManager,
        enable_parallel: bool = True,
        max_parallel_workers: int = 5
    ):
        self.llm = llm
        self.role_pool = role_pool
        self.task_pool = task_pool
        self.tool_pool = tool_pool
        self.message_bus = message_bus
        self.lifecycle_manager = lifecycle_manager
        self.current_step: int = 0
        self.max_step: int = 0
        self.running: bool = False
        self.enable_parallel = enable_parallel
        if enable_parallel:
            self.executor = ParallelExecutor(max_workers=max_parallel_workers)

    def start_episode(
        self,
        max_step: int,
        agent_count: int,
        roles_seed_path: Optional[str] = None,
        tasks_seed_path: Optional[str] = None
    ) -> None:
        self.max_step = max_step
        self.current_step = 0
        self.running = True

        if roles_seed_path:
            self.role_pool.load_seed_from_file(roles_seed_path)
        if tasks_seed_path:
            self.task_pool.load_seed_from_file(tasks_seed_path)

        self.lifecycle_manager.create_agents(agent_count)
        logger.info(f"Episode started: {agent_count} agents, max steps {max_step}")
        print(f"系统启动: {agent_count} 个Agent, 最大步数 {max_step}, 并行执行: {self.enable_parallel}")

    def advance_step(self) -> bool:
        if not self.running:
            return False

        self.current_step += 1
        if self.current_step > self.max_step:
            self.global_terminate()
            return False

        print(f"\n=== 第 {self.current_step}/{self.max_step} 步 ===")
        logger.info(f"Step {self.current_step}/{self.max_step}")

        self.message_bus.set_current_step(self.current_step)
        step_info = StepInfo(
            current_step=self.current_step,
            max_step=self.max_step
        )

        alive_agents = self.lifecycle_manager.get_alive_agents()
        if not alive_agents:
            logger.warning("No alive agents, terminating")
            print("没有存活的Agent，系统终止")
            self.global_terminate()
            return False

        if self.enable_parallel and len(alive_agents) > 1:
            # 并行执行
            def agent_step_wrapper(agent):
                return agent.step(step_info)
            
            results = self.executor.execute_parallel(agent_step_wrapper, alive_agents)
            
            # 打印结果
            for agent, result in zip(alive_agents, results):
                if result:
                    print(f"\n[{agent.agent_id}]")
                    print(f"输出: {result.output}")
        else:
            # 串行执行（兼容旧方式）
            for agent in alive_agents:
                result = agent.step(step_info)
                print(f"\n[{agent.agent_id}]")
                print(f"输出: {result.output}")

        destroyed = self.lifecycle_manager.check_and_destroy_overlimit_agents()
        if destroyed:
            logger.warning(f"Agents destroyed due to token limit: {destroyed}")
            print(f"\nAgent上下文超限被销毁: {destroyed}")

        self.message_bus.clear_step(self.current_step)
        return True

    def wait_for_step_completion(self) -> None:
        pass

    def global_terminate(self) -> None:
        print("\n=== 系统终止 ===")
        logger.info("Global terminate called")
        self.running = False
        self.lifecycle_manager.destroy_all_agents()
        self.role_pool.clear_all()
        self.task_pool.clear_all()
        self.tool_pool.clear_all_custom_tools()
        self.message_bus.clear_all()
        logger.info("Episode terminated")
