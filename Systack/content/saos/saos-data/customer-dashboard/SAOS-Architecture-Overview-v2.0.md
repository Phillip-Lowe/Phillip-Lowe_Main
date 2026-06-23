# SAOS Architecture Overview

**Document ID:** SYS-ARCH-v2.0  
**Version:** 2.0  
**Status:** SYSTACK INTERNAL  
**Prepared for:** Systack Engineering  
**Prepared by:** SOL + ORACLE  
**Builder:** SOL + ORACLE + ASSEMBLY  
**Source System:** SAOS v2026.06  
**Date:** June 23, 2026  
**Support:** Internal

---

## SAOS System Architecture

### Overview
SAOS (Systack Agent Orchestration System) is a 10-agent AI fleet deployed on dedicated VPS instances, orchestrated via PostgreSQL task queues and accessible through Tailscale-secured networks.

---

## 1. Fleet Composition

### 10-Agent Canonical Fleet

| Tier | Agent | Emoji | Role | Capabilities |
|------|-------|-------|------|-------------|
| Execution | SOL | 🛰️ | Orchestrator | orchestration, execution, synthesis |
| Execution | CODY | 💻 | Build Engine | coding, voice, streaming |
| Execution | ASSEMBLY | 🛠️ | Deployment | n8n, workflows, credentials |
| Quality/Risk | VALI | ✅ | Validation | testing, validation, quality |
| Quality/Risk | PESSI | ⚠️ | Risk Analysis | security, validation, risk |
| Intelligence | ORACLE | 🔮 | Design/Architecture | design, research, planning |
| Intelligence | ATLAS | 🗺️ | Knowledge | memory, documentation |
| Engagement | CHATTY | 💬 | Communication | communication, onboarding, content |
| Engagement | GENI | 🎨 | Creative | image_gen, video_gen, creative |
| Compliance | JURIS | ⚖️ | Legal/Compliance | legal, regulatory oversight |

### System Loop (Canonical)

```
ORACLE → Design → CODY → Build → ASSEMBLY → Deploy → VALI → Validate → PESSI → Stress-test → SOL → Execute → CHATTY → Communicate → GENI → Visualize → ATLAS → Store → JURIS → Legal → [Loop]
```

---

## 2. Infrastructure

### VPS Tiers

| Plan | Vultr Tier | vCPU | RAM | Storage | Monthly Cost |
|------|-----------|------|-----|---------|-------------|
| Business | vhp-8c-16gb-amd | 8 | 16GB | 160GB NVMe | $96 |
| Enterprise | voc-g-8c-32gb-160s-amd | 8 | 32GB | 160GB NVMe | $240 |

### Network Architecture

```
Client Device (Tailscale)
    ↓
Tailscale Tailnet (Encrypted Mesh)
    ↓
VPS (Ubuntu 22.04 + Tailscale)
    ├─ Port 8765: Fleet Dashboard API
    ├─ Port 8766: Invoice Dashboard API
    ├─ Port 8768: Customer Portal API
    ├─ Port 18789: OpenClaw Gateway
    └─ PostgreSQL (systack_memory)
```

### Persistence

| Service | Port | LaunchAgent | Status |
|---------|------|-------------|--------|
| Fleet Dashboard | 8765 | net.systack.dashboard | ✅ Running |
| Invoice Dashboard | 8766 | net.systack.invoice-dashboard | ✅ Running |
| Customer Portal | 8768 | net.systack.customer-dashboard | ✅ Running |
| Orchestrator | N/A | net.systack.orchestrator | ✅ Running |
| Webhook Bridge | 8767 | net.systack.webhook-bridge | ✅ Running |

---

## 3. Data Flow

### Customer Portal Data Flow

```
Dashboard HTML (index.html)
    ↓ fetch every 30s
Customer Portal API (api.py :8768)
    ↓
PostgreSQL (systack_memory)
    ├─ saos_clients (account info)
    ├─ agent_state (agent status)
    ├─ task_queue (task history)
    └─ message_bus (inter-agent comms)
```

### Provisioning Pipeline

```
Stripe Checkout
    ↓
n8n Webhook (test/production)
    ↓
saos_provision_bridge.py (:8767)
    ↓
PostgreSQL task_queue (DEPLOY task)
    ↓
Orchestrator polls every 10s
    ↓
ASSEMBLY executes provision_vps.py
    ↓
Vultr API → VPS created
    ↓
Client email sent
```

---

## 4. Security Model

### Network Security
- **Tailnet-only** — no public internet exposure
- **HTTPS** — TLS termination via Tailscale
- **mTLS** — Tailscale handles device authentication

### Dashboard Security (Current)
- `?client_id=` query parameter for data scoping
- **TODO:** Add JWT/session-based authentication
- **TODO:** Add login page

### Credential Management
- OAuth secrets: Never committed (see RULE 7)
- API keys: Stored in PostgreSQL, not files
- Tailscale keys: Rotated via admin console

---

## 5. Monitoring & Health

### Health Checks
- `/api/portal/health` — Customer portal API
- `/api/portal/status` — Full fleet status
- Tailscale serve status — `tailscale serve status`

### Logs
| Service | Log Location |
|---------|-------------|
| Customer Portal | `Systack/content/saos/saos-data/logs/customer-dashboard.log` |
| Fleet Dashboard | `Systack/content/saos/saos-data/logs/dashboard.log` |
| Invoice Pipeline | `Systack/content/saos/saos-data/logs/invoice-pipeline.log` |

---

## 6. Known Issues & TODO

### High Priority
- [ ] Dashboard authentication (login + session tokens)
- [ ] Vultr API key integration for auto-provisioning
- [ ] Stripe webhook production test

### Medium Priority
- [ ] Billing portal integration
- [ ] Agent performance metrics
- [ ] Cost tracking dashboard

### Completed
- [x] Customer portal static file serving
- [x] Tailscale serve configuration
- [x] LaunchAgent auto-restart
- [x] 10-agent fleet documentation

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-17 | Initial architecture |
| 2.0 | 2026-06-23 | Added customer portal, 10-agent fleet, Tailscale serve |

**Latest version:** Internal wiki
