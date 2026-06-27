# 2026-06-25 — Local Agent Experiment Results

**Time:** 08:06 CDT
**Status:** ENDED — Documenting findings, ceasing testing

## What Was Attempted

Created two local-model agents (DOOBY 🤖 and LOKI 🏠) to reduce cloud compute costs by running background tasks on local Ollama models.

## Config Changes Made

**File:** `~/.openclaw/openclaw.json`

- Added `dooby` and `loki` to `agents.list`
- Added to `subagents.allowAgents` and `agentToAgent.allow`
- Created workspaces: `~/.openclaw/workspaces/{dooby,loki}/`
- Created custom Modelfiles: `dooby-fast`, `dooby-tool` (both based on qwen2.5-coder:7b)
- Configured models:
  - DOOBY: `ollama/dooby-fast:latest` → fallback `deepseek-v4-pro:cloud`
  - LOKI: `ollama/dooby-fast:latest` → fallback `deepseek-v4-flash:cloud`

## Test Results (6 Attempts)

| Test | Agent | Model | Result | File Created |
|------|-------|-------|--------|-------------|
| test-1 | DOOBY | qwen2.5-coder:7b | ✅ Done | ❌ No |
| test-1 | LOKI | qwen2.5-coder:7b | ✅ Done | ❌ No |
| test-2 | DOOBY | qwen2.5-coder:7b | ❌ Failed | ❌ No |
| test-2 | LOKI | qwen3.5:9b | ❌ Failed (model not found) | ❌ No |
| test-3 | DOBY | qwen2.5-coder:7b | ✅ Done | ❌ No |
| test-3 | LOKI | qwen2.5-coder:7b | ❌ Failed | ❌ No |
| test-4 | DOOBY | qwen2.5-coder:14b | ❌ Timeout (6m13s) | ❌ No |
| test-4 | LOKI | qwen2.5-coder:14b | ❌ Failed (lost context) | ❌ No |
| test-5 | DOOBY | deepseek-v4-pro:cloud (fallback) | ✅ Done (9s) | ✅ YES |

## Key Findings

### 1. Local Models Cannot Reliably Invoke Tools
- 7B models: Generate JSON text responses but don't actually execute tools
- 14B model: Too large for 16GB RAM — loads but times out
- Custom Modelfiles with tool-calling instructions: Still fail to execute

### 2. Cloud Fallback Works
- When local model fails, agents fall back to cloud models
- DOOBY test-5 on `deepseek-v4-pro:cloud`: Created `~/Downloads/recent_files.py` in 9 seconds
- This proves the agent framework works — just not with local models

### 3. Hardware Limitations
- 16GB RAM insufficient for 14B models (15GB loaded, system starved)
- 7B models fit (6.4GB) but can't properly use GPU for tool execution

### 4. OpenClaw Integration Issue
- The problem is between OpenClaw's tool-calling format and Ollama's execution
- Models generate correct JSON but don't invoke the actual tool functions
- "Lost active execution context" errors suggest runtime-level failures

## What Actually Works

**DOOBY and LOKI are functional but only with cloud fallback:**
- Agents spawn successfully
- Configs load properly
- Fleet communication works
- Tool execution works — **only when using cloud models**

## Files Modified

- `~/.openclaw/openclaw.json` — Agent configs
- `~/.openclaw/workspaces/dooby/` — Identity, AGENTS.md, MEMORY.md
- `~/.openclaw/workspaces/loki/` — Identity, AGENTS.md, MEMORY.md
- `~/.openclaw/workspaces/dooby/Modelfile` — Custom tool-calling model (non-functional)
- `~/.openclaw/workspaces/dooby/Modelfile-fast` — Optimized 7B model (non-functional)

## Decision

**Stop testing local models.** Current setup:
- Agents configured with cloud fallback
- Local model experimentation deferred
- Monitor OpenClaw updates for improved Ollama integration

## Recommendation

For now, use DOOBY and LOKI as **cloud-fallback agents**:
- They'll attempt local first (instant fail)
- Fall back to cloud models
- Still achieve compute savings by only spawning when needed (not running continuously)

Revisit local models when:
- OpenClaw improves Ollama tool-calling support
- Hardware upgrade (32GB+ RAM)
- Better 7B models with native tool support

## Files Created

| File | Size | Proof |
|------|------|-------|
| `~/Downloads/recent_files.py` | 1.3 KB | `ls -la` verified |
