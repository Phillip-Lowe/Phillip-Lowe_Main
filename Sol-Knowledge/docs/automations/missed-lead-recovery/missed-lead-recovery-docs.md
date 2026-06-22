# Missed-Lead Recovery Engine — Documentation

**Automation ID:** `missed-lead-recovery`  
**Version:** 1.0  
**Status:** `draft` — Oracle proposal  
**Built:** N/A  
**Last Updated:** 2026-06-11  
**Owner:** Template for all clients  
**Builder:** SOL (planned)

---

## 1. Executive Summary

### What It Does
Captures every abandoned booking attempt and follows up automatically: 5 minutes ("forgot something?"), 2 hours ("still interested?"), 24 hours ("here's a reason to come back"). Converts lost sessions into revenue.

### Business Value
| Metric | Before | After (Target) |
|--------|--------|----------------|
| Abandoned session recovery | 0% (lost forever) | > 15% |
| Revenue from recovered leads | $0 | $300-1000/mo |
| Customer acquisition cost | Baseline | -20% (recovered vs new) |

### ROI Estimate
- Time saved: 0 (fully automated)
- Revenue captured: $300-1000/month
- Payback period: Immediate

---

## 2. System Architecture

### Flow Diagram
```
Customer Visits Booking Page
    ↓
[Partial Data Captured?]
    ├── Email entered ──→ [Store in recovery_queue]
    ├── Phone entered ──→ [Store in recovery_queue]
    └── Neither ──→ [Cookie-based retargeting only]
    ↓
[Timer: T+5 minutes]
    ↓
[Email/SMS: "Did something go wrong? Complete your booking."]
    ↓
[No booking?]
    ↓
[Timer: T+2 hours]
    ↓
[Email: "Your slot is still available" + urgency]
    ↓
[No booking?]
    ↓
[Timer: T+24 hours]
    ↓
[Email: "Come back for X% off" or "Bonus add-on free"]
    ↓
[Booked?] ──→ [Remove from queue, celebrate] ──→ [End]
[Still no?] ──→ [Tag: "lost lead"] ──→ [Monthly report]
```

### Components
| Component | Technology | Purpose |
|-----------|------------|---------|
| Page Tracker | JavaScript | Captures partial form data |
| Recovery Queue | SQLite/Postgres | Stores abandoned sessions |
| Timer Engine | n8n Cron | Triggers at 5m, 2h, 24h |
| Email Sender | n8n Email | Sends recovery messages |
| SMS Sender | Twilio (optional) | SMS recovery |
| Booking Detector | Webhook | Removes from queue on completion |

---

## 3. Technical Specifications

### Triggers
| Trigger | Type | Condition |
|---------|------|-----------|
| Page Abandon | JavaScript | `beforeunload` with partial data |
| Recovery Timer | Cron | Per lead: 5m, 2h, 24h |
| Booking Complete | Webhook | Removes lead from queue |

### Recovery Messages
| Timing | Channel | Subject/Message | Tone |
|--------|---------|----------------|------|
| 5 min | Email | "Did something go wrong?" | Helpful |
| 2 hr | Email | "Your slot is still available" | Gentle urgency |
| 24 hr | Email | "We saved something for you" | Incentive |
| 24 hr | SMS (if phone) | "Come back for 10% off" | Direct |

### Incentive Escalation
| Attempt | Offer | Rules |
|---------|-------|-------|
| 1st (5m) | No offer | Just help them complete |
| 2nd (2h) | No offer | Urgency only |
| 3rd (24h) | 10% off or free add-on | Max discount cap |
| 4th (72h) | 15% off | Final attempt |

---

## 4. Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `RECOVERY_EMAIL_5M` | Enable 5-min email | `true` |
| `RECOVERY_EMAIL_2H` | Enable 2-hour email | `true` |
| `RECOVERY_EMAIL_24H` | Enable 24-hour email | `true` |
| `RECOVERY_MAX_DISCOUNT` | Max discount % | `15` |
| `RECOVERY_SMS_ENABLED` | SMS fallback | `false` |

---

## 5. Operational Runbook

### Monitoring
| Metric | Expected | Alert If |
|--------|----------|----------|
| Abandonment rate | < 40% | > 60% |
| Recovery rate (any touch) | > 10% | < 5% |
| Recovery rate (booked) | > 5% | < 2% |
| Email open rate | > 30% | < 20% |
| Unsubscribe rate | < 1% | > 3% |

---

## 6. Build Log

### Phase 1: Core Recovery (Planned)
- **Status:** ⏳ QUEUED (Phase 2 priority)

---

## Appendix: Quick Reference

```
START:     Enable page tracking script + recovery queue
STOP:      Disable page script (no new captures)
CHECK:     Weekly recovery rate report
FIX:       If emails bouncing → clean email capture regex
ESCALATE:  If recovery rate low → review offer/incentive strategy
```

---

**Last Updated:** 2026-06-11  
**Status:** Draft — Phase 2 priority
