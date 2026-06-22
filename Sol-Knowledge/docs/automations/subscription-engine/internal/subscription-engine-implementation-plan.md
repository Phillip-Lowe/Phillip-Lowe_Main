# Subscription/Membership Engine — Implementation Plan

**Automation ID:** `subscription-engine`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Build Phases

### Phase 1: Plan Definition + Database (2 hours)

**Tasks:**

1. Create `plans` and `subscriptions` tables
2. Define plan templates (Basic, Standard, Premium)
3. Build plan management UI (add/edit/retire plans)

---

### Phase 2: Stripe Subscription Integration (3 hours)

**Tasks:**

1. Create Stripe products + prices for each plan
2. Build subscription checkout flow
3. Webhook handler for Stripe events:
   - `invoice.paid` → update subscription status
   - `invoice.payment_failed` → dunning process
   - `customer.subscription.deleted` → cancel membership
4. Sync Stripe subscription ID with local database

---

### Phase 3: Usage Tracking (2 hours)

**Tasks:**

1. On each booking, check if customer has active subscription
2. If yes: decrement `services_remaining` or increment `services_used`
3. If no services remaining: offer upgrade or pay-per-visit
4. Monthly reset for plans with monthly allowances

---

### Phase 4: Renewal + Dunning Management (2 hours)

**Tasks:**

1. Cron workflow: check subscriptions due for renewal
2. Stripe auto-charges on billing date
3. If payment fails:
   - T+1 day: "Payment failed" email + retry
   - T+3 days: "Update payment method" email
   - T+7 days: "Subscription at risk" email
   - T+14 days: Cancel subscription
4. Successful renewal: reset usage counters

---

### Phase 5: Member Portal (3 hours)

**Tasks:**

1. Customer-facing page: view plan, usage, billing history
2. Upgrade/downgrade flow
3. Cancel flow (with retention offer)
4. Payment method management

---

## 2. Timeline

| Phase | Est. Hours |
|-------|------------|
| Phase 1 | 2 |
| Phase 2 | 3 |
| Phase 3 | 2 |
| Phase 4 | 2 |
| Phase 5 | 3 |
| **Total** | **12 hours (~2–3 weeks)** |

---

## 3. Dependencies

| Dependency | Status |
|------------|--------|
| Stripe account | Client must provide |
| CRM Lite | For customer identification |
| Booking System | For usage tracking |

---

## 4. Success Metrics

| Metric | Target |
|--------|--------|
| Subscription conversion | > 15% of customers |
| Monthly churn rate | < 5% |
| Failed payment recovery | > 50% |
| LTV increase | 2–3x vs pay-per-visit |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
