# SAOS Fleet — Complete Context Handoff for ORACLE

**Document ID:** SYS-ORACLE-HANDOFF-v1.0
**Prepared for:** ORACLE (System Design & Research Agent)
**Prepared by:** SOL + ATLAS
**Date:** June 25, 2026
**Status:** AUTHORITATIVE — Build Upon This

---

## Executive Summary

ORACLE, you are receiving the complete knowledge base for Systack's **SAOS (Systack Agent OS)** product line — the AI agent fleet platform, the customer dashboard, and all related service offerings. This document consolidates everything: what exists, what's running, what we're building, pricing, architecture, and strategic direction.

Use this as your sole source of truth when designing systems, researching solutions, or advising on SAOS-related decisions.

---

## Part 1: The Big Picture — What Is Systack?

### Systack Defined
**Systack.net** is a systems automation company that builds revenue-generating infrastructure for small-to-medium businesses. We operate in three verticals:

1. **SAOS Fleet** — AI agent subscriptions ($299-$799/mo)
2. **Custom Order Systems** — One-time builds + monthly support ($3,500 + $250/mo)
3. **Workflow Automation** — Custom n8n integrations ($249-$799/mo + setup)

### The Core Philosophy
> "Your revenue is yours." — We don't take a cut of bookings. We don't own your customers. We build systems that put money in your pocket — not ours.

### Company Stats
- **3+ years** building systems
- **24/7** systems running
- **97%** revenue you keep (vs 70-85% on platforms)
- **2-3 days** average time to launch

---

## Part 1A: SAOS (Systack Agent OS) — Flagship Product

### What Is SAOS?
**SAOS = Systack Agent OS** — A managed fleet of autonomous AI agents running on dedicated cloud infrastructure, delivered to businesses as a subscription service.

### The Value Proposition
- **For Businesses:** Get an AI team that works 24/7 without hiring, training, or managing employees
- **For Us:** Recurring revenue ($299-$799/mo) with high margins (infrastructure costs ~$80/mo)
- **Differentiator:** Local AI models (privacy), dedicated VPS (no shared resources), managed service (zero client setup)

### Current Status: LIVE
- Infrastructure: Running on Vultr VPS (16GB/32GB tiers)
- Dashboard: Customer portal with PIN auth, 6 tabs, mobile-responsive
- Agents: 10-agent fleet deployed and functional
- Network: Tailscale VPN for secure client access
- Documentation: Service Manual v4.0, Dashboard User Guide v1.0, Quick Start Guide v4.0

---

## Part 2: The Dashboard — What It Is & What It Does

