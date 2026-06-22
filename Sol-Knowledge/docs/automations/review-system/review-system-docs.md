# Review + Reputation Engine — Documentation

**Automation ID:** `review-system`  
**Version:** 1.0  
**Status:** `draft` — Oracle proposal, ready to build  
**Built:** N/A  
**Last Updated:** 2026-06-11  
**Owner:** Template for all service clients  
**Builder:** SOL (planned)

---

## 1. Executive Summary

### What It Does
After every completed service, automatically requests a review. Positive reviews (4-5 stars) are routed to public platforms (Google, Yelp). Negative reviews (1-3 stars) are captured internally for private feedback and improvement.

### Business Value
| Metric | Before | After (Target) |
|--------|--------|----------------|
| Review collection rate | ~5% (only motivated customers) | > 30% (system asks everyone) |
| Public review sentiment | Mixed (only extremes) | Mostly positive (filtered) |
| Negative feedback visibility | Public, hurts reputation | Private, actionable |
| Star rating improvement | Stagnant | +0.5 stars in 90 days |

### ROI Estimate
- Time saved: 2-3 hrs/week (no manual review requests)
- Reputation impact: Priceless — higher ratings = more customers
- Feedback quality: Structured data instead of random complaints

---

## 2. System Architecture

### Flow Diagram
```
Service Marked Complete
    ↓
[Wait: 2 hours after service]
    ↓
[Send Review Request Email]
    ↓
[Customer Clicks Review Link]
    ↓
[In-App Review Form]
    ├── 5 stars → "Would you share on Google?" → [Redirect to Google]
    ├── 4 stars → "Would you share on Google?" → [Redirect to Google]
    ├── 3 stars → "Thanks! Any feedback to help us improve?" → [Internal form]
    ├── 2 stars → "We're sorry. Tell us what happened." → [Internal form + alert owner]
    └── 1 star  → "We want to make this right." → [Internal form + immediate alert]
    ↓
[Internal feedback logged to DB/sheet]
[Public reviews tracked]
[Negative alerts sent to owner]
```

### Components
| Component | Technology | Purpose |
|-----------|------------|---------|
| Completion Trigger | n8n Webhook | Fires when service done |
| Delay Timer | n8n Wait Node | 2-hour delay (not too soon) |
| Review Requester | n8n Email | Sends branded review link |
| Review Collector | HTML Form | In-app star rating + comment |
| Router | n8n IF Node | Positive → public, Negative → private |
| Public Redirect | URL redirect | Google/Yelp with pre-filled fields |
| Internal Logger | SQLite/Sheet | Stores all feedback |
| Alert System | n8n Email/SMS | Notifies owner of negative reviews |

### Data Flow
1. Service completion → 2-hour timer starts
2. Review request email sent with personalized link
3. Customer opens link → sees in-app form
4. Customer rates 1-5 stars
5. Positive (4-5): Ask to share publicly → redirect to Google/Yelp
6. Neutral (3): Ask for improvement feedback → internal only
7. Negative (1-2): Apologize + request details → internal + owner alert
8. All feedback logged → monthly report generated

---

## 3. Technical Specifications

### Triggers
| Trigger | Type | Schedule/Condition |
|---------|------|-------------------|
| Service Completed | Webhook | `POST /webhook/service-done` |
| Review Submitted | Webhook | `POST /webhook/review-submitted` |
| Negative Alert | Immediate | IF rating <= 2 |

### Review Form Fields
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `rating` | 1-5 stars | Yes | Determines routing |
| `comment` | Text | No | Required if rating <= 3 |
| `would_recommend` | Yes/No | Yes | Net Promoter signal |
| `improvement` | Text | No | Only shown if rating <= 3 |
| `public_review` | Text | No | Pre-filled Google/Yelp text |

