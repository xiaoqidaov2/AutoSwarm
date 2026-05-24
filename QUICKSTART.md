# 快速使用指南

## 立即运行

```bash
# 基本运行
python main.py --agents 3 --max-steps 5

# 指定角色和任务种子文件
python main.py --agents 2 --max-steps 3 --roles my_roles.json --tasks my_tasks.json

# 使用特定模型
python main.py --agents 4 --max-steps 10 --model deepseek-chat
```

## 运行演示

```bash
python demo.py
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--agents` | 3 | 初始Agent数量 |
| `--max-steps` | 10 | 最大步数（全局时间步） |
| `--roles` | roles.json | 角色种子文件路径 |
| `--tasks` | tasks.json | 任务种子文件路径 |
| `--model` | deepseek-chat | 模型名称 |

## 系统特点

- ✅ **完全同步**：所有Agent按统一时间步执行
- ✅ **无主架构**：没有中心调度，Agent完全自主
- ✅ **动态三池**：角色/任务/工具池可运行时修改
- ✅ **即用即销**：每轮任务结束后全部清空
- ✅ **通信总线**：支持点对点和广播消息

## 监控日志

系统运行时，你会看到：

```
系统启动: 3 个Agent, 最大步数 10

=== 第 1/10 步 ===
[agent_abc12345]
输出: (Agent的行动和输出)

=== 第 2/10 步 ===
[agent_def67890]
输出: (Agent的行动和输出)

...

=== 系统终止 ===
```

## 自定义角色和任务

编辑 `roles.json` 和 `tasks.json` 文件：

```json
[
  {
    "name": "研究员",
    "description": "负责信息收集和研究",
    "system_prompt": "你是一名研究员..."
  }
]
```

## 故障排除

1. **API Key错误**：确保 `.env` 文件中正确配置了 `DEEPSEEK_API_KEY`
2. **导入错误**：确保已安装所有依赖：`pip install -r requirements.txt`
3. **响应超时**：可以减少 `--max-steps` 参数来加快测试
