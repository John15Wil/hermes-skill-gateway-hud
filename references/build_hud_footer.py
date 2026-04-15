"""
Core HUD renderer — extracted from gateway/run.py _build_hud_footer()
This is the complete rendering function. Input: agent_result dict. Output: formatted string.
"""


def _build_hud_footer(agent_result: dict) -> str:
    """Build a compact HUD footer showing context window usage, cache, and cost.

    Returns an empty string if there's insufficient data.
    Format:
        ─
        📊 42,531 / 200,000 tokens (21%) ██░░░░░░░░ | Cache: 85% | ↻3 | $0.12
    """
    context_length = agent_result.get("context_length", 0)
    last_prompt = agent_result.get("last_prompt_tokens", 0)
    last_total = agent_result.get("last_total_tokens", 0)
    # Use last_total_tokens (input+output from last API call) as context usage;
    # fall back to last_prompt_tokens if unavailable.
    current_usage = last_total or last_prompt
    if not context_length or not current_usage:
        return ""

    pct = min(current_usage / context_length * 100, 100.0)

    # Progress bar: 10 segments
    filled = int(pct / 10)
    bar = "█" * filled + "░" * (10 - filled)

    # Color indicator via emoji
    if pct < 50:
        color_dot = "🟢"
    elif pct < 70:
        color_dot = "🟡"
    elif pct < 85:
        color_dot = "🟠"
    else:
        color_dot = "🔴"

    # Format token counts as compact "42k" / "200k"
    def _fmt(n: int) -> str:
        if n >= 1_000_000:
            return f"{n / 1_000_000:.1f}M"
        if n >= 10_000:
            return f"{n // 1000}k"
        if n >= 1000:
            return f"{n / 1000:.1f}k"
        return str(n)

    parts = [f"{color_dot} {_fmt(current_usage)} / {_fmt(context_length)} ({pct:.0f}%) {bar}"]

    # Cache hit rate
    cache_read = agent_result.get("cache_read_tokens", 0)
    input_tokens = agent_result.get("input_tokens", 0)
    if cache_read and input_tokens:
        cache_pct = min(cache_read / input_tokens * 100, 100.0)
        parts.append(f"Cache: {cache_pct:.0f}%")

    # API calls
    api_calls = agent_result.get("api_calls", 0)
    if api_calls:
        parts.append(f"↻{api_calls}")

    # Cost
    cost = agent_result.get("estimated_cost_usd")
    if cost and cost > 0:
        if cost < 0.01:
            parts.append(f"${cost:.4f}")
        elif cost < 1.0:
            parts.append(f"${cost:.3f}")
        else:
            parts.append(f"${cost:.2f}")

    # Response time
    resp_time = agent_result.get("_response_time")
    if resp_time and resp_time > 0:
        if resp_time < 60:
            parts.append(f"⏱{resp_time:.1f}s")
        else:
            _m, _s = divmod(resp_time, 60)
            parts.append(f"⏱{int(_m)}m{int(_s)}s")

    # Model name (compact: strip common prefixes)
    model = agent_result.get("model") or ""
    if model:
        for _prefix in ("aws-claude-", "anthropic/claude-", "claude-", "openai/", "google/"):
            if model.startswith(_prefix):
                model = model[len(_prefix):]
                break
        parts.append(f"📎{model}")

    return "\n─\n" + " | ".join(parts)