### Routing Logic
| Rating | Action | Destination | Owner Alert? |
|--------|--------|-------------|--------------|
| 5 | "Please share on Google" | Google review URL | No |
| 4 | "Please share on Google" | Google review URL | No |
| 3 | "Thanks, how can we improve?" | Internal feedback | Weekly digest |
| 2 | "We're sorry, tell us more" | Internal + apology | Immediate email |
| 1 | "We want to make this right" | Internal + escalation | Immediate email + SMS |

---

## 4. Configuration

### Timing
| Setting | Value | Rationale |
|---------|-------|-----------|
| Delay after service | 2 hours | Customer home, experience fresh |
| Follow-up if no response | 3 days | Gentle reminder |
| Follow-up if still no response | 7 days | Final ask |
| Negative response SLA | 4 hours | Owner must respond to 1-2 star |

### Public Review URLs
| Platform | URL Template |
|----------|-------------|
| Google | `https://search.google.com/local/writereview?placeid={PLACE_ID}` |
| Yelp | `https://www.yelp.com/writeareview/biz/{BUSINESS_ID}` |

### Alert Recipients
| Rating | Recipients | Method |
|--------|-----------|--------|
| 1 star | Owner + Manager | Email + SMS |
| 2 star | Owner | Email |
| 3 star | Weekly digest only | Email (summary) |

---

## 5. Operational Runbook

### Daily Checks
- [ ] Reviews submitted yesterday: count + sentiment
- [ ] Negative reviews: responded to within SLA?
- [ ] Public review redirect success rate: > 70%
- [ ] Unresponded negative alerts: 0

### Weekly
- [ ] Generate feedback summary report
- [ ] Identify top improvement themes
- [ ] Track star rating trend

### Monitoring
| Metric | Expected | Alert If |
|--------|----------|----------|
| Review request open rate | > 40% | < 30% |
| Review completion rate | > 30% | < 20% |
| Public review conversion | > 60% of 4-5 star | < 40% |
| Negative review response time | < 4 hours | > 8 hours |
| Avg rating trend | Stable or up | Down 0.3+ stars |

---

## 6. Build Log

### Phase 1: Core Review Collection (Planned)
- **Date:** TBD
- **What:** Completion trigger → 2h delay → review request → form → store
- **Status:** ⏳ QUEUED (Phase 1 priority)

### Phase 2: Smart Routing (Planned)
- **Date:** TBD
- **What:** Positive → public redirect, Negative → internal + alerts
- **Status:** ⏳ QUEUED

### Phase 3: Owner Dashboard (Planned)
- **Date:** TBD
- **What:** Feedback summary, trend analysis, response tracking
- **Status:** ⏳ QUEUED

---

## 7. Client Handoff

### What the Client Sees
- Weekly email: "This week: 12 reviews, 4.6 avg, 2 negative (both responded)"
- Customer view: Simple form, 30 seconds to complete
- No public shaming — negative feedback handled privately

### What They Need to Know
- System asks EVERY customer (not just happy ones)
- Negative feedback comes to them first (not public)
- 4-5 star customers are encouraged to share publicly
- Response time to negative reviews matters for retention

### What They Should NOT Touch
- Review timing — 2 hours is tested optimal
- Routing thresholds — changing star cutoffs affects public/private balance
- Public review URLs — wrong place ID breaks the flow

---

## 8. Future Enhancements

| Priority | Idea | Effort | Impact |
|----------|------|--------|--------|
| P1 | SMS review requests | Low | High |
| P2 | Photo/video review support | Medium | Medium |
| P3 | Competitor rating comparison | Medium | Medium |
| P4 | AI sentiment analysis of comments | High | Medium |
| P5 | Automated owner response suggestions | High | High |

---

## Appendix: Quick Reference

```
START:     Enable completion webhook + verify review form URL
STOP:      Disable webhook (pauses new requests)
CHECK:     Weekly report → review count + sentiment
FIX:       If public redirects failing → check Google Place ID
ESCALATE:  If avg rating dropping → review recent feedback themes
```

---

**Last Updated:** 2026-06-11  
**Status:** Draft — ready for Phase 1 build
