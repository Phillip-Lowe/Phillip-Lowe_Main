# Percy Deployment Plan — McDonald's General Manager
**Client:** [Mother's Name] — General Manager, McDonald's  
**Agent:** Percy  
**Date:** 2026-06-04  
**Status:** Draft — For Walk-Through Review

---

## Executive Summary

Percy is an AI assistant built on the same agent framework we use for ourselves. Same identity engine, same enforcement rules, same reliability — just wired to a different user with a different mission.

**She pays for infrastructure** (VPS + Ollama hosting: ~$5-10/mo).  
**We build and configure everything for free.** This is our beta pilot — we get a real-world testimonial and use case study in exchange for our setup labor.

**She uses:** A web browser. That's it. Nothing installs on her Windows laptop.

---

## What She Has vs. What She Needs

| She Has | What's Needed | Who Provides |
|---------|--------------|--------------|
| Windows laptop (low RAM) | ✅ Nothing to install | — |
| Basic computer skills | ✅ Just chat or email Percy | Systack |
| Email (work or personal) | ✅ Communication channel | Her |
| No technical background | ✅ We handle everything | Systack |
| ~$10/mo budget for server | ✅ VPS + Ollama hosting | She pays provider directly |

**Nothing gets installed on her laptop.** Percy runs on her VPS. She accesses Percy through:
- Web chat (bookmark a URL)
- Email (send tasks, Percy replies)
- Optionally: Telegram, WhatsApp, Signal

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                HER VPS (She owns, we manage)                  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                    Ubuntu Linux                       │    │
│  │  ┌──────────┐  ┌──────────────┐  ┌───────────────┐   │    │
│  │  │  Ollama  │  │ OpenClaw     │  │ Percy Agent   │   │    │
│  │  │ (AI Brain)│  │ Gateway     │  │ Workspace     │   │    │
│  │  │          │  │ (msg routing)│  │ ├ AGENTS.md   │   │    │
│  │  │ qwen2.5  │  │              │  │ ├ SOUL.md     │   │    │
│  │  │  :7b     │  │ webchat/email│  │ ├ USER.md     │   │    │
│  │  │          │  │              │  │ ├ MEMORY.md   │   │    │
│  │  │          │  │              │  │ └ TOOLS.md     │   │    │
│  │  └──────────┘  └──────────────┘  └───────────────┘   │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
│  She pays: ~$5-10/mo to Hetzner/Vultr                         │
│  We manage: Updates, security, config, models                  │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ Internet
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                 HER LAPTOP (Nothing installed)                │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ Web Browser  │  │    Email     │  │ Phone (optional)   │  │
│  │ (chat)       │  │ (Gmail/Outlk)│  │ (Telegram etc.)   │  │
│  └──────────────┘  └──────────────┘  └────────────────────┘  │
│                                                               │
│  💻 Windows, low RAM — PERFECT. Nothing to install.           │
└──────────────────────────────────────────────────────────────┘
```

---

## Percy Identity Framework

Percy is the same agent identity regardless of user. What changes is the USER.md and mission context.

### SOUL.md — Percy's Core Self
```
Name: Percy
Identity: AI personal assistant
Core traits: Helpful, direct, no corporate-speak, has opinions, resourceful
Tone: Warm but efficient. Not a sycophant. Just... good.
Boundaries: Private things stay private. Ask before external actions.
Continuity: Wakes fresh each session. Files are memory.
```

### AGENTS.md — Enforcement Layer (Same as Sol's)
Same rules apply to every Percy instance:
- Memory retrieval MANDATORY before any action
- MEMORY.md is source of truth (over chat)
- No guessing — ask if uncertain
- Document all decisions
- KUDU-7: never ask user to verify what you can verify
- Heartbeat check-ins 2-4x/day
- trasheditable > destructive commands

### USER.md — What Changes Per Client
```
Name: [Her Name]
Role: General Manager, McDonald's [location]
Context:
- Manages scheduling, inventory, staffing, reports
- Uses [Outlook/Gmail] for email
- Pain points: [discovered in discovery call]
- Quiet hours: [her preference]
- Communication preference: [chat/email/phone]
```

### MEMORY.md — Builds Over Time
Starts from discovery call, grows with every interaction:
- Decisions made and why
- Preferences and routines
- McDonald's-specific knowledge
- Lessons learned
- Active projects and next actions

---

## Tiered Capability & Restraint System

This is the framework for scaling Percy across clients. Each tier unlocks more capabilities but requires more trust/verification.

### Tier 0 — Basic Assistant (This Pilot)
**No external actions.** Read-only + internal tools.

| Capability | Restraint |
|------------|-----------|
| Task tracking & reminders | Can't send anything external |
| Draft emails/messages | Drafts only — she copies/sends |
| Schedule review (read-only) | Can't modify calendar |
| Document summaries | No file upload (paste text) |
| Web search for info | Read-only browsing |
| Note-taking & memory | Local storage only |
| Basic Q&A | No McDonald's system access |

**Approval required for:** Nothing — zero risk tier.  
**Setup complexity:** Lowest. Just Ollama + OpenClaw + webchat.  
**Client profile:** New users, risk-averse, trial period.

### Tier 1 — Trusted Assistant
**Email integration.** Can draft and send with approval.

| Added Capability | Added Restraint |
|-----------------|-----------------|
| Send emails (drafts → approve → send) | Approval gate on all outbound |
| Calendar read/write | Confirmation required for changes |
| Contact management | Read-only unless directed |
| Template-based responses | No free-form external comms |
| File attachment handling | Whitelist file types only |

**Approval required for:** Outbound emails, calendar changes.  
**Setup complexity:** Email server config, OAuth for calendar.  
**Client profile:** Trusted, daily users, passed Tier 0 for 30+ days.

### Tier 2 — Proactive Partner
**Limited autonomy.** Can act within defined parameters without asking every time.

| Added Capability | Added Restraint |
|-----------------|-----------------|
| Auto-respond to routine emails | Whitelist patterns only |
| Proactive reminders & nudges | Within quiet hours only |
| Calendar management | Pre-approved meeting types |
| Weekly digest reports | Template-driven |
| Vendor/supplier follow-ups | Canned templates only |
| Basic web form filling | Sandboxed browser |
| Slack/Teams integration | Read-only channels default |

**Approval required for:** New contacts, new email patterns, financial actions.  
**Setup complexity:** OAuth integration, browser sandbox, channel config.  
**Client profile:** Heavy users, 3+ months trust, defined SOPs for Percy.

### Tier 3 — Autonomous Operator
**Full capability.** Acts as a true digital employee within defined scope.

| Added Capability | Added Restraint |
|-----------------|-----------------|
| Full email autonomy (within rules) | Hard boundaries on financial/legal |
| Proactive task generation | Human review weekly |
| System integrations (HR, payroll) | Read-only unless explicitly allowed |
| Data analysis & reporting | No PII export |
| Vendor ordering (pre-approved) | Spend limits + approval |
| Social media management | Draft queue → human publish |
| Multi-channel presence | Per-channel rules |

**Approval required for:** Financial transactions, legal docs, new integrations.  
**Setup complexity:** Full integration suite, monitoring dashboards, audit logging.  
**Client profile:** Enterprise, dedicated IT contact, legal review done.

---

## McDonald's GM — Tier 0 Pilot Plan

She starts at **Tier 0** — zero risk, zero external actions. Build trust, learn her workflow, prove value.

### Phase 1: Infrastructure Setup (We Do This)

**Step 1: VPS**
- She creates account on Hetzner or Vultr (we walk her through it on a call)
- She buys cheapest 4GB plan (~$5-10/mo)
- She shares SSH key or we generate one together
- **She controls billing, she owns the server**

**Step 2: Software Stack**
```bash
# We SSH in and run:
sudo apt update && sudo apt upgrade -y
sudo apt install -y ufw fail2ban

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model (qwen2.5:7b for 4GB VPS, qwen2.5:3b for 2GB)
ollama pull qwen2.5:7b

# Install OpenClaw Gateway
npm install -g openclaw

# Create Percy workspace
openclaw workspace create percy-mcdonalds
```

**Step 3: Configure Percy Workspace**
Drop in our template files:
- `AGENTS.md` — enforcement layer (same as Sol)
- `SOUL.md` — Percy's identity (same as Sol)
- `USER.md` — her info from discovery call
- `MEMORY.md` — empty, builds over time
- `TOOLS.md` — McDonald's-specific tools/notes
- `HEARTBEAT.md` — proactive check-in list

**Step 4: Channel Setup**
- WebChat: Enable on OpenClaw — give her a URL
- Email: Configure inbound/outbound if she wants
- Testing: Send "Hi Percy, introduce yourself" — verify response

### Phase 2: Onboarding Call (With Her)

**Part 1 — Show It Working (10 min)**
- Open webchat URL on Zoom/screenshare
- "Hi Percy, what can you do?"
- "Percy, remind me to check the schedule tomorrow at 8am"
- "Percy, draft an email to my district manager about Q2 results"

**Part 2 — Discovery (15 min)**
Key questions:
1. Walk me through your typical day — what eats your time?
2. What software do you use? (email, scheduling, McDonald's internal)
3. What's the #1 thing you wish you could hand off?
4. What hours should Percy NEVER bother you?
5. Any McDonald's policies we should know about?

**Part 3 — The Deal (5 min)**
- "You pay the server bill directly — about $5-10/month"
- "We configure everything for free"
- "Percy starts in 'safe mode' — can't send anything, can't change anything. Reads and helps only."
- "If it works, we level Percy up. If not, cancel the server — no hard feelings."
- "What we get: your honest feedback and if it's great, a testimonial"

### Phase 3: First Week

**Day 1-2:** She plays with Percy. We watch logs.  
**Day 3:** Check-in call — what's confusing? What's useful?  
**Day 5:** Adjust SOUL.md/MEMORY.md based on her patterns.  
**Day 7:** First weekly digest — what Percy did, what it learned.

### Phase 4: Tier Progression

| Milestone | Tier Unlock |
|-----------|-------------|
| 30 days active use, 3+ tasks/day | Consider Tier 1 (email send) |
| She asks Percy to do more unprompted | Good signal |
| She wants Percy to actually send emails | Tier 1 trigger |
| She shares Percy with shift managers | Tier 2 consideration |
| McDonald's district approval | Tier 2+ possible |

---

## Cost Breakdown

| Item | Monthly | Who Pays | Notes |
|------|---------|----------|-------|
| VPS (Hetzner CPX11 or Vultr 4GB) | $5-10 | **Her** (direct to provider) | She controls billing |
| Ollama (runs on VPS) | $0 | Included in VPS | Self-hosted, no API fees |
| Domain (optional) | $0-1 | Her (optional) | Can use IP for now |
| Systack setup/config | $0 | **Us** (labor investment) | ~4-6 hours |
| Systack ongoing mgmt | $0 | **Us** (~1-2 hrs/mo) | Our beta investment |
| **Total Her Cost** | **$5-10/mo** | | |
| **Total Our Cash Cost** | **$0** | | Labor only |

---

## Files to Create Before First Call

```
clients/mcdonalds-gm/percy-workspace/
├── AGENTS.md          # Enforcement layer (copy from Sol, same rules)
├── SOUL.md            # Percy identity (copy from Sol, same personality)
├── USER.md            # Her info (TEMPLATE — filled after discovery)
├── MEMORY.md          # Starts empty, builds over time
├── TOOLS.md           # McDonald's-specific tools/notes
├── HEARTBEAT.md       # Proactive checklist for Percy
├── KUDU-7.md          # Same rule — never ask user to verify
└── PERCY-DEPLOYMENT-PLAN.md  # This file
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| VPS too slow | Medium | Medium | Upgrade to 8GB ($20/mo) or lighter model |
| She forgets to use it | Medium | Medium | Proactive check-ins, show value weekly |
| McDonald's blocks external tools | Unknown | High | Tier 0 has no integration — just webchat |
| Data privacy concern | Low | High | Ollama is local, nothing leaves VPS |
| VPS security | Low | Medium | SSH key only, UFW, fail2ban, auto-updates |
| She wants features Tier 0 can't do | Medium | Low | Clear tier roadmap, upgrade path ready |

---

## Success Metrics (30 Days)

- [ ] Percy responds within 10 seconds (local model)
- [ ] She uses Percy 3+ times/day by week 2
- [ ] 5+ tasks successfully delegated
- [ ] Zero "Percy did something wrong/scary"
- [ ] She refers to Percy by name (adoption signal)
- [ ] She voluntarily suggests a new use case
- [ ] Ready for Tier 1 consideration at day 30

---

## Walk-Through Cheat Sheet

### Opening
> "You know how I'm always tinkering with AI stuff? I built an assistant called Percy. It's the same one I use myself. I want you to try it — for free. You just talk to it through a website."

### Demo
> "Watch this — 'Percy, what's my name?' ... 'Percy, remind me to call the district manager Friday at 10am.' ... See? It remembers things and helps you stay organized."

### Infrastructure (simple)
> "Percy lives on a server in the cloud. You pay about $10 a month for that server — like a Netflix subscription. I set everything up. You don't install anything. You just open this website."

### Safety
> "Right now Percy can't send emails or change anything. It's in training wheels mode. As you trust it more, we unlock more abilities. You're always in control."

### Close
> "Want to try it for a week? If you hate it, cancel the server. If it helps, great — you tell me what worked and I make it better."

---

## Appendix A: VPS Setup Checklist (For Us)

- [ ] She creates Hetzner/Vultr account
- [ ] She purchases 4GB VPS
- [ ] SSH key generated/exchanged
- [ ] Ubuntu updated, firewall enabled
- [ ] Ollama installed + model pulled
- [ ] OpenClaw Gateway installed
- [ ] Percy workspace created with all files
- [ ] WebChat channel enabled
- [ ] Test message: "Hi Percy, introduce yourself"
- [ ] Send her the webchat URL
- [ ] Schedule day-3 check-in

---

## Appendix B: Tier Comparison at a Glance

| | Tier 0 | Tier 1 | Tier 2 | Tier 3 |
|------|--------|--------|--------|--------|
| **External actions** | None | Email (approved) | Limited auto | Full autonomy |
| **Calendar** | Read | Read/Write (approved) | Auto-manage | Full integration |
| **Email** | Draft only | Send (approved) | Pattern-based auto | Full auto |
| **Systems** | None | None | Slack/Teams read | Full integrations |
| **Trust required** | Zero | Low | Medium | High |
| **Setup complexity** | 4-6 hours | +2 hours | +4 hours | +10 hours |
| **Client profile** | New/risk-averse | 30-day active user | 90-day trusted | Enterprise |
| **Pricing** | $0 setup / $5-10 VPS | TBD | TBD | TBD |

---

## Document Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-04 | Initial draft with tiered capability framework |
