# Systack — Client Onboarding System
## Internal Implementation Guide

**Automation ID:** `client-onboarding`  
**Version:** 1.0  
**Status:** Template — Ready for Deployment  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## Brand Reference

| Role | Color | Hex |
|------|-------|-----|
| Headers, CTAs | Navy | `#001a2d` |
| Secondary accents | Teal | `#007da9` |
| Primary buttons, links | Cyan | `#00a1db` |
| Body text | Gray 600 | `#475569` |
| Headings | Gray 800 | `#1e293b` |
| Success | Green | `#22c55e` |
| Error | Red | `#ef4444` |

---

## 1. Overview

Automated client onboarding system. When a new client signs, the system creates project folders, schedules kickoff calls, sends welcome emails, and notifies the team. Available in two tiers: Private (local everything) and Accelerate (Google Drive + Slack).

**Templates:**
- `templates/private/n8n-client-onboarding.json`
- `templates/accelerate/n8n-client-onboarding.json`

---

## 2. System Architecture

```
Client Signed (trigger)
  → Create project folder structure
    → Schedule kickoff call (calendar)
      → Send welcome email to client
        → Send credential setup guide
          → Notify team (Slack/SMS)
            → Create onboarding checklist
              → Timer: 48h follow-up
                → Timer: 1-week check-in
```

---

## 3. Tier Comparison

| Component | Private | Accelerate |
|-----------|---------|------------|
| Project folders | Local filesystem | Google Drive |
| Kickoff calendar | Local CalDAV | Google Calendar |
| Welcome email | Local SMTP | Client SMTP |
| Team notify | SMS (Twilio) | Slack |
| Onboarding log | Postgres local | Postgres cloud VPS |

---

## 4. Setup Process

### Step 1 — Choose Tier

- **Private:** Client has on-premise hardware, zero cloud apps
- **Accelerate:** Client uses Google Workspace + Slack

### Step 2 — Import Template

- Import appropriate JSON into n8n
- Configure credentials (SMTP, Google, Slack, Postgres)

### Step 3 — Customize

- Update welcome email template with client branding
- Set kickoff call availability
- Configure project folder template

---

## 5. Onboarding Checklist (Automated)

- [ ] Project folder created
- [ ] Kickoff call scheduled
- [ ] Welcome email sent
- [ ] Credential setup guide sent
- [ ] Team notified
- [ ] 48h follow-up: check credential progress
- [ ] 1-week check-in: first automation live?

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
