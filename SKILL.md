---
name: gateway-hud
description: "Implement and maintain the HUD (Heads-Up Display) feature for Hermes Agent gateway — shows context window usage, cache hit rate, API calls, cost, and response time after each response."
tags: [hermes, gateway, hud, context-window, token-usage, cost-tracking]
triggers:
  - user asks about HUD implementation
  - user wants to add/fix/modify the context usage display
  - user mentions token tracking or cost display in gateway responses
  - user asks about show_hud config
---

# Gateway HUD (Heads-Up Display)

Compact status bar appended to every gateway response showing real-time context window usage.

## Output Example

```
─
🟢 42k / 200k (21%) ██░░░░░░░░ | Cache: 85% | ↻3 | $0.12 | ⏱8.2s | 📎opus-4-6
```

## Architecture Overview

HUD is **not** a standalone module — it's embedded across `gateway/run.py` with config in `hermes_cli/config.py` and command registration in `hermes_cli/commands.py`.

### File Map

| Component | File | Lines (approx) |
|-----------|------|-----------------|
| Config default | `hermes_cli/config.py` | `"show_hud": False` in DEFAULT_CONFIG display section |
| Command registration | `hermes_cli/commands.py` | `CommandDef("hud", ...)` in COMMAND_REGISTRY |
| Init load | `gateway/run.py` | `self._show_hud = self._load_show_hud()` in `__init__` |
| Config loader | `gateway/run.py` | `_load_show_hud()` static method |
| **Core renderer** | `gateway/run.py` | `_build_hud_footer()` static method (~87 lines) |
| Streaming send | `gateway/run.py` | In message handler, after streaming completes |
| Non-streaming append | `gateway/run.py` | In message handler, appended to response string |
| `/hud` command | `gateway/run.py` | Handler for on/off/status |
| Data source | `gateway/run.py` | `_run_agent()` return dict carries HUD fields |

## Implementation Details

### 1. Config & Toggle

```yaml
# ~/.hermes/config.yaml
display:
  show_hud: false  # default off
```

Toggle at runtime: `/hud on` or `/hud off` — persists to config.yaml via `atomic_yaml_write()`.

### 2. Data Flow

```
AIAgent.run_conversation()
  → returns result dict with token/cost metadata
    → _run_agent() extracts and forwards HUD fields:
        context_length, last_total_tokens, last_prompt_tokens,
        cache_read_tokens, input_tokens, estimated_cost_usd,
        api_calls, model
      → _build_hud_footer(agent_result) renders the string
        → delivered to user (streaming: separate msg, non-streaming: appended)
```

### 3. Core Renderer Logic (`_build_hud_footer`)

**Input:** `agent_result` dict from `_run_agent()`

**Components rendered (in order):**

1. **Color emoji** — context pressure indicator:
   - 🟢 < 50% | 🟡 < 70% | 🟠 < 85% | 🔴 ≥ 85%
2. **Token count** — `current / max (pct%)` with compact formatting (42k, 1.2M)
3. **Progress bar** — 10-segment `█░` bar
4. **Cache hit rate** — `cache_read_tokens / input_tokens` percentage
5. **API calls** — `↻N` iteration count
6. **Cost** — adaptive precision ($0.0012, $0.123, $1.23)
7. **Response time** — `⏱8.2s` or `⏱2m15s`
8. **Model name** — `📎opus-4-6` (auto-strips common prefixes)

**Output:** `"\n─\n" + " | ".join(parts)` or empty string if insufficient data.

### 4. Delivery (Two Paths)

- **Streaming:** HUD sent as a **separate message** after stream completes (avoids breaking the stream)
- **Non-streaming:** HUD **concatenated** to the response string

### 5. Key Data Fields from `_run_agent()`

```python
return {
    "context_length": ...,        # model's max context window
    "last_total_tokens": ...,     # input+output tokens from last API call
    "last_prompt_tokens": ...,    # fallback if last_total unavailable
    "cache_read_tokens": ...,     # prompt cache hits
    "input_tokens": ...,          # total input tokens
    "estimated_cost_usd": ...,    # cost estimate
    "api_calls": ...,             # number of LLM calls this turn
    "model": ...,                 # resolved model name
}
```

## FAQ

**Does HUD consume extra tokens?** No. Zero. HUD data is collected *after* the LLM call completes — it reads metadata from the agent result dict and renders with pure Python string formatting. It never enters the system prompt or conversation history, so the LLM never sees it and no additional API calls are made.

## Pitfalls

1. **HUD shows nothing?** — `_run_agent()` must return `context_length` AND `last_total_tokens` (or `last_prompt_tokens`). If either is 0/None, `_build_hud_footer()` returns empty string.
2. **Streaming path** — HUD is a separate message; if the adapter's `send()` fails silently, HUD disappears with no error.
3. **`_response_time`** — injected *after* `_run_agent()` returns, at the call site: `agent_result["_response_time"] = time.time() - _msg_start_time`
4. **Config persistence** — `/hud on` writes to config.yaml via `atomic_yaml_write()`. If config is corrupt, `_load_show_hud()` silently returns False.

## Maintenance Notes

- To add a new HUD component: add it to `_build_hud_footer()` parts list, ensure the data field is carried through `_run_agent()` return dict.
- Token formatting helper `_fmt()` is defined inline inside `_build_hud_footer()`.
- Model name prefix stripping list may need updates as new providers are added.
