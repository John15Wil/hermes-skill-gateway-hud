"""
Integration snippets — how HUD is wired into the gateway.
These are the key touchpoints in gateway/run.py (not standalone runnable code).
"""

# ── 1. Init: load toggle from config ──────────────────────────────
# In GatewayBot.__init__():
#   self._show_hud = self._load_show_hud()

@staticmethod
def _load_show_hud() -> bool:
    """Load show_hud toggle from config.yaml display section."""
    try:
        import yaml as _y
        cfg_path = _hermes_home / "config.yaml"
        if cfg_path.exists():
            with open(cfg_path, encoding="utf-8") as _f:
                cfg = _y.safe_load(_f) or {}
            return bool(cfg.get("display", {}).get("show_hud", False))
    except Exception:
        pass
    return False


# ── 2. Data source: _run_agent() return dict ─────────────────────
# At the end of _run_agent(), carry over HUD-relevant fields:

_r = result_holder[0] or {}
return {
    "final_response": final_response,
    # ... other fields ...
    # HUD fields:
    "context_length": _r.get("context_length") or (
        getattr(_agent.context_compressor, "context_length", 0)
        if _agent and hasattr(_agent, "context_compressor") else 0
    ),
    "last_total_tokens": _r.get("last_total_tokens") or (
        getattr(_agent.context_compressor, "last_total_tokens", 0)
        if _agent and hasattr(_agent, "context_compressor") else 0
    ),
    "cache_read_tokens": _r.get("cache_read_tokens", 0),
    "cache_write_tokens": _r.get("cache_write_tokens", 0),
    "estimated_cost_usd": _r.get("estimated_cost_usd", 0),
    "api_calls": _r.get("api_calls", 0),
    "model": _resolved_model,
}


# ── 3. Delivery: streaming path ──────────────────────────────────
# After streaming completes, send HUD as separate message:

if getattr(self, "_show_hud", False) and agent_result:
    agent_result["_response_time"] = time.time() - _msg_start_time
    _hud = self._build_hud_footer(agent_result)
    if _hud and _hud_adapter:
        try:
            await _hud_adapter.send(source.chat_id, _hud.lstrip())
        except Exception:
            pass


# ── 4. Delivery: non-streaming path ──────────────────────────────
# Append HUD to response string:

if getattr(self, "_show_hud", False) and response and agent_result:
    agent_result["_response_time"] = time.time() - _msg_start_time
    _hud = self._build_hud_footer(agent_result)
    if _hud:
        response = response + _hud


# ── 5. /hud command handler ──────────────────────────────────────

# In hermes_cli/commands.py COMMAND_REGISTRY:
#   CommandDef("hud", "Toggle context window HUD on responses", "Configuration",
#              aliases=("hud",), args_hint="[on|off]")

# In gateway/run.py command dispatcher:
def _handle_hud_command(self, args: str):
    def _save_hud(value: bool):
        display = user_config.setdefault("display", {})
        display["show_hud"] = value
        atomic_yaml_write(config_path, user_config)

    if not args:
        state = "**ON** ✅" if getattr(self, "_show_hud", False) else "**OFF**"
        return f"📊 **HUD Status:** {state}\n\n..."

    if args in ("on", "enable", "show"):
        self._show_hud = True
        _save_hud(True)
        return "📊 ✓ HUD: **ON** — context usage will be shown after each response."

    if args in ("off", "disable", "hide"):
        self._show_hud = False
        _save_hud(False)
        return "📊 ✓ HUD: **OFF**"
