---
name: catering-lead-system
description: "Build complete catering/event lead capture with multi-step forms, lead scoring, automated email responses, SQLite logging, and n8n workflow integration."
---

# Catering Lead System

Build complete catering/event lead capture: multi-step form → validation → webhook → scoring → auto-email → SQLite database → dashboard.

## When to Use
- Restaurant/venue needs catering inquiry system
- Event-based business (weddings, corporate, parties)
- High-value leads requiring qualification
- Need automated lead nurturing before human follow-up

## Architecture

```
Customer fills form →
    ├── Step 1: Contact info
    ├── Step 2: Event details
    ├── Step 3: Menu preferences
    ├── Step 4: Budget/details
    └── Step 5: Review + Submit
        ↓
WebSocket/POST to n8n webhook
    ↓
n8n processes:
    ├── Validate data
    ├── Calculate lead score
    ├── Write to SQLite
    ├── Send auto-reply email
    └── Alert business owner
```

## Lead Scoring Algorithm

```javascript
function scoreLead(data) {
  let score = 0;
  
  // Event size (highest weight)
  if (data.guest_count >= 100) score += 30;
  else if (data.guest_count >= 50) score += 20;
  else if (data.guest_count >= 25) score += 10;
  else score += 5;
  
  // Budget (per person)
  const budget = parseFloat(data.budget_per_person) || 0;
  if (budget >= 25) score += 20;
  else if (budget >= 15) score += 15;
  else if (budget >= 10) score += 10;
  else score += 5;
  
  // Event date proximity
  const eventDate = new Date(data.event_date);
  const daysUntil = Math.ceil((eventDate - new Date()) / (1000 * 60 * 60 * 24));
  if (daysUntil <= 14 && daysUntil >= 0) score += 15; // Urgent
  else if (daysUntil <= 60) score += 10; // Planning ahead
  else if (daysUntil > 60) score += 5;
  
  // Event type
  const highValueEvents = ['wedding', 'corporate', 'graduation'];
  if (highValueEvents.includes(data.event_type?.toLowerCase())) score += 10;
  
  // Dietary restrictions detail (engagement signal)
  if (data.dietary_restrictions && data.dietary_restrictions.length > 20) score += 5;
  
  return Math.min(score, 100);
}
```

## Score Ranges

| Score | Priority | Action |
|-------|----------|--------|
| 80-100 | 🔴 Hot | Immediate call + priority email |
| 60-79 | 🟡 Warm | Email within 2 hours |
| 40-59 | 🟢 Qualified | Email within 4 hours |
| 20-39 | ⚪ Cold | Email within 24 hours |
| 0-19 | ❄️ Unqualified | Auto-reply only, flag for review |

## Database Schema

```sql
CREATE TABLE catering_leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    event_type TEXT,
    guest_count INTEGER,
    event_date TEXT,
    venue TEXT,
    budget_per_person REAL,
    service_style TEXT,
    dietary_restrictions TEXT,
    special_requests TEXT,
    lead_score INTEGER,
    priority TEXT,
    status TEXT DEFAULT 'new', -- new, contacted, quoted, booked, lost
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Auto-Reply Email Template

```html
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
  <h2 style="color:#001a2d;">Thank you for your catering inquiry!</h2>
  
  <p>Hi {{ customer_name }},</p>
  
  <p>We've received your request for {{ event_type }} catering on {{ event_date }} 
     for {{ guest_count }} guests.</p>
  
  <p><strong>What happens next:</strong></p>
  <ol>
    <li>Our team will review your details within 24 hours</li>
    <li>We'll prepare a custom proposal based on your preferences</li>
    <li>A team member will call you to discuss options</li>
  </ol>
  
  <p>Expected response time: {{ response_time }}</p>
  
  <p>Questions? Reply to this email or call us at {{ phone }}.</p>
  
  <p>Best,<br>{{ business_name }} Team</p>
</body>
</html>
```

## Critical Rules

1. **Guest count validation**: Must be numeric, ≥ 1
2. **Phone format**: Strip non-digits, validate length (10 digits US)
3. **Budget**: Allow text entry but normalize to number for scoring
4. **Event date**: Must be in future, warn if < 2 weeks
5. **Auto-reply**: Send immediately, personalized with form data

## Quick Start

```bash
# 1. Create database
python3 -c "
import sqlite3
conn = sqlite3.connect('catering_leads.db')
conn.execute(open('catering_schema.sql').read())
conn.commit()
"

# 2. Deploy form
# Upload catering/ directory to hosting

# 3. Configure n8n webhook
# Import: utopia-deli-catering-v4.json

# 4. Test
# Fill form → verify email received → check database
```

## Testing Checklist

- [ ] All 5 steps work sequentially
- [ ] Back button preserves data
- [ ] Score calculates correctly for different inputs
- [ ] Auto-reply email received
- [ ] Database records inserted
- [ ] Business owner alert sent
- [ ] Edge cases handled (1 guest, past date, etc.)
- [ ] Mobile responsive
- [ ] Hours gate (if applicable)

## Gotchas

| Issue | Fix |
|-------|-----|
| Score not calculating | Check guest_count parsed as int |
| Auto-reply not sending | Verify n8n workflow ACTIVE |
| Database locked | Use connection pool, close after write |
| Phone validation failing | Strip all non-digits before checking length |
| Past date accepted | Add client-side + server-side validation |

## Files

- `catering/index.html` — 5-step form
- `catering/catering-form.js` — Validation + scoring logic
- `CATERING-PLAN.md` — Full architecture
- `CATERING-DEPLOYMENT-STATUS.md` — Current status
- `utopia-deli-catering-v4.json` — n8n workflow

## Reference

- Full system: `docs/automations/catering-lead/`
- Client manual: `docs/automations/catering-lead/client/`
- Internal guide: `docs/automations/catering-lead/internal/`
- Scoring algorithm: `docs/automations/catering-lead/internal/utopia-deli-catering-scoring-algorithm.md`
