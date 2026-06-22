# Auto-Scheduling Optimizer — Documentation

**Automation ID:** `scheduling-optimizer`  
**Version:** 1.0  
**Status:** `draft` — Oracle proposal  
**Built:** N/A  
**Last Updated:** 2026-06-11  
**Owner:** Template for all clients  
**Builder:** SOL (planned)

---

## 1. Executive Summary

### What It Does
Detects gaps in the schedule (30-min holes, dead zones) and automatically creates discount slots. Pushes availability to past customers via SMS/email to fill empty time.

### Business Value
| Metric | Before | After (Target) |
|--------|--------|----------------|
| Schedule utilization | ~70% | > 90% |
| Revenue from discount slots | $0 | $200-500/week |
| Dead time | 2-3 hrs/day | < 30 min/day |

---

## 2. System Architecture

### Gap Detection
```
Calendar Analysis (daily at 6 PM for tomorrow)
    ↓
[Scan all slots for next 48h]
    ↓
[Identify gaps:
  - 30+ min hole between bookings
  - Full hour+ with no bookings
  - Day-before empty slots]
    ↓
[Create discount slot:
  - Normal price → 10-20% off
  - Label: "Flash slot — book in next 2h"]
    ↓
[Push to:
  - Past customers (segmented)
  - Waitlist
  - SMS subscribers]
```

---

## 3. Technical Specifications

### Discount Rules
| Gap Type | Discount | Urgency | Window |
|----------|----------|---------|--------|
| 30-min hole | 10% | Low | 24h |
| 1-hour+ empty | 15% | Medium | 12h |
| Same-day empty | 20% | High | 2h |
| Tomorrow empty | 15% | Medium | 6h |

### Push Targets
| Segment | Message | Channel |
|---------|---------|---------|
| Past customers (same service) | "Your usual slot is open tomorrow" | Email |
| Lapsed customers | "Come back for 20% off" | SMS |
| Waitlist | "A slot opened up — grab it" | SMS |
| VIPs | "Exclusive flash slot for you" | SMS |

---

## 4. Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SCHEDULE_SCAN_TIME` | When to scan (daily) | `18:00` |
| `MIN_GAP_MINUTES` | Min gap to create discount | `30` |
| `MAX_DISCOUNT` | Cap discount % | `20` |
| `FLASH_WINDOW_HOURS` | Hours to offer flash slot | `2` |

---

## 5. Build Log

### Phase 1: Gap Detection (Planned)
- **Status:** ⏳ QUEUED (Phase 3 priority)

---

## Appendix: Quick Reference

```
START:     Enable calendar scan + discount slot creation
STOP:      Disable scan (manual scheduling only)
CHECK:     Daily utilization report
FIX:       If too many discount slots → raise min gap threshold
ESCALATE:  If utilization not improving → review pricing strategy
```

---

**Last Updated:** 2026-06-11  
**Status:** Draft — Phase 3 priority
