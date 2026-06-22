# Utopia Deli — Catering Lead System
## Internal Implementation Guide

**Document ID:** `UD-CAT-IMPL-001`  
**Version:** 1.0  
**Status:** Internal — Systack Only  
**Source System:** Utopia Deli (Live since 2026-06-08)  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## Brand Reference

| Role | Color | Hex |
|------|-------|-----|
| Primary | Deep Burgundy | `#590B3F` |
| Primary Light | Burgundy Light | `#7a1a55` |
| Accent | Rust Red | `#AF3D4B` |
| Accent Hover | Rust Light | `#c44d5b` |
| Secondary | Purple | `#754681` |
| Gold | Warm Gold | `#D59F5C` |
| Gold Light | Cream | `#f5e6d0` |
| Background | Off-White | `#FBFCFE` |
| Card | White | `#FFFFFF` |
| Text | Dark Gray | `#1F2937` |
| Text Light | Medium Gray | `#6B7280` |
| Border | Light Gray | `#E5E7EB` |
| Success | Green | `#22c55e` |
| Error | Red | `#dc2626` |

---

## 1. System Architecture

```
Customer visits /catering/
  → 5-Step Form (progressive disclosure)
    → n8n Webhook (POST)
      → Lead Scoring (Code Node)
        → Conditional Email Router
          ├── High (80+): Detailed quote + calendar link
          ├── Medium (50-79): Standard info + follow-up offer
          └── Low (<50): Basic info
        → SQLite Logging
        → Internal Notification
```

---

## 2. Core Components

### Frontend

- 5-step HTML form with progressive disclosure
- Field validation via `catering-form.js`
- Located at `order.theutopiadeli.com/catering/`

---

### n8n Workflow

**Webhook:** `POST https://utopia-api.systack.net/webhook/utopia-deli-catering-v2`

Key nodes:

| # | Node | Purpose |
|---|------|---------|
| 1 | Webhook (POST) | Receives form submission |
| 2 | Validate Fields | Checks required fields present |
| 3 | Score Lead (Code Node) | Calculates lead score |
| 4 | Route by Score (Switch) | Branches based on score threshold |
| 5 | High Score Email | Detailed quote template |
| 6 | Medium Score Email | Standard info template |
| 7 | Low Score Email | Basic info template |
| 8 | Log to SQLite | Stores lead in database |
| 9 | Internal Notification | Alerts deli of new lead |

---

### Database

- **Type:** SQLite
- **File:** `utopia-deli-catering.db`
- **Table:** `catering_leads`

---

## 3. Lead Scoring Algorithm

### Scoring Formula

```
Score = (GuestCountScore × 0.40) + (DateProximityScore × 0.30) + (ServiceTypeScore × 0.20) + (BudgetBonus × 0.10)
```

### Factor Breakdown

| Factor | Weight | Scoring Logic |
|--------|--------|---------------|
| **Guest Count** | 40% | >100 guests = 100 pts, 50–100 = 65 pts, <50 = 30 pts |
| **Date Proximity** | 30% | <2 weeks = 100 pts, 2–4 weeks = 65 pts, >4 weeks = 30 pts |
| **Service Type** | 20% | Full service = 100 pts, Drop-off = 30 pts |
| **Budget Mentioned** | 10% | Budget provided = 100 pts, Not provided = 0 pts |

### Thresholds

| Score Range | Category | Action |
|-------------|----------|--------|
| 80–100 | High | Send detailed quote + calendar link |
| 50–79 | Medium | Send standard info + follow-up offer |
| 0–49 | Low | Send basic info |

---

## 4. Setup Process (Replication)

### Step 1 — Deploy Frontend

- Copy `catering-form.html` and `catering-form.js`
- Deploy to client domain (e.g., `order.client.com/catering/`)
- Update webhook endpoint URL in form JS

---

### Step 2 — Create n8n Webhook

- **Method:** POST
- **Path:** `CLIENT-catering-v2`
- **Mode:** `responseNode`

---

### Step 3 — Add Scoring Node

```javascript
// Lead scoring code node
const guestCount = $json.guest_count || 0;
const eventDate = new Date($json.event_date);
const now = new Date();
const daysUntil = Math.ceil((eventDate - now) / (1000 * 60 * 60 * 24));
const serviceType = $json.service_type || 'drop-off';
const hasBudget = $json.budget && $json.budget > 0;

// Guest count score
let guestScore = 30;
if (guestCount > 100) guestScore = 100;
else if (guestCount >= 50) guestScore = 65;

// Date proximity score
let dateScore = 30;
if (daysUntil <= 14) dateScore = 100;
else if (daysUntil <= 28) dateScore = 65;

// Service type score
let serviceScore = serviceType === 'full-service' ? 100 : 30;

// Budget bonus
let budgetScore = hasBudget ? 100 : 0;

// Weighted total
const totalScore = Math.round(
  (guestScore * 0.40) + (dateScore * 0.30) + (serviceScore * 0.20) + (budgetScore * 0.10)
);

return [{
  json: {
    ...$json,
    lead_score: totalScore,
    lead_category: totalScore >= 80 ? 'high' : totalScore >= 50 ? 'medium' : 'low'
  }
}];
```

---

### Step 4 — Configure Email Templates

Three templates based on score category. See Email Template Library document for full templates.

---

### Step 5 — Set Up SQLite Logging

- Create database file
- Create `catering_leads` table
- Configure n8n SQLite node

---

### Step 6 — Configure Internal Notification

- Set deli owner email for high-score alerts
- Optionally add SMS via Twilio

---

## 5. Configuration Requirements

### Credentials

| Credential | Type | Purpose |
|------------|------|---------|
| SMTP (Gmail) | n8n credential | Email delivery |
| SQLite | n8n credential | Lead storage |
| Twilio (SMS) | Optional | Internal alerts |

---

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `CATERING_WEBHOOK_PATH` | Webhook endpoint path |
| `DELI_NOTIFICATION_EMAIL` | Where internal alerts are sent |

---

## 6. Testing Procedure

| Step | Action | Verify |
|------|--------|--------|
| 1 | Submit test lead (high score) | Detailed quote email sent |
| 2 | Submit test lead (medium score) | Standard info email sent |
| 3 | Submit test lead (low score) | Basic info email sent |
| 4 | Check SQLite database | Lead row inserted |
| 5 | Check internal notification | Deli alert received |
| 6 | Submit incomplete form | Validation errors display |

---

## 7. Maintenance

- Monitor webhook activity in n8n
- Review lead scores for accuracy
- Check email delivery rates
- Update email templates as services change

---

## 8. Critical Constraints

| Constraint | Detail |
|------------|--------|
| **Response order** | Score → route → email → THEN respond to webhook |
| **Webhook mode** | Use `responseNode` mode |
| **Scoring weights** | Must total 1.0 (100%) |
| **SQLite path** | Must be accessible from n8n runtime |

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
