# CRM Lite (Client Profile Engine) — Documentation

**Automation ID:** `crm-lite`  
**Version:** 1.0  
**Status:** `draft` — Oracle proposal  
**Built:** N/A  
**Last Updated:** 2026-06-11  
**Owner:** Template for all clients  
**Builder:** SOL (planned)

---

## 1. Executive Summary

### What It Does
Builds a lightweight profile for every customer: visit history, average spend, preferred services, last booking. Enables "Welcome back — same service?" and "You usually add X" personalization.

### Business Value
| Metric | Before | After (Target) |
|--------|--------|----------------|
| Personalization | None | Every interaction personalized |
| Repeat booking ease | Baseline | 30% faster (pre-filled) |
| Upsell relevance | Generic | Targeted based on history |
| Customer lifetime value | Unknown | Tracked and growing |

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
  "frequency_days": 21,
  "next_predicted_visit": "2026-06-22",
  "upsell_history": {
    "accepted": ["Beard Trim", "Hot Towel"],
    "declined": ["Hair Wash"]
  },
  "referral_count": 3,
  "review_submitted": true,
  "status": "active"
}
```

### Components
| Component | Technology | Purpose |
|-----------|------------|---------|
| Data Aggregator | n8n | Collects from bookings, payments, reviews |
| Profile DB | SQLite/Postgres | Stores customer profiles |
| API | FastAPI/Express | Serves profile data to booking form |
| Upsell Engine | Code | Recommends based on profile |

---

## 3. Technical Specifications

### Profile API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/profile/{customer_id}` | GET | Full profile |
| `/profile/{id}/suggest` | GET | Upsell suggestions |
| `/profile/{id}/history` | GET | Visit history |

### Upsell Logic
```
IF customer.has_bought("Beard Trim") AND last_visit > 14_days:
  SUGGEST: "Beard trim touch-up?"

IF customer.avg_spend > 2000 AND NOT customer.has_bought("Hot Towel"):
  SUGGEST: "Add Hot Towel? (customers like you love it)"

IF customer.visit_count > 10:
  SUGGEST: "You're a regular — 10% off today"
```

---

## 4. Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `CRM_UPSELL_MAX` | Max upsells shown | `3` |
| `CRM_VIP_THRESHOLD` | Visits to be VIP | `10` |
| `CRM_LAPSED_DAYS` | Days since last visit = lapsed | `45` |

---

## 5. Operational Runbook

### Monitoring
| Metric | Expected | Alert If |
|--------|----------|----------|
| Profile coverage | > 90% of customers | < 80% |
| API response time | < 200ms | > 500ms |
| Upsell acceptance rate | > 15% | < 10% |

---

## 6. Build Log

### Phase 1: Profile Aggregation (Planned)
- **Status:** ⏳ QUEUED (Phase 2 priority)

---

## Appendix: Quick Reference

```
START:     Enable profile aggregation webhook
STOP:      Stop aggregation (profiles frozen)
CHECK:     Weekly profile coverage report
FIX:       If API slow → check DB indexes
ESCALATE:  If upsell rate drops → review suggestion logic
```

---

**Last Updated:** 2026-06-11  
**Status:** Draft — Phase 2 priority
