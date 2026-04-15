# 📊 Gateway HUD — Hermes Agent Skill

[English](#english) · [中文](#中文)

---

<a id="english"></a>

## Gateway HUD for Hermes Agent

A **Heads-Up Display** skill for [Hermes Agent](https://github.com/nicholasgriffintn/hermes-agent) gateway — appends a compact status bar after every response showing real-time context window usage, cache hit rate, API calls, cost, and response time.

### Preview

```
─
🟢 42k / 200k (21%) ██░░░░░░░░ | Cache: 85% | ↻3 | $0.12 | ⏱8.2s | 📎opus-4-6
```

| Emoji | Context Usage |
|-------|--------------|
| 🟢 | < 50% — plenty of room |
| 🟡 | 50–70% — moderate |
| 🟠 | 70–85% — getting tight |
| 🔴 | ≥ 85% — consider context compression |

### Why You Need This

- **See your costs in real time** — know exactly how much each conversation costs
- **Monitor context pressure** — avoid hitting the context window limit unexpectedly
- **Track cache efficiency** — see if your prompt caching strategy is working
- **Zero overhead** — HUD renders *after* the LLM call, consumes zero extra tokens

### Install

```bash
hermes skills install https://github.com/John15Wil/hermes-skill-gateway-hud
```

Or manually:

```bash
git clone https://github.com/John15Wil/hermes-skill-gateway-hud \
  ~/.hermes/skills/gateway-hud
```

### Usage

**Config:**

```yaml
# ~/.hermes/config.yaml
display:
  show_hud: true
```

**Runtime toggle** — in any gateway chat (Telegram, Discord, Slack, etc.):

```
/hud on      # Enable
/hud off     # Disable
/hud         # Show current status
```

### How It Works

HUD is embedded into the gateway message pipeline. The skill provides the core rendering function and integration documentation — the actual code lives in `gateway/run.py`.

```
AIAgent.run_conversation()
  → returns result dict with token/cost metadata
    → _run_agent() extracts HUD fields
      → _build_hud_footer() renders the status bar
        → delivered to user (streaming: separate msg · non-streaming: appended)
```

### Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Agent knowledge — architecture, data flow, pitfalls |
| `references/build_hud_footer.py` | Core rendering function (~93 lines) |
| `references/integration_snippets.py` | Integration touchpoints in gateway |

### Required Data Fields

```python
{
    "context_length": 200000,          # model's max context window
    "last_total_tokens": 42531,        # input+output from last API call
    "cache_read_tokens": 36150,        # prompt cache hits
    "input_tokens": 42531,             # total input tokens
    "estimated_cost_usd": 0.12,        # cost estimate
    "api_calls": 3,                    # LLM calls this turn
    "model": "anthropic/claude-opus-4.6",
}
```

---

<a id="中文"></a>

## Gateway HUD — Hermes Agent 网关状态栏技能

为 [Hermes Agent](https://github.com/nicholasgriffintn/hermes-agent) 网关设计的 **抬头显示（HUD）** 技能——在每条回复后附加一行紧凑的状态栏，实时显示上下文窗口用量、缓存命中率、API 调用次数、费用和响应时间。

### 效果预览

```
─
🟢 42k / 200k (21%) ██░░░░░░░░ | Cache: 85% | ↻3 | $0.12 | ⏱8.2s | 📎opus-4-6
```

| 图标 | 上下文压力 |
|------|-----------|
| 🟢 | < 50% — 空间充足 |
| 🟡 | 50–70% — 中等压力 |
| 🟠 | 70–85% — 即将接近上限 |
| 🔴 | ≥ 85% — 建议压缩上下文 |

### 为什么需要它

- **实时看费用** —— 每轮对话花了多少钱一目了然
- **监控上下文压力** —— 避免突然撞到上下文窗口上限
- **追踪缓存效率** —— 看看你的 prompt caching 策略是否生效
- **零额外开销** —— HUD 在 LLM 调用完成后渲染，不消耗任何额外 token

### 安装

```bash
hermes skills install https://github.com/John15Wil/hermes-skill-gateway-hud
```

或手动安装：

```bash
git clone https://github.com/John15Wil/hermes-skill-gateway-hud \
  ~/.hermes/skills/gateway-hud
```

### 使用方法

**配置文件：**

```yaml
# ~/.hermes/config.yaml
display:
  show_hud: true
```

**运行时切换** —— 在任意网关聊天中（Telegram、Discord、Slack 等）：

```
/hud on      # 开启
/hud off     # 关闭
/hud         # 查看当前状态
```

### 工作原理

HUD 嵌入在网关消息管道中。本技能提供核心渲染函数和集成文档——实际代码位于 `gateway/run.py`。

```
AIAgent.run_conversation()
  → 返回包含 token/费用元数据的结果字典
    → _run_agent() 提取 HUD 所需字段
      → _build_hud_footer() 渲染状态栏
        → 投递给用户（流式：单独消息 · 非流式：追加到回复末尾）
```

### 文件说明

| 文件 | 用途 |
|------|------|
| `SKILL.md` | Agent 知识文档——架构、数据流、注意事项 |
| `references/build_hud_footer.py` | 核心渲染函数（约 93 行） |
| `references/integration_snippets.py` | 网关集成代码片段 |

---

## License

[MIT](LICENSE)

## Author

Joseph ([@John15Wil](https://github.com/John15Wil))
