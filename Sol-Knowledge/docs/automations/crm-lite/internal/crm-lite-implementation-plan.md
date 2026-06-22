# CRM Lite — Implementation Plan

**Automation ID:** `crm-lite`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Build Phases

### Phase 1: Database Schema + Profile Creation (2 hours)

**Tasks:**

1. Create `customer_profiles` table in Postgres
2. On first booking: create profile with basic info
3. On each subsequent booking: update profile counters
4. Auto-detect: preferred service (most frequent), preferred time (most common slot)

---

### Phase 2: Profile Aggregation (3 hours)

**Tasks:**

1. Build aggregation queries:

```sql
-- Preferred service
SELECT service_type, COUNT(*) as count 
FROM bookings 
WHERE customer_id = $1 
GROUP BY service_type 
ORDER BY count DESC LIMIT 1;

-- Average spend
SELECT AVG(total_cents) FROM bookings WHERE customer_id = $1;

-- Preferred time
SELECT slot_time, COUNT(*) as count 
FROM bookings 
WHERE customer_id = $1 
GROUP BY slot_time 
ORDER BY count DESC LIMIT 1;
```

2. Run aggregation after each booking completion
3. Update profile with computed preferences

---

### Phase 3: Personalization API (2 hours)

**Tasks:**

1. Build simple API endpoint: `GET /profile?customer_id=xxx`
2. Returns profile JSON for use by other automations
3. Used by: Smart Rebooking, Upsell Intelligence, Booking Form

---

### Phase 4: Booking Form Integration (2 hours)

**Tasks:**

1. On return visit (email recognized):
   - Pre-fill service selection ("Same as last time?")
   - Suggest preferred time slot
   - Show "You usually add [upsell]" prompt
2. Reduce booking friction for repeat customers

---

### Phase 5: Privacy + Data Retention (1 hour)

**Tasks:**

1. Implement data deletion endpoint
2. Auto-anonymize profiles inactive > 24 months
3. Document data handling for GDPR/CCPA compliance
4. Customer-accessible data export

---

## 2. Timeline

| Phase | Est. Hours |
|-------|------------|
| Phase 1 | 2 |
| Phase 2 | 3 |
| Phase 3 | 2 |
| Phase 4 | 2 |
| Phase 5 | 1 |
| **Total** | **10 hours (~2 weeks)** |

---

## 3. Dependencies

| System | Relationship |
|--------|-------------|
| Booking System | Primary data source |
| Smart Rebooking | Consumes profile data |
| Upsell Intelligence | Consumes profile data |
| Referral Engine | Updates referral count |

---

## 4. Success Metrics

| Metric | Target |
|--------|--------|
| Profile coverage | > 90% of customers |
| Repeat booking speed | 30% faster |
| Personalization accuracy | > 80% (preferred service correct) |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
