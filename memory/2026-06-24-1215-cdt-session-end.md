# Session — 2026-06-24 12:15 CDT

## SAOS Dashboard Agent Emojis Fixed

### What Was Done
Fixed agent emoji mapping in SAOS customer dashboard to use correct per-agent avatars instead of 🛰️ (SOL's satellite) as fallback for all agents.

### File Changed
- `Systack/content/saos/saos-data/customer-dashboard/index.html`

### Changes Made
1. Added `getAgentAvatar(agentName)` function (line ~1034) with canonical emoji mapping
2. Updated agent fleet display to use `getAgentAvatar(a.agent_name)` instead of `a.avatar || '🛰️'`
3. Updated chat message avatars to use `getAgentAvatar(msg.sender_agent)` instead of `msg.sender_agent || '🛰️'`

### Final Agent Emoji Mapping

| Agent | Emoji | Source |
|-------|-------|--------|
| SOL | 🛰️ | `~/.openclaw/openclaw.json` |
| CODY | 💻 | `~/.openclaw/openclaw.json` |
| ASSEMBLY | 🛠️ | `~/.openclaw/openclaw.json` |
| VALI | ✅ | `~/.openclaw/openclaw.json` |
| PESSI | ⚠️ | `~/.openclaw/openclaw.json` |
| ORACLE | 🔮 | User directive |
| ATLAS | 🗺️ | `~/.openclaw/openclaw.json` |
| CHATTY | 💬 | `~/.openclaw/openclaw.json` |
| GENI | 🎨 | `~/.openclaw/openclaw.json` |
| JURIS | ⚖️ | `~/.openclaw/openclaw.json` |

### Note
- ORACLE is not yet in `openclaw.json` config — added manually per user directive
- If ORACLE gets added to config later, verify emoji matches 🔮

### Session Ended
12:15 CDT
