# ORACLE SYSTEMS — WORK ORDER
## Service Manuals & Workflow Documentation
**From:** Systack (Phillip Lowe / SOL)
**To:** Oracle Systems
**Date:** 2026-06-16
**Priority:** URGENT

---

## DELIVERABLES REQUIRED

### TIER 1: LIVE SYSTEMS (Complete Immediately)
These systems are running production clients. Full documentation needed NOW.

#### 1. Order System (Utopia Deli)
**Status:** ✅ LIVE since 2026-06-03
**Client:** Utopia Deli, Little Rock AR
**URL:** https://order.theutopiadeli.com/pickup-order/

**Deliverables Needed:**
- [ ] **Client Service Manual** — What Utopia Deli sees, how orders flow, how to read Google Sheet
- [ ] **Internal Implementation Guide** — How to replicate for new restaurant clients
- [ ] **Workflow Walkthrough** — n8n workflow node-by-node explanation
- [ ] **Technical Architecture Diagram** — Frontend → Square → n8n → Sheets → Email
- [ ] **Troubleshooting Guide** — Common failures and fixes

**Key Technical Details:**
- Square Checkout API v2 integration
- n8n webhook receives payment confirmation
- ES6 spread operator NOT supported in n8n Code nodes
- Logo path must use `../images/logo.png` from subdirectory
- Webhook must process → email → THEN respond to customer

---

#### 2. Invoice Parser
**Status:** ✅ LIVE since 2026-06-10
**Client:** Internal (Systack) + available as add-on
**URL:** https://invoices.systack.net/extract

**Deliverables Needed:**
- [ ] **Client Service Manual** — How to use: forward email with PDF, what to expect
- [ ] **Internal Implementation Guide** — Setting up IMAP, adding vendor formats
- [ ] **Workflow Walkthrough** — IMAP → attachment → API → Postgres → email
- [ ] **API Documentation** — Endpoint, parameters, response format
- [ ] **Vendor Format Guide** — How to add new invoice templates

**Key Technical Details:**
- IMAP format MUST be "resolved" (not shallow)
- Binary key is `attachment_0` NOT `attachment_`
- IF node checks `mimeType` = `application/pdf` (NOT filename)
- 9 vendor formats supported + OCR fallback
- Gmail app passwords may be revoked silently

---

#### 3. Catering Lead System (Utopia Deli)
**Status:** ✅ LIVE since 2026-06-08
**Client:** Utopia Deli
**URL:** https://order.theutopiadeli.com/catering/

**Deliverables Needed:**
- [ ] **Client Service Manual** — How catering leads work, what auto-responses look like
- [ ] **Internal Implementation Guide** — Modifying scoring, customizing emails
- [ ] **Workflow Walkthrough** — Form → webhook → scorer → conditional email → SQLite
- [ ] **Lead Scoring Algorithm Documentation** — Weights and thresholds
- [ ] **Email Template Library** — High/Medium/Low score responses

**Key Technical Details:**
- 5-step form with progressive disclosure
- Lead scores: High (80+), Medium (50-79), Low (<50)
- Payment policy: 50% deposit to book, balance 2 weeks prior
- SQLite database: `utopia-deli-catering.db`

---

#### 4. Confirmation Email System
**Status:** ✅ LIVE since 2026-06-12
**Client:** Utopia Deli
**URL:** https://order.theutopiadeli.com/payment-confirmed/

**Deliverables Needed:**
- [ ] **Client Service Manual** — What customers see after payment
- [ ] **Internal Implementation Guide** — Customizing confirmation templates
- [ ] **Workflow Walkthrough** — Payment webhook → confirmation email dispatch

---

### TIER 2: PARTIAL SYSTEMS (Complete After Build)
These are partially built. Document what exists, flag what's missing.

#### 5. No-Show Prevention System
**Status:** 🚧 PARTIAL (Phase 1 done, Phase 2 in progress)
**Client:** Utopia Deli (template for all clients)

**Current State:**
- ✅ Deposit collection via Square
- ✅ Confirmation email with token
- ✅ Confirmation webhook handler
- ✅ T-24h reminder scheduler
- ✅ T-2h reminder scheduler
- 🚧 Auto-release unconfirmed slots (NOT BUILT)
- 🚧 Frontend booking form (NOT BUILT)

**Deliverables Needed:**
- [ ] **Current State Documentation** — What's working, what's not
- [ ] **Completion Roadmap** — What needs to be built to finish
- [ ] **Client Policy Manual** — Deposit rules, cancellation terms
- [ ] **Internal Implementation Guide** — When completed
- [ ] **Workflow Walkthrough** — Current + planned nodes

---

### TIER 3: PLANNED SYSTEMS (Architecture Documents)
These don't exist yet. Create specification documents only.

#### 6. Missed-Lead Recovery Engine
**Status:** 📋 DRAFT
**Concept:** Capture abandoned bookings, follow up at 5min/2hr/24hr

**Deliverables Needed:**
- [ ] **Specification Document** — Architecture, flow, components
- [ ] **Implementation Plan** — Steps to build
- [ ] **ROI Projection** — Estimated conversion lift

---

#### 7. Smart Rebooking Engine
**Status:** 📋 DRAFT
**Concept:** Track service cycles, predict return dates, send pre-filled booking links

**Deliverables Needed:**
- [ ] **Specification Document** — Algorithm for predicting rebooking
- [ ] **Implementation Plan** — Database schema, trigger logic
- [ ] **ROI Projection** — Retention impact

