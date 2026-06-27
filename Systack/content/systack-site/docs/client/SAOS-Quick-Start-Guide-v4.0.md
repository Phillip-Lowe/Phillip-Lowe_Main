# SAOS Quick Start Guide

**Document ID:** SYS-QUICKSTART-v4.0
**Version:** 4.0
**Status:** LIVE
**Prepared for:** SAOS Business & Enterprise Fleet Clients
**Prepared by:** Systack
**Builder:** SOL + ASSEMBLY
**Source System:** SAOS v2026.06
**Date:** June 25, 2026
**Support:** support@systack.net

---

## For Business Fleet Clients (10 Agents)

**Your SAOS deployment is ready. Here's how to actually use it.**

---

## 1. Connect to Your Server

Your dedicated SAOS server runs on a private VPS. Access it securely through Tailscale:

```
1. Install Tailscale: https://tailscale.com/download
2. Accept the invite email from Systack
3. Join the network: tailscale up
4. Your server will appear as: saos-[your-business].tail573d57.ts.net
```

**Server details:**
- IP: (shown in your dashboard)
- RAM: 16GB (Business) or 32GB (Enterprise)
- vCPU: 8
- OS: Ubuntu 22.04 LTS

---

## 2. Access Your Dashboard

### Customer Portal (New)
- URL: https://phillips-macbook-air.tail573d57.ts.net/dashboard/
- **Login:** PIN-based authentication (no passwords to remember)
- **Mobile-friendly:** Works on iPhone, iPad, Android, any device with Tailscale
- **Auto-refreshes:** Real-time updates every 5 seconds
- **Available:** Any device connected to your Tailscale network

### Dashboard Tabs

| Tab | What You See | When to Use |
|-----|-------------|-------------|
| **💬 Chat** | Conversations with your AI agents | Daily operations, task requests |
| **📊 Fleet Status** | Agent health, active tasks, metrics | Morning check-in, status overview |
| **📦 Services** | Your included services by tier | Review what's active vs. pending |
| **✅ Tasks** | Task history, status, assignments | Track work in progress |
| **📋 Activity** | Recent agent actions, timestamps | Audit trail, history review |
| **📄 Docs** | Quick Start, Service Manual, Architecture | Reference documentation |

### Mobile Access

**iPhone/iPad:**
1. Install Tailscale app
2. Connect to your tailnet
3. Open Safari, visit your dashboard URL
4. Enter Client ID + PIN
5. Bookmark to home screen for app-like experience

**Android:**
1. Install Tailscale app
2. Connect to your tailnet
3. Open Chrome, visit your dashboard URL
4. Enter Client ID + PIN
5. Add to home screen

### Internal Fleet Dashboard
- URL: http://localhost:8765 (when connected via Tailscale)
- Shows: Full fleet control, task queue, system health
- For administrator use only

### Messaging Channels
- **WhatsApp:** Text your business number
- **SMS:** Text your assigned number
- **WebChat:** Embedded on your website

---

## 3. Your 10 Agents — What Each Does

### Core Agents (All Plans)

| Agent | Emoji | Role | What to Ask It |
|-------|-------|------|----------------|
| **SOL** | 🛰️ | Orchestrator | "What's the status?" "Queue a task" |
| **VALI** | ✅ | Quality | "Check this for errors" "Validate output" |
| **PESSI** | ⚠️ | Risk | "What could go wrong?" "Flag issues" |
| **ORACLE** | 🔮 | Architecture | "How should we build this?" "Research solution" |
| **ATLAS** | 🗺️ | Knowledge | "What did we decide last week?" "Find previous task" |
| **ASSEMBLY** | 🛠️ | Deploy | "Push this live" "Rollback last change" |
| **JURIS** | ⚖️ | Compliance | "Review this contract" "Is this allowed?" |

### Extended Agents (All Plans)

| Agent | Emoji | Role | What to Ask It |
|-------|-------|------|----------------|
| **CODY** | 💻 | Build Engine | "Build me a script" "Create workflow" |
| **CHATTY** | 💬 | Communication | "Draft email" "Onboard new client" |
| **GENI** | 🎨 | Creative | "Make a diagram" "Generate image" |

---

## 4. Common Tasks

### Invoice Processing
Forward invoices to your agent email:
- The agent reads and extracts data automatically
- Reviewed by JURIS for compliance
- Stored in your database
- View: Dashboard → Tasks

### Order Taking (WhatsApp/SMS)
Customers text your number:
- Agent confirms order details
- Sends to your POS or email
- No app required for customers

### Lead Qualification
Ask ORACLE: "Check for new leads"
- Scrapes configured sources
- Scores and ranks prospects
- Delivers morning briefing

### Daily Morning Briefing
Ask SOL: "Morning briefing"
- Overnight task summary
- Pending items requiring attention
- New leads or orders

---

## 5. Troubleshooting

| Problem | Fix |
|---------|-----|
| Can't connect to dashboard | Check Tailscale is running: `tailscale status` |
| Agent not responding | Check customer portal for agent status (green dot = online) |
| Messages not sending | Verify phone number configuration in n8n |
| Invoice not processing | Check spam folder; ensure PDF attachment |
| Slow responses | Check server load in dashboard; may need RAM upgrade |
| Dashboard not loading | Ensure you're on the Tailscale network |
| PIN not working | Contact support to reset your PIN |
| Mobile layout broken | Refresh page; ensure iOS Safari or Chrome updated |

---

## 6. Support

**Emergency (service down):** Call emergency line (provided after signup)
**General:** support@systack.net
**Dashboard:** Check status at https://systack.net/status

**Response times:**
- Critical: Under 30 minutes
- Broken feature: Under 2 hours
- General: Under 24 hours

---

## 7. Next Steps

1. [ ] Connect via Tailscale
2. [ ] Open customer portal at the provided URL
3. [ ] Log in with your Client ID and PIN
4. [ ] Send test message to your agent via Chat tab
5. [ ] Forward one invoice to test pipeline
6. [ ] Review dashboard daily for first week
7. [ ] Schedule training call if needed

**Questions?** Message SOL directly: "I need help with [topic]"

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-19 | Initial release (7 agents) |
| 2.0 | 2026-06-22 | Added Enterprise agents, updated pricing |
| 3.0 | 2026-06-23 | Updated to 10-agent fleet, added customer portal URL |
| 4.0 | 2026-06-25 | Added PIN authentication, mobile access guide, 6-tab dashboard, Activity tab |

**Latest version:** https://systack.net/docs/client/SyStack-Service-Manual-Client-v4.0.pdf
