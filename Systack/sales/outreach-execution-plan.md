# SAOS Outreach Execution Plan v1.0

**Created:** 2026-07-07
**Author:** SOL 🛰️
**Status:** Ready for Green's approval

---

## Overview

This plan turns 20 named prospects into a runnable outreach campaign. It maps directly to the n8n workflows being built (Cold Email Sequence Sender + Pipeline Tracker Sync) and uses the templates from the Outreach Asset Library.

**Pipeline value:** $10,980/mo potential MRR across 20 prospects
**Hot prospects (score 8-10):** 8 companies
**Target:** First 5 discovery calls within 2 weeks of launch

---

## Phase 1: Setup (Day 0 — Before Sending)

### What needs to happen before any email goes out:

| # | Task | Owner | Status |
|---|------|-------|--------|
| 1 | Set up dedicated sending email (saos.outreach@systack.net or green@systack.net) | Green | ⏳ |
| 2 | Configure Gmail SMTP credentials in n8n | Green/SOL | ⏳ |
| 3 | Connect Google Sheets with prospect data (or use local JSON) | SOL | ⏳ |
| 4 | Import Cold Email Sequence workflow to n8n | SOL | ⏳ (DOOBY building) |
| 5 | Import Pipeline Sync workflow to n8n | SOL | ⏳ (DOOBY building) |
| 6 | Set up Calendly link for discovery calls | Green | ⏳ |
| 7 | Test email sending with 1 prospect (yourself) | SOL | ⏳ |
| 8 | Review + approve prospect list (20 names) | Green | ⏳ |

### Credentials needed in n8n before activation:
- **Gmail credential** — for sending cold emails (saos.outreach@systack.net)
- **Google Sheets credential** — for prospect data source (if using Sheets)
- **Webhook secret** — for pipeline sync endpoint

---

## Phase 2: First Batch — Hot Prospects (Days 1-14)

### Batch 1: Priority 9-10 (5 prospects — highest conversion probability)

| # | Company | Contact | Industry | Score | Tier | First Touch |
|---|---------|---------|----------|-------|------|-------------|
| 1 | Midwest Fulfillment Partners | Jim Harrison | 3PL | 10 | Enterprise | Cold email (logistics template) |
| 2 | Copper Kettle Group | Marcus Chen | Restaurant | 9 | Enterprise | LinkedIn + cold email (restaurant template) |
| 3 | Great Lakes Distribution Co. | Sarah Mitchell | 3PL | 9 | Enterprise | LinkedIn + cold email (logistics template) |
| 4 | Parkside Medical Associates | Dr. Rebecca Nguyen | Healthcare | 9 | Enterprise | Cold email (healthcare angle) |
| 5 | Brightpath Accounting Group | Kevin Liu | Accounting | 9 | Business | Cold email (accounting template) |
| 6 | Heritage Property Management | Victoria Chen | Property Mgmt | 9 | Enterprise | Cold email (property mgmt angle) |

### Sequence timeline for each prospect:
- **Day 0**: Email 1 (pain-driven) + LinkedIn connection request
- **Day 3**: Email 2 (case study follow-up)
- **Day 10**: Email 3 (breakup)
- **Any reply**: Auto-log to pipeline tracker → notify Green

### Channel mix:
- **Cold email**: All 6 hot prospects (via n8n workflow)
- **LinkedIn**: 3 of 6 (Copper Kettle, Great Lakes, + 1 more) — manual by Green
- **Phone**: 2 of 6 (Midwest Fulfillment + Brightpath Accounting) — manual by Green

---

## Phase 3: Second Batch — Warm Prospects (Days 7-21)

### Batch 2: Priority 7-8 (7 prospects)

| # | Company | Contact | Industry | Score | Tier |
|---|---------|---------|----------|-------|------|
| 1 | Bayou Bites Hospitality | Tanya Williams | Restaurant | 8 | Enterprise |
| 2 | Velocity Supply Chain | Raj Patel | 3PL | 8 | Business |
| 3 | Summit Orthopedics | Michael Torres | Healthcare | 8 | Enterprise |
| 4 | Lakeside Residential Group | Thomas Reeves | Property Mgmt | 8 | Business |
| 5 | Cornerstone Commercial Realty | James Whitfield | Property Mgmt | 8 | Enterprise |
| 6 | Hawkins & Cole Law Firm | Rachel Hawkins | Legal | 8 | Enterprise |
| 7 | Apex Consulting Partners | Danielle Foster | Consulting | 8 | Business |

Stagger batch 2 starting Day 7 (overlap with batch 1 follow-ups).

---

## Phase 4: Third Batch — Remaining (Days 14-28)

