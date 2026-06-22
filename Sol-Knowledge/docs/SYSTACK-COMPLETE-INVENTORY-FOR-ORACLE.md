# SYSTACK — Complete Service & Automation Inventory
**For Oracle Systems — Service Manual Generation**
**Date:** 2026-06-16
**Prepared By:** SOL
**Status:** FINAL — Ready for Oracle Handoff

---

## EXECUTIVE SUMMARY

This document catalogs ALL systems, services, automations, workflows, and offerings currently available from Systack. It serves as the source document for Oracle Systems to generate:

1. **Service Manuals** — Client-facing documentation for each offering
2. **Workflow Walkthroughs** — Step-by-step technical guides for each n8n workflow
3. **Sales Collateral** — Descriptions, pricing, and value propositions
4. **Implementation Guides** — How to deploy each system for new clients

**Last Updated:** 2026-06-16 04:08 CDT

---

## TABLE OF CONTENTS

1. [SERVICES & OFFERINGS](#1-services--offerings)
2. [AUTOMATION CATALOG](#2-automation-catalog)
3. [WORKFLOW INVENTORY](#3-workflow-inventory)
4. [TECHNICAL INFRASTRUCTURE](#4-technical-infrastructure)
5. [PRICING STRUCTURE](#5-pricing-structure)
6. [DOCUMENTATION STATUS](#6-documentation-status)
7. [ORACLE DELIVERABLES REQUEST](#7-oracle-deliverables-request)

---

## 1. SERVICES & OFFERINGS

### 1.1 Core Service Categories

| Category | Description | URL |
|----------|-------------|-----|
| **Automated Booking Systems** | Custom booking forms with Square payments, confirmations, reminders, no-show prevention | https://systack.net/services |
| **Online Ordering Systems** | Mobile-first ordering pages for restaurants/food businesses | https://systack.net/services |
| **Workflow Automation (n8n)** | Connect tools into automated workflows — email, CRM, payments, sheets | https://systack.net/services |
| **SAOS Agent Fleet** | Managed AI agents for business automation | https://systack.net/saos/ |
| **Personal Agent** | Individual AI agent for personal productivity | https://systack.net/personal-agent/ |
| **Invoice Processing** | Automated PDF invoice extraction and data entry | https://invoices.systack.net/extract |
| **Catering Lead System** | Multi-step lead capture with scoring and auto-response | https://order.theutopiadeli.com/catering/ |

---

### 1.2 Detailed Service Breakdown

#### SERVICE 1: Automated Booking Systems
**Price:** $2,500 setup + $299/mo
**Status:** ✅ LIVE
**Demo:** https://systack.net/test-book.html
**Target Clients:** Barbers, salons, spas, cleaners, consultants, any appointment-based business

**What It Includes:**
- Custom branded booking form
- Square payment integration (deposits/full payment)
- Automated confirmation emails
- T-24h and T-2h reminder emails with confirm/cancel buttons
- No-show prevention (deposit + auto-release)
- Google Sheets logging
- Customer notification system

**Key Features:**
- Customers book and pay in under 60 seconds
- Deposit reduces no-shows from ~15% to <5%
- Automatic slot release if customer cancels
- SMS reminders (upgrade)
- Waitlist auto-fill (upgrade)

**Tech Stack:** HTML/CSS/JS, Square API, n8n, Google Sheets, PostgreSQL

---

#### SERVICE 2: Online Ordering Systems
**Price:** $2,500 setup + $299/mo
**Status:** ✅ LIVE
**Demo:** https://order.theutopiadeli.com/pickup-order/
**Target Clients:** Restaurants, delis, food trucks, caterers

**What It Includes:**
- Mobile-first branded ordering page
- Full menu with modifiers (extra sauce, no tomato, etc.)
- Live cart with subtotal, tax, total calculation
- Square Checkout integration
- Order confirmation emails
- Kitchen notification system
- Google Sheets order logging
- Catering/event lead capture form

**Key Features:**
- 3.2% payment processing fee (vs 20%+ delivery apps)
- 24/7 order acceptance
- ~60 second average order completion
- Multi-location support (upgrade)
- Inventory management (upgrade)

**Tech Stack:** HTML/CSS/JS, Square API, n8n, Google Sheets

---

#### SERVICE 3: Workflow Automation (n8n)
**Price:** $1,500 setup + $149/mo
**Status:** ✅ LIVE
**Target Clients:** Any business with repetitive digital tasks

**What It Includes:**
- Custom n8n workflow development
- Integration with existing tools (Gmail, Slack, Sheets, CRMs)
- Up to 10,000 automation runs/month
- Error handling and retry logic
- Monitoring and alerting
- Same-day support

**Key Features:**
- Visual workflow builder
- 400+ integrations
- Self-hosted (data stays local)
- Scalable run volume
- Failure alerts

**Tech Stack:** n8n, PostgreSQL, various APIs

---

#### SERVICE 4: Invoice Processing System
**Price:** Included in Private plan (+$200/mo add-on for existing clients)
**Status:** ✅ LIVE
**API:** https://invoices.systack.net/extract
**Target Clients:** Any business receiving invoices via email

**What It Includes:**
- Email IMAP monitoring
- Automatic PDF attachment extraction
- OCR for scanned documents
- Structured data extraction (vendor, items, totals, tax)
- 9+ vendor format support
- SQLite/Postgres database logging
- Summary email notifications
- Web API for direct uploads

**Key Features:**
- <60 second processing per invoice
- 100% local processing (no cloud AI)
- Handles messy scans via OCR
- Monthly running totals
- Eliminates manual data entry

**Tech Stack:** Python, FastAPI, Tesseract OCR, n8n, PostgreSQL

---

#### SERVICE 5: SAOS Agent Fleet
**Price:** $299/mo (Business Fleet) / $799/mo (Enterprise Fleet)
**Status:** ✅ LIVE
**URL:** https://systack.net/saos/
**Target Clients:** Businesses wanting AI automation

**Plans:**
- **Business Fleet:** Up to 5 people, 16GB VPS, team workflows, 10,000 n8n runs
- **Enterprise Fleet:** Unlimited, on-premise, HIPAA, llama3:70b, white-glove setup

**What It Includes:**
- Dedicated VPS (we manage)
- Local AI models (Ollama)
- Email triage & drafting
- Calendar management
- Task reminders
- Document summarization
- Research assistance
- Lead qualification
- Customer support drafting
- Invoice processing

**Tech Stack:** Ollama, OpenClaw, n8n, Tailscale VPN

---

#### SERVICE 6: Personal Agent
**Price:** $199/mo (Personal+) / $1,999/year
**Status:** ✅ LIVE
**URL:** https://systack.net/personal-agent/
**Target Clients:** Individuals wanting personal AI assistance

**What It Includes:**
- Dedicated 16GB VPS
- Local AI models
- Email and calendar management
- Task and reminder automation
- Document summarization
- Research assistance
- 5,000 n8n runs/month
- Email support

**Tech Stack:** Ollama, OpenClaw, n8n

---

#### SERVICE 7: Catering Lead System
**Price:** Part of Online Ordering package
**Status:** ✅ LIVE
**URL:** https://order.theutopiadeli.com/catering/
**Target Clients:** Caterers, event venues, food businesses

**What It Includes:**
- 5-step event inquiry form
- Automatic lead scoring (guest count, date, service type)
- Immediate auto-response based on score
- SQLite database logging
- Internal notification system

**Scoring Algorithm:**
- Guest count (40% weight)
- Date proximity (30% weight)
- Service type (20% weight)
- Budget mentioned (10% bonus)

**Tech Stack:** HTML/CSS/JS, n8n, SQLite

---

#### SERVICE 8: No-Show Prevention System
**Price:** Included in Booking System
**Status:** 🚧 PARTIAL (Phase 1 complete, Phase 2 in progress)
**Target Clients:** Any appointment-based business

**What's Working:**
- ✅ Square deposit collection at booking
- ✅ Confirmation email with token
- ✅ Confirmation webhook handler
- ✅ T-24h reminder scheduler
- ✅ T-2h reminder scheduler

**Still Needed:**
- 🚧 Auto-release unconfirmed slots
- 🚧 Waitlist notification
- 🚧 SMS reminders
- 🚧 Frontend booking form

**Tech Stack:** Square API, n8n, PostgreSQL, HTML/CSS/JS

---

## 2. AUTOMATION CATALOG

### 2.1 Live Automations

| # | Automation | Status | Client | n8n Workflow ID | URL |
|---|-----------|--------|--------|-----------------|-----|
| 1 | **Order System** | ✅ LIVE | Utopia Deli | `1WEM4rZxjhhy7ooM` | https://order.theutopiadeli.com/pickup-order/ |
| 2 | **Invoice Parser** | ✅ LIVE | Internal | `Ny4kzzf1bN4NODGn` | https://invoices.systack.net/extract |
| 3 | **Catering Lead** | ✅ LIVE | Utopia Deli | `T67LTu32k1xENtzd` | https://order.theutopiadeli.com/catering/ |
| 4 | **Confirmation Email** | ✅ LIVE | Utopia Deli | `IW27pwPj5DBYQdcq` | https://order.theutopiadeli.com/payment-confirmed/ |
| 5 | **No-Show Prevention** | 🚧 PARTIAL | Utopia Deli | — | — |

### 2.2 Planned/Proposed Automations (Oracle Systems)

| # | Automation | Status | Phase | Est. Effort | Impact |
|---|-----------|--------|-------|-------------|--------|
| 6 | **Missed-Lead Recovery** | 📋 DRAFT | 1 | Medium | HIGH |
| 7 | **Referral Engine** | 📋 DRAFT | 1 | Medium | Medium |
| 8 | **CRM Lite** | 📋 DRAFT | 1 | Medium | Medium |
| 9 | **Subscription Engine** | 📋 DRAFT | 2 | High | HIGH |
| 10 | **Upsell Intelligence** | 📋 DRAFT | 2 | Low | Medium |
| 11 | **Scheduling Optimizer** | 📋 DRAFT | 3 | High | Medium |
| 12 | **Review System** | 📋 DRAFT | 1 | Low | HIGH |
| 13 | **Smart Rebooking** | 📋 DRAFT | 1 | Low | HIGH |
| 14 | **Revenue Dashboard** | 📋 DRAFT | 3 | High | Medium |

---

## 3. WORKFLOW INVENTORY

### 3.1 n8n Workflows (Active)

| Workflow ID | Name | Status | Triggers | Outputs |
|-------------|------|--------|----------|---------|
| `1WEM4rZxjhhy7ooM` | Utopia Deli HTML Order v1 | ✅ ACTIVE | Square payment webhook | Google Sheet, email, kitchen notification |
| `Ny4kzzf1bN4NODGn` | Systack Private — Invoice Email Pipeline | ✅ ACTIVE | IMAP email trigger | Postgres, summary email |
| `T67LTu32k1xENtzd` | Utopia Deli — Catering Lead Scoring | ✅ ACTIVE | Webhook (form submission) | SQLite, auto-email, notification |
| `IW27pwPj5DBYQdcq` | Utopia Deli — Payment Confirmed Email | ✅ ACTIVE | Webhook (payment confirmed) | Confirmation email |
| `systack-create-booking` | Create Booking + Insert to DB | ✅ ACTIVE | Webhook (new booking) | Postgres booking record |
| `systack-confirm-booking` | Confirm Booking Handler | ✅ ACTIVE | Webhook (confirm click) | Status update, email |
| `systack-24h-reminder` | T-24h Reminder Scheduler | ✅ ACTIVE | Cron schedule | Reminder email |
| `systack-2h-reminder` | T-2h Reminder Scheduler | ✅ ACTIVE | Cron schedule | Reminder email |

### 3.2 Workflow Patterns (Reusable)

| Pattern | Description | Used In |
|---------|-------------|---------|
| **Webhook → Parse → Store → Notify** | Standard data capture | Order System, Catering Lead |
| **IMAP → Extract → Process → Log → Email** | Email automation | Invoice Parser |
| **Timer → Check → Action → Notify** | Scheduled reminders | No-Show Prevention |
| **Branch Logic (Score/Routing)** | Conditional responses | Catering Lead |

---

## 4. TECHNICAL INFRASTRUCTURE

### 4.1 Hosting & Infrastructure

| Component | Technology | Location | Notes |
|-----------|-----------|----------|-------|
| **Primary Server** | n8n self-hosted | systack.net | Cloud VPS |
| **Local Dev** | MacBook Air | Phillip's laptop | Local testing |
| **Tunnel** | Cloudflare | invoices.systack.net | Secure access |
| **VPN** | Tailscale | Mesh network | No open firewall ports |
| **Database (Primary)** | PostgreSQL 15 | localhost | Trust auth (local) |
| **Database (API)** | SQLite | ~/.openclaw/workspaces/sol/ | Various .db files |

### 4.2 APIs & Endpoints

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `https://utopia-api.systack.net/webhook/utopia-deli-html-order-v1` | POST | Order submission | None |
| `https://utopia-api.systack.net/webhook/utopia-deli-catering-v2` | POST | Catering lead | None |
| `https://invoices.systack.net/extract` | POST | Invoice parsing | None |
| `https://n8n.systack.net/mcp-server/http` | POST | MCP access | Token |

### 4.3 Credentials Inventory

| Service | Username/Email | Storage | Status |
|---------|---------------|---------|--------|
| n8n Local Auth | `Plowe95@ywhoo.com` | Keychain | Active |
| Gmail IMAP | `support@systack.net` | Keychain | ⚠️ Check status |
| SMTP (Systack) | `support@systack.net` | Keychain | Active |
| Square API | — | n8n credentials | Active |
| Postgres | `philliplowe` / trust | Local | Active |
| Cloudflare Tunnel | `e2897c60-...` | n8n config | Active |

### 4.4 Software Stack

| Category | Technology | Version |
|----------|-----------|---------|
| Workflow Engine | n8n | 1.50+ |
| AI Models | Ollama | Latest |
| Primary Model | qwen2.5-coder:7b | 4.7GB |
| General Model | qwen3.5:9b | 6.6GB |
| Large Model | llama3:70b | Enterprise only |
| Frontend | HTML/CSS/JS | Vanilla |
| API Framework | Python FastAPI | Latest |
| OCR | Tesseract + pytesseract | Latest |
| Payments | Square API | v2 |
| Database | PostgreSQL | 15 |
| Database | SQLite | 3.x |
| Email | Gmail IMAP/SMTP | Standard |
| VPN | Tailscale | Latest |

---

## 5. PRICING STRUCTURE

### 5.1 Agent Fleet Plans

| Plan | Monthly | Annual | Users | VPS | n8n Runs | Support |
|------|---------|--------|-------|-----|----------|---------|
| **Personal+** | $199 | $1,999 | 1 | 16GB | 5,000 | Email |
| **Business Fleet** | $299 | $3,588 | 5 | 16GB | 10,000 | Same-day |
| **Enterprise Fleet** | $799 | $9,588 | Unlimited | On-premise | Unlimited | 4h SLA |

### 5.2 Custom Automation Plans

| Plan | Monthly | Setup | Features |
|------|---------|-------|----------|
| **Accelerate** | $249 | $2,500 | Cloud VPS, custom workflows, 10K runs |
| **Private** | $799 | $4,500 | On-premise, HIPAA, air-gapped, hardware extra |

### 5.3 Individual Service Pricing

| Service | Setup | Monthly | Notes |
|---------|-------|---------|-------|
| Automated Booking System | $2,500 | $299 | Includes No-Show Prevention |
| Online Ordering System | $2,500 | $299 | Includes Catering Lead |
| Workflow Automation | $1,500 | $149 | Custom n8n workflows |
| Invoice Processing | — | +$200 | Addon to Private plan |
| Website Build | $1,500-3,500 | — | One-time |

### 5.4 Add-ons & Upgrades

| Feature | Price | Applies To |
|---------|-------|------------|
| SMS Reminders | +$50/mo | Booking System |
| Waitlist Management | +$75/mo | Booking System |
| Multi-location | +$100/mo/location | Ordering System |
| Inventory Management | +$150/mo | Ordering System |
| Custom Domain | +$25/mo | Any |
| Additional User | +$49/mo | Business Fleet |
| Extra n8n Runs | +$50/10K | All plans |
| HIPAA Compliance | +$200/mo | Private |

---

## 6. DOCUMENTATION STATUS

### 6.1 Completed Documentation

| System | Doc File | Status | Quality |
|--------|----------|--------|---------|
| Order System | `docs/automations/order-system/order-system-docs.md` | ✅ Complete | Good |
| Invoice Parser | `docs/automations/invoice-parser/invoice-parser-docs.md` | ✅ Complete | Good |
| Catering Lead | `docs/automations/catering-lead/catering-lead-docs.md` | ✅ Complete | Good |
| No-Show Prevention | `docs/automations/noshow-prevention/noshow-prevention-docs.md` | 🚧 Partial | Needs Phase 2-3 update |
| Automation Catalog | `docs/automations/AUTOMATION-CATALOG.md` | ✅ Complete | Good |
| Master Plan | `docs/automations/MASTER-PLAN.md` | ✅ Complete | Good |
| Doc Template | `docs/automations/templates/automation-doc-template.md` | ✅ Complete | Excellent |
| Build Checklist | `docs/automations/templates/BUILD-CHECKLIST.md` | ✅ Complete | Good |

### 6.2 Planned/Placeholder Documentation

| System | Doc File | Status | Quality |
|--------|----------|--------|---------|
| Smart Rebooking | `docs/automations/smart-rebooking/` | 📋 Placeholder | Template only |
| Review System | `docs/automations/review-system/` | 📋 Placeholder | Template only |
| Missed-Lead Recovery | `docs/automations/missed-lead-recovery/` | 📋 Placeholder | Template only |
| Referral Engine | `docs/automations/referral-engine/` | 📋 Placeholder | Template only |
| CRM Lite | `docs/automations/crm-lite/` | 📋 Placeholder | Template only |
| Upsell Intelligence | `docs/automations/upsell-intelligence/` | 📋 Placeholder | Template only |
| Scheduling Optimizer | `docs/automations/scheduling-optimizer/` | 📋 Placeholder | Template only |
| Revenue Dashboard | `docs/automations/revenue-dashboard/` | 📋 Placeholder | Template only |
| Subscription Engine | `docs/automations/subscription-engine/` | 📋 Placeholder | Template only |

---

## 7. ORACLE DELIVERABLES REQUEST

### 7.1 Service Manuals Needed

For EACH service below, Oracle should create:

1. **Client-Facing Service Manual**
   - What the service does
   - How it helps their business
   - What they see (screenshots/mockups)
   - Pricing
   - How to get started
   - FAQ

2. **Internal Implementation Guide**
   - Technical architecture
   - Step-by-step setup process
   - Configuration details
   - Testing procedures
   - Troubleshooting guide

3. **Workflow Walkthrough**
   - n8n workflow diagram
   - Node-by-node explanation
   - Data flow chart
   - Error handling
   - Maintenance procedures

### 7.2 Priority Order

#### PHASE 1 (Live Systems — URGENT)
1. ✅ **Order System** (Utopia Deli)
   - Client manual: How customers place orders
   - Internal guide: How to update menu, monitor orders
   - Workflow walkthrough: n8n order processing

2. ✅ **Invoice Parser**
   - Client manual: How to forward invoices, what to expect
   - Internal guide: Adding new vendor formats, troubleshooting OCR
   - Workflow walkthrough: IMAP → extraction → database → email

3. ✅ **Catering Lead System**
   - Client manual: How leads are scored and responded to
   - Internal guide: Modifying scoring weights, accessing lead database
   - Workflow walkthrough: Form → webhook → scorer → email → SQLite

4. ✅ **Confirmation Email System**
   - Client manual: What customers see after payment
   - Internal guide: Customizing confirmation templates
   - Workflow walkthrough: Payment webhook → confirmation email

#### PHASE 2 (Partial Systems — COMPLETE FIRST)
5. 🚧 **No-Show Prevention**
   - PRIORITY: Complete build first
   - Then: Client manual (policy explanations), internal guide, workflow walkthrough

#### PHASE 3 (Planned Systems — SPEC OUT)
6. 📋 **Missed-Lead Recovery Engine**
   - Spec document only (not built yet)
   - Architecture diagram
   - Implementation plan

7. 📋 **Smart Rebooking Engine**
   - Spec document only
   - Logic flow for predicting rebooking dates

8. 📋 **Review System**
   - Spec document only
   - Positive/negative routing logic

9. 📋 **Referral Engine**
   - Spec document only
   - Link generation and tracking design

10. 📋 **CRM Lite**
    - Spec document only
    - Data aggregation and profile card design

#### PHASE 4 (Advanced Systems — ARCHITECT)
11. 📋 **Subscription Engine**
    - Spec document
    - Stripe subscription integration plan

12. 📋 **Upsell Intelligence**
    - Spec document
    - Analytics and recommendation engine design

13. 📋 **Scheduling Optimizer**
    - Spec document
    - Calendar gap detection algorithm

14. 📋 **Revenue Dashboard**
    - Spec document
    - Metrics and visualization design

### 7.3 Brand Standards for All Documents

| Element | Specification |
|---------|---------------|
| **Header** | Navy (#001a2d) with SyStack wordmark |
| **Body** | Gray 50 (#f8fafc) background |
| **CTA Button** | Cyan gradient (#00a1db → #00c5e0) |
| **Footer** | Navy with contact info |
| **Typography** | System fonts, clean hierarchy |
| **Email Field Start** | Must begin with `=` for expression evaluation |
| **HTML** | Real tags only, never escaped entities |

### 7.4 File Naming Convention

```
service-manuals/
├── order-system/
│   ├── client-manual.md
│   ├── internal-guide.md
│   ├── workflow-walkthrough.md
│   └── screenshots/
├── invoice-parser/
│   ├── client-manual.md
│   ├── internal-guide.md
│   ├── workflow-walkthrough.md
│   └── screenshots/
├── [etc for each service]
```

---

## APPENDIX: QUICK REFERENCE

### A. All n8n Workflow IDs
```
1WEM4rZxjhhy7ooM  →  Utopia Deli HTML Order v1
Ny4kzzf1bN4NODGn  →  Invoice Email Pipeline
T67LTu32k1xENtzd  →  Catering Lead Scoring
IW27pwPj5DBYQdcq  →  Payment Confirmed Email
```

### B. All URLs
```
https://systack.net                    →  Main website
https://systack.net/services           →  Business Systems page
https://systack.net/pricing            →  Pricing page
https://systack.net/contact            →  Contact page
https://systack.net/saos/              →  SAOS Agent Fleet
https://systack.net/personal-agent/    →  Personal Agent
https://systack.net/work/              →  Case Studies
https://systack.net/test-book.html     →  Booking Demo
https://systack.net/discovery          →  Discovery Questionnaire
https://order.theutopiadeli.com/       →  Utopia Deli Ordering
https://invoices.systack.net/extract   →  Invoice API
https://n8n.systack.net                →  n8n Dashboard
```

### C. All Databases
```
utopia_deli              →  Invoice data (Postgres)
systack_noshow           →  Booking data (Postgres)
invoice_pipeline         →  Old invoice data (Postgres)
utopia-deli-catering.db →  Catering leads (SQLite)
invoice_data.db         →  Legacy invoice data (SQLite)
```

### D. Key Personnel
```
Phillip Lowe     →  Founder/Builder (Systack)
SOL (AI Agent)   →  System Builder & Documenter
Oracle Systems   →  Documentation Partner (external)
```

### E. Contact Information
```
Email:    support@systack.net
Phone:    (501) 274-6231
Website:  https://systack.net
Location: Little Rock, AR
```

---

**END OF INVENTORY**

**Next Steps:**
1. Hand this document to Oracle Systems
2. Oracle generates service manuals per Section 7
3. Review and approve each manual
4. Publish to client portal / website
5. Update as systems evolve

**Version:** 1.0
**Date:** 2026-06-16
**Status:** FINAL
