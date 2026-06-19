---
title: "SyStack Service Manual"
subtitle: "Brand Standards, Fleet Architecture & Client Operations"
version: "1.0"
date: "2026-06-19"
status: "INTERNAL / CLIENT-FACING"
classification: "SYSTACK PROPRIETARY"
author: "SOL (Systack Operations Layer)"
repo: "github.com/Phillip-Lowe/systack-saas"
website: "https://systack.net"
---

# SyStack Service Manual

## Document Metadata

| Field | Value |
|-------|-------|
| **Document ID** | SYS-MANUAL-v1.0 |
| **Version** | 1.0 |
| **Status** | 🟢 ACTIVE |
| **Date** | 2026-06-19 |
| **Classification** | SyStack Proprietary (Internal / Client-Facing) |
| **Author** | SOL — Systack Operations Layer |
| **Website** | https://systack.net |
| **Repository** | github.com/Phillip-Lowe/systack-saas |
| **Support** | support@systack.net |

---

# Part I: Brand Identity

## Chapter 1: Who We Are

### Mission
**SyStack builds autonomous operations infrastructure for businesses that refuse to operate at human speed.**

Every business has repetitive work that shouldn't require a human. We build the infrastructure — agents, automations, and orchestration layers — that removes the friction between "need it done" and "it's done."

### Vision
By 2028, every business operating at fewer than 50 employees will have a digital operations layer as standard as a website. SyStack defines what that layer looks like, how it integrates, and how it scales.

### Values

| Value | What It Means |
|-------|---------------|
| **Competence over Noise** | We ship working systems, not slide decks. Every deliverable is tested end-to-end before it leaves the shop. |
| **Autonomy, Not Replacement** | Our agents don't replace people. They remove the parts of the job that waste human attention. |
| **Local First, Cloud When Needed** | Data stays with the client. Cloud is transport, not storage. |
| **Transparency in Everything** | Clients see what we built, how it works, and how to maintain it. No black boxes. |
| **Earned Trust** | We don't promise what we can't deliver. We document what we delivered so future-us can maintain it. |

---

## Chapter 2: Visual Identity

### Color Palette

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Primary Brand | Navy | `#001a2d` | Headers, CTAs, dark backgrounds |
| Secondary | Teal | `#007da9` | Accents, secondary buttons, gradients |
| Primary Action | Cyan | `#00a1db` | Buttons, links, active states |
| Highlight | Cyan Bright | `#00c5e0` | Gradients, highlights, hover states |
| Background Light | Gray 50 | `#f8fafc` | Page backgrounds, cards |
| Background Medium | Gray 100 | `#f1f5f9` | Alternate rows, subtle fills |
| Border | Gray 200 | `#e2e8f0` | Dividers, borders, separators |
| Body Text | Gray 600 | `#475569` | Paragraphs, descriptions |
| Headings | Gray 800 | `#1e293b` | Titles, labels, emphasis |
| Success | Green | `#22c55e` | Confirmed, active, positive |
| Error | Red | `#ef4444` | Failed, blocked, negative |
| Warning | Purple | `#8b5cf6` | Pending, needs attention |

### Typography

| Element | Font | Weight | Size | Color |
|---------|------|--------|------|-------|
| H1 | Helvetica Neue | Bold | 24pt | Navy `#001a2d` |
| H2 | Helvetica Neue | Semibold | 16pt | Gray 800 `#1e293b` |
| H3 | Helvetica Neue | Medium | 12pt | Gray 800 `#1e293b` |
| Body | Helvetica Neue | Regular | 10.5pt | Gray 600 `#475569` |
| Caption | Helvetica Neue | Regular | 8pt | Gray 400 `#94a3b8` |
| Code | Courier New | Regular | 9pt | Navy `#001a2d` |

### Logo Usage

The SyStack logo is the primary visual identifier. It appears on:
- All documentation headers
- Client deliverables (top-right corner)
- Website and landing pages
- Email templates
- Business cards and printed materials

**Do not:** distort, recolor (except approved monochrome), or place over busy backgrounds.

---

## Chapter 3: Voice & Tone

### Writing Principles

| Principle | Application |
|-----------|-------------|
| **Concise** | One idea per sentence. No filler. |
| **Direct** | "Do this" not "It might be suggested that one could potentially consider..." |
| **Specific** | Numbers, names, paths — never vague hand-waving. |
| **Honest** | If something has limitations, say so. If something is experimental, label it. |
| **Action-oriented** | Every paragraph should move toward a decision or action. |

### Tone by Context

