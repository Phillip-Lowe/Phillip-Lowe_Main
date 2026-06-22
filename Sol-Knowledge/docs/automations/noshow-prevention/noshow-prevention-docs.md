# No-Show Prevention System — Documentation

**Automation ID:** `noshow-prevention`  
**Version:** 1.0  
**Status:** `building` (was partial — completing now)  
**Built:** 2026-06-03 (deposit logic), completing 2026-06-11  
**Last Updated:** 2026-06-11  
**Owner:** Utopia Deli (template for all clients)  
**Builder:** SOL

---

## 1. Executive Summary

### What It Does
Eliminates revenue loss from no-shows by requiring deposits at booking and sending automated reminders with confirmation requirements. If a customer doesn't confirm, their slot is automatically released for resale.

### Business Value
| Metric | Before | After (Target) |
|--------|--------|----------------|
| No-show rate | ~15-20% | < 5% |
| Revenue lost to no-shows | ~$500-1000/mo | < $100/mo |
| Staff idle time | 2-3 hrs/day | < 30 min/day |

### ROI Estimate
- Time saved: 5-10 hrs/week (fewer last-minute scrambles)
- Revenue protected: $400-900/month
- Payback period: Immediate (deposit covers implementation cost)

---

## 2. System Architecture

### Flow Diagram
```
Booking Made
    ↓
[Deposit Required?] ──No──→ [Proceed Normally]
    ↓ Yes
[Collect Deposit via Square]
    ↓
[Store in DB: customer, slot, deposit_amount, status="pending"]
    ↓
[Timer: T-24h] ──→ [Send Reminder + "Confirm or Cancel" Button]
    ↓
[Timer: T-2h]  ──→ [Send Final Reminder + "I'm on my way" Button]
    ↓
[Customer Confirms?]
    ↓ Yes                          ↓ No / No Response (T-30min)
[Status: "confirmed"]          [Status: "unconfirmed"]
    ↓                                ↓
[Proceed]                      [Auto-release slot]
                               [Notify waitlist if exists]
                               [Flag for follow-up]
```

### Components
| Component | Technology | Purpose |
|-----------|------------|---------|
| Booking Trigger | n8n Webhook | Captures new booking |
| Deposit Collection | Square API | Holds deposit amount |
| Database | SQLite / Postgres | Stores booking state |
| Reminder Engine | n8n Timer + Email | Sends timed reminders |
| Confirmation Handler | n8n Webhook | Processes confirm/cancel |
| Slot Manager | n8n Code Node | Releases unconfirmed slots |

### Data Flow
1. Booking captured → deposit calculated → payment link sent
2. Payment confirmed → booking stored with "pending" status
3. T-24h: reminder email with confirm/cancel buttons
4. T-2h: final reminder with "I'm on my way" button
5. T-30min: check confirmation status
6. Confirmed → proceed | Unconfirmed → release slot + notify

---

## 3. Technical Specifications

### Triggers
| Trigger | Type | Schedule/Condition |
|---------|------|-------------------|
| New Booking | Webhook | `POST /webhook/booking-created` |
| Confirmation Click | Webhook | `GET /confirm?token={token}` |
| Cancellation Click | Webhook | `GET /cancel?token={token}` |
| "On My Way" Click | Webhook | `GET /omw?token={token}` |
| Timer T-24h | Cron | `0 9 * * *` (9 AM day before) |
| Timer T-2h | Cron | Custom per-booking |
| Auto-release | Cron | `T-30min` per booking |

### Inputs
| Field | Type | Required | Source |
|-------|------|----------|--------|
| `booking_id` | string | Yes | Booking system |
| `customer_email` | string | Yes | Booking form |
| `customer_phone` | string | No | Booking form |
| `service_type` | string | Yes | Booking form |
| `slot_datetime` | ISO datetime | Yes | Booking system |
| `deposit_amount` | cents | Yes | Config (e.g., $20 = 2000) |
| `total_value` | cents | Yes | Booking system |

### Outputs
| Destination | Format | Frequency |
|-------------|--------|-----------|
| Customer Email | HTML | Per reminder event |
| Internal Alert | Text/Email | Per no-show risk |
| Google Sheet | Row | Per booking |
| Square | Transaction | Per deposit |

### Dependencies
| System | Version | Credential ID |
|--------|---------|---------------|
| n8n | 1.50+ | — |
| Square | API v2 | `square_deposit_cred` |
| Gmail/SMTP | IMAP/SMTP | `gmail_app_password` |
| SQLite | 3.x | Local file |

---

## 4. Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `NOSHOW_DEPOSIT_PERCENT` | Deposit as % of total | `25` |
| `NOSHOW_MIN_DEPOSIT` | Minimum deposit in cents | `1000` ($10) |
| `NOSHOW_REMINDER_24H` | Enable 24h reminder | `true` |
| `NOSHOW_REMINDER_2H` | Enable 2h reminder | `true` |
| `NOSHOW_AUTO_RELEASE` | Auto-release unconfirmed | `true` |
| `NOSHOW_RELEASE_BUFFER` | Minutes before slot to release | `30` |

### Deposit Rules
| Service Value | Deposit % | Min Deposit | Max Deposit |
|---------------|-----------|-------------|-------------|
| < $50 | 100% | $10 | $50 |
| $50-$150 | 50% | $20 | $75 |
| > $150 | 25% | $37.50 | No max |

### Retry Policy
| Condition | Action | Max Attempts |
|-----------|--------|--------------|
| Email bounce | Retry with backup SMTP | 3 |
| Square API fail | Exponential backoff (1m, 5m, 15m) | 5 |
| Webhook timeout | Retry immediate | 3 |
| DB write fail | Alert + queue for retry | 5 |

---

## 5. Operational Runbook

