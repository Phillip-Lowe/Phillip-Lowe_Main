# Systack Services — Gap Analysis & Missing Automations

**Date:** 2026-06-06
**Status:** Utopia Deli working end-to-end ✅ | Taking stock of what's missing

---

## What We Have (CURRENT STATE)

### ✅ WORKING
| Service | Status | What It Does |
|---------|--------|-------------|
| **Utopia Deli Order System** | ✅ LIVE | Custom order form → n8n webhook → Square payment → Google Sheets |
| **Invoice Parser (Core)** | ✅ Working locally | Python script extracts data from PDF invoices to SQLite |
| **Lead Capture Webhook** | ✅ Built, needs deploy | n8n workflow to capture leads from discovery form |
| **Error Catcher v2** | ✅ Built, needs import | Master error handling for all n8n workflows |
| **Systack Website** | ✅ Published | Homepage, pricing, services, contact, discovery questionnaire |

### ⚠️ PARTIALLY BUILT
| Service | Status | What's Missing |
|---------|--------|---------------|
| **Invoice Parser Service** | Core works | n8n email trigger, client upload form, paywall, billing |
| **Lead Automation** | Frontend done | n8n workflow deploy, Google Sheets, email creds |
| **Error Catcher** | JSON ready | Import into n8n, configure notifications |
| **Business Systems Demo** | Utopia Deli only | Generic demo for non-food service businesses |

### ❌ NOT BUILT
| Service | What It Is | Priority |
|---------|-----------|----------|
| **Personal Agent** | AI assistant for individuals | P2 — last per production plan |
| **SAOS Fleet Deployment** | Multi-agent system for businesses | P1 — foundation spec exists |
| **Generic Booking System** | Template for salons, auto shops, etc. | P1 — fastest new revenue |
| **Automated Onboarding** | Client self-setup wizard | P1 — reduces manual work |
| **Review Collection** | Auto-request reviews post-purchase | P2 — nice to have |
| **Weekly Reporting** | Business performance summaries | P2 — internal + client value |
| **Content Repurposing** | Blog → social posts automation | P3 — marketing accelerator |
| **Email Triage** | AI-sort incoming emails | P2 — internal productivity |

---

## Gap Analysis: What Systack Offers vs. What's Missing

### From Service Packages (sales.md + service-packages.md)

**Systack Accelerate ($249/mo) includes:**
1. ✅ Invoice Processing System — partial (parser works, not deployed)
2. ❌ Customer Support Automations — not built
3. ✅ Data Entry Elimination — partial (invoice only)
4. ❌ Lead Qualification Pipeline — built but not deployed
5. ❌ Document Classification & Routing — not built
6. ❌ Scheduled Report Generator — not built

**Systack Private ($799/mo) includes:**
1. ✅ Document Extraction Pipeline — partial (invoice only)
2. ✅ Invoice Processing System — partial
3. ❌ Customer Support Automations — not built
4. ✅ Data Entry Elimination — partial
5. ❌ Private Knowledge Base Search — not built
6. ❌ Compliance Audit Trail — not built

---

## Top 10 n8n Templates We Should Build (from web research)

Based on the BK Web Designs analysis of highest-value small business automations:

| # | Template | Time Saved | Systack Relevance | Priority |
|---|----------|-----------|-------------------|----------|
| 1 | **AI Email Triage + Auto-Draft** | 12 hrs/mo | Internal + client support | HIGH |
| 2 | **Lead Capture → CRM + Alert** | 3-5 hrs/wk | Core to our funnel | HIGH |
| 3 | **Invoice Gen + Overdue Follow-Up** | 3-5 hrs/wk | Invoice parser extension | HIGH |
| 4 | **Client Onboarding Sequence** | 2-4 hrs/client | Every new client needs this | HIGH |
| 5 | **Weekly Performance Report** | 2-3 hrs/wk | Internal + client reporting | MEDIUM |
| 6 | **Content Repurposing Machine** | 4-8 hrs/wk | Marketing accelerator | LOW |
| 7 | **Enrollment Automation** | 5-10 hrs/wk | Course/education clients | MEDIUM |
| 8 | **Low-Stock Alert + Purchase Order** | — | E-commerce clients | MEDIUM |
| 9 | **Review Collection Post-Purchase** | — | All service businesses | MEDIUM |
| 10 | **Meeting Action Items Extract** | — | Internal productivity | LOW |

---

## What We Need to Build (Priority Order)

### P0 — Revenue Critical (This Week)
1. **Deploy Lead Capture Webhook** — n8n import, Sheets, email credentials
2. **Deploy Error Catcher** — import JSON, configure notifications
3. **Invoice Parser n8n Workflow** — email trigger → parser → notification

### P1 — New Service Lines (Next 2 Weeks)
4. **Generic Booking System Template** — configurable for any service business
5. **Client Onboarding Sequence** — welcome email + folder + tasks + calendar
6. **AI Email Triage** — for Systack support + client support offerings

### P2 — Scale & Efficiency (Next Month)
7. **Weekly Reporting** — internal metrics + client reporting addon
8. **Review Collection** — post-purchase automated review requests
9. **Document Classification** — auto-route incoming docs by type

### P3 — Future / Nice to Have
10. **Content Repurposing** — blog → social pipeline
11. **Knowledge Base Search** — RAG on client documents
12. **Compliance Audit Trail** — full logging for regulated clients

---

## Template Creation Plan

For each missing automation, we will create:
1. **n8n workflow JSON** — import-ready
2. **Documentation** — setup guide for each template
3. **Demo page** — on systack-site if client-facing
4. **Pricing** — addon or included in tier

### First Three to Build (Starting Now)

| Template | File | What It Needs |
|----------|------|---------------|
| **Generic Booking System** | `templates/n8n-generic-booking.json` | Configurable services, time slots, deposit logic |
| **Client Onboarding** | `templates/n8n-client-onboarding.json` | Stripe trigger → email → Drive → Slack → Calendar |
| **Invoice Email Trigger** | `templates/n8n-invoice-email-pipeline.json` | Email trigger → PDF save → parser → Sheets → notify |

---

## Files to Create

1. `SYSTACK-SERVICES-GAP-ANALYSIS.md` — this file ✅
2. `templates/n8n-generic-booking.json` — configurable booking template
3. `templates/n8n-client-onboarding.json` — onboarding sequence
4. `templates/n8n-invoice-email-pipeline.json` — invoice processing
5. `templates/README.md` — template index with setup instructions
6. Update `SYSTACK-PRODUCTION-PLAN.md` — add template creation timeline

---

## Sources
- MEMORY.md — Systack services, production plan, active projects
- SYSTACK-PRODUCTION-PLAN.md — phase priorities
- systack-site/services/service-packages.md — pricing tiers and included automations
- systack-site/niches/services/sales.md — target business types
- https://bkwebdesigns.com/blog/n8n-workflow-examples/ — top 10 n8n automations for SMBs