---

#### 8. Review + Reputation Engine
**Status:** 📋 DRAFT
**Concept:** Post-service review request with routing (positive → public, negative → internal)

**Deliverables Needed:**
- [ ] **Specification Document** — Trigger conditions, routing logic
- [ ] **Implementation Plan** — Review form, conditional logic
- [ ] **Policy Guide** — How to handle negative reviews

---

#### 9. Referral Engine
**Status:** 📋 DRAFT
**Concept:** Unique referral links per customer with trackable incentives

**Deliverables Needed:**
- [ ] **Specification Document** — Link generation, tracking, payout logic
- [ ] **Implementation Plan** — Database design, webhook flow
- [ ] **Incentive Structure Guide** — Sample programs

---

#### 10. CRM Lite
**Status:** 📋 DRAFT
**Concept:** Per-customer history, spend, preferences, "welcome back" prompts

**Deliverables Needed:**
- [ ] **Specification Document** — Data model, profile cards
- [ ] **Implementation Plan** — Aggregation pipeline, UI design
- [ ] **Privacy Compliance** — GDPR considerations

---

#### 11. Subscription/Membership Engine
**Status:** 📋 DRAFT
**Concept:** Recurring revenue plans (e.g., $120/mo for 4 haircuts)

**Deliverables Needed:**
- [ ] **Specification Document** — Stripe/Square subscription integration
- [ ] **Implementation Plan** — Billing cycle, member benefits
- [ ] **Pricing Strategy Guide** — Common membership models

---

#### 12. Upsell Intelligence Engine
**Status:** 📋 DRAFT
**Concept:** Adaptive upsell ordering based on performance data

**Deliverables Needed:**
- [ ] **Specification Document** — Analytics pipeline, suggestion algorithm
- [ ] **Implementation Plan** — A/B testing framework
- [ ] **Performance Guide** — How to measure upsell success

---

#### 13. Auto-Scheduling Optimizer
**Status:** 📋 DRAFT
**Concept:** Detect calendar gaps, create discount slots, push availability

**Deliverables Needed:**
- [ ] **Specification Document** — Gap detection, pricing model
- [ ] **Implementation Plan** — Calendar integration, slot creation
- [ ] **Revenue Impact Model** — Fill-rate projections

---

#### 14. Revenue Dashboard
**Status:** 📋 DRAFT
**Concept:** Operator view of bookings, upsells, time slots, customer visits

**Deliverables Needed:**
- [ ] **Specification Document** — Metrics, visualizations, access control
- [ ] **Implementation Plan** — Data sources, aggregation, UI
- [ ] **Metrics Dictionary** — KPI definitions and calculations

---

## BRAND STANDARDS (Apply to ALL Documents)

### Colors
| Name | Hex | Usage |
|------|-----|-------|
| Navy | #001a2d | Headers, footers, CTAs |
| Navy Light | #002845 | Gradients, hover states |
| Teal | #007da9 | Secondary accents |
| Cyan | #00a1db | Primary CTA buttons |
| Cyan Bright | #00c5e0 | Gradients |
| Gray 50 | #f8fafc | Backgrounds |
| Gray 100 | #f1f5f9 | Cards |
| Gray 200 | #e2e8f0 | Borders |
| Gray 400 | #94a3b8 | Muted text |
| Gray 600 | #475569 | Body text |
| Gray 800 | #1e293b | Headings |
| Green | #22c55e | Success states |
| Red | #ef4444 | Error states |
| Purple | #8b5cf6 | Accent highlights |

### Typography
- Headings: System font stack, bold weight
- Body: System font stack, regular weight
- Monospace: Code samples, technical data

### Email Template Rules
1. HTML field MUST start with `=` (expression evaluation)
2. Use REAL HTML tags — never escaped entities
3. Navy header bar + gray body + cyan CTA button + navy footer
4. Variables: `{{ $json.field_name }}`

---

## RESOURCES PROVIDED

### Files
- `/docs/automations/order-system/order-system-docs.md`
- `/docs/automations/invoice-parser/invoice-parser-docs.md`
- `/docs/automations/catering-lead/catering-lead-docs.md`
- `/docs/automations/noshow-prevention/noshow-prevention-docs.md`
- `/docs/automations/noshow-prevention/noshow-status-2026-06-11.md`
- `/docs/automations/AUTOMATION-CATALOG.md`
- `/docs/automations/MASTER-PLAN.md`
- `/docs/automations/templates/automation-doc-template.md`
- `/docs/SYSTACK-COMPLETE-INVENTORY-FOR-ORACLE.md` (this document)

### Access
- n8n: https://n8n.systack.net
- Test site: https://order.theutopiadeli.com/
- Invoice API: https://invoices.systack.net/extract

### Contact for Questions
- **Phillip Lowe:** support@systack.net / (501) 274-6231
- **SOL (AI Agent):** Available via OpenClaw interface

---

## TIMELINE

| Phase | Deliverables | Target Date |
|-------|-------------|-------------|
| Week 1 | Tier 1 manuals (4 live systems) | 2026-06-23 |
| Week 2 | Tier 2 manual (No-Show, current state) | 2026-06-30 |
| Week 3 | Tier 3 specifications (10 planned systems) | 2026-07-07 |
| Week 4 | Review, revise, finalize | 2026-07-14 |

---

**AUTHORIZED BY:** Phillip Lowe, Systack
**DATE:** 2026-06-16
**PRIORITY:** URGENT — Client deliveries pending