| Context | Tone | Example |
|---------|------|---------|
| **Client Documentation** | Professional, instructional | "Run `python3 provision.py --client-id ABC123` to begin deployment." |
| **Internal Notes** | Direct, abbreviated | "FIXME: hardcoded region in provision_vps.py line 87" |
| **Error Messages** | Clear, actionable | "Connection refused on port 5678. Ensure n8n is running: `systemctl status n8n`" |
| **Marketing** | Bold, confident | "Your operations layer, delivered in minutes, not months." |
| **Support** | Patient, systematic | "Let's check three things: logs, credentials, and network state." |

---

# Part II: The Fleet

## Chapter 4: Agent Architecture

The SyStack Fleet is composed of 10 specialized agents organized in 5 functional tiers. Each agent has a specific role, decision authority, and operational scope.

### Fleet Table

| Tier | Agent | Role | Emoji | Status |
|------|-------|------|-------|--------|
| **Execution** | SOL | Orchestrator, Synthesis, Strategy | 🌞 | 🟢 Active |
| **Execution** | CODY | Build Engine, Code, Technical Docs | 🛠️ | 🟢 Active |
| **Execution** | ASSEMBLY | Deployment, n8n, Workflows | 🔧 | 🟢 Active |
| **Quality/Risk** | VALI | Validation, Testing, QA | ✅ | 🟢 Active |
| **Quality/Risk** | PESSI | Risk Analysis, Security, Stress-Test | ⚠️ | 🟢 Active |
| **Intelligence** | ORACLE | Design, Architecture, Planning | 🔮 | 🟢 Active |
| **Intelligence** | ATLAS | Knowledge, Documentation, Memory | 📚 | 🟢 Active |
| **Engagement** | CHATTY | Communication, Client Onboarding, Content | 💬 | 🟢 Active |
| **Engagement** | GENI | Creative, Image Gen, Video Gen | 🎨 | 🟢 Active |
| **Compliance** | JURIS | Legal, Compliance, Audit | ⚖️ | 🟢 Active |

### System Loop

```
ORACLE → Design → CODY → Build → ASSEMBLY → Deploy → VALI → Validate → PESSI → Stress-test → SOL → Execute → CHATTY → Communicate → GENI → Visualize → ATLAS → Store → JURIS → Legal → [Loop]
```

Each phase gates the next. No deployment proceeds without VALI validation. No communication goes out without JURIS compliance review.

---

## Chapter 5: Agent Profiles

### SOL (Orchestrator)
- **Responsibility:** Strategy, planning, task allocation, synthesis of multi-agent work
- **Authority:** Can override any agent decision with justification
- **Primary Model:** kimi-k2.6:cloud / qwen3.5:9b
- **Scope:** Cross-fleet coordination, client-facing decisions, resource allocation

### CODY (Build Engine)
- **Responsibility:** Code generation, refactoring, multi-file technical changes
- **Authority:** Manages Git repos, CI/CD pipelines, build integrity
- **Primary Model:** qwen2.5-coder:7b (local) / kimi-k2.6:cloud
- **Scope:** All technical implementation, test writing, deployment scripts

### ASSEMBLY (Deployment)
- **Responsibility:** n8n workflow management, credential handling, service deployment
- **Authority:** Admin on all automation infrastructure
- **Primary Model:** qwen3.5:9b
- **Scope:** n8n, Vultr VPS, Tailscale, OpenClaw instances

### VALI (Validation)
- **Responsibility:** Testing, quality gates, pre-deployment verification
- **Authority:** Can block deployment to production
- **Primary Model:** qwen3.5:9b
- **Scope:** All code review, test execution, staging validation

### PESSI (Risk)
- **Responsibility:** Security auditing, penetration testing, stress analysis
- **Authority:** Flags high-risk patterns, enforces safety rules
- **Primary Model:** qwen3.5:9b
- **Scope:** Security review, compliance checks, credential safety

### ORACLE (Architecture)
- **Responsibility:** System design, technology selection, capacity planning
- **Authority:** Defines technical direction, approves new stack additions
- **Primary Model:** kimi-k2.6:cloud
- **Scope:** Architecture decisions, design patterns, scalability planning

### ATLAS (Knowledge)
- **Responsibility:** Documentation, memory maintenance, wiki curation
- **Authority:** Defines information architecture, naming conventions
- **Primary Model:** qwen3.5:9b
- **Scope:** MEMORY.md, daily logs, wiki, entity management

### CHATTY (Communication)
- **Responsibility:** Client communication, onboarding, support responses
- **Authority:** Manages all external messaging channels
- **Primary Model:** qwen3.5:9b
- **Scope:** Email, Slack, support tickets, social media

### GENI (Creative)
- **Responsibility:** Image generation, video creation, branding assets
- **Authority:** Defines visual standards, generates deliverable graphics
- **Primary Model:** ComfyUI (local)
- **Scope:** Marketing assets, client visuals, social media content

