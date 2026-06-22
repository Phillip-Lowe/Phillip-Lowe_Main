# Review + Reputation Engine — Policy Guide

**Automation ID:** `review-system`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Review Routing Policy

| Rating | Route | Customer Sees | Owner Action |
|--------|-------|---------------|--------------|
| ⭐⭐⭐⭐⭐ (5) | Public | "Thank you! Share on Google?" → Google review page | None (monitor) |
| ⭐⭐⭐⭐ (4) | Public | "Thank you! Share on Google?" → Google review page | None (monitor) |
| ⭐⭐⭐ (3) | Internal | "Thanks! Any feedback to help us improve?" → Text box | Review within 24h |
| ⭐⭐ (2) | Internal + Alert | "We're sorry. Tell us what happened." → Text box | Respond within 4h |
| ⭐ (1) | Internal + Urgent Alert | "We want to make this right." → Text box + phone | Respond within 1h |

---

## 2. Negative Review Response Protocol

### Step 1 — Acknowledge (Within Timeframe)

- 3 stars: Email within 24 hours
- 2 stars: Email or call within 4 hours
- 1 star: Call within 1 hour

**Template (2–3 star):**

> "Thank you for your feedback, [Name]. We're sorry your experience wasn't perfect. I'd like to understand what happened and make it right. Can we connect briefly?"

**Template (1 star):**

> "[Name], I just saw your feedback and I want to personally apologize. This is not the experience we aim for. I'm calling to make this right. What's the best number to reach you?"

---

### Step 2 — Investigate

- Review service details (provider, time, service type)
- Check for patterns (same provider, same service, same time slot)
- Document findings

---

### Step 3 — Make Good

| Rating | Suggested Make-Good |
|--------|---------------------|
| 3 stars | 15% off next service |
| 2 stars | 25% off next service or free add-on |
| 1 star | Full refund or free re-service |

---

### Step 4 — Follow Up

- Check in after next visit
- Confirm issue resolved
- Ask if they'd update their feedback

---

### Step 5 — Log Outcome

Record in `reviews` table:

- Resolution offered
- Customer accepted?
- Follow-up outcome
- Pattern flag (if recurring issue)

---

## 3. Public Review Best Practices

### Responding to Public Reviews

| Review Type | Response Strategy |
|-------------|------------------|
| Positive (4–5 stars) | Thank them, mention something specific |
| Neutral (3 stars public) | Thank them, acknowledge feedback, offer to improve |
| Negative (1–2 stars leaked) | Apologize, take offline, offer resolution |

**Never:**

- Argue with reviewer publicly
- Share customer details
- Offer compensation publicly (take it offline)
- Ignore negative reviews

---

## 4. Review Request Timing

| Service Type | Wait Before Requesting |
|--------------|----------------------|
| Quick service (< 30 min) | 1 hour |
| Standard service (30–90 min) | 2 hours |
| Long service (> 90 min) | 4 hours |
| Multi-visit (packages) | After final visit |

**Rationale:** Give customer time to experience results before asking for feedback.

---

## 5. Compliance Notes

- Never incentivize positive reviews (against Google/Yelp TOS)
- Never filter reviews — all collected, just routed differently
- Customers can always choose to post publicly regardless of rating
- Internal-only routing is a suggestion, not a block

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
