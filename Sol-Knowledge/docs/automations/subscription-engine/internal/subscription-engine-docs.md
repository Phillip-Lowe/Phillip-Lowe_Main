# Subscription / Membership Engine — Documentation

**Automation ID:** `subscription-engine`  
**Version:** 1.0  
**Status:** `draft` — Oracle proposal  
**Built:** N/A  
**Last Updated:** 2026-06-11  
**Owner:** Template for all clients  
**Builder:** SOL (planned)

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
| Lifetime value | Unknown | 2-3x vs pay-per-visit |

---

## 2. System Architecture

### Subscription Types
| Plan | Frequency | Services | Price | Value |
|------|-----------|----------|-------|-------|
| Basic | Monthly | 2 services | $X | Save 10% |
| Standard | Monthly | 4 services | $Y | Save 15% |
| Premium | Monthly | Unlimited | $Z | Save 20% |
| Annual | Yearly | All included | $W | Save 25% |

### Components
| Component | Technology | Purpose |
|-----------|------------|---------|
| Plan Manager | n8n + DB | Defines plans, pricing, inclusions |
| Subscription Creator | Stripe/Square API | Creates recurring charge |
| Usage Tracker | SQLite | Counts services used vs plan limit |
| Renewal Engine | n8n Cron | Handles renewals, failures, dunning |
| Priority Booking | Booking system | Members see exclusive slots |
| Member Portal | HTML/JS | Customer views usage, next billing |

---

## 3. Technical Specifications

### Billing Cycle
```
Subscription Created
    ↓
[Charge immediately for first period]
    ↓
[Set renewal date]
    ↓
[Timer: 3 days before renewal]
    ↓
[Send: "Your membership renews in 3 days"]
    ↓
[Timer: Renewal date]
    ↓
[Attempt charge]
    ├── Success → Continue
    └── Failure → Dunning sequence
```

### Dunning (Failed Payment)
| Attempt | Timing | Action |
|---------|--------|--------|
| 1 | Day of failure | Retry immediately |
| 2 | +1 day | Retry + email "Update payment method" |
| 3 | +3 days | Retry + SMS warning |
| 4 | +5 days | Final retry + "Grace period ending" |
| 5 | +7 days | Cancel subscription, notify owner |

---

## 4. Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SUB_GRACE_DAYS` | Days after failure before cancel | `7` |
| `SUB_RETRY_COUNT` | Payment retries | `5` |
| `SUB_REMINDER_DAYS` | Days before renewal to notify | `3` |

---

## 5. Build Log

### Phase 1: Core Subscription (Planned)
- **Status:** ⏳ QUEUED (Phase 2 priority — high effort, high impact)

---

## Appendix: Quick Reference

```
START:     Enable Stripe/Square recurring + plan definitions
STOP:      Disable new subscriptions (existing continue)
CHECK:     Daily renewal queue + failed payment report
FIX:       If renewal rate drops → check dunning sequence
ESCALATE:  If churn high → review plan pricing/value
```

---

**Last Updated:** 2026-06-11  
**Status:** Draft — Phase 2 priority (high effort)
