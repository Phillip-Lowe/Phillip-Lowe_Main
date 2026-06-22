# Review + Reputation Engine — Specification Document

**Automation ID:** `review-system`  
**Version:** 1.0  
**Status:** Draft — Specification  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## Brand Reference

| Role | Color | Hex |
|------|-------|-----|
| Headers, CTAs | Navy | `#001a2d` |
| Secondary accents | Teal | `#007da9` |
| Primary buttons, links | Cyan | `#00a1db` |
| Body text | Gray 600 | `#475569` |
| Headings | Gray 800 | `#1e293b` |
| Success | Green | `#22c55e` |
| Error | Red | `#ef4444` |

---

## 1. Executive Summary

### What It Does

After every completed service, automatically requests a review. Positive reviews (4–5 stars) are routed to public platforms (Google, Yelp). Negative reviews (1–3 stars) are captured internally for private feedback — protecting your reputation while collecting actionable insights.

### Business Value

| Metric | Before | After (Target) |
|--------|--------|----------------|
| Review collection rate | ~5% | > 30% |
| Public review sentiment | Mixed | Mostly positive (filtered) |
| Negative feedback visibility | Public | Private, actionable |
| Star rating improvement | Stagnant | +0.5 stars in 90 days |

---

## 2. System Architecture

### Flow Diagram

```
Service Marked Complete
  → Wait: 2 hours after service
    → Send Review Request Email
      → Customer Clicks Review Link
        → In-App Review Form
          → 5 stars → "Share on Google?" → Redirect to Google
          → 4 stars → "Share on Google?" → Redirect to Google
          → 3 stars → "Feedback to improve?" → Internal form
          → 2 stars → "Tell us what happened" → Internal + alert owner
          → 1 star → "We want to make this right" → Internal + immediate alert
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Completion Trigger | n8n Webhook | Fires when service done |
| Review Form | HTML/CSS/JS | Star rating + feedback |
| Routing Logic | n8n Code Node | Positive → public, Negative → internal |
| Internal Logger | Postgres/Sheets | Stores negative feedback |
| Alert System | n8n Email/SMS | Immediate negative alerts |

---

## 3. Implementation Plan

| Phase | Task | Est. Effort |
|-------|------|-------------|
| 1 | Service completion trigger | 1 hour |
| 2 | Review request email + form | 3 hours |
| 3 | Star rating routing logic | 2 hours |
| 4 | Internal feedback logging | 1 hour |
| 5 | Negative review alerts | 1 hour |
| **Total** | | **~8 hours** |

---

## 4. Policy Guide: Handling Negative Reviews

| Star Rating | Response | Timing |
|-------------|----------|--------|
| 3 stars | Internal form: "Any feedback to help us improve?" | Within 24h |
| 2 stars | Internal form + alert owner: "Tell us what happened." | Within 4h |
| 1 star | Internal form + immediate alert: "We want to make this right." | Within 1h |

**Owner response protocol:**

1. Acknowledge within timeframe
2. Investigate what went wrong
3. Offer make-good (discount, free service, refund)
4. Follow up after resolution
5. Log outcome for pattern analysis

---

## 5. ROI Projection

| Assumption | Value |
|------------|-------|
| Monthly services | 200 |
| Review collection rate (target) | 30% (60 reviews) |
| Positive routing rate | ~70% (42 public reviews) |
| Star rating improvement | +0.5 stars |
| Revenue impact of +0.5 stars | ~10% booking increase |
| **Monthly additional revenue** | **$500–1,000** |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
