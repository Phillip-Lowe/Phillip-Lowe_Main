# CLIENT DEPLOYMENT — Model Context Sizing Guide

**Date:** 2026-06-05
**Lesson:** System prompt size determines minimum model context

---

## The Problem

Percy's identity files (SOUL.md, AGENTS.md, USER.md, TOOLS.md, etc.) create a **system prompt of ~8,800 tokens**. This happens on EVERY request — not just at startup.

If the model's context window is too small, OpenClaw tries "auto-compaction" but fails, causing:
- "Context overflow: prompt too large for the model"
- "Auto-compaction could not recover this turn"
- Percy appears to "not respond" (actually failing silently)

---

## The Math

```
System prompt (identity files + OpenClaw bootstrap): ~8,800 tokens
Conversation history: variable
Available for response: contextWindow - systemPrompt - compactionReserve

For 4K context:
  4096 - 8800 - 2048 = NEGATIVE ❌ (impossible)

For 8K context:
  8192 - 8800 - 2048 = NEGATIVE ❌ (still impossible)

For 16K context:
  16384 - 8800 - 8192 = -6,088 ❌ (tight, needs compaction)
  
For 32K context:
  32768 - 8800 - 8192 = 15,776 ✅ (comfortable)
```

**Rule of thumb:** contextWindow must be at least **2x the system prompt size**.

---

## Solution: "Bootstrap Model Pattern"

**For 4GB VPS (minimum):**
1. Use **qwen2.5:3b** with **16K context** (fits in ~2.5GB RAM)
2. Set `compaction.reserveTokensFloor = 8192`
3. Identity files must stay under ~6,000 tokens
4. Or strip down identity files significantly

**For 8GB VPS (recommended):**
1. Use **qwen2.5:7b** with **32K context** (fits in ~3.5GB RAM)
2. Set `compaction.reserveTokensFloor = 16384`
3. Full identity files work fine
4. Much faster responses, better quality

**For 2GB VPS (budget):**
1. Use **qwen2.5:1.5b** with **8K context**
2. **STRIP identity files to bare minimum** (<2,000 tokens)
3. Set `compaction.reserveTokensFloor = 2048`
4. Limited capabilities but functional

---

## Standard Config Per VPS Size

### 4GB VPS (Default for Clients)

```json
{
  "models": {
    "providers": {
      "ollama": {
        "models": [
          {
            "id": "qwen2.5:3b",
            "name": "qwen2.5:3b",
            "contextWindow": 16384,
            "maxTokens": 8192,
            "params": { "num_ctx": 16384 }
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": "ollama/qwen2.5:3b",
      "compaction": {
        "reserveTokensFloor": 8192
      }
    }
  }
}
```

**RAM usage:** ~2.5GB for model, ~500MB for OS, ~500MB for gateway = 3.5GB total ✅

### 8GB VPS (Premium Clients)

```json
{
  "models": {
    "providers": {
      "ollama": {
        "models": [
          {
            "id": "qwen2.5:7b",
            "name": "qwen2.5:7b",
            "contextWindow": 32768,
            "maxTokens": 8192,
            "params": { "num_ctx": 32768 }
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": "ollama/qwen2.5:7b",
      "compaction": {
        "reserveTokensFloor": 16384
      }
    }
  }
}
```

**RAM usage:** ~3.5GB for model, ~1GB for OS, ~500MB for gateway = 5GB total ✅

---

## Identity File Size Limits

| VPS Size | Model | Max Context | Max System Prompt | Identity File Size |
|----------|-------|-------------|-------------------|-------------------|
| 4GB | qwen2.5:3b | 16K | ~6,000 tokens | ~8KB total |
| 8GB | qwen2.5:7b | 32K | ~14,000 tokens | ~20KB total |
| 2GB | qwen2.5:1.5b | 8K | ~2,000 tokens | ~3KB total |

**To check identity file size:**
```bash
du -sh ~/.openclaw/workspaces/[client]/*.md
```

**To estimate token count:**
```bash
# Rough rule: 1 token ≈ 0.75 words
wc -w ~/.openclaw/workspaces/[client]/*.md
```

---

## How to Strip Identity Files for Small VPS

**Keep (essential):**
- `SOUL.md` — personality (1-2 paragraphs max)
- `USER.md` — client info (bullet points)
- `AGENTS.md` — 3-4 core rules only

**Remove/reduce:**
- `KUDU-7.md` — remove, too verbose
- `HEARTBEAT.md` — reduce to 3-4 lines
- `TOOLS.md` — remove, not needed for basic agent
- `MEMORY.md` — start empty, grow organically

**Mini SOUL.md for 2GB VPS:**
```markdown
# SOUL.md

**Name:** Percy
**Role:** Assistant for [Client Name]
**Vibe:** Patient, helpful, professional

## Core Rules
1. Be patient with technology questions
2. Explain step by step
3. Never assume technical knowledge
4. Confirm understanding before moving on

## Boundaries
- I run on a server, not your devices
- I help with schedules, reminders, drafting, research
- I cannot fix your computer directly
- I will not send emails without your approval
```

This is ~150 words = ~200 tokens. Fits in any context.

---

## Testing the Setup

**After deployment, test in this order:**

1. **Check model loaded:** `ollama ps`
2. **Check RAM:** `free -h`
3. **Check config valid:** `openclaw config validate`
4. **Send test message:** "Say hello in one sentence"
5. **Check logs for overflow:** `grep -i "overflow\|compaction" /tmp/openclaw/openclaw-*.log`
6. **If overflow occurs:** Increase context or reduce identity files

---

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| "Context overflow" | System prompt > available context | Increase contextWindow or reduce identity files |
| "Auto-compaction failed" | Compaction reserve too large | Lower `reserveTokensFloor` or increase context |
| "llm-idle-timeout" | Model too slow (RAM pressure) | Use smaller model or upgrade VPS |
| "prompt too large" | Context window too small | Upgrade to larger model or VPS |

---

## Decision Tree for Model Selection

```
VPS RAM?
├── 8GB+ → qwen2.5:7b (32K context) ✅ Best quality
├── 4GB  → qwen2.5:3b (16K context) ⚠️ Tight, strip identity files
├── 2GB  → qwen2.5:1.5b (8K context) ⚠️ Must strip identity files heavily
└── <2GB → Not recommended ❌
```

---

## McDonald's GM (Jacqueline) — Final Config

**VPS:** Vultr 4GB ($20/mo)
**Model:** qwen2.5:3b with 16K context
**Identity files:** Stripped to ~6KB total
**RAM usage:** ~2.5GB model + 1GB OS/gateway = 3.5GB ✅
**Status:** Working after context sizing fix

**Tailscale:** https://percy-mcdonalds.taildd162e.ts.net
**Auth:** None (Tailscale only)
**Device:** iPhone 15 Plus (working), Windows laptop (pending S mode fix)

---

*Documented by Sol on 2026-06-05*
*For all future Systack client deployments*