### What Is the Customer Dashboard?
The **SAOS Customer Dashboard** is the client-facing portal where SAOS subscribers:
- Monitor their AI fleet status in real-time
- Chat with agents through a web interface
- Track tasks and agent activity
- Access documentation and service manuals
- Manage their account settings

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT BROWSER                          │
│         (Tailscale-connected, mobile + desktop)             │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTPS
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              TAILSCALE SERVE PROXY                           │
│     https://phillips-macbook-air.tail573d57.ts.net           │
│                    /dashboard/*  ─────►                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│           FLASK API (Python) — Port 8768                      │
│  • Serves static HTML/CSS/JS (customer-dashboard/index.html)  │
│  • RESTful API endpoints (/api/*)                             │
│  • PostgreSQL database backend                                │
│  • PIN-based authentication + session tokens                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              POSTGRESQL DATABASE                             │
│  • saos_clients (client profiles, PINs)                      │
│  • client_auth_tokens (session management)                  │
│  • tasks (task queue and history)                            │
│  • agents (fleet metadata)                                    │
│  • messages (chat history)                                   │
└─────────────────────────────────────────────────────────────┘
```

### Dashboard Tabs (6 Total)

| Tab | Purpose | Key Features |
|-----|---------|-------------|
| **💬 Chat** | Real-time agent conversations | Message history, agent selector, typing indicators |
| **📊 Fleet Status** | Agent health & metrics | 10 agent cards, status dots, task counts |
| **📦 Services** | Tier-specific service catalog | Business vs Enterprise access levels |
| **✅ Tasks** | Task history & tracking | Status filtering, timestamps, priority indicators |
| **📋 Activity** | Audit trail of recent actions | Timestamped log of system events |
| **📄 Docs** | In-app documentation | Service Manual, Quick Start, Mobile Access Guide |

### Authentication
- **PIN-based login** (4-digit PIN, no passwords)
- **Session tokens** stored in browser localStorage (30-day expiry)
- **Tailscale required** — dashboard only accessible within tailnet
- **Client ID + PIN** pair required for first login

### Mobile Support
- Full responsive design (iOS Safari, Android Chrome)
- Hamburger menu navigation
- Sidebar toggle for chat conversations
- Touch-optimized buttons (44px minimum)
- Auto-hiding navigation on scroll

### Files
- **Frontend:** `Systack/content/saos/saos-data/customer-dashboard/index.html` (~2,900 lines)
- **Backend:** `Systack/content/saos/saos-data/customer-dashboard/api.py` (Flask, port 8768)
- **LaunchAgent:** `net.systack.customer-dashboard` (auto-restart on crash)

---

## Part 3: The Agent Fleet (10 Agents)

### Core Tier (Included in Business + Enterprise)

| Agent | Emoji | Role | Model | When to Use |
|-------|-------|------|-------|-------------|
| **SOL** | 🛰️ | Strategic oversight, routing | `kimi-k2.6:cloud` | Task dispatch, status checks |
| **VALI** | ✅ | Validation, QA | `kimi-k2.6:cloud` | Code review, verification |
| **PESSI** | ⚠️ | Risk identification | `deepseek-v4-pro:cloud` | Stress-testing, edge cases |
| **ORACLE** | 🔮 | System design, research | `kimi-k2.6:cloud` | Architecture decisions |
| **ATLAS** | 🗺️ | Memory, knowledge | `kimi-k2.6:cloud` | Historical lookups |
| **ASSEMBLY** | 🛠️ | Deployment, releases | `deepseek-v4-pro:cloud` | Build/push operations |
| **JURIS** | ⚖️ | Legal/compliance | `kimi-k2.6:cloud` | Contract review |

### Extended Tier (Included in ALL plans — previously Enterprise-only)

| Agent | Emoji | Role | Model | When to Use |
|-------|-------|------|-------|-------------|
| **CODY** | 💻 | Coding, scripting | `deepseek-v4-pro:cloud` | Build workflows, scripts |
| **CHATTY** | 💬 | Communications | `kimi-k2.6:cloud` | Client emails, onboarding |
| **GENI** | 🎨 | Creative, visuals | `deepseek-v4-pro:cloud` | Images, diagrams, content |

### Agent Communication
- Agents can spawn subagents for delegation
- Cross-agent messaging via OpenClaw's agent-to-agent protocol
- Each agent has its own workspace (`~/.openclaw/workspaces/{agent}/`)
- Identity files: `IDENTITY.md`, `SOUL.md`, `USER.md`, `AGENTS.md`

---

## Part 4: Service Offerings (Complete Portfolio)

### PRIMARY: SAOS Fleet Subscriptions

| Plan | Price | What You Get | Target |
|------|-------|-------------|--------|
| **Business Fleet** | $299/mo ($2,988/yr) | 10 agents, 16GB VPS, 5 team members, 10K n8n runs, same-day support | Small-medium businesses |
| **Enterprise Fleet** | $799/mo ($7,990/yr) | 10 agents, 32GB VPS, unlimited n8n, dedicated support line, 4hr SLA, quarterly reviews | Larger orgs |

### SECONDARY: Custom Automation Systems

| Service | Price | Description |
|---------|-------|-------------|
| **Accelerate** | $249/mo + $2,500 setup | Cloud VPS, custom n8n workflows, up to 10K runs, Slack/Google integration |
| **Private** | $799/mo + $4,500 setup | On-premise, air-gapped, HIPAA-ready, 24K models, white-glove setup |

### ONE-OFF: Project Work

| Service | Price Range | Description |
|---------|-------------|-------------|
| **Booking/Order System** | $2,500-$5,000 | Custom branded booking + payment (Square/Stripe), confirmations, reminders |
| **Invoice Extractor** | $1,500-$3,000 | Email PDF → structured data, 8+ vendor formats, <60s processing |
| **AI Video Ad Production** | $500-$1,500/video | Kling AI + ElevenLabs voiceover + Premiere assembly, 4K delivery |
| **Campaign Series** | $1,500-$5,000 | 3-5 themed videos per business |
| **Monthly Social Retainer** | $2,000-$5,000/mo | Ongoing content production and management |

### EXAMPLES OF LIVE SYSTEMS

| Client | System | URL | Status |
|--------|--------|-----|--------|
| Utopia Deli | Online ordering + payment | order.theutopiadeli.com | LIVE — Accepts orders 24/7 |
| Systack Internal | Invoice processing | Internal tool | LIVE — <60s per invoice |
| Systack Internal | Fleet dashboard | localhost:8765 | LIVE — 10-agent monitoring |

---

## Part 5: Infrastructure & Architecture

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Models** | Ollama (local) + Cloud fallback (Kimi, DeepSeek) |
| **Orchestration** | OpenClaw (agent framework) |
| **Workflows** | n8n (automation engine) |
| **Database** | PostgreSQL (primary) + SQLite (local) |
| **Server** | Vultr VPS (16GB or 32GB) |
| **Network** | Tailscale VPN (encrypted mesh) |
| **Dashboard** | Flask + vanilla JS (no framework) |
| **Payments** | Stripe (subscriptions), Square (client checkout) |

### Network Architecture
```
Client Device → Tailscale → Vultr VPS (agent host)
                     ↓
              Dashboard API (port 8768)
                     ↓
              PostgreSQL (port 5432)
                     ↓
              OpenClaw Agents
                     ↓
              n8n Workflows
                     ↓
              External APIs (Stripe, Square, etc.)
```

### Running Services (Ports)

| Port | Service | Purpose |
|------|---------|---------|
| 8765 | Fleet Dashboard API | Internal fleet control |
| 8766 | Invoice Dashboard API | Invoice processing UI |
| 8768 | Customer Portal API | Client-facing dashboard |
| 1234 | BlueBubbles Server | iMessage bridge |

---

## Part 6: Pricing & Business Model

### Revenue Streams

| Stream | Monthly Revenue | Notes |
|--------|----------------|-------|
| SAOS Business ($299) | TBD | Primary target |
| SAOS Enterprise ($799) | TBD | Higher margin |
| Custom Projects | $2,500-$5,000 each | One-time + ongoing maintenance |
| Retainers | $2,000-$5,000/mo | Social content, ongoing automation |

### Costs

| Cost Item | Monthly |
|-----------|---------|
| Vultr VPS (16GB) | ~$80 |
| Vultr VPS (32GB) | ~$160 |
| Domain/SSL | ~$10 |
| n8n hosting | Included in VPS |
| Total per client | ~$90-$170 |

### Margin
- Business Fleet: ~70% margin ($299 - $90 = $209)
- Enterprise Fleet: ~80% margin ($799 - $170 = $629)

---

## Part 7: Strategic Direction & Roadmap

### Completed (June 2026)
- ✅ 10-agent fleet operational
- ✅ Customer dashboard with PIN auth
- ✅ Mobile-responsive dashboard
- ✅ Tailscale VPN deployment
- ✅ Service documentation v4.0
- ✅ BlueBubbles delivery fixed
- ✅ Real-time chat in dashboard

### In Progress / Next Up
- 🔄 End-to-end SAOS provisioning testing (real Vultr/Tailscale/n8n credentials)
- 🔄 Fix Tailscale `.ts.net` URL on iOS Safari (cert trust issue)
- 🔄 Update PDF documentation (Dashboard User Guide v2.0 with Activity tab)
- 🔄 Create new "Dashboard Mobile Access Guide" PDF

### Future Opportunities (Revenue)
- 📌 AI Video Ad Service — $500-1500/video (systematized pipeline exists)
- 📌 Monthly Social Retainer — $2-5K/mo
- 📌 White-label dashboard for resellers
- 📌 API access for developers
- 📌 Integration marketplace (connectors for popular tools)

---

---

## Part 9: ALL SYSTACK SERVICE OFFERINGS (Complete)

This section documents EVERY service Systack offers — not just SAOS. When ORACLE designs systems or researches solutions, she must consider the full portfolio.

---

### A. SAOS Fleet Subscriptions (Flagship)

| Plan | Price | What You Get | Target |
|------|-------|-------------|--------|
| **Business Fleet** | $299/mo ($2,988/yr) | 10 agents, 16GB VPS, 5 team members, 10K n8n runs, same-day support | Small-medium businesses |
| **Enterprise Fleet** | $799/mo ($7,990/yr) | 10 agents, 32GB VPS, unlimited n8n, dedicated support line, 4hr SLA, quarterly reviews | Larger orgs |

**Delivery:** Managed VPS via Vultr, Tailscale VPN, customer dashboard, PIN auth
**Contracts:** No contracts, cancel anytime, 30-day refund
**Setup:** Zero client setup — we handle everything

---

### B. Custom Order/Booking Systems (Primary Revenue Driver)

**What It Is:** Branded online order/booking forms with payment integration

**Target Businesses:**
- Restaurants (pickup orders)
- Salons/barbers (appointment booking)
- Auto shops (service scheduling)
- Cleaning services (booking + quotes)
- Photographers (session packages)
- Consultants/coaches (session booking)
- Fitness trainers (package sales)
- Contractors (job estimates)
- Tutors (recurring sessions)
- And any service business that takes appointments or orders

**Pricing:**
- **One-time build:** $3,500
- **Monthly support:** $250/mo (or $2,400/yr — save $600)
- **Payment processing:** Client's Square/Stripe account (2.9% + 30¢)

**What's Included:**
- Custom branded order form (logo, colors, menu/services)
- Square/Stripe payment integration
- Email + SMS confirmations
- Modifier/add-on pricing
- Tax automation (configured for city/state)
- Hours gating (blocks orders when closed)
- Google Sheets order logging
- After-hours queue (order ahead)
- Mobile-responsive design
- Testing + go-live support

**Ongoing Monthly:**
- Form monitoring (stays live)
- Menu/service edits
- Technical support

**What's NOT Included:**
- Square processing fees (2.9% + 30¢ — client pays)
- Domain/hosting (~$12/yr if needed)
- Custom calendar integration (available as add-on)

**Real Example — Utopia Deli:**
- URL: order.theutopiadeli.com
- Average order time: ~60 seconds
- Payment fee: 3.2% (vs 20%+ on delivery apps)
- Orders accepted: 24/7 (even when closed)
- Time to launch: 2 days

---

### C. Workflow Automation (n8n-Based)

**What It Is:** Custom automation workflows connecting business tools

**Use Cases:**
- Invoice processing (email PDF → structured data)
- Lead qualification (form → CRM → notification)
- Customer support drafting (ticket → AI response → approval)
- Data extraction and routing
- Social media posting automation
- Report generation and delivery

**Pricing Tiers:**

| Tier | Price | Features |
|------|-------|----------|
| **Accelerate** | $249/mo + $2,500 setup | Cloud VPS, custom workflows, up to 10K runs, Slack + Google integration, same-day support |
| **Private** | $799/mo + $4,500 setup | On-premise hardware, air-gapped, HIPAA-ready, 24K models, white-glove setup, 4hr SLA |

**What's Included:**
- n8n hosting and management
- PostgreSQL database
- Custom workflow development
- Up to 10K automation runs/mo (Accelerate) / unlimited (Private)
- Slack + Google integration
- Technical support

**Real Example — Invoice Extractor:**
- Forward invoice PDF to system
- Extracts vendor, line items, totals, tax automatically
- Handles 8+ vendor formats
- Processing time: <60 seconds per invoice
- 100% local processing (data never leaves)

---

### D. AI Video Ad Production (Emerging Service)

**What It Is:** AI-generated video ads for social media marketing

**Pricing:**
- **Single video:** $500-$1,500
- **Campaign series (3-5 videos):** $1,500-$5,000
- **Monthly social retainer:** $2,000-$5,000/mo

**Workflow:**
1. AI generate clips (Kling AI)
2. Upscale to 4K
3. Add ElevenLabs voiceover + music
4. Assembly in Premiere Pro
5. Deliver 9:16 + 16:9 variants

**Platform Sweet Spots:**
- TikTok / Instagram Reels: 9:16 vertical, 15-24s
- YouTube Shorts: 15s cuts optimal
- Facebook Reels: Local business targeting

**Real Example — Utopia Deli Campaign:**
- 5-day weekly email campaign (completed)
- Video ads for social media (in production)
- Systematized pipeline ready for scaling

---

### E. One-Off Project Work

| Service | Price Range | Description |
|---------|-------------|-------------|
| **Booking/Order System** | $2,500-$5,000 | Custom branded booking + payment |
| **Invoice Extractor** | $1,500-$3,000 | Email PDF → structured data |
| **AI Video Ad** | $500-$1,500/video | 4K video with voiceover |
| **Campaign Series** | $1,500-$5,000 | 3-5 themed videos |
| **Custom Integration** | $1,000-$3,000 | Connect tools via API |

---

### F. All Service Tiers Summary

| Service | Entry Price | Best For | Revenue Type |
|---------|-------------|----------|--------------|
| **SAOS Business** | $299/mo | SMBs wanting AI team | Recurring |
| **SAOS Enterprise** | $799/mo | Larger orgs needing compliance | Recurring |
| **Order System Build** | $3,500 + $250/mo | Restaurants, salons, service biz | One-time + recurring |
| **Accelerate Automation** | $249/mo + $2,500 setup | Workflow automation | Recurring |
| **Private Automation** | $799/mo + $4,500 setup | HIPAA/air-gapped needs | Recurring |
| **AI Video Ad** | $500-$1,500 | Social media marketing | One-time/project |
| **Monthly Retainer** | $2,000-$5,000/mo | Ongoing content/services | Recurring |

---

## Part 10: Key Business Metrics

### Target Margins by Service

| Service | Gross Margin | Why |
|---------|-------------|-----|
| SAOS Business | ~70% | $299 - $90 costs |
| SAOS Enterprise | ~80% | $799 - $170 costs |
| Order System (monthly) | ~85% | $250 - minimal infra |
| Accelerate Automation | ~65% | $249 - $90 costs |
| AI Video Production | ~60% | Labor + AI costs |

### Sales Targets
- **Order systems:** 2-3 new clients/month
- **SAOS subscriptions:** 1-2 new clients/month
- **Video ads:** 5-10 videos/month
- **Goal:** $20K MRR by end of 2026

---

## Part 11: Strategic Direction & Roadmap

### Completed (June 2026)
- ✅ 10-agent fleet operational
- ✅ Customer dashboard with PIN auth
- ✅ Mobile-responsive dashboard
- ✅ Tailscale VPN deployment
- ✅ Service documentation v4.0
- ✅ BlueBubbles delivery fixed
- ✅ Real-time chat in dashboard
- ✅ Utopia Deli ordering system LIVE

### In Progress / Next Up
- 🔄 End-to-end SAOS provisioning testing (real Vultr/Tailscale/n8n credentials)
- 🔄 Fix Tailscale `.ts.net` URL on iOS Safari (cert trust issue)
- 🔄 Update PDF documentation (Dashboard User Guide v2.0 with Activity tab)
- 🔄 Create new "Dashboard Mobile Access Guide" PDF

### Future Opportunities (Revenue)
- 📌 AI Video Ad Service — systematize pipeline for recurring revenue
- 📌 Monthly Social Retainer — $2-5K/mo per client
- 📌 White-label dashboard for resellers
- 📌 API access for developers
- 📌 Integration marketplace (connectors for popular tools)
- 📌 Franchise model for order systems
- 📌 SAOS agent marketplace (sell custom agents)

---

## Part 12: Key Constraints & Rules

### Authentication
- Dashboard requires Tailscale + PIN
- No public internet access to dashboard
- Session tokens expire in 30 days (auto-renew on activity)

### Security
- Never commit credentials to public repos
- Credentials stored in `Sol-Knowledge/credentials/`
- `.gitignore` must protect all secret files

### Data Sovereignty
- Local models only (no cloud AI for client data)
- PostgreSQL on client's dedicated VPS
- No third-party data sharing

### Brand Protection
- Product name: **SAOS** (NOT "SaaS")
- Repo slug: `systack-saas` (legacy, clarify in comms)
- External communications must use correct branding

---

## Part 13: Document References

| Document | Location | Purpose |
|----------|----------|---------|
| Service Manual v4.0 | `docs/client/SyStack-Service-Manual-Client-v4.0.pdf` | Client-facing: what they get, how to use it |
| Dashboard User Guide | `docs/client/SAOS-Dashboard-User-Guide-v1.0.pdf` | How to use the dashboard |
| Quick Start Guide | `docs/client/SAOS-Quick-Start-Guide-v4.0.pdf` | First-time setup instructions |
| Mobile Access Guide | `docs/client/SAOS-Dashboard-Mobile-Access-Guide-v1.0.pdf` | Mobile-specific instructions |
| Architecture Overview | `docs/client/SyStack-Enterprise-Deployment-Guide-v1.0.pdf` | Internal architecture |
| Food Service Sales Page | `niches/food/sales.md` | Restaurant order system sales copy |
| Services Sales Page | `niches/services/sales.md` | Service business sales copy |
| Main Website | `systack-site/index.html` | Primary marketing site |
| Pricing Page | `systack-site/pricing.html` | All pricing tiers |
| Our Work Page | `systack-site/work/index.html` | Case studies and portfolio |

---

## Part 14: How ORACLE Should Use This

### When Designing Systems
- Reference the agent table — know which agent does what
- Check constraints in Part 8 before proposing solutions
- Consider the Tailscale + PIN requirement for any client-facing system

### When Researching
- Know our price points — don't propose solutions that break margin
- Understand our tech stack — prefer tools that integrate with PostgreSQL, Flask, n8n
- Remember: local-first, privacy-preserving, managed service

### When Advising
- Business Fleet ($299) is our primary target — optimize for this tier
- Enterprise ($799) adds RAM + compliance — don't over-engineer for it
- One-off projects are cash flow — retainers are the goal

---

## Contact

**Builder:** SOL + ATLAS + ASSEMBLY  
**Support:** support@systack.net  
**Emergency:** (501) 274-6231

**Document Status:** AUTHORITATIVE — This is the single source of truth. Update when changes occur.

---

*End of handoff document. ORACLE: Build upon this. Question what doesn't make sense. Design systems that compound. Remember — Systack offers more than just SAOS. We build revenue-generating infrastructure for businesses of all sizes.*
