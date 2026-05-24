# AutoSwarm v0.0.2 优化方案和功能设计

## 1. 现状分析 (v0.0.1)

### 1.1 当前核心功能
- ✅ 完全同步时间步的无主多 Agent 系统
- ✅ 动态三池（角色池、任务池、工具池）
- ✅ Agent 可以发布/修改/删除角色、任务和工具
- ✅ Agent 可以互相通信（点对点或广播）
- ✅ 内置工具支持（命令执行、文件写入等）
- ✅ 简单的内存管理

### 1.2 存在的问题和局限性

#### 架构层面
1. **Agent 串行执行** - 所有 Agent 逐个调用 LLM，没有利用多线程/多进程并行处理
2. **无动态 Agent 创建** - 只能在初始化时创建固定数量的 Agent，无法根据需要动态增减
3. **无会话持久化** - 每轮任务结束后全部销毁，无法保存和恢复
4. **缺少任务分解和进度追踪** - 没有明确的任务状态管理机制

#### 功能层面
1. **工具池自定义工具无法执行** - 虽然有 ToolInfo 模型，但没有加载和执行机制
2. **缺少文件读取工具** - 只有 write_file，没有 read_file
3. **缺少 Agent 状态查询** - 无法查询其他 Agent 的状态
4. **缺少任务完成检测** - 没有机制判断整体任务是否完成
5. **简单的 Token 计数** - Token 计算不准确（仅按字符数估算）

#### 交互层面
1. **CLI 输出混乱** - 多个 Agent 输出交错，难以阅读
2. **无可视化界面** - 纯终端输出，缺少系统状态可视化
3. **缺少配置管理 UI** - 只能通过命令行和环境变量配置

#### 稳定性层面
1. **缺少错误重试机制** - LLM 调用失败直接中断
2. **缺少速率限制** - 没有控制 API 调用频率
3. **消息总线无过期机制** - 消息会一直累积

## 2. v0.0.2 版本目标

### 2.1 核心目标
- **性能提升**：Agent 并行执行，提升系统吞吐量
- **功能增强**：完善工具系统，增加动态 Agent 管理
- **稳定性提升**：增加错误处理和重试机制
- **可扩展性**：为后续版本打下良好架构基础

### 2.2 版本亮点
1. 🚀 **并行执行** - 多 Agent 同时独立运行
2. 🛠️ **完善工具系统** - 支持自定义工具动态加载和执行
3. 🧩 **动态 Agent 管理** - 支持运行时创建/销毁 Agent
4. 📊 **改进的任务追踪** - 任务状态和进度管理
5. ⚡ **优化的性能** - 更好的资源利用和错误恢复

## 3. 详细功能设计

### 3.1 核心架构优化

#### 3.1.1 并行执行引擎
**模块**: `core/executor.py`

**功能设计**:
- 使用 `concurrent.futures.ThreadPoolExecutor` 实现并行执行
- 配置可调整的最大线程数
- 保持时间步同步（等待所有 Agent 完成当前步再进入下一步）
- 异常隔离：单个 Agent 失败不影响其他 Agent

**关键类**:
```python
class ParallelExecutor:
    def __init__(self, max_workers: int = 5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def execute_agents_parallel(self, agents: List[Agent], step_info: StepInfo) -> List[StepResult]:
        # 并行执行所有 Agent 的 step
        # 返回所有结果
```

#### 3.1.2 动态 Agent 管理器
**模块**: 增强 `core/agent.py` 的 `AgentLifecycleManager`

**新增功能**:
- `create_agent()` - 单个创建
- `destroy_agent(agent_id)` - 单个销毁
- `spawn_agent_from_role(role_id)` - 根据角色创建 Agent
- 跟踪 Agent 的创建时间、活跃状态等元数据

**Agent 元数据模型** (新增到 `models.py`):
```python
@dataclass
class AgentMetadata:
    agent_id: str
    role_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_active_step: int = 0
    status: str = "active"  # active, paused, destroyed
```

#### 3.1.3 任务状态管理
**模块**: 增强 `core/pools.py` 的 `DynamicTaskPool`

**新增任务状态**:
```python
class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

@dataclass
class Task:
    # ... 原有字段
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0  # 0.0 - 1.0
    assigned_agent_id: Optional[str] = None
    completed_at: Optional[datetime] = None
    parent_task_id: Optional[str] = None  # 支持子任务
```

**新增方法**:
- `update_task_status(task_id, status, progress)`
- `get_task_hierarchy(task_id)` - 获取任务树
- `list_tasks_by_status(status)`

### 3.2 工具系统增强

#### 3.2.1 自定义工具执行引擎
**模块**: `core/tool_executor.py`

**功能设计**:
- 动态加载 Python 代码作为工具
- 沙箱执行环境（可选）
- 工具权限管理
- 工具执行日志

**关键类**:
```python
class DynamicToolExecutor:
    def load_tool(self, tool_info: ToolInfo) -> bool:
        # 动态编译和加载工具代码
    
    def execute_tool(self, tool_id: str, **kwargs) -> Any:
        # 安全执行工具
```

