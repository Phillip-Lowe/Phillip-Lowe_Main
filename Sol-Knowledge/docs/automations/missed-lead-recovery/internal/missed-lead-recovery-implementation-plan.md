# Missed-Lead Recovery Engine — Implementation Plan

**Automation ID:** `missed-lead-recovery`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Build Phases

### Phase 1: Frontend Abandonment Detection (3 hours)

**Objective:** Capture partial form data when users abandon booking.

**Tasks:**

1. Add `beforeunload` event listener to booking form
2. On email/phone field blur, POST partial data to webhook
3. Set cookie for users without email (retargeting fallback)
4. Test: start booking, enter email, close tab → data captured

**Files to create/modify:**
- `booking-form.js` — add abandonment detection
- `recovery-webhook` — n8n webhook endpoint

---

### Phase 2: Recovery Queue Database (2 hours)

**Objective:** Store abandoned sessions for follow-up.

**Tasks:**

1. Create `recovery_queue` table in Postgres
2. Build n8n webhook to receive and store abandoned data
3. Add deduplication: don't re-queue if already recovered
4. Test: submit abandoned data → row appears in DB

---

### Phase 3: T+5min Follow-Up (2 hours)

**Objective:** Send immediate helpful follow-up.

**Tasks:**

1. Build n8n Cron workflow (runs every 5 minutes)
2. Query: `abandoned_at <= NOW() - 5min AND followup_5min_sent = FALSE`
3. Email template: "Did something go wrong? Complete your booking here."
4. Mark `followup_5min_sent = TRUE`
5. Test: abandon booking → receive email within 5–10 minutes

---

### Phase 4: T+2hr Follow-Up (1 hour)

**Objective:** Second touch with mild urgency.

**Tasks:**

1. Extend Cron workflow to check 2-hour window
2. Query: `abandoned_at <= NOW() - 2hr AND followup_2hr_sent = FALSE AND recovered = FALSE`
3. Email template: "Your slot is still available — book now before it's gone."
4. Mark `followup_2hr_sent = TRUE`

---

### Phase 5: T+24hr Incentive Follow-Up (2 hours)

**Objective:** Final attempt with incentive.

**Tasks:**

1. Extend Cron workflow to check 24-hour window
2. Query: `abandoned_at <= NOW() - 24hr AND followup_24hr_sent = FALSE AND recovered = FALSE`
3. Email template: "Come back for 10% off" or "Free add-on with your booking"
4. Include unique discount code (trackable)
5. Mark `followup_24hr_sent = TRUE`
6. If still no booking after 48hr: set `status = 'lost'`

---

### Phase 6: Conversion Tracking + Reporting (2 hours)

**Objective:** Measure recovery effectiveness.

**Tasks:**

1. Track when abandoned email books (match on email)
2. Update `recovered = TRUE, recovered_at = NOW()`
3. Build monthly report: abandoned vs recovered vs lost
4. Calculate recovery rate and revenue impact

---

## 2. Timeline

| Phase | Est. Hours | Dependencies |
|-------|------------|--------------|
| Phase 1 | 3 | None |
| Phase 2 | 2 | Phase 1 |
| Phase 3 | 2 | Phase 2 |
| Phase 4 | 1 | Phase 3 |
| Phase 5 | 2 | Phase 4 |
| Phase 6 | 2 | Phase 5 |
| **Total** | **12** | **~2 weeks part-time** |

---

## 3. Dependencies

| Dependency | Status |
|------------|--------|
| Booking form (frontend) | 🚧 Not built (No-Show Phase 4) |
| Postgres database | ✅ Available |
| n8n Cron workflows | ✅ Pattern established |
| Email (SMTP) | ✅ Configured |

---

## 4. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Recovery rate | > 15% | recovered / total abandoned |
| T+5min response rate | > 25% open rate | Email analytics |
| T+24hr conversion | > 5% | Discount code usage |
| Monthly recovered revenue | > $300 | Sum of recovered bookings |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
