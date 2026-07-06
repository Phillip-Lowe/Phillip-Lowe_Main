# Usage Metrics + Billing Tracking — Added 2026-07-01

## Status: ✅ DEPLOYED — Database + API + Wired into SAOS Dashboard

---

## What Was Built

### Database Schema (systack_memory)

**Table: `usage_metrics`**
| Column | Type | Description |
|--------|------|-------------|
| id | serial PK | Auto-increment |
| client_id | int FK → saos_clients | Which client |
| metric_type | varchar(50) | Category: api_call, task_created, task_completed, chat_message, agent_spawned, deliverable_uploaded, workflow_run, email_sent, sms_sent |
| metric_name | varchar(255) | Specific name: endpoint path, service name, etc. |
| quantity | int default 1 | Usually 1, can be batch count |
| metadata | jsonb | Extra context: { endpoint: "GET", agent: "dooby" } |
| recorded_at | timestamptz | Auto now() |

**Table: `usage_daily_rollup`** (auto-maintained via trigger)
| Column | Description |
|--------|-------------|
| client_id + metric_type + metric_date | Composite unique key |
| total_count | Number of calls |
| total_quantity | Sum of quantities |

**View: `v_current_month_usage`**
Pre-aggregated current month data per client.

### API Endpoints (Command Center)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/fleet/usage` | PIN | Usage summary by metric type, top clients, daily trend (last 30 days) |
| POST | `/api/fleet/usage/record` | PIN | Record a metric from external service |

Query params for GET:
- `client_id` — filter to one client
- `days` — lookback period (default 30)
- `type` — filter to one metric_type

### SAOS Customer Dashboard Integration

**Helper function:** `track_usage(client_id, metric_type, metric_name, quantity, metadata)`
- Silently fails on error (doesn't break user-facing requests)
- Logs to stdout for debugging

**Wired into:**
| Endpoint | Event Tracked |
|----------|---------------|
| `POST /api/tasks/request` | `task_created` with service name |
| `POST /api/chat/conversations/:id/messages` | `chat_message` from client |
| `POST /api/internal/deliverables/upload` | `deliverable_uploaded` with filename + size |

### Test Results

```bash
# Recorded test metric
POST /api/fleet/usage/record
→ { "id": 1, "message": "Usage recorded" }

# Query confirmed rollup working
GET /api/fleet/usage
→ {
  "summary": [{ "metric_type": "api_call", "calls": 1, "total": 1 }],
  "by_client": [{ "customer_name": "Test User", "metric_type": "api_call", "calls": 1, "total": 1 }],
  "daily_trend": [{ "day": "2026-07-01", "metric_type": "api_call", "total": 1 }]
}
```

---

## Files Changed

| File | Change |
|------|--------|
| `systack-command-center/migrations/add_usage_metrics.sql` | New — full schema + trigger + view |
| `systack-command-center/api.py` | Added `/api/fleet/usage` GET + `/api/fleet/usage/record` POST |
| `Systack/content/saos/saos-data/customer-dashboard/api.py` | Added `track_usage()` helper + 3 wiring points |

---

## Next Steps

1. **Wire remaining endpoints:** agent spawn, workflow run, email sent
2. **Build usage UI:** Add Usage tab to SAOS customer dashboard showing "You've used X of Y this month"
3. **Add billing limits:** Soft caps per tier, alert at 80%
4. **Stripe integration:** Connect usage to actual billing events
5. **Export:** Monthly usage reports per client (CSV/PDF)

---

## Commit
`7f0d63d` — Add usage_metrics table + billing tracking endpoints