### Batch 3: Priority 6-7 (7 prospects)
These are lower priority but still qualified. Start once batch 1+2 are in follow-up mode.

---

## Email Template → Industry Mapping

The Cold Email Sequence workflow uses these templates from `outreach-asset-library.md`:

| Industry | Email 1 Template | Email 2 Template | Email 3 Template |
|----------|----------------|----------------|----------------|
| Restaurants | "Your kitchen staff is doing data entry" | "How [similar restaurant] reclaimed 10 hours/week" | "Permission to close your file?" |
| Accounting | "Your team is the bottleneck" | "This firm added 40 billable hours/month" | "Last note—then I'm out" |
| Logistics/3PL | "Your dispatchers shouldn't be data clerks" | "How a 3PL cut processing time by 70%" | "Closing this loop" |
| Healthcare | Custom (use accounting template structure, healthcare pain points) | Custom case study | Breakup template |
| Property Mgmt | Custom (use restaurant template structure, property pain points) | Custom case study | Breakup template |
| Professional Services | Custom (use accounting template structure) | Custom case study | Breakup template |

---

## Pipeline Stages & Auto-Updates

| Stage | Trigger | What Happens |
|-------|---------|-------------|
| Researching | Manual entry to tracker | Prospect added to pipeline |
| Outreach Sent | Cold email workflow sends Email 1 | Stage auto-updates via webhook |
| Discovery Scheduled | Prospect books Calendly call | Calendly webhook → stage update |
| Proposal Sent | Manual trigger after discovery | SOL drafts proposal from template |
| Contract Sent | Manual trigger after proposal | JURIS templates sent |
| Closed Won | Stripe webhook (payment received) | Auto-update + celebration notification |
| Closed Lost | Manual update | Move to re-engagement campaign (90 days) |

---

## What SOL Handles vs What Green Handles

### SOL / Fleet Handles:
- ✅ Build + deploy cold email workflow to n8n
- ✅ Automate email sequence sends
- ✅ Track email opens, clicks, replies (via pipeline sync workflow)
- ✅ Auto-update pipeline tracker
- ✅ Notify Green when someone replies
- ✅ Draft proposals from templates after discovery calls
- ✅ Schedule re-engagement emails for cold leads

### Green Handles:
- 🔲 Set up sending email address
- 🔲 Configure Gmail credentials in n8n
- 🔲 Send LinkedIn connection requests (manual, personalized)
- 🔲 Make phone calls to hot prospects
- 🔲 Conduct discovery calls
- 🔲 Approve proposals before sending
- 🔲 Close deals + collect payment

---

## Metrics to Track

| Metric | Target | Measurement |
|--------|--------|-------------|
| Emails sent | 20 (batch 1+2) | n8n execution log |
| Open rate | >40% | Email tracking |
| Reply rate | >8% | Pipeline tracker |
| Discovery calls booked | 5+ in 14 days | Calendly |
| Proposals sent | 3+ in 21 days | Pipeline tracker |
| Closed deals | 1+ in 30 days | Stripe |

---

## What's Built vs What's Needed

### ✅ Built (Ready)
- 20-prospect target database with contact info + pain points
- Cold email templates (5 industries × 3 emails each)
- LinkedIn connection message templates
- SMS follow-up sequences
- Discovery call script
- Objection handling library (8 responses)
- Proposal templates (Business + Enterprise)
- Pipeline tracker template
- Post-discovery follow-up sequence
- Post-proposal follow-up sequence
- 90-day re-engagement campaign
- n8n cold email sequence workflow (building now — DOOBY)
- n8n pipeline sync workflow (building now — DOOBY)

### ⏳ Needed Before Launch
- Dedicated sending email address (Green decision)
- Gmail credentials configured in n8n (Green + SOL setup)
- Calendly link for discovery call booking (Green)
- Prospect data in Google Sheets (or local JSON) for workflow to read
- Green's approval of the 20 prospects + first batch

### 🔲 Deferred (Needs First Customer)
- Proposal auto-generation from templates (manual for now)
- Stripe checkout automation
- Client onboarding workflow activation
- Re-engagement campaign automation (manual for first 3 months)

---

## Next Steps for Green

1. **Review this plan** — approve or modify the batch approach
2. **Pick sending email** — green@systack.net or dedicated address?
3. **Set up Calendly** — discovery call booking link
4. **Approve first 6 hot prospects** — give me the green light to start
5. **Configure Gmail in n8n** — I'll walk you through it (5 min)

Once those are done, I import the workflows and we start sending within 24 hours.

---

*SOL 🛰️ — 2026-07-07*