### JURIS (Compliance)
- **Responsibility:** Legal review, compliance framework, data governance
- **Authority:** Blocks any action that violates compliance policy
- **Primary Model:** qwen3.5:9b
- **Scope:** GDPR/CCPA, data retention, breach response, audit trails

---

# Part III: Service Offerings

## Chapter 6: SAOS (Systack Autonomous Operations Stack)

### What Is SAOS?

SAOS is a fully managed AI operations layer deployed to a dedicated cloud VPS. It includes:
- Local AI inference (Ollama with qwen2.5:7b)
- Workflow automation (n8n)
- Agent orchestration (OpenClaw)
- Secure networking (Tailscale VPN)
- Monitoring, backups, and updates

### SAOS Tiers

| Feature | Starter | Professional | Business | Enterprise |
|---------|---------|--------------|----------|------------|
| **Price** | $49/mo | $149/mo | $299/mo | Custom |
| **VPS Specs** | 1 vCPU / 1GB | 2 vCPU / 4GB | 4 vCPU / 16GB | 8 vCPU / 32GB |
| **RAM** | 1 GB | 4 GB | 16 GB | 32 GB |
| **AI Model** | None | qwen2.5:7b | qwen2.5:7b + whisper | Multi-model cluster |
| **Agents** | 3 | 7 | 10 | 10+ custom |
| **n8n Workflows** | 5 | 20 | Unlimited | Unlimited |
| **Storage** | 25 GB SSD | 80 GB SSD | 160 GB NVMe | 320 GB NVMe |
| **Bandwidth** | 1 TB | 3 TB | 6 TB | Unmetered |
| **Backups** | Weekly | Daily | Hourly | Continuous |
| **Support** | Email | Email + Chat | Priority + Phone | Dedicated + SLA |
| **Setup Time** | 5 min | 10 min | 8 min | 15 min |

### What's Included in All Tiers

- Tailscale VPN (zero-config secure access)
- UFW firewall with fail2ban
- Automated security updates
- PostgreSQL database
- SQLite local storage
- Webhook endpoints (n8n)
- Email integration (SMTP/IMAP)
- Agent memory system (OpenClaw)

### Cost Breakdown (Business Tier)

| Component | Monthly Cost |
|-----------|-------------|
| Vultr VPS (16GB) | $96 |
| Monitoring & Backup | $10 |
| Bandwidth | Included |
| License (self-hosted) | $0 |
| **Cost to Serve** | **$106** |
| **SAOS Price** | **$299** |
| **Profit Margin** | **$193 (65%)** |

---

## Chapter 7: Product Catalog

### Invoice Automation
- **Description:** IMAP-triggered invoice capture, OCR extraction, database logging, dashboard
- **Status:** ✅ Production
- **Demo:** https://invoices.systack.net/extract
- **Price:** Included in Professional+

### Online Ordering System
- **Description:** White-label food ordering with payment (Square) and kitchen management
- **Status:** ✅ Production (Utopia Deli)
- **Demo:** https://order.theutopiadeli.com
- **Price:** $299/mo + $200 setup

### No-Show Prevention
- **Description:** Booking system with SMS/email reminders and auto-reschedule
- **Status:** ✅ Production (Fearless Kutz)
- **Price:** Included in Professional+

### VPS Provisioning Pipeline
- **Description:** Automated cloud VPS deployment with AI agents
- **Status:** ✅ Production (validated 2026-06-19)
- **Price:** See SAOS tiers

---

# Part IV: Operations

## Chapter 8: Provisioning Procedure

### SAAS VPS Deployment (Automatic)

```
Stripe Payment → n8n Webhook → Create Client → Queue DEPLOY Task
                                                ↓
                                    Bridge Picks Up (30s interval)
                                                ↓
                                    Vultr API Creates VPS
                                                ↓
                                    Cloud-Init First Boot (install)
                                                ↓
                                    Auto-Reboot
                                                ↓
                                    Second Boot (systemd finalize)
                                                ↓
                                    Webhook: saos-vps-ready
                                                ↓
                                    Client Notified
```

**Total Time:** 7-8 minutes from payment to ready

### Manual VPS Deployment

```bash
cd /tmp/systack-saas-init
python3 scripts/provision_vps.py \
  --client-id CLIENT-001 \
  --tier business \
  --email "client@example.com" \
  --agent-name "ClientAgent" \
  --wait
```

### Health Verification

After provisioning, verify:

```bash
# SSH to VPS
ssh root@<vps-ip>

# Check services
systemctl is-active ollama docker tailscaled

# Check AI model
ollama list

# Check Tailscale
tailscale status

# Check logs
cat /var/lib/cloud/instance/saas-provision.log
```

---

## Chapter 9: Monitoring & Support

### Monitoring Stack

