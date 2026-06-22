# Mother's Personal Agent — Config Template

**Date:** 2026-06-05
**Client:** [Mother's Name]
**VPS:** Vultr 4GB ($20/mo) — or 8GB ($40/mo) if upgrading
**Model:** llama3.1:8b (American/Meta, local)
**Status:** Template — adapt and deploy

---

## Why Llama 3.1 8B

- ✅ American company (Meta)
- ✅ Fully local — no cloud dependency
- ✅ 128K context window (8x Percy's 16K)
- ✅ Good at scheduling, reminders, chat
- ✅ Fits on 4GB VPS (tight but works)

---

## Gateway Config (openclaw.json)

```json
{
  "gateway": {
    "mode": "local",
    "auth": {
      "mode": "none"
    },
    "port": 18789,
    "bind": "loopback",
    "tailscale": {
      "mode": "serve",
      "resetOnExit": false
    },
    "controlUi": {
      "allowedOrigins": [
        "http://localhost:18789",
        "http://127.0.0.1:18789",
        "https://[mother-name].tail[NNNN].ts.net"
      ],
      "allowInsecureAuth": true
    }
  },
  "models": {
    "providers": {
      "ollama": {
        "baseUrl": "http://127.0.0.1:11434",
        "api": "ollama",
        "models": [
          {
            "id": "llama3.1:8b",
            "name": "llama3.1:8b",
            "reasoning": false,
            "input": ["text"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 32768,
            "maxTokens": 8192,
            "compat": {
              "supportsTools": true,
              "supportsUsageInStreaming": true
            },
            "params": {
              "num_ctx": 32768
            }
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": "ollama/llama3.1:8b",
      "compaction": {
        "reserveTokensFloor": 8192
      }
    }
  }
}
```

**Key changes from Percy:**
- `model`: `llama3.1:8b` (was `qwen2.5:3b`)
- `contextWindow`: 32768 (was 16384) — enough for big identity files
- `num_ctx`: 32768 (was 16384)
- `compaction.reserveTokensFloor`: 8192 (same)

**Note:** I capped context at 32K instead of 128K because 4GB RAM can't handle the full 128K. If she upgrades to 8GB VPS, bump to 65536 or 128000.

---

## Deployment Steps

### Phase 1: VPS Setup (Same as Percy)
```bash
# 1. Deploy Vultr 4GB VPS (AlmaLinux 8 or Ubuntu 22.04)
# 2. Update system
dnf update -y  # AlmaLinux
# or
apt update && apt upgrade -y  # Ubuntu

# 3. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
systemctl enable ollama

# 4. Pull Llama 3.1 8B (AMERICAN MODEL)
ollama pull llama3.1:8b
# Size: 4.9GB download, ~6GB RAM to run

# 5. Install OpenClaw
npm install -g openclaw

# 6. Run non-interactive setup
openclaw onboard --non-interactive --provider ollama --model llama3.1:8b --no-model-pull

# 7. Write config (paste the JSON above into ~/.openclaw/openclaw.json)
# 8. Install gateway service
openclaw gateway install

# 9. Open firewall
firewall-cmd --permanent --add-port=18789/tcp  # AlmaLinux
firewall-cmd --reload
# or
ufw allow 18789/tcp  # Ubuntu
```

### Phase 2: Tailscale (Same as Percy)
```bash
# 1. Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
systemctl enable --now tailscaled

# 2. Authenticate
tailscale up --hostname mother-agent

# 3. Enable HTTPS in Tailscale admin
# 4. Start serve
tailscale serve --bg http://localhost:18789

# 5. Note the URL
tailscale serve status
# https://mother-agent.tail[NNNN].ts.net
```

### Phase 3: Identity Files (Bigger than Percy's!)

With 32K context, identity files can be ~3,000 words (vs Percy's 1,000).

| File | Words | Purpose |
|------|-------|---------|
| SOUL.md | 300-500 | Personality |
| USER.md | 200-300 | Mother's profile |
| AGENTS.md | 200-300 | Rules |
| MEMORY.md | 500-800 | Knowledge |
| HEARTBEAT.md | 50-100 | Schedule |
| KUDU-7.md | 50-100 | Verification |
| TOOLS.md | 50-100 | Tool notes |
| IDENTITY.md | 100-200 | Metadata |
| **TOTAL** | **~2,000-2,500** | **~1,500-2,000 tokens** |

### Phase 4: Config & Restart
```bash
# 1. Update allowedOrigins with actual Tailscale URL
# 2. Validate
openclaw config validate

# 3. Restart
systemctl --user restart openclaw-gateway

# 4. Test
ollama ps  # Should show llama3.1:8b running
free -h    # Should show <3.8GB used
```

### Phase 5: Device Pairing
```bash
# Mother connects from phone/laptop
# Approve:
openclaw devices approve [request-id]
```

---

## RAM Math for 4GB VPS

| Component | RAM |
|-----------|-----|
| OS + OpenClaw | ~1GB |
| Llama 3.1 8B (4-bit) | ~5GB |
| **Total** | **~6GB** |
| **Available** | **4GB** |
| **Gap** | **-2GB** ❌ |

**Reality check:** 4GB is tight. The model will swap to disk. It'll work but be slower than Percy.

**Options:**
1. **Accept the slowness** — it works, just patience needed
2. **Add swap** — `fallocate -l 4G /swapfile && mkswap /swapfile && swapon /swapfile`
3. **Upgrade to 8GB VPS** — $40/mo, runs smoothly

---

## Comparison: Percy vs Mother

| | Percy (Jacqueline) | Mother |
|---|-------------------|--------|
| VPS | 4GB | 4GB (or 8GB) |
| Model | qwen2.5:3b (Chinese) | llama3.1:8b (American) |
| Model Size | 1.9GB | 4.9GB |
| Context | 16K | 32K |
| Identity Files | 1,000 words | 2,500 words |
| Speed | ~10s response | ~15-20s (swapping) |
| RAM Used | 3.5GB | 4GB+ (swaps) |
| Data Privacy | Cloud-ish (Chinese) | Fully local |

---

## Testing Checklist

- [ ] `ollama ps` shows llama3.1:8b running
- [ ] `free -h` shows usage (expect swapping on 4GB)
- [ ] `tailscale serve status` shows HTTPS URL
- [ ] Control UI loads from phone
- [ ] "Hi" gets response in <30 seconds
- [ ] Schedule reminder: "Remind me to call John at 3pm"
- [ ] Interview prep: "Help me prepare for a manager interview"
- [ ] Employee schedule: "Add Sarah to the Tuesday shift"

---

## Files to Create

```
clients/mother-workspace/
├── MOTHER-CONFIG.md          # This file
├── DEPLOYMENT-PLAYBOOK.md    # Lessons learned
├── TAILSCALE-CONFIG.md       # Domain, IPs
├── GATEWAY-CONFIG.md         # Final working JSON
├── SOUL.md                   # AI personality
├── USER.md                   # Mother's profile
├── AGENTS.md                 # Rules
├── MEMORY.md                 # Knowledge
├── HEARTBEAT.md              # Proactive schedule
├── KUDU-7.md                 # Verification rule
└── TOOLS.md                  # Tool notes
```

---

## Next Steps

1. Confirm VPS size (4GB or 8GB?)
2. Choose hostname for Tailscale
3. Fill in identity files
4. Deploy
5. Test with mother
