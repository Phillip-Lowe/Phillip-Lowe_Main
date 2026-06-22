# Referral Engine — Specification Document

**Automation ID:** `referral-engine`  
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

Generates unique referral links for every customer. When someone books via that link, both referrer and referee get rewarded. Tracks attribution automatically through the booking process.

### Business Value

| Metric | Before | After (Target) |
|--------|--------|----------------|
| Word-of-mouth tracking | None | Full attribution |
| New customer CAC | Baseline | ~$0 (referral cost only) |
| Viral coefficient | 0 | > 0.3 |

---

## 2. System Architecture

### Flow Diagram

```
Customer Completes Service
  → Generate Unique Referral Link
    → Send: "Share and earn" email
      → Referee clicks link → Lands on booking page with referral code
        → Referee books → Referral code captured
          → Both parties rewarded:
            → Referrer: Credit/discount applied
            → Referee: First-visit discount
          → Track in referral_log
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Link Generator | n8n Code Node | Unique referral URLs |
| Attribution Tracker | Postgres | Tracks referral chain |
| Reward Engine | n8n Code Node | Applies credits/discounts |
| Notification | n8n Email | "You earned a reward!" |

---

## 3. Database Schema

```sql
CREATE TABLE referrals (
  id SERIAL PRIMARY KEY,
  referrer_customer_id TEXT,
  referral_code TEXT UNIQUE,
  referee_email TEXT,
  referee_booked BOOLEAN DEFAULT FALSE,
  reward_given BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Implementation Plan

| Phase | Task | Est. Effort |
|-------|------|-------------|
| 1 | Referral link generation | 2 hours |
| 2 | Attribution tracking on booking | 2 hours |
| 3 | Reward application logic | 2 hours |
| 4 | Notification emails | 1 hour |
| 5 | Referral dashboard | 2 hours |
| **Total** | | **~9 hours** |

---

## 5. Incentive Structure Guide

### Sample Programs

| Program | Referrer Reward | Referee Reward |
|---------|-----------------|----------------|
| **Standard** | $10 credit | 10% off first visit |
| **Premium** | $20 credit | 20% off first visit |
| **Tiered** | $10/20/50 based on volume | 10% off |
| **Service-based** | Free add-on next visit | Free add-on first visit |

### Reward Rules

- Credit applied after referee completes first booking
- Credits expire after 90 days
- Maximum 5 referral credits per month (prevents abuse)
- Referrer and referee must be different people

---

## 6. ROI Projection

| Assumption | Value |
|------------|-------|
| Monthly customers | 100 |
| Referral participation | 20% (20 referrers) |
| Avg referrals per referrer | 1.5 |
| New customers via referral | 30/month |
| Avg booking value | $50 |
| Referral reward cost | $10 |
| **Monthly new revenue** | **$1,200** (net of rewards) |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
