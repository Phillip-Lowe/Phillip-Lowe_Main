# Review + Reputation Engine — Implementation Plan

**Automation ID:** `review-system`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Build Phases

### Phase 1: Service Completion Trigger (1 hour)

**Tasks:**

1. Add webhook trigger on service completion
2. Receive: customer email, service type, provider, timestamp
3. Queue for review request (wait 2 hours)

---

### Phase 2: Review Request Email + Form (3 hours)

**Tasks:**

1. Build review form HTML (star rating + optional text)
2. Email template: "How was your [service]?" with review link
3. Unique token per review (prevents spam/duplicates)
4. Form captures: star rating, feedback text, public share permission

---

### Phase 3: Star Rating Routing Logic (2 hours)

**Tasks:**

1. n8n Code node for routing:

```javascript
const rating = $json.rating;
if (rating >= 4) {
  // Route to public platforms
  return [{ json: { ...$json, route: "public" } }];
} else if (rating === 3) {
  // Internal feedback, no alert
  return [{ json: { ...$json, route: "internal", alert: false } }];
} else {
  // Internal feedback + alert owner
  return [{ json: { ...$json, route: "internal", alert: true } }];
}
```

2. Public route: redirect to Google/Yelp with pre-filled positive context
3. Internal route: thank customer, log feedback privately

---

### Phase 4: Internal Feedback Logging (1 hour)

**Tasks:**

1. Create `reviews` table in Postgres
2. Log all reviews (public and internal)
3. Track: rating, feedback text, service, provider, date
4. Dashboard: average rating trend, common complaints

---

### Phase 5: Negative Review Alerts (1 hour)

**Tasks:**

1. On 1–2 star review: immediate email/SMS to owner
2. Alert includes: customer name, service, rating, feedback
3. Owner can respond directly from alert

---

## 2. Timeline

| Phase | Est. Hours |
|-------|------------|
| Phase 1 | 1 |
| Phase 2 | 3 |
| Phase 3 | 2 |
| Phase 4 | 1 |
| Phase 5 | 1 |
| **Total** | **8 hours (~1 week)** |

---

## 3. Success Metrics

| Metric | Target |
|--------|--------|
| Review collection rate | > 30% |
| Public review percentage | > 70% of collected |
| Average public rating | > 4.2 stars |
| Negative feedback response time | < 4 hours |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
