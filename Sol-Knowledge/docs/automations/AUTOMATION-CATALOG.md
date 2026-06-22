# Systack — Complete Automation Catalog

**Current Status:** Building documentation + finishing incomplete systems  
**Oracle Systems:** 10 proposed — in planning/validation phase  
**Rule:** Every automation gets docs (client + internal + future agents/employees)

---

## ✅ LIVE SYSTEMS (Documentation Required)

### 1. Order Workflow (Utopia Deli)
- **What:** Online ordering with payment capture
- **URL:** https://order.theutopiadeli.com/pickup-order/
- **Status:** LIVE — needs docs
- **Docs:** `docs/automations/order-system/` (TODO)
- **Components:** HTML form → Square API → n8n → Google Sheets → Email
- **Last Updated:** 2026-06-03

### 2. Invoice Parser
- **What:** PDF invoice extraction via API
- **URL:** https://invoices.systack.net/extract
- **Status:** LIVE — needs docs
- **Docs:** `docs/automations/invoice-parser/` (TODO)
- **Components:** Email trigger → PDF save → API call → Postgres → Email summary
- **Last Updated:** 2026-06-10

### 3. Catering Lead System
- **What:** Catering/event lead capture + scoring
- **URL:** https://order.theutopiadeli.com/catering/
- **Status:** LIVE — needs docs
- **Docs:** `docs/automations/catering-lead/` (TODO)
- **Components:** 5-step form → webhook → n8n scoring → SQLite → email
- **Last Updated:** 2026-06-08

---

## 🚧 PARTIALLY BUILT / NEEDS COMPLETION

### 4. No-Show Prevention System
- **What:** Deposit + reminder + confirmation workflow
- **Status:** PARTIAL — deposit exists, reminders missing
- **Docs:** `docs/automations/noshow-prevention/` (TODO)
- **Gap:** 24h reminder, 2h reminder, "confirm or cancel" button, auto-release slot
- **Priority:** HIGH — Phase 1 (Immediate ROI)

### 5. Smart Rebooking Engine
- **What:** Automatic repeat booking reminders based on service cycle
- **Status:** NOT BUILT
- **Docs:** `docs/automations/smart-rebooking/` (draft)
- **Gap:** Service cycle tracking, predicted return date calculation, pre-filled booking links
- **Priority:** HIGH — Phase 1

### 6. Review + Reputation Engine
- **What:** Post-service review request with routing (positive → public, negative → internal)
- **Status:** NOT BUILT
- **Docs:** `docs/automations/review-system/` (draft)
- **Gap:** Trigger on service completion, review form, conditional routing
- **Priority:** HIGH — Phase 1

---

## 📋 ORACLE SYSTEMS — Planning Phase

### Phase 1 (Immediate ROI)

#### 7. Missed-Lead Recovery Engine
- **What:** Capture abandoned bookings, follow up at 5min / 2hr / 24hr
- **Status:** DRAFT — Oracle proposal
- **Docs:** `docs/automations/missed-lead-recovery/` (draft)
- **Value:** Converts abandoned sessions → revenue
- **Components:** Partial form capture → Google Sheets/DB → Timer nodes → Email/SMS

#### 8. Referral Engine
- **What:** Unique referral links per customer with trackable incentives
- **Status:** DRAFT — Oracle proposal
- **Docs:** `docs/automations/referral-engine/` (draft)
- **Value:** Viral growth, low CAC
- **Components:** Link generation → booking form metadata → incentive tracking

#### 9. CRM Lite (Client Profile Engine)
- **What:** Per-customer history, spend, preferences
- **Status:** DRAFT — Oracle proposal
- **Docs:** `docs/automations/crm-lite/` (draft)
- **Value:** Personalization, retention, upsell targeting
- **Components:** Data aggregation → profile cards → "welcome back" prompts

---

### Phase 2 (Growth)

#### 10. Subscription / Membership Engine
- **What:** Recurring revenue plans (e.g., $120/mo for 4 cuts)
- **Status:** DRAFT — Oracle proposal
- **Docs:** `docs/automations/subscription-engine/` (draft)
- **Value:** Predictable recurring revenue
- **Components:** Stripe/Square subscriptions → priority booking → member pricing

#### 11. Upsell Intelligence Engine
- **What:** Adaptive upsell ordering based on performance data
- **Status:** DRAFT — Oracle proposal
- **Docs:** `docs/automations/upsell-intelligence/` (draft)
- **Value:** Higher AOV through data-driven suggestions
- **Components:** Track add-on popularity → reorder suggestions → hide poor performers

