# Percy Deployment — FINAL WORKING CONFIG

**Date:** 2026-06-05  
**Client:** Jacqueline, McDonald's GM  
**VPS:** Vultr 4GB ($20/mo)  
**Status:** ✅ WORKING

---

## What Works

- **Model:** qwen2.5:3b with 16K context
- **RAM usage:** ~2.5GB model + 1GB OS/gateway = 3.5GB ✅
- **Identity files:** 1,009 words (~756 tokens) — stripped to fit
- **Tailscale:** https://percy-mcdonalds.taildd162e.ts.net
- **Auth:** None (Tailscale is the security)
- **Device:** iPhone 15 Plus ✅ connected and approved

---

## The Breakthrough

**Problem:** Context overflow — system prompt (8,800 tokens) > model context (4K)
**Root cause:** Identity files + OpenClaw bootstrap exceeded available context
**Solution:** 
1. Switch to qwen2.5:3b with 16K context
2. Strip identity files from 3,500+ words to 1,009 words
3. Set compaction.reserveTokensFloor = 8192

---

## Final Gateway Config

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
        "https://percy-mcdonalds.taildd162e.ts.net"
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
            "id": "qwen2.5:3b",
            "name": "qwen2.5:3b",
            "reasoning": false,
            "input": ["text"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 16384,
            "maxTokens": 8192,
            "compat": {
              "supportsTools": true,
              "supportsUsageInStreaming": true
            },
            "params": {
              "num_ctx": 16384
            }
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

---

## Identity File Sizes (Target: <1,500 words)

| File | Words | Purpose |
|------|-------|---------|
| SOUL.md | 221 | Personality |
| USER.md | 131 | Client profile |
| AGENTS.md | 173 | Rules |
| MEMORY.md | 314 | Knowledge |
| HEARTBEAT.md | 26 | Schedule |
| KUDU-7.md | 30 | Verification rule |
| TOOLS.md | 12 | Tool notes |
| IDENTITY.md | 102 | Metadata |
| **TOTAL** | **1,009** | **~756 tokens** |

---

## Deployment Steps (For Future Clients)

### Phase 1: VPS Setup
```bash
# 1. Deploy Vultr 4GB VPS (AlmaLinux 8)
# 2. Update system
dnf update -y

# 3. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
systemctl enable ollama

# 4. Pull 3B model (smallest that fits context)
ollama pull qwen2.5:3b

# 5. Install OpenClaw
npm install -g openclaw

# 6. Run non-interactive setup
openclaw onboard --non-interactive --provider ollama --model qwen2.5:3b --no-model-pull

# 7. Configure auth, bind, controlUi
cat > ~/.openclaw/openclaw.json <>EOF
{
  "gateway": {
    "mode": "local",
    "auth": { "mode": "none" },
    "port": 18789,
    "bind": "loopback",
    "tailscale": { "mode": "serve", "resetOnExit": false },
    "controlUi": {
      "allowedOrigins": [
        "http://localhost:18789",
        "http://127.0.0.1:18789"
      ],
      "allowInsecureAuth": true
    }
  }
}
EOF

# 8. Install gateway service
openclaw gateway install

# 9. Open firewall
firewall-cmd --permanent --add-port=18789/tcp
firewall-cmd --reload
```

### Phase 2: Tailscale Setup
```bash
# 1. Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
systemctl enable --now tailscaled

# 2. Authenticate (gives URL to open in browser)
tailscale up --hostname [client-name]

# 3. Enable HTTPS in admin console
# Go to https://login.tailscale.com/admin/dns
# Click "Enable HTTPS"

# 4. Start serve
tailscale serve --bg http://localhost:18789

# 5. Note the HTTPS URL
tailscale serve status
# Output: https://[client-name].tail[NNNN].ts.net
```

### Phase 3: Identity Files
```bash
# Create workspace
mkdir -p ~/.openclaw/workspaces/[client]/percy-[client]

# Write minimal identity files:
# - SOUL.md (200-300 words)
# - USER.md (100-150 words)
# - AGENTS.md (150-200 words)
# - MEMORY.md (300-400 words)
# - HEARTBEAT.md (20-30 words)
# - KUDU-7.md (20-30 words)
# - TOOLS.md (10-20 words)
# - IDENTITY.md (100 words)

# TOTAL: 1,000-1,200 words max
```

### Phase 4: Config Update
```bash
# 1. Add model config with 16K context
# 2. Set default model
# 3. Set compaction reserve
# 4. Add Tailscale URL to allowedOrigins
# 5. Validate
openclaw config validate

# 6. Restart
systemctl --user restart openclaw-gateway
```

### Phase 5: Device Approval
```bash
# When client first connects:
openclaw devices list
openclaw devices approve [request-id]
```

---

## Testing Checklist

- [ ] Gateway running: `systemctl --user status openclaw-gateway`
- [ ] Port open: `ss -tlnp | grep 18789`
- [ ] Tailscale serve: `tailscale serve status`
- [ ] Model loaded: `ollama ps`
- [ ] RAM OK: `free -h` (<3.5GB used)
- [ ] Config valid: `openclaw config validate`
- [ ] Device approved: `openclaw devices list`
- [ ] Test message: Send "Hi Percy" from client device
- [ ] Check for overflow: `grep -i overflow /tmp/openclaw/openclaw-*.log`
- [ ] Response time: Should be <15 seconds

---

## Known Working Setup (Jacqueline)

| Component | Value |
|-----------|-------|
| VPS | Vultr 4GB, Chicago |
| OS | AlmaLinux 8.10 |
| OpenClaw | v2026.6.1 |
| Model | qwen2.5:3b (1.9GB file) |
| Context | 16,384 tokens |
| RAM used | 3.0-3.5GB |
| Tailscale | percy-mcdonalds.taildd162e.ts.net |
| Client device | iPhone 15 Plus ✅ |

---

## What We Learned (Documented for Future)

1. **Context overflow is silent failure** — model doesn't respond, just spins
2. **Identity file size matters** — every word adds to system prompt
3. **4GB VPS minimum** — 3B model with stripped files, or upgrade to 8GB
4. **Tailscale Serve + HTTPS** — only way to avoid "secure browser context" error
5. **No `--bind` in systemd** — let config handle it
6. **Device approval loop** — caused by service/config mismatch
7. **Windows S mode blocks Tailscale** — exit S mode first
8. **Heredocs break over sshpass** — write local, pipe via ssh
9. **Phone works before laptop** — always test phone first
10. **`/new` starts fresh session** — clears old model context

---

## File References

- `DEPLOYMENT-PLAYBOOK.md` — Full troubleshooting guide
- `MODEL-CONTEXT-SIZING-GUIDE.md` — Context math and model selection
- `PERCY-DEPLOYMENT-PLAN.md` — Original deployment steps
- `memory/2026-06-04-percy-deployment.md` — Raw day 1 log

---

*Deployment complete. Percy is operational.*
*For future clients, copy this pattern.*
*Sol, on behalf of Systack*
