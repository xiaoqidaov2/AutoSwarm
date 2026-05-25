from typing import List, Optional, Dict
import json
import logging
from .models import Role, Task, ToolInfo


logger = logging.getLogger(__name__)


class DynamicRolePool:
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.claims: Dict[str, str] = {}
        self.agent_roles: Dict[str, str] = {}

    def load_seed_from_file(self, path: str) -> None:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for role_data in data:
                    role = Role(**role_data)
                    self.roles[role.role_id] = role
            logger.info(f"Loaded {len(data)} roles from {path}")
        except Exception as e:
            logger.warning(f"Failed to load roles seed: {e}")

    def add_role(self, role: Role, publisher_agent_id: str) -> bool:
        if role.role_id in self.roles:
            logger.warning(f"Role {role.role_id} already exists")
            return False
        role.publisher_agent_id = publisher_agent_id
        self.roles[role.role_id] = role
        logger.info(f"Added role {role.role_id} by agent {publisher_agent_id}")
        return True

    def update_role(self, role_id: str, new_role: Role) -> bool:
        if role_id not in self.roles:
            logger.warning(f"Role {role_id} not found for update")
            return False
        new_role.role_id = role_id
        new_role.publisher_agent_id = self.roles[role_id].publisher_agent_id
        self.roles[role_id] = new_role
        logger.info(f"Updated role {role_id}")
        return True

    def delete_role(self, role_id: str, requester_agent_id: str) -> bool:
        if role_id not in self.roles:
            logger.warning(f"Role {role_id} not found for deletion")
            return False
        if role_id in self.claims:
            agent_id = self.claims[role_id]
            del self.agent_roles[agent_id]
            del self.claims[role_id]
        del self.roles[role_id]
        logger.info(f"Deleted role {role_id} by agent {requester_agent_id}")
        return True

    def list_roles(self) -> List[Role]:
        return list(self.roles.values())

    def claim(self, agent_id: str, role_id: str) -> bool:
        if role_id not in self.roles:
            logger.warning(f"Role {role_id} not found for claiming")
            return False
        if role_id in self.claims:
            logger.warning(f"Role {role_id} already claimed")
            return False
        if agent_id in self.agent_roles:
            self.release(agent_id, self.agent_roles[agent_id])
        self.claims[role_id] = agent_id
        self.agent_roles[agent_id] = role_id
        logger.info(f"Agent {agent_id} claimed role {role_id}")
        return True

    def release(self, agent_id: str, role_id: str) -> bool:
        if role_id not in self.claims:
            return False
        if self.claims[role_id] != agent_id:
            return False
        del self.claims[role_id]
        del self.agent_roles[agent_id]
        logger.info(f"Agent {agent_id} released role {role_id}")
        return True

    def clear_all(self) -> None:
        self.roles.clear()
        self.claims.clear()
        self.agent_roles.clear()
        logger.info("Role pool cleared")


class DynamicTaskPool:
    def __init__(self, role_pool: Optional[DynamicRolePool] = None):
        self.tasks: Dict[str, Task] = {}
        self.claims: Dict[str, str] = {}
        self.agent_tasks: Dict[str, str] = {}
        self.role_pool = role_pool

    def load_seed_from_file(self, path: str) -> None:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for task_data in data:
                    task = Task(**task_data)
                    self.tasks[task.task_id] = task
            logger.info(f"Loaded {len(data)} tasks from {path}")
        except Exception as e:
            logger.warning(f"Failed to load tasks seed: {e}")

    def add_task(self, task: Task, publisher_agent_id: str) -> bool:
        if task.task_id in self.tasks:
            logger.warning(f"Task {task.task_id} already exists")
            return False
        task.publisher_agent_id = publisher_agent_id
        self.tasks[task.task_id] = task
        logger.info(f"Added task {task.task_id} by agent {publisher_agent_id}")
        return True

    def update_task(self, task_id: str, new_task: Task) -> bool:
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found for update")
            return False
        new_task.task_id = task_id
        new_task.publisher_agent_id = self.tasks[task_id].publisher_agent_id
        self.tasks[task_id] = new_task
        logger.info(f"Updated task {task_id}")
        return True

    def delete_task(self, task_id: str, requester_agent_id: str) -> bool:
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found for deletion")
            return False
        if task_id in self.claims:
            agent_id = self.claims[task_id]
            del self.agent_tasks[agent_id]
            del self.claims[task_id]
        del self.tasks[task_id]
        logger.info(f"Deleted task {task_id} by agent {requester_agent_id}")
        return True

    def list_tasks(self) -> List[Task]:
        return list(self.tasks.values())

    def claim(self, agent_id: str, task_id: str) -> bool:
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found for claiming")
            return False
        if task_id in self.claims:
            logger.warning(f"Task {task_id} already claimed")
            return False
        # 检查是否已申领角色
        if self.role_pool and agent_id not in self.role_pool.agent_roles:
            logger.warning(f"Agent {agent_id} must claim a role first before claiming task {task_id}")
            return False
        if agent_id in self.agent_tasks:
            self.release(agent_id, self.agent_tasks[agent_id])
        self.claims[task_id] = agent_id
        self.agent_tasks[agent_id] = task_id
        logger.info(f"Agent {agent_id} claimed task {task_id}")
        return True

    def release(self, agent_id: str, task_id: str) -> bool:
        if task_id not in self.claims:
            return False
        if self.claims[task_id] != agent_id:
            return False
        del self.claims[task_id]
        del self.agent_tasks[agent_id]
        logger.info(f"Agent {agent_id} released task {task_id}")
        return True

    def clear_all(self) -> None:
        self.tasks.clear()
        self.claims.clear()
        self.agent_tasks.clear()
        logger.info("Task pool cleared")