### Startup / Shutdown
- **Activate:** Enable webhook in n8n, verify Square credential active, test reminder timers
- **Deactivate:** Disable webhook, pause reminder cron jobs, finish processing in-flight bookings
- **Emergency stop:** Disable webhook + pause all cron jobs → manual review of today's bookings

### Daily Checks
- [ ] Yesterday's no-show rate < 5%
- [ ] Today's bookings all have deposit status
- [ ] Reminder emails sent successfully (check n8n execution log)
- [ ] Any unconfirmed bookings flagged for release

### Monitoring
| Metric | Expected | Alert If |
|--------|----------|----------|
| Bookings/day | Varies | Sudden drop > 50% |
| Deposit collection rate | > 95% | < 90% |
| Confirmation rate | > 80% | < 70% |
| Auto-release rate | < 10% | > 20% (too aggressive) |
| Email delivery rate | > 98% | < 95% |

### Failure Scenarios
| Scenario | Symptom | Response |
|----------|---------|----------|
| Square API down | Deposits fail | Switch to "pay at arrival" mode, alert manager |
| Email blocked | Reminders not sent | Check SMTP credential, switch to SMS if phone available |
| Customer clicks expired link | 404 or "booking not found" | Redirect to "contact us" page, log for follow-up |
| Double-booking after release | Two customers same slot | Manual override, honor first confirmation, offer alternative |

---

## 6. Build Log

### Phase 1: Deposit Collection (2026-06-03)
- **Date:** 2026-06-03
- **What:** Square deposit integration at booking time
- **Blockers:** Square API credential setup
- **Decisions:** 25% deposit default, $10 minimum
- **Status:** ✅ COMPLETE

### Phase 2: Reminder System (2026-06-11 06:30)
- **Date:** 2026-06-11
- **What:** T-24h and T-2h reminders with confirm/cancel buttons
- **Completed:**
  - Database `systack_noshow` created
  - `bookings` table created with confirmation tracking
  - Postgres credential configured (localhost, trust auth)
  - Booking INSERT branch tested — data persisting
  - Confirmation branch tested — email delivered ✅
  - T-24h scheduler working ✅
  - T-2h scheduler working ✅
- **Next:** Build frontend + test/prod separation
- **Status:** 🚧 IN PROGRESS

### Phase 3: Frontend + Test/Prod Architecture (2026-06-11 08:30)
- **Date:** 2026-06-11
- **What:** Build systack.net booking form with test/prod separation
- **Test DB:** `systack_test` created with matching schema
- **Test workflows:** `booking-website-demo` + `confirm-booking-website-demo` created
- **Pages needed:**
  - `/test-book` — test form (internal only)
  - `/book` — production form (customer-facing)
- **Status:** ⏳ QUEUED

### Phase 3: Auto-Release + Waitlist (NEXT)
- **Date:** TBD
- **What:** Automatic slot release, waitlist notification
- **Blockers:** Need waitlist system built first
- **Status:** ⏳ QUEUED

---

## 7. Client Handoff

### What the Client Sees
- Booking form with deposit notice: "A 25% deposit is required to hold your slot"
- Confirmation emails: "Your booking is confirmed. You'll receive reminders 24h and 2h before."
- Reminder emails with clear buttons: **[Confirm]** **[Cancel]** **[Reschedule]**

### What They Need to Know
- Deposits are collected via Square (same system as regular payments)
- No-shows forfeit deposit (policy clearly stated at booking)
- Cancellations > 24h ahead get full deposit refund
- Cancellations < 24h forfeit deposit (or can reschedule)

### What They Should NOT Touch
- n8n workflow configuration — any changes break reminders
- Square API credentials — managed by Systack
- Deposit percentages — changing without analysis affects conversion
- Email templates — changes may break formatting

### Support Escalation
| Issue | First Response | Escalate To |
|-------|---------------|-------------|
| Deposits not collecting | Check Square dashboard | Systack — within 4h |
| Reminders not sending | Check n8n executions | Systack — within 4h |
| Customer complaints about deposits | Explain policy, offer credit | Systack if pattern emerges |
| Want to change deposit rules | Document request | Systack — next business day |

---

## 8. Future Enhancements

| Priority | Idea | Effort | Impact |
|----------|------|--------|--------|
| P1 | SMS reminders | Low | High |
| P2 | Waitlist auto-fill | Medium | High |
| P3 | Weather-based reminders | Medium | Medium |
| P4 | "Running late" button (T-15min) | Low | Medium |
| P5 | Deposit refund automation | Low | Medium |
| P6 | No-show prediction ML | High | Medium |

---

## 9. References

### Related Documentation
- [Order System Docs](../order-system/) — Booking source
- [Catering Lead Docs](../catering-lead/) — Similar reminder patterns
- [n8n Workflow Runbook](../../templates/BUILD-CHECKLIST.md)

### Source Code
- n8n workflow ID: `TODO — create in n8n`
- Frontend: `order.theutopiadeli.com/pickup-order/`
- API endpoint: `https://utopia-api.systack.net/webhook/...`

### Test Data
```json
{
  "booking_id": "test-001",
  "customer_email": "test@example.com",
  "customer_phone": "+15551234567",
  "service_type": "Deluxe Cut",
  "slot_datetime": "2026-06-15T14:00:00-05:00",
  "deposit_amount": 2500,
  "total_value": 10000
}
```

---

## Appendix: Quick Reference Card

```
START:     Enable webhook + cron jobs in n8n
STOP:      Disable webhook + pause cron jobs
CHECK:     n8n execution log → look for reminder sends
FIX:       If emails failing: check SMTP credential in n8n
ESCALATE:  If deposit collection fails → check Square API status
```

---

**Last Updated:** 2026-06-11  
**Automation Version:** 1.0 (partial — completing Phase 2)
