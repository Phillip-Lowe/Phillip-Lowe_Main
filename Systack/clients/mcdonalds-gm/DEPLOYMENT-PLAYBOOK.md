# Percy Deployment — Client Onboarding Playbook

**Client:** McDonald's GM (Jacqueline)
**Date:** 2026-06-05
**Deployer:** Phillip Lowe (Systack)
**Revision:** 2.0 (Post-RAM + SAOS lessons)

---

## ⚠️ DATA SENSITIVITY ASSESSMENT (NEW — MANDATORY)

| Field | Assessment |
|-------|-----------|
| **Data Tier** | Tier 2 — Internal |
| **Rationale** | Schedules, employee data, financials — proprietary but not HIPAA |
| **Deployment Type** | Cloud VPS + Tailscale (local model, no cloud APIs) |
| **Model** | Local Ollama only (no external model calls) |
| **Compliance** | None formally required, but data is sensitive enough for local-only |
| **Recommended Tier** | Silver (8GB VPS) — currently on Bronze (4GB) pending upgrade |

---

## RAM REQUIREMENTS

| VPS Size | Model | Context | Model RAM | OS+Gateway | Total | Headroom | Status |
|----------|-------|---------|-----------|------------|-------|----------|--------|
| 4GB (current) | qwen2.5:3b | 16K | ~2.5GB | ~1.0GB | 3.5GB | 0.5GB | ⚠️ Slow, needs upgrade |
| 8GB (target) | qwen2.5:7b | 32K | ~3.5GB | ~1.0GB | 4.5GB | 3.5GB | ✅ Recommended |

**Note:** 4GB works but with stripped identity files and 2+ minute response times. 8GB is the real production minimum.

---

## What We Learned (CRITICAL)

### 1. OpenClaw Control UI REQUIRES HTTPS for Remote Access
- `gateway.controlUi.allowInsecureAuth: true` does NOT work with password auth
- Browsers enforce secure context for WebSocket connections
- **Solution:** Use Tailscale Serve (free HTTPS) or Cloudflare Tunnel

### 2. Gateway `--bind` Flag Overrides Config File
- Systemd service with `--bind lan` overrides `bind: loopback` in config
- This causes device pairing loops and scope upgrade failures
- **Solution:** Remove `--bind` from systemd service, let config handle it

### 3. Scope Upgrade Loop = Service/Config Mismatch
- "scope upgrade pending approval" appearing repeatedly
- Means the gateway is starting with different parameters each time
- **Solution:** Ensure systemd service args match config exactly

### 4. SSH Heredocs Break Over sshpass
- Writing multi-line files via sshpass/bash causes mangled content
- **Solution:** Write locally, use SCP or Python one-liners

### 5. Windows S Mode Blocks Tailscale Install
- Windows S mode only allows Microsoft Store apps
- **Solution:** Switch out of S mode (Settings → Activation → Go to Store)

### 6. VPS 4GB RAM is Minimum for qwen2.5:7b
- Model takes ~3.2GB RAM when loaded
- Gateway takes ~150MB
- **Solution:** 4GB VPS minimum, 8GB recommended for multiple models

---

## Standard Deployment Steps (Future Clients)

### 6. VPS 4GB RAM is Minimum for qwen2.5:3b, NOT 7b
- qwen2.5:7b needs ~3.2GB RAM, leaving only ~0.3GB for OS + Gateway
- qwen2.5:3b with 16K context is the realistic 4GB option
- **Solution:** 8GB VPS minimum for production, 4GB for budget/stripped demo
- **For clients with proprietary data:** Must use local models — no cloud API fallback

---

## Standard Deployment Steps (Future Clients)

### Pre-Deployment (NEW — REQUIRED)

#### Data Sensitivity Classification
- [x] Classify client data tier (Tier 1-4)
- [x] Determine deployment type (cloud vs on-premise vs air-gapped)
- [x] Check compliance requirements (HIPAA, SOX, etc.)
- [x] Select appropriate pricing tier

#### Infrastructure Sizing
- [x] Calculate RAM requirements (OS + model + headroom)
- [x] Select context window based on identity file size
- [x] Choose model tier (3b / 7b / 14b)

## Pre-Deployment (NEW — REQUIRED)

### Data Sensitivity Classification
- [x] Classify client data tier (Tier 1-4)
- [x] Determine deployment type (cloud vs on-premise vs air-gapped)
- [x] Check compliance requirements (HIPAA, SOX, etc.)
- [x] Select appropriate pricing tier
- [x] Client completes discovery questionnaire

### Infrastructure Sizing
- [x] Calculate RAM requirements (OS + model + headroom)
- [x] Select context window based on identity file size
- [x] Choose model tier (3b / 7b / 14b)
- [x] Verify internet speed (>=10 Mbps for Tailscale)