class DynamicToolPool:
    def __init__(self):
        self.tools: Dict[str, ToolInfo] = {}
        self.claims: Dict[str, List[str]] = {}
        self.agent_tools: Dict[str, List[str]] = {}

    def add_custom_tool(self, tool: ToolInfo, publisher_agent_id: Optional[str] = None) -> bool:
        if tool.tool_id in self.tools:
            logger.warning(f"Tool {tool.tool_id} already exists")
            return False
        tool.publisher_agent_id = publisher_agent_id
        self.tools[tool.tool_id] = tool
        self.claims[tool.tool_id] = []
        logger.info(f"Added tool {tool.tool_id} by agent {publisher_agent_id}")
        return True

    def update_custom_tool(self, tool_id: str, new_tool: ToolInfo) -> bool:
        if tool_id not in self.tools:
            logger.warning(f"Tool {tool_id} not found for update")
            return False
        new_tool.tool_id = tool_id
        new_tool.publisher_agent_id = self.tools[tool_id].publisher_agent_id
        self.tools[tool_id] = new_tool
        logger.info(f"Updated tool {tool_id}")
        return True

    def delete_custom_tool(self, tool_id: str, requester_agent_id: str) -> bool:
        if tool_id not in self.tools:
            logger.warning(f"Tool {tool_id} not found for deletion")
            return False
        for agent_id in self.claims.get(tool_id, []):
            if agent_id in self.agent_tools and tool_id in self.agent_tools[agent_id]:
                self.agent_tools[agent_id].remove(tool_id)
        del self.tools[tool_id]
        if tool_id in self.claims:
            del self.claims[tool_id]
        logger.info(f"Deleted tool {tool_id} by agent {requester_agent_id}")
        return True

    def list_tools(self) -> List[ToolInfo]:
        return list(self.tools.values())

    def claim(self, agent_id: str, tool_id: str) -> bool:
        if tool_id not in self.tools:
            logger.warning(f"Tool {tool_id} not found for claiming")
            return False
        if agent_id not in self.agent_tools:
            self.agent_tools[agent_id] = []
        if tool_id in self.agent_tools[agent_id]:
            return False
        self.agent_tools[agent_id].append(tool_id)
        if agent_id not in self.claims.get(tool_id, []):
            self.claims[tool_id].append(agent_id)
        logger.info(f"Agent {agent_id} claimed tool {tool_id}")
        return True

    def release(self, agent_id: str, tool_id: str) -> bool:
        if agent_id not in self.agent_tools:
            return False
        if tool_id not in self.agent_tools[agent_id]:
            return False
        self.agent_tools[agent_id].remove(tool_id)
        if tool_id in self.claims and agent_id in self.claims[tool_id]:
            self.claims[tool_id].remove(agent_id)
        logger.info(f"Agent {agent_id} released tool {tool_id}")
        return True

    def get_agent_tools(self, agent_id: str) -> List[ToolInfo]:
        tool_ids = self.agent_tools.get(agent_id, [])
        return [self.tools[tid] for tid in tool_ids if tid in self.tools]

    def clear_all_custom_tools(self) -> None:
        self.tools.clear()
        self.claims.clear()
        self.agent_tools.clear()
        logger.info("Tool pool cleared")
