# SAOS Service Manual

**Document ID:** SYS-CLIENT-MANUAL-v4.0
**Version:** 4.0
**Status:** LIVE
**Prepared for:** SAOS Business & Enterprise Fleet Clients
**Prepared by:** Systack
**Builder:** SOL + ATLAS
**Source System:** SAOS v2026.06
**Date:** June 25, 2026
**Support:** support@systack.net

---

## What's Included

This manual covers your SAOS deployment — what's running, how it works, and how to get help.

---

## 1. Your Deployment

### Business Fleet ($299/mo)
- **10 AI agents:** SOL, VALI, PESSI, ORACLE, ATLAS, ASSEMBLY, JURIS, CODY, CHATTY, GENI
- **Server:** Dedicated 16GB VPS (Vultr vhp-8c-16gb-amd)
- **Network:** Tailscale VPN access
- **Channels:** WhatsApp, SMS, WebChat, Dashboard Chat
- **Storage:** 160GB NVMe SSD
- **Support:** Priority email (same-day)
- **Dashboard:** Customer portal with PIN auth, 6 tabs, mobile-responsive

### Enterprise Fleet ($799/mo)
Everything in Business Fleet plus:
- **RAM:** 32GB (double the memory)
- **Compliance:** SOC2 + HIPAA + GDPR
- **Multi-region:** Up to 5 locations
- **Support:** Dedicated line + SLA

**Note:** Both tiers include all 10 agents. Enterprise adds RAM and compliance certifications.

---

## 2. Agent Functions

### Core Agents (All Plans)

| Agent | Emoji | What It Does | When to Use |
|-------|-------|-------------|-------------|
| **SOL** | 🛰️ | Routes tasks, manages conversations | "Status check" "Queue work" |
| **VALI** | ✅ | Validates outputs, catches errors | "Review this" "Is this correct?" |
| **PESSI** | ⚠️ | Identifies risks, edge cases | "What could break?" "Stress-test this" |
| **ORACLE** | 🔮 | Designs systems, researches | "How should we build this?" |
| **ATLAS** | 🗺️ | Maintains memory, lessons learned | "What did we decide last week?" |
| **ASSEMBLY** | 🛠️ | Deploys changes, manages releases | "Push this live" "Rollback" |
| **JURIS** | ⚖️ | Legal review, compliance | "Review this contract" "Is this allowed?" |

### Extended Agents (All Plans)

| Agent | Emoji | What It Does | When to Use |
|-------|-------|-------------|-------------|
| **CODY** | 💻 | Generates code, builds systems | "Build me a script" "Create workflow" |
| **CHATTY** | 💬 | Client comms, onboarding | "Draft email" "Onboard new client" |
| **GENI** | 🎨 | Creates visuals, content | "Make a diagram" "Generate image" |

---

## 3. Accessing Your Fleet

### Customer Portal (Primary)
- URL: https://phillips-macbook-air.tail573d57.ts.net/dashboard/
- **Authentication:** PIN-based login (Client ID + 4-digit PIN)
- **Sessions:** 30-day session tokens, auto-renewing
- **Mobile:** Full support for iOS Safari, Android Chrome
- **Features:**
  - 💬 Chat: Real-time conversations with agents
  - 📊 Fleet Status: Agent health, task counts, metrics
  - 📦 Services: Tier-specific service catalog
  - ✅ Tasks: Task history with status tracking
  - 📋 Activity: Audit trail of recent actions
  - 📄 Docs: In-app documentation access

### Mobile Dashboard Access

**Requirements:**
- Tailscale connected
- Modern mobile browser (Safari iOS 14+, Chrome Android 90+)

**Features:**
- Hamburger menu navigation
- Sidebar toggle for chat conversations
- Touch-optimized buttons (44px minimum)
- Auto-hiding navigation on scroll
- Responsive grid layouts

### Internal Fleet Dashboard
- URL: http://localhost:8765 (via Tailscale)
- Shows: Full fleet control, task queue, system health
- For administrator use only

### Messaging
- **WhatsApp/SMS:** Text your assigned number
- **WebChat:** Embedded on your site
- **Email:** Forward documents to agent address

### API (Advanced)
- POST /api/tasks — Create tasks programmatically
- GET /api/status — Fleet health check
- Full API docs: Contact support

---

## 4. Data & Security

### Where Your Data Lives
- **Server:** Your dedicated VPS (US-based)
- **Database:** PostgreSQL + SQLite (local to your server)
- **Backups:** Hourly snapshots, retained 30 days
- **Network:** Tailscale encrypted mesh (no public exposure)
- **Dashboard:** Tailnet-only access (requires Tailscale connection)

### Authentication
- **PIN-based:** 4-digit PIN (no passwords to forget)
- **Session tokens:** Secure random tokens stored in browser localStorage
- **30-day expiry:** Sessions auto-renew on activity
- **Logout:** Manual logout clears all sessions

### Who Can Access
- You (via Tailscale + PIN)
- Systack support (with your permission)
- No third-party AI companies — models run locally

### Compliance
- Business: SOC2 Type II
- Enterprise: SOC2 + HIPAA + GDPR

---

## 5. Billing

| Plan | Monthly | Annual (2 months free) |
|------|---------|------------------------|
| Business | $299 | $2,988 |
| Enterprise | $799 | $7,990 |

**Payment:** Via Stripe (auto-renewing)
**Cancellation:** Anytime, prorated refund within 30 days
**Upgrades:** Pro-rated, instant

---

## 6. Support

| Issue Type | Response | Resolution |
|-----------|----------|------------|
| Service Down | < 30 min | 2-4 hours |
| Feature Broken | < 2 hours | Same day |
| Performance | < 4 hours | 24 hours |
| Question | < 24 hours | 72 hours |
| Feature Request | < 48 hours | Roadmap review |

**Contact:**
- Email: support@systack.net
- Emergency: (Provided after signup)
- Hours: 24/7 for critical issues

---

## 7. FAQ

**Q: Can I add more agents?**
All 10 agents are included in both plans. Agent capabilities expand with usage.

**Q: What if I need more RAM?**
Contact support. Upgrades typically complete within 1 hour.

**Q: Do you offer refunds?**
Full refund within 30 days. After that, prorated based on usage.

**Q: Can I export my data?**
Yes. Full database export available on request. Your data is yours.

**Q: What happens if Systack shuts down?**
Your server continues running. We provide documentation for self-management.

**Q: How do I access the customer dashboard?**
Connect to your Tailscale network, then visit your dashboard URL. Log in with your Client ID and PIN.

**Q: Is the dashboard secure?**
Yes. Dashboard is only accessible within your Tailscale tailnet. PIN authentication adds another layer. No public internet exposure.

**Q: What if I forget my PIN?**
Contact support. We can reset your PIN instantly.

**Q: Does the dashboard work on mobile?**
Yes. Full mobile support with responsive layout, touch-optimized buttons, and hamburger navigation.

**Q: What browsers are supported?**
- Desktop: Chrome, Firefox, Safari, Edge (latest 2 versions)
- Mobile: Safari iOS 14+, Chrome Android 90+

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-19 | Initial release |
| 2.0 | 2026-06-22 | Updated pricing, added agent details, expanded FAQ |
| 3.0 | 2026-06-23 | Updated to 10-agent fleet, added customer portal, Tailscale URLs |
| 4.0 | 2026-06-25 | Added PIN authentication, mobile access, 6-tab dashboard, Activity tab, session tokens |

**Latest version:** https://systack.net/docs/client/SyStack-Service-Manual-Client-v4.0.pdf
