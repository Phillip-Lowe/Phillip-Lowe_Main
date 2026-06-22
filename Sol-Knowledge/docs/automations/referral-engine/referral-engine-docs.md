# Referral Engine — Documentation

**Automation ID:** `referral-engine`  
**Version:** 1.0  
**Status:** `draft` — Oracle proposal  
**Built:** N/A  
**Last Updated:** 2026-06-11  
**Owner:** Template for all clients  
**Builder:** SOL (planned)

---

## 1. Executive Summary

### What It Does
Generates unique referral links for every customer. When someone books via that link, both referrer and referee get rewarded. Tracks attribution automatically through the booking process.

### Business Value
| Metric | Before | After (Target) |
|--------|--------|----------------|
| Word-of-mouth tracking | None (can't measure) | Full attribution |
| New customer CAC | Baseline (ads, etc.) | ~$0 (referral cost only) |
| Viral coefficient | 0 | > 0.3 (1 customer refers > 0.3 more) |

### ROI Estimate
- Time saved: 0 (fully automated)
- New customers: +10-30% via referrals
- CAC reduction: 50-80% vs paid ads

---

## 2. System Architecture

### Flow Diagram
```
Customer Completes Service
    ↓
[Generate Unique Referral Link]
    ↓
[Send: "Share and earn"]
    ├── Email with link
    └── SMS with link (optional)
    ↓
[Friend Clicks Link]
    ↓
[Booking Form Opens with ?ref={customer_id}]
    ↓
[Friend Completes Booking + Pays]
    ↓
[Trigger: Booking Detected with ref param]
    ↓
[Reward Both Parties]
    ├── Referrer: $10 credit / notification
    └── Referee: $10 off first booking (if new customer)
    ↓
[Log to Referral Ledger]
```

### Components
| Component | Technology | Purpose |
|-----------|------------|---------|
| Link Generator | Code | Creates unique URLs per customer |
| Email/SMS | n8n | Sends referral invitation |
| URL Tracker | URL params | ?ref={id} on booking links |
| Booking Parser | n8n | Detects ref param on completed booking |
| Reward Engine | n8n + DB | Credits accounts, sends notifications |
| Ledger | SQLite/Sheet | Tracks all referrals |

---

## 3. Technical Specifications

### Referral URL Format
```
https://order.theutopiadeli.com/pickup-order/?ref={customer_id}
```

### Reward Rules
| Scenario | Referrer Gets | Referee Gets |
|----------|---------------|--------------|
| New customer books | $10 credit | $10 off first booking |
| Existing customer books | Thanks only | No reward (not a referral) |
| Referee cancels | Credit revoked | Refund minus reward |

### Incentive Options
| Type | Give | Get | Example |
|------|------|-----|---------|
| Credit | $10 | $10 | "Give $10, Get $10" |
| Percentage | 15% | 15% | "Give 15% off, Get 15% off next" |
| Service | Free add-on | Free add-on | "Give free wax, Get free wax" |

---

## 4. Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `REFERRAL_REWARD_AMOUNT` | Dollar credit | `1000` (cents = $10) |
| `REFERRAL_REWARD_TYPE` | credit/percentage/service | `credit` |
| `REFERRAL_MIN_BOOKING` | Min booking value to qualify | `5000` ($50) |
| `REFERRAL_MAX_PER_MONTH` | Max rewards per referrer/month | `5` |

---

## 5. Operational Runbook

### Monitoring
| Metric | Expected | Alert If |
|--------|----------|----------|
| Referral link send rate | > 50% of customers | < 30% |
| Link click rate | > 20% | < 10% |
| Conversion to booking | > 10% | < 5% |
| Fraud rate (self-referral) | < 2% | > 5% |

### Fraud Prevention
| Check | Action |
|-------|--------|
| Same email/IP | Block + flag |
| Multiple refs from one referrer | Cap at max/month |
| Referee is existing customer | No reward |
| Booking cancelled < 24h | Reverse credit |

---

## 6. Build Log

### Phase 1: Core Referral (Planned)
- **Status:** ⏳ QUEUED (Phase 2 priority)

---

## Appendix: Quick Reference

```
START:     Enable post-service referral email + link generation
STOP:      Disable referral emails (existing links still work)
CHECK:     Weekly referral ledger → count + fraud flags
FIX:       If fraud rate high → tighten same-email checks
ESCALATE:  If conversion low → review offer attractiveness
```

---

**Last Updated:** 2026-06-11  
**Status:** Draft — Phase 2 priority
