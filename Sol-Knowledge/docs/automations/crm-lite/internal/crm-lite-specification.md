# CRM Lite — Specification Document

**Automation ID:** `crm-lite`  
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

Builds a lightweight profile for every customer: visit history, average spend, preferred services, last booking. Enables "Welcome back — same service?" and "You usually add X" personalization across all other automations.

### Business Value

| Metric | Before | After (Target) |
|--------|--------|----------------|
| Personalization | None | Every interaction personalized |
| Repeat booking ease | Baseline | 30% faster (pre-filled) |
| Upsell relevance | Generic | Targeted based on history |
| Customer LTV | Unknown | Tracked and growing |

---

## 2. System Architecture

### Customer Profile Schema

```json
{
  "customer_id": "cust_001",
  "first_visit": "2026-01-15",
  "total_visits": 12,
  "total_spent": 184000,
  "avg_spend": 15333,
  "preferred_services": ["Deluxe Cut", "Beard Trim"],
  "last_visit": "2026-06-01",
  "last_service": "Deluxe Cut",
  "preferred_provider": "provider_03",
  "preferred_time": "morning",
  "referral_count": 2,
  "review_avg": 4.8,
  "tags": ["VIP", "big_spender"]
}
```

### Data Sources

| Source | Data |
|--------|------|
| Booking System | Visits, services, spend |
| Referral Engine | Referral count |
| Review System | Average rating |
| Upsell Engine | Preferred add-ons |

---

## 3. Database Schema

```sql
CREATE TABLE customer_profiles (
  customer_id TEXT PRIMARY KEY,
  email TEXT,
  phone TEXT,
  name TEXT,
  first_visit DATE,
  total_visits INTEGER DEFAULT 0,
  total_spent_cents INTEGER DEFAULT 0,
  preferred_services JSONB,
  last_visit DATE,
  last_service TEXT,
  preferred_provider TEXT,
  preferred_time_slot TEXT,
  tags TEXT[],
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Implementation Plan

| Phase | Task | Est. Effort |
|-------|------|-------------|
| 1 | Database schema + profile creation | 2 hours |
| 2 | Profile aggregation from bookings | 3 hours |
| 3 | Personalization API (query profile) | 2 hours |
| 4 | Integration with booking form | 2 hours |
| 5 | Privacy + data retention | 1 hour |
| **Total** | | **~10 hours** |

---

## 5. Privacy Compliance

| Requirement | Implementation |
|-------------|---------------|
| Data minimization | Only store service-relevant data |
| Customer access | Provide profile on request |
| Data deletion | Delete profile on customer request |
| Retention | Auto-anonymize after 24 months inactive |
| Consent | Implied by booking (service relationship) |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