### Phase 1: VPS Setup (Systack does this)
1. Deploy Vultr 4GB VPS ($20/mo)
2. Install Ollama, pull qwen2.5:7b
3. Install OpenClaw Gateway
4. Configure password auth
5. Open firewall port 18789

### Phase 2: Tailscale Setup (Client or Systack)
1. Install Tailscale on VPS
2. Enable HTTPS in admin console (https://login.tailscale.com/admin/dns)
3. Start `tailscale serve --bg http://localhost:18789`
4. Note the HTTPS URL: `https://[machine-name].tail[NNNN].ts.net`

### Phase 3: Client Device Setup
1. Install Tailscale on client device (Windows/Mac/Phone)
2. Sign in with same account as VPS
3. Ensure device shows "Connected" in Tailscale app
4. Open browser to Tailscale HTTPS URL
5. Log in with password

### Phase 4: Agent Identity Files
1. Create SOUL.md, AGENTS.md, USER.md, MEMORY.md
2. Copy to VPS workspace: `/root/.openclaw/workspaces/percy/`
3. Restart gateway to pick up identity

---

## Percy Identity Template

```
Name: Percy
Creature: AI Personal Assistant
Vibe: Professional, helpful, GM-focused
Emoji: 🍟
Role: McDonald's General Manager Assistant
```

---

## Known Issues & Workarounds

| Issue | Symptom | Fix |
|-------|---------|-----|
| Secure browser context | "requires device identity" | Use HTTPS via Tailscale Serve |
| Scope upgrade loop | Repeated approval requests | Fix systemd service args |
| Windows S mode | Can't install Tailscale | Exit S mode first |
| Device not paired | "Unknown device" | Approve in `openclaw devices approve` |
| Gateway not listening | Port 18789 not shown | Check systemd service config |

---

## Cost Breakdown (Client Pays)

| Item | Cost | Notes |
|------|------|-------|
| Vultr VPS 4GB | $20/mo | Required infrastructure |
| Vultr VPS 8GB (target) | $40/mo | Upgrade for production |
| Tailscale | Free | Personal plan sufficient |
| OpenClaw | Free | Open source |
| Ollama | Free | Open source |
| Systack Setup | Free (beta) | In exchange for testimonial |
| Systack Monthly (Bronze) | $50/mo | Monitoring, support, identity management |

### Full Pricing Options

| Scenario | VPS | Systack | Total | Annual | Notes |
|----------|-----|---------|-------|--------|-------|
| Current (4GB) | $20/mo | $50/mo | $70/mo | $840 | Bronze — tight, slow |
| Upgrade (8GB) | $40/mo | $90/mo | $130/mo | $1,560 | Silver — recommended |
| Premium (16GB) | $80/mo | $140/mo | $220/mo | $2,640 | Gold — future-proof |

**Why the jump from $20-40 to $70-130?**
Real infrastructure costs include RAM headroom, local-only model guarantee, monitoring, and support.

**What's included in Systack monthly:**
- Agent configuration and maintenance
- Identity file management
- Health monitoring alerts
- Monthly improvement reviews
- Priority support (4-hour response)

---

## Files to Document Per Client

- `PERCY-DEPLOYMENT-PLAN.md` — Full deployment steps
- `VULTR-SETUP-LOG.md` — Server setup commands
- `TAILSCALE-CONFIG.md` — Tailscale domain, IPs
- `GATEWAY-CONFIG.md` — Final working config
- `CLIENT-DEVICE-SETUP.md` — How client connects

---

## Quick Reference

**VPS IP:** 66.42.121.145
**Tailscale Domain:** percy-mcdonalds.taildd162e.ts.net
**HTTPS URL:** https://percy-mcdonalds.taildd162e.ts.net/
**Password:** jac123
**Ollama Model:** qwen2.5:7b
**Workspace:** /root/.openclaw/workspaces/percy-mcdonalds

---

## Lessons for Next Client

1. **Always use Tailscale Serve from the start** — don't try HTTP workarounds
2. **Write service files locally, SCP them** — never use heredocs over sshpass
3. **Check Windows S mode before Tailscale install** — saves 30 minutes
4. **Document Tailscale admin console steps** — client may need to enable HTTPS
5. **Test full chain before client tries** — VPS → Tailscale → Device → Browser
6. **Have client test on phone first** — easier than Windows troubleshooting
7. **Assess data sensitivity BEFORE quoting** — determines deployment type and cost
8. **8GB VPS is the real minimum for production** — 4GB is demo/budget only
9. **Local-only model is the default** — cloud APIs only if client explicitly approves

---

*Logged by Sol on behalf of Systack*
*For Percy's memory and future deployments*
