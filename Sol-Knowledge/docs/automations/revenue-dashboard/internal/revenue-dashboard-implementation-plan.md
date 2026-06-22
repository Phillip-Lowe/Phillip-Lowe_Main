# Revenue Dashboard — Implementation Plan

**Automation ID:** `revenue-dashboard`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Build Phases

### Phase 1: Data Aggregation Pipeline (3 hours)

**Tasks:**

1. Build n8n Cron workflow (runs every 15 minutes)
2. Aggregate from all data sources:

```sql
-- Daily revenue
SELECT DATE(created_at), SUM(total_cents) 
FROM bookings 
WHERE status = 'completed' 
GROUP BY DATE(created_at);

-- Top services
SELECT service_type, COUNT(*) 
FROM bookings 
GROUP BY service_type 
ORDER BY COUNT(*) DESC LIMIT 5;

-- Peak hours
SELECT EXTRACT(HOUR FROM slot_datetime) as hour, COUNT(*) 
FROM bookings 
GROUP BY hour 
ORDER BY COUNT(*) DESC;

-- New vs returning
SELECT 
  CASE WHEN total_visits = 1 THEN 'new' ELSE 'returning' END,
  COUNT(*)
FROM customer_profiles
GROUP BY 1;
```

3. Store aggregated results in `dashboard_metrics` table

---

### Phase 2: Dashboard API (2 hours)

**Tasks:**

1. Build simple REST API:
   - `GET /dashboard/today` — today's metrics
   - `GET /dashboard/weekly` — 7-day trends
   - `GET /dashboard/monthly` — 30-day deep dive
2. JSON response format
3. Cache results (15-min refresh)

---

### Phase 3: Web UI (4 hours)

**Tasks:**

1. Build three dashboard views in HTML/CSS/JS
2. **Today View:**
   - Revenue counter (big number)
   - Booking count
   - Slot utilization gauge
   - No-show alert
3. **Weekly View:**
   - Revenue line chart (7 days)
   - Booking bar chart
   - Top services table
4. **Monthly View:**
   - Revenue by week
   - Customer retention curve
   - Upsell + referral performance

---

### Phase 4: Access Control (1 hour)

**Tasks:**

1. Simple token-based auth
2. Owner view: all metrics
3. Staff view: today only (no financials)
4. Public view: none

---

## 2. Timeline

| Phase | Est. Hours |
|-------|------------|
| Phase 1 | 3 |
| Phase 2 | 2 |
| Phase 3 | 4 |
| Phase 4 | 1 |
| **Total** | **10 hours (~2 weeks)** |

---

## 3. Dependencies

| System | Data Provided |
|--------|--------------|
| Booking System | Revenue, services, slots |
| CRM Lite | Customer profiles, retention |
| Upsell Engine | Upsell performance |
| Referral Engine | Referral attribution |
| No-Show System | No-show rate |

---

## 4. Success Metrics

| Metric | Target |
|--------|--------|
| Dashboard load time | < 2 seconds |
| Data freshness | < 15 minutes |
| Owner weekly check rate | > 3x/week |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