---

### Phase 3 (Optimization)

#### 12. Auto-Scheduling Optimizer
- **What:** Detect calendar gaps, create discount slots, push availability
- **Status:** DRAFT — Oracle proposal
- **Docs:** `docs/automations/scheduling-optimizer/` (draft)
- **Value:** Maximize time utilization, reduce dead zones
- **Components:** Calendar analysis → gap detection → discount slot creation → SMS/email push

#### 13. Revenue Dashboard
- **What:** Operator view of bookings, upsells, time slots, customer visits
- **Status:** DRAFT — Oracle proposal
- **Docs:** `docs/automations/revenue-dashboard/` (draft)
- **Value:** Full visibility for decision-making
- **Components:** Data aggregation → visual dashboard → key metrics

---

## 🗺️ System Expansion Map

```
LAYER 1: REVENUE EXPANSION
├── Missed-Lead Recovery (7)
├── Subscription Engine (10)
└── Upsell Intelligence (11)

LAYER 2: OPERATIONS AUTOMATION
├── No-Show Prevention (4) ← PARTIALLY BUILT
├── Auto-Scheduling Optimizer (12)
└── CRM Lite (9)

LAYER 3: INTELLIGENCE + RETENTION
├── Smart Rebooking (5) ← NOT BUILT
├── Review System (6) ← NOT BUILT
└── Referral Engine (8)

HIGH-LEVERAGE COMBO: "AUTO BUSINESS MODE"
Customer visits → Books + pays → Gets reminders → Shows up 
→ Gets upsold → Leaves review → Gets rebook reminder → Refers someone
```

---

## 📊 Build Priority Matrix

| Priority | System | Effort | Impact | Status |
|----------|--------|--------|--------|--------|
| 1 | No-Show Prevention | Low | High | Partial |
| 2 | Smart Rebooking | Low | High | Not Built |
| 3 | Review System | Low | High | Not Built |
| 4 | Missed-Lead Recovery | Medium | High | Draft |
| 5 | Referral Engine | Medium | Medium | Draft |
| 6 | CRM Lite | Medium | Medium | Draft |
| 7 | Upsell Intelligence | Low | Medium | Draft |
| 8 | Scheduling Optimizer | High | Medium | Draft |
| 9 | Revenue Dashboard | High | Medium | Draft |
| 10 | Subscription Engine | High | High | Draft |

---

## 🔧 System Design Standard (Oracle Requirement)

For every automation:

| Requirement | Implementation |
|-------------|---------------|
| Explicit triggers | Documented in section 3 of template |
| Stored state | Google Sheets / DB / SQLite — documented |
| Retry logic | 5 attempts with exponential backoff |
| Failure alerts | Email to Systack + client (if applicable) |

---

## 📁 Documentation Coverage

| System | Docs Created | Status | Client-Ready |
|--------|-------------|--------|--------------|
| Order Workflow | ❌ | Live, no docs | No |
| Invoice Parser | ❌ | Live, no docs | No |
| Catering Lead | ❌ | Live, no docs | No |
| No-Show Prevention | ❌ | Partial | No |
| All Others | ❌ | Draft/planning | No |

**Action Required:** Create documentation for ALL live systems immediately. Use template at `docs/automations/templates/automation-doc-template.md`.

---

## 🎯 Next Steps

### Immediate (Today)
1. [ ] Document existing live systems (3 systems)
2. [ ] Complete No-Show Prevention (add reminders + confirmation)
3. [ ] Create draft docs for Oracle Phase 1 systems

### This Week
4. [ ] Build Smart Rebooking Engine
5. [ ] Build Review System
6. [ ] Client handoff docs for Utopia Deli (all 3 systems)

### Next 2 Weeks
7. [ ] Missed-Lead Recovery Engine
8. [ ] CRM Lite
9. [ ] Referral Engine

### Oracle Validation
10. [ ] Get client approval on Phase 1 scope
11. [ ] Validate "Auto Business Mode" concept with Utopia Deli
12. [ ] Build Revenue Dashboard (internal use first)

---

**Last Updated:** 2026-06-11  
**Catalog Version:** 1.0  
**Oracle Systems Source:** 2026-06-11 user directive + Oracle proposal  
**Rule:** Every automation gets docs — this is a hard rule now, saved in all places
