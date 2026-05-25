from typing import Optional, Dict, Any
from langchain.tools import BaseTool
import subprocess
import os
import uuid
import logging
from .models import Role, Task, ToolInfo, TaskStatus
from .pools import DynamicRolePool, DynamicTaskPool, DynamicToolPool
from .message_bus import MessageBus


logger = logging.getLogger(__name__)


class ClaimRoleTool(BaseTool):
    name: str = "claim_role"
    description: str = "申领一个角色，一个角色同时只能被一个Agent申领。参数: role_id (字符串)"
    role_pool: DynamicRolePool
    agent_id: str

    def _run(self, role_id: str) -> str:
        success = self.role_pool.claim(self.agent_id, role_id)
        if success:
            return f"成功申领角色 {role_id}"
        else:
            return f"申领角色失败: {role_id} 可能不存在或已被申领"


class ClaimTaskTool(BaseTool):
    name: str = "claim_task"
    description: str = "申领一个任务，一个任务同时只能被一个Agent申领。参数: task_id (字符串)"
    task_pool: DynamicTaskPool
    agent_id: str

    def _run(self, task_id: str) -> str:
        success = self.task_pool.claim(self.agent_id, task_id)
        if success:
            return f"成功申领任务 {task_id}"
        else:
            return f"申领任务失败: {task_id} 可能不存在或已被申领"


class ClaimToolTool(BaseTool):
    name: str = "claim_tool"
    description: str = "申领一个工具。参数: tool_id (字符串)"
    tool_pool: DynamicToolPool
    agent_id: str

    def _run(self, tool_id: str) -> str:
        success = self.tool_pool.claim(self.agent_id, tool_id)
        if success:
            return f"成功申领工具 {tool_id}"
        else:
            return f"申领工具失败: {tool_id} 可能不存在"


class SendMessageTool(BaseTool):
    name: str = "send_message"
    description: str = "发送消息，支持点对点或广播。参数: content (字符串), receiver_id (可选字符串), broadcast (可选布尔值，默认False)"
    message_bus: MessageBus
    agent_id: str

    def _run(self, content: str, receiver_id: Optional[str] = None, broadcast: bool = False) -> str:
        message_id = self.message_bus.send(self.agent_id, receiver_id, content, broadcast)
        return f"消息已发送，ID: {message_id}"


class PublishRoleTool(BaseTool):
    name: str = "publish_role"
    description: str = "发布一个新角色到角色池。参数: name (字符串), description (字符串), system_prompt (字符串)"
    role_pool: DynamicRolePool
    agent_id: str

    def _run(self, name: str, description: str, system_prompt: str) -> str:
        role = Role(
            role_id=str(uuid.uuid4()),
            name=name,
            description=description,
            system_prompt=system_prompt
        )
        success = self.role_pool.add_role(role, self.agent_id)
        if success:
            return f"成功发布角色，ID: {role.role_id}"
        else:
            return "发布角色失败"


class PublishTaskTool(BaseTool):
    name: str = "publish_task"
    description: str = "发布一个新任务到任务池。参数: title (字符串), description (字符串), requirements (字符串)"
    task_pool: DynamicTaskPool
    agent_id: str

    def _run(self, title: str, description: str, requirements: str) -> str:
        task = Task(
            task_id=str(uuid.uuid4()),
            title=title,
            description=description,
            requirements=requirements
        )
        success = self.task_pool.add_task(task, self.agent_id)
        if success:
            return f"成功发布任务，ID: {task.task_id}"
        else:
            return "发布任务失败"


class ListRolesTool(BaseTool):
    name: str = "list_roles"
    description: str = "列出所有可用的角色。无参数。"
    role_pool: DynamicRolePool

    def _run(self) -> str:
        roles = self.role_pool.list_roles()
        if not roles:
            return "当前没有可用的角色"
        result = "可用角色:\n"
        for role in roles:
            result += f"  ID: {role.role_id}\n  名称: {role.name}\n  描述: {role.description}\n\n"
        return result


class UpdateRoleTool(BaseTool):
    name: str = "update_role"
    description: str = "更新一个角色。参数: role_id (字符串), name (字符串), description (字符串), system_prompt (字符串)"
    role_pool: DynamicRolePool
    agent_id: str

    def _run(self, role_id: str, name: str, description: str, system_prompt: str) -> str:
        role = Role(
            role_id=role_id,
            name=name,
            description=description,
            system_prompt=system_prompt
        )
        success = self.role_pool.update_role(role_id, role)
        if success:
            return f"成功更新角色 {role_id}"
        else:
            return "更新角色失败"


class DeleteRoleTool(BaseTool):
    name: str = "delete_role"
    description: str = "删除一个角色。参数: role_id (字符串)"
    role_pool: DynamicRolePool
    agent_id: str

    def _run(self, role_id: str) -> str:
        success = self.role_pool.delete_role(role_id, self.agent_id)
        if success:
            return f"成功删除角色 {role_id}"
        else:
            return "删除角色失败"


class ListTasksTool(BaseTool):
    name: str = "list_tasks"
    description: str = "列出所有可用的任务。无参数。"
    task_pool: DynamicTaskPool

    def _run(self) -> str:
        tasks = self.task_pool.list_tasks()
        if not tasks:
            return "当前没有可用的任务"
        result = "可用任务:\n"
        for task in tasks:
            result += f"  ID: {task.task_id}\n  标题: {task.title}\n  状态: {task.status.value}\n  进度: {task.progress:.0%}\n  描述: {task.description}\n\n"
        return result


