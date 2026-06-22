# Subscription/Membership Engine — Specification Document

**Automation ID:** `subscription-engine`  
**Version:** 1.0  
**Status:** Draft — Specification  
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

## 1. Executive Summary

### What It Does

Recurring revenue plans: customer pays monthly/weekly for a bundle of services. Auto-renews, priority booking, member-only pricing. Examples: barber $120/mo for 4 cuts, cleaning weekly plan, coaching monthly access.

### Business Value

| Metric | Before | After (Target) |
|--------|--------|----------------|
| Revenue predictability | Erratic | Stable monthly |
| Customer retention | Variable | > 80% (locked in) |
| Cash flow | Lumpy | Smooth |
| Lifetime value | Unknown | 2–3x vs pay-per-visit |

---

## 2. System Architecture

### Subscription Types

| Plan | Frequency | Services | Example Price | Savings |
|------|-----------|----------|---------------|---------|
| Basic | Monthly | 2 services | $X | Save 10% |
| Standard | Monthly | 4 services | $Y | Save 15% |
| Premium | Monthly | Unlimited | $Z | Save 20% |
| Annual | Yearly | All included | $W | Save 25% |

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Plan Management | n8n + Postgres | Define and store plans |
| Billing Engine | Stripe/Square | Recurring payments |
| Usage Tracker | Postgres | Track service usage against plan |
| Renewal Handler | n8n Cron | Process renewals, handle failures |
| Member Portal | HTML/CSS/JS | Customer view of plan + usage |

---

## 3. Database Schema

```sql
CREATE TABLE subscriptions (
  id SERIAL PRIMARY KEY,
  customer_id TEXT,
  plan_id TEXT,
  status TEXT DEFAULT 'active',
  start_date DATE,
  next_billing_date DATE,
  billing_amount_cents INTEGER,
  services_used INTEGER DEFAULT 0,
  services_included INTEGER,
  stripe_subscription_id TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Implementation Plan

| Phase | Task | Est. Effort |
|-------|------|-------------|
| 1 | Plan definition + database | 2 hours |
| 2 | Stripe subscription integration | 3 hours |
| 3 | Usage tracking | 2 hours |
| 4 | Renewal + dunning management | 2 hours |
| 5 | Member portal | 3 hours |
| **Total** | | **~12 hours** |

---

## 5. Pricing Strategy Guide

### Common Models

| Industry | Plan Example | Price Point |
|----------|-------------|-------------|
| Barber/Beauty | 4 cuts/month | $120/mo ($30/cut vs $35 walk-in) |
| Cleaning | Weekly cleaning | $200/mo ($50/visit vs $65 walk-in) |
| Fitness/Coaching | Monthly access | $150/mo (unlimited vs $25/session) |
| Massage | 2 sessions/month | $140/mo ($70/session vs $85 walk-in) |

### Pricing Formula

```
Subscription Price = (Per-Visit Price × Visits Included) × (1 - Discount %)
```

Example: $35 cut × 4 visits × 0.85 (15% off) = $119 → round to $120

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
