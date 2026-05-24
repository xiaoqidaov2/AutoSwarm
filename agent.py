from typing import List, Optional, Dict
from langchain_openai import ChatOpenAI
from models import StepInfo, StepResult
from pools import DynamicRolePool, DynamicTaskPool, DynamicToolPool
from message_bus import MessageBus
from tools import (
    ClaimRoleTool, ClaimTaskTool, ClaimToolTool,
    SendMessageTool, PublishRoleTool, PublishTaskTool,
    ListRolesTool, UpdateRoleTool, DeleteRoleTool,
    ListTasksTool, UpdateTaskTool, DeleteTaskTool,
    ListToolsTool, UpdateToolTool, DeleteToolTool,
    ExecuteCommandTool, WriteFileTool
)
import uuid
import json
import re


class SimpleMemory:
    def __init__(self):
        self.messages: List[Dict] = []

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})

    def add_ai_message(self, content: str):
        self.messages.append({"role": "assistant", "content": content})

    def add_system_message(self, content: str):
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0]["content"] += "\n" + content
        else:
            self.messages.insert(0, {"role": "system", "content": content})

    def get_messages(self) -> List[Dict]:
        return self.messages

    def get_token_count(self) -> int:
        return sum(len(str(msg["content"])) for msg in self.messages)


class Agent:
    def __init__(
        self,
        agent_id: str,
        llm: ChatOpenAI,
        role_pool: DynamicRolePool,
        task_pool: DynamicTaskPool,
        tool_pool: DynamicToolPool,
        message_bus: MessageBus
    ):
        self.agent_id = agent_id
        self.llm = llm
        self.role_pool = role_pool
        self.task_pool = task_pool
        self.tool_pool = tool_pool
        self.message_bus = message_bus
        self.alive = True

        self.memory = SimpleMemory()

        self.builtin_tools = self._init_builtin_tools()
        self.public_tools = self._init_public_tools()
        self.all_tools = {tool.name: tool for tool in self.builtin_tools + self.public_tools}

        self.system_prompt = f"""你是一个自主运行的Agent，在一个多Agent系统中工作。
系统以固定步数（step）推进，每一步你需要基于当前状态做出决策。

你的ID是: {self.agent_id}

你可以使用以下工具：
1. list_roles() - 列出所有可用的角色
2. list_tasks() - 列出所有可用的任务
3. list_tools() - 列出所有可用的工具
4. claim_role(role_id) - 申领角色
5. claim_task(task_id) - 申领任务
6. claim_tool(tool_id) - 申领工具
7. send_message(content, receiver_id, broadcast) - 发送消息
   - 点对点消息：send_message("你好", "agent_abc123", False)
   - 广播消息：send_message("大家好", None, True)
8. publish_role(name, description, system_prompt) - 发布新角色
9. publish_task(title, description, requirements) - 发布新任务
10. execute_command(command) - 执行终端命令
11. write_file(filename, content) - 写文件到磁盘

使用工具的格式：工具名(参数1, 参数2)
多个工具调用用换行分隔。

示例：
list_roles()
claim_role(role_leader)
send_message("大家好！", None, True)  # 广播
send_message("我们可以合作", "agent_abc123", False)  # 点对点
write_file("test.txt", "Hello World")
execute_command("ls -la")

请优先使用点对点消息进行具体沟通，只在必要时使用广播！
你的目标是与其他Agent协作完成任务。"""

    def _init_builtin_tools(self):
        return [
            ClaimRoleTool(role_pool=self.role_pool, agent_id=self.agent_id),
            ClaimTaskTool(task_pool=self.task_pool, agent_id=self.agent_id),
            ClaimToolTool(tool_pool=self.tool_pool, agent_id=self.agent_id),
            SendMessageTool(message_bus=self.message_bus, agent_id=self.agent_id),
            PublishRoleTool(role_pool=self.role_pool, agent_id=self.agent_id),
            PublishTaskTool(task_pool=self.task_pool, agent_id=self.agent_id),
        ]

    def _init_public_tools(self):
        return [
            ListRolesTool(role_pool=self.role_pool),
            UpdateRoleTool(role_pool=self.role_pool, agent_id=self.agent_id),
            DeleteRoleTool(role_pool=self.role_pool, agent_id=self.agent_id),
            ListTasksTool(task_pool=self.task_pool),
            UpdateTaskTool(task_pool=self.task_pool, agent_id=self.agent_id),
            DeleteTaskTool(task_pool=self.task_pool, agent_id=self.agent_id),
            ListToolsTool(tool_pool=self.tool_pool),
            UpdateToolTool(tool_pool=self.tool_pool, agent_id=self.agent_id),
            DeleteToolTool(tool_pool=self.tool_pool, agent_id=self.agent_id),
            ExecuteCommandTool(),
            WriteFileTool(),
        ]

    def get_available_tools(self):
        claimed_tools_info = self.tool_pool.get_agent_tools(self.agent_id)
        all_tools = self.builtin_tools + self.public_tools
        return all_tools

    def get_context_token_count(self) -> int:
        return self.memory.get_token_count()

    def _parse_tool_calls(self, text: str) -> List[tuple]:
        tool_calls = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            match = re.match(r'^(\w+)\((.*)\)$', line)
            if not match:
                continue
                
            tool_name = match.group(1)
            args_str = match.group(2)
            
            args = []
            kwargs = {}
            
            if args_str:
                current = ""
                in_quotes = False
                quote_char = ""
                i = 0
                while i < len(args_str):
                    char = args_str[i]
                    if char in ('"', "'"):
                        if not in_quotes:
                            in_quotes = True
                            quote_char = char
                            current += char
                        elif char == quote_char:
                            in_quotes = False
                            quote_char = ""
                            current += char
                        else:
                            current += char
                    elif char == ',' and not in_quotes:
                        if current.strip():
                            args.append(current.strip())
                        current = ""
                    else:
                        current += char
                    i += 1
                
                if current.strip():
                    args.append(current.strip())
                
                final_args = []
                for arg in args:
                    arg = arg.strip()
                    if '=' in arg and not (arg.startswith('"') or arg.startswith("'")):
                        key, value = arg.split('=', 1)
                        kwargs[key.strip()] = value.strip().strip('"\'')
                    else:
                        final_args.append(arg.strip('"\''))
                args = final_args
            
            tool_calls.append((tool_name, args, kwargs))
        return tool_calls

    def _call_tool(self, tool_name: str, args: List, kwargs: Dict) -> str:
        if tool_name not in self.all_tools:
            return f"错误: 未知工具 {tool_name}"
        tool = self.all_tools[tool_name]
        try:
            if len(args) > 0:
                result = tool._run(*args)
            elif len(kwargs) > 0:
                result = tool._run(**kwargs)
            else:
                result = tool._run()
            return str(result)
        except Exception as e:
            import traceback
            return f"工具执行错误: {str(e)}\n{traceback.format_exc()}"

    def step(self, step_info: StepInfo) -> StepResult:
        if not self.alive:
            return StepResult(
                agent_id=self.agent_id,
                completed=False,
                output="Agent已停止"
            )

        self.memory.add_system_message(
            f"\n\n当前步骤: {step_info.current_step}/{step_info.max_step}"
        )

        messages = self.message_bus.receive(self.agent_id, step_info.current_step)
        for msg in messages:
            prefix = "广播消息" if msg.broadcast else "消息"
            self.memory.add_user_message(
                f"\n\n{prefix} 来自 {msg.sender_id}: {msg.content}"
            )

        messages_for_llm = [
            {"role": "system", "content": self.system_prompt}
        ] + [{"role": msg["role"], "content": msg["content"]} for msg in self.memory.get_messages()]

        output = ""

        try:
            response = self.llm.invoke(messages_for_llm)

            if hasattr(response, 'content') and response.content:
                output = response.content
                self.memory.add_ai_message(output)

                tool_calls = self._parse_tool_calls(output)
                for tool_name, args, kwargs in tool_calls:
                    tool_result = self._call_tool(tool_name, args, kwargs)
                    self.memory.add_user_message(
                        f"\n\n[调用工具 {tool_name}]\n结果: {tool_result}"
                    )
                    output += f"\n\n[调用工具 {tool_name}]\n结果: {tool_result}"
            else:
                output = "Agent未返回有效响应"
                self.memory.add_ai_message(output)

        except Exception as e:
            output = f"执行出错: {str(e)}"
            self.memory.add_ai_message(output)

        return StepResult(
            agent_id=self.agent_id,
            completed=True,
            output=output
        )