#### 3.2.2 新增内置工具
1. **ReadFileTool** - 读取文件内容
2. **ListDirectoryTool** - 列出目录内容
3. **CreateAgentTool** - 创建新 Agent
4. **DestroyAgentTool** - 销毁 Agent
5. **GetAgentStatusTool** - 查询 Agent 状态
6. **GetSystemInfoTool** - 获取系统信息（当前步数、存活 Agent 数等）
7. **UpdateTaskProgressTool** - 更新任务进度

### 3.3 通信系统优化

#### 3.3.1 增强的 MessageBus
**模块**: 增强 `core/message_bus.py`

**新增功能**:
- 消息 TTL（Time To Live）
- 消息优先级
- 消息主题/频道支持
- 消息历史查询

**增强的 Message 模型**:
```python
@dataclass
class Message:
    # ... 原有字段
    priority: int = 0  # 数字越大优先级越高
    ttl: int = 3  # 消息存活步数
    topic: Optional[str] = None
    read_by: List[str] = field(default_factory=list)
```

#### 3.3.2 消息订阅机制
- Agent 可以订阅特定主题的消息
- 支持通配符订阅

### 3.4 内存和上下文优化

#### 3.4.1 改进的 Token 计算
**模块**: 增强 `core/agent.py` 的 `SimpleMemory`

**功能**:
- 使用 `tiktoken` 库进行准确的 Token 计数
- 支持不同模型的 Tokenizer
- 上下文压缩策略（可选）

#### 3.4.2 记忆总结机制
- 当 Token 接近上限时，自动总结旧消息
- 保留关键信息，压缩历史记录

### 3.5 稳定性和可靠性

#### 3.5.1 LLM 调用重试机制
**模块**: `core/llm_client.py` (新增)

**功能**:
- 指数退避重试
- 可配置的重试次数和间隔
- 不同错误类型的处理策略

#### 3.5.2 速率限制
- 控制 API 调用频率
- 令牌桶算法

### 3.6 CLI 和输出优化

#### 3.6.1 结构化输出
- 使用颜色和格式化区分不同 Agent 的输出
- 进度条显示当前步数
- 摘要模式和详细模式切换

#### 3.6.2 新增 CLI 参数
- `--parallel-workers` - 并行执行的最大工作线程数
- `--output-mode` - 输出模式 (simple/detailed/quiet)
- `--enable-retry` - 启用重试机制
- `--save-session` - 保存会话到文件

### 3.7 配置增强

#### 3.7.1 增强的 Config 模型
**模块**: 增强 `config.py`

**新增配置项**:
```python
@dataclass
class ExecutionConfig:
    max_parallel_workers: int = 5
    enable_retries: bool = True
    max_retries: int = 3
    retry_base_delay: float = 1.0

@dataclass
class AgentConfig:
    # ... 原有字段
    enable_memory_summarization: bool = False
    summarization_threshold: float = 0.7
```

## 4. 文件结构变更

```
autoswarm/
├── src/
│   └── autoswarm/
│       ├── __init__.py
│       ├── __version__.py          # 更新到 0.0.2
│       ├── config.py              # 增强
│       ├── logger.py
│       ├── cli.py                 # 增强
│       └── core/
│           ├── __init__.py
│           ├── models.py          # 增强（新增 AgentMetadata, TaskStatus 等）
│           ├── pools.py           # 增强
│           ├── message_bus.py     # 增强
│           ├── tools.py           # 增强（新增多个工具）
│           ├── agent.py           # 增强
│           ├── coordinator.py     # 增强（集成并行执行）
│           ├── executor.py        # 新增（并行执行引擎）
│           ├── tool_executor.py   # 新增（自定义工具执行）
│           └── llm_client.py      # 新增（LLM 客户端封装）
├── docs/
│   └── version_0.0.2_design.md    # 本文件
└── ...
```

## 5. 实施优先级

### Phase 1 (核心改进) - 必须实现
1. 并行执行引擎
2. 新增内置工具（ReadFile, ListDirectory 等）
3. 增强的任务状态管理
4. LLM 重试机制
5. 改进的 CLI 输出

### Phase 2 (功能增强) - 高优先级
1. 动态 Agent 创建/销毁
2. 自定义工具执行引擎
3. 增强的 MessageBus
4. 准确的 Token 计算

### Phase 3 (优化完善) - 中优先级
1. 记忆总结机制
2. 速率限制
3. 会话持久化框架

## 6. 验收标准

### 功能验收
- [ ] Agent 能够并行执行，性能有明显提升
- [ ] 新增内置工具正常工作
- [ ] 任务状态能够正确更新和追踪
- [ ] LLM 调用失败时能够自动重试
- [ ] 支持动态创建和销毁 Agent

### 性能验收
- [ ] 并行执行比串行执行快至少 2 倍（5 个 Agent 时）
- [ ] 内存使用稳定，无明显泄漏
- [ ] 响应时间在可接受范围内

### 稳定性验收
- [ ] 单个 Agent 失败不影响整个系统
- [ ] 网络波动时能够自动恢复
- [ ] 长时间运行（>100 步）稳定

## 7. 后续版本展望 (v0.0.3+)

- Web UI 界面
- 会话持久化和恢复
- 更高级的记忆管理（向量数据库）
- Agent 协作模式模板
- 插件系统
- 性能监控和分析仪表盘
