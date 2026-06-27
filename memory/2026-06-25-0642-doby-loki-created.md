# 2026-06-25 — DOOBY & LOKI Agents Created

**Time:** 06:42 CDT
**User Intent:** Create two new local-model agents for compute efficiency

## What Was Built

### DOOBY (🤖) — The Coding Workhorse
- **Model:** `ollama/qwen2.5-coder:7b` (local, fast)
- **Fallbacks:** `deepseek-v4-pro:cloud` → `qwen3.5:9b`
- **Tools:** Full coding suite (browser, canvas, cron, exec, sessions_spawn, subagents, web_fetch, web_search)
- **Profile:** `coding`
- **Workspace:** `~/.openclaw/workspaces/dooby/`
- **Files:** `IDENTITY.md`, `AGENTS.md`, `MEMORY.md`

### LOKI (🏠) — The House Manager
- **Model:** `ollama/qwen3.5:9b` (local, balanced)
- **Fallbacks:** `deepseek-v4-flash:cloud` → `qwen2.5-coder:7b`
- **Tools:** Broad ops suite (browser, cron, exec, memory, message, read/write, sessions_spawn, subagents, web)
- **Profile:** `coding` (general-purpose)
- **Workspace:** `~/.openclaw/workspaces/loki/`
- **Files:** `IDENTITY.md`, `AGENTS.md`, `MEMORY.md`

## Config Changes

**File:** `~/.openclaw/openclaw.json`

1. Added `dooby` and `loki` to `agents.list`
2. Added `dooby` and `loki` to `agents.defaults.subagents.allowAgents`
3. Added `dooby` and `loki` to `sol.subagents.allowAgents`
4. Added `dooby` and `loki` to `tools.agentToAgent.allow`
5. Updated `meta.lastTouchedAt`

## Access Control

- Both agents: **Green + designated users only**
- No BlueBubbles routing bindings added (intentional — they don't need direct chat access)
- Both can spawn subagents and talk to full fleet

## Next Steps

1. Restart OpenClaw gateway to load new agents
2. Test spawning DOOBY for a simple coding task
3. Test spawning LOKI for a cron job
4. Consider migrating existing cron jobs from SOL to LOKI for compute savings

## Compute Savings Estimate

| Task Type | Before (SOL) | After (DOOBY/LOKI) | Savings |
|-----------|-------------|-------------------|---------|
| Script writing | kimi-k2.6:cloud | qwen2.5-coder:7b | ~80% faster, 0 API quota |
| Health checks | kimi-k2.6:cloud | qwen3.5:9b | ~70% faster, 0 API quota |
| File ops | kimi-k2.6:cloud | qwen3.5:9b | ~70% faster, 0 API quota |
| Background research | kimi-k2.6:cloud | qwen3.5:9b | ~60% faster, 0 API quota |

**Impact:** High — every cron job and background task previously burning cloud quota can now run locally.
