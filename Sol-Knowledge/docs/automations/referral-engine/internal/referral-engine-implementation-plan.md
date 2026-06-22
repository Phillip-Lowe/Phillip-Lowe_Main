# Referral Engine — Implementation Plan

**Automation ID:** `referral-engine`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Build Phases

### Phase 1: Referral Link Generation (2 hours)

**Tasks:**

1. Generate unique referral code per customer (e.g., `REF-CUST001-A7X9`)
2. Create referral URL: `https://order.client.com/?ref=REF-CUST001-A7X9`
3. Store in `referrals` table
4. Send "Share and earn" email after service completion

---

### Phase 2: Attribution Tracking (2 hours)

**Tasks:**

1. Booking page detects `?ref=` parameter
2. Stores referral code in booking session
3. On booking completion, log referral attribution
4. Validate: referee is not the referrer, code is valid, not expired

---

### Phase 3: Reward Application (2 hours)

**Tasks:**

1. On referee's first completed booking:
   - Apply referee discount (e.g., 10% off)
   - Queue referrer reward
2. On referrer's next booking:
   - Apply credit automatically
   - Send "You earned $X from referrals!" notification
3. Track reward redemption

---

### Phase 4: Notification Emails (1 hour)

**Tasks:**

1. Referrer notification: "Your friend just booked — you earned $10!"
2. Referee welcome: "Welcome! Your first visit includes 10% off."
3. Monthly referral summary: "You've earned $X this month."

---

### Phase 5: Referral Dashboard (2 hours)

**Tasks:**

1. Track: total referrals, conversion rate, revenue from referrals
2. Top referrers leaderboard
3. Reward liability tracking (outstanding credits)

---

## 2. Timeline

| Phase | Est. Hours |
|-------|------------|
| Phase 1 | 2 |
| Phase 2 | 2 |
| Phase 3 | 2 |
| Phase 4 | 1 |
| Phase 5 | 2 |
| **Total** | **9 hours (~1–2 weeks)** |

---

## 3. Success Metrics

| Metric | Target |
|--------|--------|
| Referral program participation | > 20% of customers |
| Referral conversion rate | > 15% of clicks |
| Viral coefficient | > 0.3 |
| CAC reduction from referrals | > 50% vs paid channels |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
