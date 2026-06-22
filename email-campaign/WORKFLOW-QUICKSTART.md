# Utopia Deli — Weekly Email Campaign Workflow

## Quick Reference

### Workflow File
`utopia-deli-weekly-email-campaign.json` — Import into n8n

### How It Works
```
Daily 9AM Trigger → Set Day & Week → Route by Day (Switch) → [Day Template] → Send Email
```

### Nodes (10 total)

| # | Node | Type | What It Does |
|---|------|------|-------------|
| 1 | Daily 9AM Trigger | Schedule | Fires every day at 9:00 AM |
| 2 | Set Day & Week | Code | Calculates `campaign_day` + `week_number` |
| 3 | Route by Day | Switch | Routes to correct day template |
| 4 | Monday — Item of the Week | Code | Item spotlight template |
| 5 | Tuesday — Catering | Code | Auto-rotating catering (3 themes) |
| 6 | Wednesday — Meal Prep Close | Code | Deadline urgency template |
| 7 | Thursday — Reopen + Deli | Code | Reopen + daily specials |
| 8 | Friday — Weekend Kickoff | Code | Weekend vibes template |
| 9 | Saturday — Weekend Reminder | Code | "Open today" template |
| 10 | Sunday — Week Preview | Code | Menu preview + Monday lunch |
| 11 | Send Email | Email | Sends to contact list |

### Setup Steps

1. **Import** `utopia-deli-weekly-email-campaign.json` into n8n
2. **Configure** the "Send Email" node with your email credentials (Gmail or SendGrid)
3. **Connect** your contact data source BEFORE the "Set Day & Week" node:
   - Option A: Google Sheets node → reads contact list
   - Option B: Database node → queries contacts
   - Option C: HTTP Request → fetches from CRM
4. **Test** by manually executing with a test contact
5. **Activate** the workflow

### Weekly Maintenance

Each week, update the **SWAP ZONE** in each Code node:

| Node | What to Update |
|------|---------------|
| Monday | `itemOfTheWeek` — hero image, headline, body, alsoTry |
| Tuesday | Nothing (auto-rotates) — just verify images |
| Wednesday | `thisWeekMenu.bowls` — current week's bowls |
| Thursday | `nextWeekBowls` + `dailySpecials` |
| Friday | `weekendContent.features` + optional special |
| Saturday | `todayFeature` + `quickMenu` |
| Sunday | `nextWeekMenu` + `mondayLunch` + optional `thisWeek` |

### Schedule Reference

| Event | Time |
|-------|------|
| Meal prep orders CLOSE | Wednesday 12:00 PM |
| Meal prep orders REOPEN | Thursday 8:00 PM |
| Meal prep pickup | Thursday 12:30–7:30 PM |
| Walk-up deli hours | Monday–Saturday 12:30–7:30 PM |

### Tuesday Rotation

| Week | Theme | Subject |
|------|-------|---------|
| 1 | Events & Parties | 🎉 Planning an Event? |
| 2 | Corporate | 🏢 Feed Your Team |
| 3 | Pickup Platters | 🍽️ Pickup Platters |

Auto-cycles using `week_number % 3` — no manual switching.

### Testing

```bash
# Manual trigger (from n8n UI or API)
curl -X POST http://localhost:5678/api/v1/workflows/{id}/execute \
  -H "X-N8N-API-KEY: $N8N_API_KEY"
```

---

**Built:** 2026-06-22
**For:** The Utopia Deli · 801 S Chester St, Little Rock, AR 72202
