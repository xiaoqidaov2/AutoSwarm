# AutoSwarm: Step-Driven Autonomous Multi-Agent System

## 📋 项目概述

AutoSwarm 是一个完全**时间步长驱动**的无主多智能体系统，所有 Agent 平等独立，按照全局统一时钟同步执行。

## 🎯 核心特性

- ✅ **绝对同步时间步**：全局统一时钟，Agent 行为严格按步同步
- ✅ **无主架构**：无调度中心、无管理者，所有 Agent 平等独立
- ✅ **完全并行**：Agent 独立 LLM 调用、独立上下文、独立生命周期
- ✅ **动态三池生态**：
  - 🎭 角色池：动态可写，Agent 可发布/修改/删除角色
  - 📋 任务池：动态可写，Agent 可发布/修改/删除任务
  - 🛠️ 工具池：动态可写，Agent 可自研并发布工具
- ✅ **即用即销**：每轮任务结束后全部 Agent 销毁、三池清空、无状态残留

## 🏗️ 系统架构

### 核心模块

| 模块 | 功能 |
|------|------|
| **StepCoordinator** | 全局步进协调器、同步屏障、终止检测 |
| **AgentLifecycleManager** | Agent 创建、销毁、上下文窗口监控 |
| **DynamicRolePool** | 动态角色池、CRUD、互斥申领/释放 |
| **DynamicTaskPool** | 动态任务池、CRUD、互斥申领/释放 |
| **DynamicToolPool** | 动态工具池、内置工具注册、工具申领 |
| **AgentExecutor** | 个体 Agent 执行器、LLM 调用、工具执行 |
| **MessageBus** | Agent 通信总线、消息路由、时效管理 |

### 内置工具

每个 Agent 初始自带：
- `claim_role`：申领角色
- `claim_task`：申领任务
- `claim_tool`：申领工具
- `send_message`：跨 Agent 通信
- `publish_role`：发布新角色
- `publish_task`：发布新任务

公共预装工具（可申领）：
- 工具池 CRUD：`create_tool` / `update_tool` / `delete_tool` / `list_tools`
- 角色池 CRUD：`create_role` / `update_role` / `delete_role` / `list_roles`
- 任务池 CRUD：`create_task` / `update_task` / `delete_task` / `list_tasks`
- 终端执行：`execute_command`
- 文件操作：`write_file`

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

复制并编辑 `.env` 文件：

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 3. 运行系统

```bash
python main.py --agents 5 --max-steps 20
```

参数说明：
- `--agents`：初始 Agent 数量
- `--max-steps`：最大步数

### 4. 自定义角色和任务

编辑 `roles.json` 和 `tasks.json` 设置初始配置。

## 📊 运行流程

```
初始化
  ↓
[Step 1] 系统向所有 Agent 发送 step info
  ↓
[Step 2] 所有 Agent 并行独立思考、决策、工具调用
  ↓
[Step 3] 消息路由、通信处理
  ↓
[Step 4] 检测上下文超限，销毁超限 Agent
  ↓
[Step 5] 步进，回到 Step 1，直至 max_steps
  ↓
终止：全部 Agent 销毁，三池清空
```

## 🎭 角色示例

```json
[
  {
    "role_id": "role_leader",
    "name": "领导者",
    "description": "负责项目整体规划、发布招聘角色、分配任务",
    "system_prompt": "你是一个领导者！你的首要任务是分析任务需求，主动发布新角色招聘人才..."
  }
]
```

## 📋 任务示例

```json
[
  {
    "task_id": "task_dashboard",
    "title": "数据面板全栈开发",
    "description": "创建一个包含前后端的完整数据面板应用",
    "requirements": "需要前端、后端、UI设计等多个角色协作完成"
  }
]
```

## 🛠️ 技术栈

- **框架**：LangChain 原生架构
- **内存**：ConversationBufferMemory（纯原始存储）
- **交互**：纯 CLI 终端
- **运行模式**：同步全局步进、无主并行、独立上下文

## 📖 核心概念

### 时间步驱动

全局唯一 step / max_step，所有 Agent 严格同步，必须等待本 step 所有 Agent 执行完毕才进入下一步。

### 即用即销

一旦达到 max_step，所有 Agent 立即停止，所有动态创建的角色、任务、工具全部清空，无状态残留。用户再次发起任务 = 全新初始化。

### 无主协作

多 Agent 观点冲突无仲裁，自由博弈、自主协同，通过消息传递实现协作。

## 📂 项目结构

```
autoswarm/
├── __init__.py
├── main.py                 # CLI 主入口
├── agent.py                # Agent 个体执行器
├── coordinator.py          # 全局步进协调器
├── models.py               # 核心数据模型
├── pools.py                # 动态三池服务
├── tools.py                # 内置工具定义
├── message_bus.py          # Agent 通信总线
├── requirements.txt        # Python 依赖
├── roles.json             # 初始角色配置
├── tasks.json             # 初始任务配置
├── .env.example           # API Key 配置示例
├── .gitignore
├── README.md
└── QUICKSTART.md          # 快速开始指南
```

## 💡 研究价值

这个系统特别适合研究：
- 多 Agent 自主协作机制
- 动态角色和任务分配
- 工具自研和生态演化
- 无主群体智能

## 📝 License

MIT License