class UpdateTaskTool(BaseTool):
    name: str = "update_task"
    description: str = "更新一个任务。参数: task_id (字符串), title (字符串), description (字符串), requirements (字符串)"
    task_pool: DynamicTaskPool
    agent_id: str

    def _run(self, task_id: str, title: str, description: str, requirements: str) -> str:
        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            requirements=requirements
        )
        success = self.task_pool.update_task(task_id, task)
        if success:
            return f"成功更新任务 {task_id}"
        else:
            return "更新任务失败"


class DeleteTaskTool(BaseTool):
    name: str = "delete_task"
    description: str = "删除一个任务。参数: task_id (字符串)"
    task_pool: DynamicTaskPool
    agent_id: str

    def _run(self, task_id: str) -> str:
        success = self.task_pool.delete_task(task_id, self.agent_id)
        if success:
            return f"成功删除任务 {task_id}"
        else:
            return "删除任务失败"


class ListToolsTool(BaseTool):
    name: str = "list_tools"
    description: str = "列出所有可用的工具。无参数。"
    tool_pool: DynamicToolPool

    def _run(self) -> str:
        tools = self.tool_pool.list_tools()
        if not tools:
            return "当前没有可用的自定义工具"
        result = "可用工具:\n"
        for tool in tools:
            result += f"  ID: {tool.tool_id}\n  名称: {tool.name}\n  描述: {tool.description}\n  类型: {tool.tool_type}\n\n"
        return result


class UpdateToolTool(BaseTool):
    name: str = "update_tool"
    description: str = "更新一个工具。参数: tool_id (字符串), name (字符串), description (字符串), tool_type (字符串), code (可选字符串)"
    tool_pool: DynamicToolPool
    agent_id: str

    def _run(self, tool_id: str, name: str, description: str, tool_type: str, code: Optional[str] = None) -> str:
        tool = ToolInfo(
            tool_id=tool_id,
            name=name,
            description=description,
            tool_type=tool_type,
            code=code
        )
        success = self.tool_pool.update_custom_tool(tool_id, tool)
        if success:
            return f"成功更新工具 {tool_id}"
        else:
            return "更新工具失败"


class DeleteToolTool(BaseTool):
    name: str = "delete_tool"
    description: str = "删除一个工具。参数: tool_id (字符串)"
    tool_pool: DynamicToolPool
    agent_id: str

    def _run(self, tool_id: str) -> str:
        success = self.tool_pool.delete_custom_tool(tool_id, self.agent_id)
        if success:
            return f"成功删除工具 {tool_id}"
        else:
            return "删除工具失败"


class ExecuteCommandTool(BaseTool):
    name: str = "execute_command"
    description: str = "在终端执行命令。参数: command (字符串)"

    def _run(self, command: str) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout
            if result.stderr:
                output += f"\n错误: {result.stderr}"
            return f"命令执行完成:\n{output}"
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return f"命令执行失败: {str(e)}"


class WriteFileTool(BaseTool):
    name: str = "write_file"
    description: str = "写文件内容到磁盘。参数: filename (字符串), content (字符串)"

    def _run(self, filename: str, content: str) -> str:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"File written: {filename}")
            return f"成功创建文件: {filename}"
        except Exception as e:
            logger.error(f"Write file failed: {e}")
            return f"写文件失败: {str(e)}"


class ReadFileTool(BaseTool):
    name: str = "read_file"
    description: str = "读取文件内容。参数: filename (字符串)"

    def _run(self, filename: str) -> str:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"File read: {filename}")
            return f"文件内容:\n{content}"
        except Exception as e:
            logger.error(f"Read file failed: {e}")
            return f"读文件失败: {str(e)}"


class ListDirectoryTool(BaseTool):
    name: str = "list_directory"
    description: str = "列出目录内容。参数: path (字符串，默认当前目录)"

    def _run(self, path: str = ".") -> str:
        try:
            items = os.listdir(path)
            result = f"目录 {path} 内容:\n"
            for item in items:
                item_path = os.path.join(path, item)
                item_type = "目录" if os.path.isdir(item_path) else "文件"
                result += f"  [{item_type}] {item}\n"
            logger.info(f"Directory listed: {path}")
            return result
        except Exception as e:
            logger.error(f"List directory failed: {e}")
            return f"列出目录失败: {str(e)}"


class UpdateTaskProgressTool(BaseTool):
    name: str = "update_task_progress"
    description: str = "更新任务进度和状态。参数: task_id (字符串), progress (0.0-1.0的浮点数), status (可选字符串: pending/in_progress/completed/failed/blocked)"
    task_pool: DynamicTaskPool
    agent_id: str

    def _run(self, task_id: str, progress: float, status: Optional[str] = None) -> str:
        try:
            task_status = None
            if status:
                status_map = {
                    "pending": TaskStatus.PENDING,
                    "in_progress": TaskStatus.IN_PROGRESS,
                    "completed": TaskStatus.COMPLETED,
                    "failed": TaskStatus.FAILED,
                    "blocked": TaskStatus.BLOCKED
                }
                task_status = status_map.get(status.lower())
            
            success = self.task_pool.update_task_status(
                task_id, 
                task_status or TaskStatus.IN_PROGRESS, 
                progress,
                self.agent_id
            )
            
            if success:
                return f"成功更新任务 {task_id} 进度到 {progress:.0%}"
            else:
                return "更新任务进度失败"
        except Exception as e:
            logger.error(f"Update task progress failed: {e}")
            return f"更新任务进度失败: {str(e)}"
