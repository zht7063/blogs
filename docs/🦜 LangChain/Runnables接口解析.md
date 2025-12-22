---
title: LangChain Runnable 接口全解析：从 LCEL 到生产级 AI 工作流
tags:
  - LangChain
  - 开发
  - 智能体
  - LCEL
---

在 LangChain 1.x 时代，**Runnable 协议**已成为整个框架的基石。它不仅规范了所有组件的调用方式，更通过 **LCEL (LangChain Expression Language)** 彻底终结了早期版本中“黑盒式”的 Legacy Chains。

本文将从核心协议、调用接口、链式逻辑及运行时配置四个维度，深入解析 Runnable 接口的强大之处。

# 一、 引言：从 Legacy Chains 到 Runnable 协议

早期 LangChain 依赖于大量的硬编码类（如 `LLMChain`, `RetrievalQA`），这些类虽然上手简单，但在面对复杂的流式输出（Streaming）、异步调用及中间步骤追踪时显得捉襟见肘。

**Runnable 协议**的出现，将所有组件（模型、提示词、解析器、工具等）抽象为统一的可执行单元，并赋予了它们天然的“管道化”能力。其核心愿景是：**一次编写，自动获得异步、流式、并行及监控能力。**

# 二、 标准调用接口：统一的执行入口

无论是一个简单的 LLM，还是一个复杂的 RAG 链，它们都遵循相同的调用接口。

## 2.1 同步与异步单次调用 (invoke / ainvoke)

`invoke()` 是最基础的执行入口。

### `input` 参数：执行的输入载体
`input` 的格式取决于 Runnable 的类型：
- **PromptValue**: 接收字典，如 `{"topic": "cats"}`。
- **ChatModel**: 接收消息列表（`BaseMessage` 对象或消息字典）。
- **Chain / Agent**: 通常是一个字典，聚合了链中所有需要的键值。

### `config` 参数：执行时的运行配置
`config` 是一个可选的对象（类型为 `RunnableConfig`），用于控制执行细节。

| 常用键名 | 功能 |
| :--- | :--- |
| `tags` | 给执行打标签，方便在 LangSmith 中追踪。 |
| `metadata` | 附带元信息（如任务名、Session ID）。 |
| `callbacks` | 设置回调钩子。 |
| `run_name` | 给这次执行命名。 |

> **示例：通用调用方式**
```python
# 一个典型的 LCEL 链调用
chain = prompt | model | parser
resp = chain.invoke(
    {"input": "解释一下量子力学"},
    config={"tags": ["demo-task"], "metadata": {"user_id": "123"}}
)
```

## 2.2 批量处理 (batch / abatch)
用于同时处理多个输入。LangChain 在底层自动处理了并发，比循环调用 `invoke` 效率更高。

## 2.3 流式输出 (stream / astream)
允许实时获取生成内容。对于大语言模型，这意味着可以逐个字地输出。

## 2.4 高级事件流 (astream_events)
**LangChain 1.x 的杀手锏**。它能以流的形式输出链中**所有步骤**的事件（如 Prompt 开始、Tool 开始、模型生成等），是构建复杂 UI 进度条的核心。

# 三、 LCEL 链式逻辑：管道运算符的魔法

## 3.1 核心对比：Legacy vs. LCEL

| 特性 | Legacy Chains (如 LLMChain) | LCEL (Modern Runnable) |
| :--- | :--- | :--- |
| **透明度** | 黑盒，难以查看中间状态 | 白盒，每步逻辑清晰可见 |
| **自定义** | 需继承类并重写方法，极其繁琐 | 使用 `|` 或 `RunnableLambda` 轻松组合 |
| **流式支持** | 部分支持，且实现复杂 | 原生支持，自动穿透所有步骤 |

## 3.2 组合原语
- **`RunnableSequence`**: `|` 运算符的本质，将 A 的输出作为 B 的输入。
- **`RunnableParallel`**: 用于并行执行多个分支，并将结果合并为字典。
- **`RunnablePassthrough`**: “透传”数据，或者在不改变原数据的情况下添加新键。
- **`RunnableLambda`**: 将任意 Python 函数包装成 Runnable，使其获得 `invoke/stream` 等能力。

# 四、 运行时动态配置与增强

## 4.1 参数绑定 (.bind)
在运行时之前预设模型参数（如 `stop_sequences` 或挂载 `tools`），而无需在调用链的每一步手动传递。

## 4.2 回退与重试 (.with_fallbacks / .with_retry)
生产级必备。当主模型失败时，自动切换到备用模型（Fallback）或按策略重试。

## 4.3 进阶：通过 ToolRuntime 获取 Config Metadata

当调用 `invoke()` 并传入 `config` 后，这些 `metadata` 会向下继承。Tool 如果声明了 `runtime: ToolRuntime` 参数，就能读到这些元数据。

```python
@tool
def get_user_preference(
    runtime: ToolRuntime
) -> str:
    """获取用户偏好设置。"""
    # 从运行时配置中提取 metadata
    meta = (runtime.config or {}).get("metadata", {})
    user_info = meta.get("user_info", {})
    return f"User info: {user_info}"
```

## 4.4 进阶：使用 context_schema 传递业务上下文信息

如果信息是“业务上下文”（如用户权限、多租户 ID），官方更推荐使用 **context** 机制。

```python
@dataclass
class UserContext:
    user_name: str

@tool
def hello(runtime: ToolRuntime[UserContext]) -> str:
    # 强类型支持
    return f"Hi {runtime.context.user_name}, from tool."

# 在创建 Agent 或 Chain 时指定 context_schema
# agent = create_agent(..., context_schema=UserContext)
```

# 五、 总结：迈向 LangGraph 的基石

Runnable 协议不仅简化了链的构建，它更是 **LangGraph** 等高级框架的底层基石。理解了 Runnable 的输入输出流转和运行时配置，你才能真正掌握 LangChain 1.x 的开发精髓。