| Component | Tool | Alert Channel |
|-----------|------|---------------|
| VPS Health | Custom health_check.py | n8n + Slack |
| Agent Status | OpenClaw heartbeat | n8n + Email |
| Disk Space | df monitoring | Slack |
| Memory Usage | vmstat | Slack |
| Service Status | systemctl | n8n |
| SSL Certificates | certbot | Email |

### Support Levels

| Severity | Response Time | Resolution Target | Escalation |
|----------|--------------|-------------------|------------|
| P0 (Down) | 15 min | 2 hours | SOL + Phillip |
| P1 (Broken) | 1 hour | 4 hours | ASSEMBLY + SOL |
| P2 (Degraded) | 4 hours | 24 hours | CHATTY + Support |
| P3 (Question) | 24 hours | 72 hours | CHATTY |

### On-Call Schedule

- **Primary:** SOL (automated monitoring)
- **Secondary:** Phillip Lowe (human escalation)
- **Escalation:** Direct to Phillip via SMS for P0/P1

---

## Chapter 10: Compliance & Security

### Compliance Framework (JURIS)

| Document | Purpose | Status |
|----------|---------|--------|
| Compliance Quick-Reference | Daily decision guide | ✅ Active |
| Breach Response Procedure | Incident response playbook | ✅ Active |
| Data Destruction Policy | Retention & deletion rules | ✅ Active |
| Compliance Framework Master | Governance & controls | ✅ Active |

### Security Standards

| Standard | Implementation |
|----------|---------------|
| Data Encryption | TLS 1.3 in transit, AES-256 at rest |
| Network Security | Tailscale WireGuard VPN, UFW firewall, fail2ban |
| Access Control | Role-based Postgres permissions, keychain-only credentials |
| Backup Policy | Hourly snapshots (Business tier), 7-day retention |
| Audit Logging | Full execution_log table, immutable entries |

### Incident Response

1. **Detect:** Automated monitoring alerts
2. **Assess:** PESSI evaluates severity and scope
3. **Contain:** ASSEMBLY isolates affected systems
4. **Notify:** CHATTY informs client within SLA
5. **Remediate:** CODY + ASSEMBLY implement fix
6. **Review:** VALI validates fix, JURIS documents lesson
7. **Close:** SOL updates MEMORY.md with post-mortem

---

# Part V: Appendices

## Appendix A: Contact Directory

| Role | Name | Contact | Availability |
|------|------|---------|--------------|
| Founder & CTO | Phillip Lowe | plowe@systack.net | Mon-Fri, 5PM-10AM CT |
| Operations Lead | SOL | sol@systack.net | 24/7 (automated) |
| Support | CHATTY | support@systack.net | 24/7 (automated) |
| Security | PESSI | security@systack.net | 24/7 (automated) |
| Billing | JURIS | billing@systack.net | Business hours |

## Appendix B: API Endpoints

| Service | Endpoint | Auth |
|---------|----------|------|
| Invoice Extractor | https://invoices.systack.net/extract | API key |
| n8n Webhook | https://n8n.systack.net/webhook/{path} | n8n API key |
| Utopia Deli Orders | https://order.theutopiadeli.com | Square token |
| Dashboard API | http://localhost:8765 | Local only |
| Invoice Dashboard | http://localhost:8766 | Local only |
| Postgres | localhost:5432 | DB credentials |

## Appendix C: Credential Storage

All credentials stored in `~/.openclaw/workspaces/sol/credentials/` with service subdirectories:
- `Green/Vultr/` — Vultr API key
- `Green/Tailscale/` — Tailscale auth + API keys
- `Green/n8n/` — n8n API token
- `Green/postgres/` — DB passwords
- `Green/stripe/` — Stripe keys

**Rule:** Never commit credentials. Keychain only. Check git diff before push.

## Appendix D: Quick Commands

```bash
# Start bridge manually
cd /tmp/systack-saas-init
python3 scripts/saos_provision_bridge.py --interval 30

# Check bridge status
launchctl list | grep saos-provision-bridge

# Restart bridge
launchctl unload ~/Library/LaunchAgents/net.systack.saos-provision-bridge.plist
launchctl load ~/Library/LaunchAgents/net.systack.saos-provision-bridge.plist

# View bridge logs
tail -f /tmp/systack-saas-init/logs/saos-bridge.log

# Check task queue
psql -U systack -d systack_memory -c "SELECT id, status, assigned_agent FROM task_queue WHERE status='PENDING';"
```

## Appendix E: Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-06-19 | Initial manual after VPS pipeline E2E validation | SOL |

---

*SyStack Service Manual v1.0 — Generated by SOL after full end-to-end validation of the SAOS Business Tier VPS Provisioning Pipeline (2026-06-19).*

*All test instances destroyed. Production pipeline ready for client onboarding.*
*For updates, edit the source Markdown and regenerate via branded PDF pipeline.*