class AgentLifecycleManager:
    def __init__(
        self,
        llm: ChatOpenAI,
        role_pool: DynamicRolePool,
        task_pool: DynamicTaskPool,
        tool_pool: DynamicToolPool,
        message_bus: MessageBus
    ):
        self.llm = llm
        self.role_pool = role_pool
        self.task_pool = task_pool
        self.tool_pool = tool_pool
        self.message_bus = message_bus
        self.agents: dict[str, Agent] = {}
        self.max_token_limit: int = 32000

    def create_agents(self, count: int) -> List[Agent]:
        new_agents = []
        for i in range(count):
            agent_id = f"agent_{str(uuid.uuid4())[:8]}"
            agent = Agent(
                agent_id=agent_id,
                llm=self.llm,
                role_pool=self.role_pool,
                task_pool=self.task_pool,
                tool_pool=self.tool_pool,
                message_bus=self.message_bus
            )
            self.agents[agent_id] = agent
            new_agents.append(agent)
        return new_agents

    def check_and_destroy_overlimit_agents(self) -> List[str]:
        destroyed = []
        for agent_id, agent in list(self.agents.items()):
            token_count = agent.get_context_token_count()
            if token_count > self.max_token_limit * 0.8:
                agent.alive = False
                destroyed.append(agent_id)
        for agent_id in destroyed:
            del self.agents[agent_id]
        return destroyed

    def destroy_all_agents(self) -> None:
        for agent in self.agents.values():
            agent.alive = False
        self.agents.clear()

    def get_alive_agents(self) -> List[Agent]:
        return [a for a in self.agents.values() if a.alive]
