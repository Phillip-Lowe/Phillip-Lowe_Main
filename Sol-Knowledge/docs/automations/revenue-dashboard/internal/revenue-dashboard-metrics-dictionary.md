# Revenue Dashboard — Metrics Dictionary

**Automation ID:** `revenue-dashboard`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Revenue Metrics

| Metric | Definition | Formula | Source |
|--------|-----------|---------|--------|
| **Daily Revenue** | Total completed booking value today | `SUM(total_cents) WHERE DATE = today AND status = 'completed'` | Bookings DB |
| **Weekly Revenue** | Total completed booking value this week | `SUM(total_cents) WHERE week = current` | Bookings DB |
| **Monthly Revenue** | Total completed booking value this month | `SUM(total_cents) WHERE month = current` | Bookings DB |
| **Avg Booking Value** | Mean revenue per booking | `total_revenue / booking_count` | Bookings DB |
| **Revenue by Service** | Revenue breakdown by service type | `SUM(total_cents) GROUP BY service_type` | Bookings DB |
| **Revenue per Hour** | Revenue efficiency by time slot | `SUM(total_cents) GROUP BY hour` | Bookings DB |

---

## 2. Customer Metrics

| Metric | Definition | Formula | Source |
|--------|-----------|---------|--------|
| **Total Customers** | Unique customers ever | `COUNT(DISTINCT customer_id)` | CRM Lite |
| **New Customers (Month)** | First visit this month | `COUNT WHERE first_visit IN current_month` | CRM Lite |
| **Returning Customers** | Customers with 2+ visits | `COUNT WHERE total_visits >= 2` | CRM Lite |
| **Retention Rate** | % of customers who return within 30 days | `returned_within_30d / total_first_visits` | CRM Lite |
| **Churn Rate** | % of customers inactive > 90 days | `inactive_90d / total_customers` | CRM Lite |
| **Avg Visits/Customer** | Mean lifetime visits | `SUM(total_visits) / total_customers` | CRM Lite |
| **Customer LTV** | Average lifetime value | `SUM(total_spent) / total_customers` | CRM Lite |

---

## 3. Operations Metrics

| Metric | Definition | Formula | Source |
|--------|-----------|---------|--------|
| **Slot Utilization** | % of available slots filled | `filled_slots / total_slots` | Calendar |
| **Peak Hours** | Hours with most bookings | `COUNT GROUP BY hour ORDER BY count DESC` | Bookings DB |
| **No-Show Rate** | % of bookings not fulfilled | `unconfirmed / total_bookings` | No-Show System |
| **Avg Service Duration** | Mean time per service | `AVG(service_duration)` | Bookings DB |
| **Booking Lead Time** | Avg days between booking and service | `AVG(slot_date - booking_date)` | Bookings DB |

---

## 4. Growth Metrics

| Metric | Definition | Formula | Source |
|--------|-----------|---------|--------|
| **Conversion Rate** | % of visitors who book | `bookings / page_visits` | Analytics + Bookings |
| **Upsell Rate** | % of bookings with add-ons | `bookings_with_upsells / total_bookings` | Upsell Engine |
| **Referral Rate** | % of bookings via referral | `referral_bookings / total_bookings` | Referral Engine |
| **Review Avg** | Mean star rating | `AVG(rating)` | Review System |
| **Month-over-Month Growth** | Revenue change vs last month | `(this_month - last_month) / last_month` | Bookings DB |

---

## 5. Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Daily Revenue | < 50% of 30-day avg | < 25% of 30-day avg |
| No-Show Rate | > 10% | > 20% |
| Slot Utilization | < 70% | < 50% |
| New Customers (Week) | 0 for 3+ days | 0 for 7+ days |
| Review Avg | < 4.0 | < 3.5 |

---

## 6. Data Refresh Schedule

| Data Type | Refresh Frequency |
|-----------|-------------------|
| Today metrics | Every 15 minutes |
| Weekly trends | Every hour |
| Monthly deep dive | Every 6 hours |
| Customer LTV | Daily |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
