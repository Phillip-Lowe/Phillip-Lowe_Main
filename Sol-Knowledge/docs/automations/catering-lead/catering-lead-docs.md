# Catering Lead System (Utopia Deli) — Documentation

**Automation ID:** `catering-lead`  
**Version:** 2.1  
**Status:** `live` — needs full documentation  
**Built:** 2026-06-08  
**Last Updated:** 2026-06-11  
**Owner:** Utopia Deli  
**Builder:** SOL

---

## 1. Executive Summary

### What It Does
5-step catering/event lead capture form with automatic scoring, email response, and SQLite logging. Identifies high-value leads and responds immediately with tailored information.

### Business Value
| Metric | Before | After |
|--------|--------|-------|
| Lead response time | Hours/days | < 5 minutes |
| Lead qualification | Manual | Automatic scoring |
| Data collection | Phone/email back-and-forth | Single form |

### URL
- https://order.theutopiadeli.com/catering/

---

## 2. System Architecture

### Flow Diagram
```
Customer visits /catering/
    ↓
[Step 1: Event Details]
[Step 2: Guest Count + Date]
[Step 3: Service Style]
[Step 4: Contact Info]
[Step 5: Special Requests]
    ↓
[Submit → n8n Webhook]
    ↓
[Score Lead:
  - Guest count (weight: high)
  - Date proximity (weight: medium)
  - Service type (weight: low)]
    ↓
[Auto-Email Based on Score]
    ├── High (80+): Detailed quote + calendar link
    ├── Medium (50-79): Standard info + follow-up offer
    └── Low (<50): Basic info + "let us know if dates change"
    ↓
[Log to SQLite]
    ↓
[Internal notification to deli]
```

### Components
| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | HTML/CSS/JS | 5-step form |
| Validation | `catering-form.js` | Field validation |
| Webhook | n8n | Receives submission |
| Scorer | n8n Code Node | Calculates lead score |
| Responder | n8n Email | Auto-response based on score |
| Database | SQLite | Lead storage |

---

## 3. Technical Specifications

### Lead Scoring
| Factor | Weight | Calculation |
|--------|--------|-------------|
| Guest count | 40% | >100 = max, 50-100 = med, <50 = low |
| Date proximity | 30% | <2 weeks = max, 2-4 weeks = med, >4 weeks = low |
| Service type | 20% | Full service = max, Drop-off = low |
| Budget mentioned | 10% | Yes = bonus |

### Payment Policy
- 50% deposit when invoice sent to book event
- Balance due 2 weeks prior to event
- Events within 2 weeks: full payment upfront

---

## 4. Configuration

### Webhook
- **URL:** `POST https://utopia-api.systack.net/webhook/utopia-deli-catering-v2`
- **Method:** JSON payload

### Database
- **File:** `~/.openclaw/workspaces/sol/utopia-deli-catering.db`
- **Table:** `catering_leads`

---

## 5. Operational Runbook

### Daily Checks
- [ ] New leads in last 24h
- [ ] Auto-emails sent successfully
- [ ] High-score leads flagged for personal follow-up

---

## 6. Build Log

### Phase 1: Core Form (2026-06-08)
- Built 5-step HTML form
- Added validation logic
- Connected to n8n webhook

### Phase 2: Scoring + Response (2026-06-08)
- Added lead scoring algorithm
- Built conditional email templates
- Connected SQLite logging

---

## Appendix: Quick Reference

```
START:     Verify webhook active + email templates correct
STOP:      Disable webhook in n8n
CHECK:     SQLite database for recent leads
FIX:       If emails not sending → check n8n execution log
ESCALATE:  If form submissions failing → check frontend console
```

---

**Last Updated:** 2026-06-11  
**Status:** Live — operational
