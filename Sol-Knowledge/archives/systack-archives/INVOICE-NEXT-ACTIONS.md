# Invoice Pipeline — Next Actions

**Started:** 2026-06-08 07:07 CDT
**Last Updated:** 2026-06-16 03:00 CDT

---

## DONE ✅

### Task 0: n8n Email Trigger (Previously blocked)
- **Status:** Gmail app password was revoked by Google on 2026-06-08
- **Resolution:** System pivoted to API-first approach — invoices uploaded via web form
- **Current flow:** IMAP trigger → extract PDF → forward to parser API
- **Blocker resolved:** Parser works end-to-end, pipeline tested successfully

### Task 1: Web Dashboard — DONE ✅
- **Built:** 2026-06-16 03:00 CDT
- **Files:** `invoice_dashboard_api.py` (API, port 8766), `invoice-dashboard.html` (frontend, port 8768)
- **Features:** Invoice list with search/filter/sort, detail modal with line items, aging report, vendor directory, CSV export
- **Access:** `http://localhost:8768/invoice-dashboard.html`

---

## REMAINING TASKS (Priority Order)

### Task 2: Find 3 Beta Testers — NEXT
**Status:** ⏳ Ready to start (dashboard exists now)
**Target:** Local Little Rock businesses receiving 5-20 invoices/month
**Offer:** 30-day free trial for feedback
**Potential revenue:** $49-$399/mo per customer
**Effort:** 1-2 days

---

### Task 3: Add QuickBooks/Xero Export
**Status:** ⏳ Not started
**Priority:** HIGH — accountants won't adopt without this
**Options:**
- CSV export (2-3 days) — basic CSV already works via `/api/export/csv`
- QuickBooks API (1-2 weeks)
- Xero OAuth API (1-2 weeks)

**Revenue impact:** Unlocks accountant white-label channel ($99/mo per accountant)

---

### Task 4: Set Up Stripe Billing
**Status:** ⏳ Not started
**Products:**
- Starter: $49/mo (50 invoices)
- Professional: $149/mo (250 invoices + dashboard)
- Business: $399/mo (unlimited + API)
- Systack Private bundle: $999/mo

**Effort:** 1-2 hours
**Prerequisite:** Dashboard exists ✅

---

## RECOMMENDED SEQUENCE

```
TODAY ────▶ Find 3 beta testers (Task 2)
TOMORROW ──▶ Set up Stripe + onboard first paying customer
THIS WEEK ──▶ QuickBooks/Xero export (Task 3)
```

---

## Key Metrics to Track

| Metric | Target | Current |
|--------|--------|---------|
| Invoices processed | 100+ | 95 |
| Beta testers acquired | 3 | 0 |
| First paying customer | 1 | 0 |
| Accuracy rate | > 95% | TBD |
| AR total | — | $1,174,555.38 |
| AP total | — | $951,819.74 |
| Net position | — | +$222,735.64 |

---

**Last Updated:** 2026-06-16 03:00 CDT