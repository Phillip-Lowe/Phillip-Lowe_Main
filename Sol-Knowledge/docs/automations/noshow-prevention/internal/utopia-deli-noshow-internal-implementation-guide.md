# Utopia Deli — No-Show Prevention System
## Internal Implementation Guide

**Document ID:** `UD-NSHOW-IMPL-001`  
**Version:** 1.0  
**Status:** Internal — Systack Only  
**Source System:** Utopia Deli (Partial — Phase 1 complete, Phase 2 in progress)  
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
Booking Made
  → Deposit Required? → No → Proceed Normally
  → Yes → Collect Deposit via Square
    → Store in DB: status="pending"
      → Timer: T-24h → Send Reminder + Confirm/Cancel Button
        → Timer: T-2h → Send Final Reminder + "I'm on my way" Button
          → Customer Confirms?
            → Yes → Status: "confirmed" → Proceed
            → No → T-30min → Auto-release slot → Notify waitlist
```

---

## 2. Core Components

### Database

| Field | Detail |
|-------|--------|
| **Name** | `systack_noshow` |
| **Type** | PostgreSQL |
| **Host** | localhost |
| **Auth** | Trust (no password for local) |
| **Table** | `bookings` (15 columns) |

**Key columns:**

| Column | Type | Purpose |
|--------|------|---------|
| `booking_id` | TEXT PK | Unique booking identifier |
| `customer_email` | TEXT | For reminders |
| `customer_phone` | TEXT | Optional SMS |
| `slot_datetime` | TIMESTAMP | When booking is scheduled |
| `deposit_amount` | INTEGER | In cents |
| `status` | TEXT | pending/confirmed/unconfirmed/released |
| `confirmation_token` | TEXT | Unique token for confirm/cancel links |
| `reminder_24h_sent` | BOOLEAN | Deduplication |
| `reminder_2h_sent` | BOOLEAN | Deduplication |

---

### n8n Workflows

| Workflow | Trigger | Status |
|----------|---------|--------|
| Create Booking | `POST /systack-create-booking` | ✅ Active |
| Confirm Handler | `GET /systack-confirm-booking` | ✅ Active |
| 24h Reminder | Schedule Trigger | ✅ Active |
| 2h Reminder | Schedule Trigger | 📋 Built, needs test |
| Auto-Release | Schedule Trigger | 🚧 NOT BUILT |

---

## 3. Setup Process (Replication)

### Step 1 — Create Database

```sql
CREATE TABLE bookings (
  booking_id TEXT PRIMARY KEY,
  customer_name TEXT,
  customer_email TEXT,
  customer_phone TEXT,
  service_type TEXT,
  slot_datetime TIMESTAMP,
  deposit_amount INTEGER,
  total_value INTEGER,
  status TEXT DEFAULT 'pending',
  confirmation_token TEXT,
  reminder_24h_sent BOOLEAN DEFAULT FALSE,
  reminder_2h_sent BOOLEAN DEFAULT FALSE,
  confirmed_at TIMESTAMP,
  released_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### Step 2 — Configure Deposit Collection

- Square API integration for deposit holds
- Deposit rules based on service value:

| Service Value | Deposit % | Min |
|---------------|-----------|-----|
| < $50 | 100% | $10 |
| $50–$150 | 50% | $20 |
| > $150 | 25% | $37.50 |

---

### Step 3 — Build Booking Webhook

**Endpoint:** `POST /CLIENT-create-booking`

Receives booking data, collects deposit, inserts into DB with `status="pending"`.

---

### Step 4 — Build Confirmation Handler

**Endpoint:** `GET /CLIENT-confirm-booking?token=xxx`

Validates token, updates status:

- `status = "confirmed"` on confirm
- `status = "cancelled"` on cancel

---

### Step 5 — Configure Reminder Schedulers

**T-24h Reminder:**

- Cron: runs periodically, checks for bookings 24h out
- Sends email with Confirm/Cancel buttons
- Sets `reminder_24h_sent = TRUE`

**T-2h Reminder:**

- Cron: runs periodically, checks for bookings 2h out
- Sends email with "I'm on my way" button
- Sets `reminder_2h_sent = TRUE`

---

### Step 6 — Build Auto-Release (NOT YET BUILT)

**Logic:**

```javascript
// For each booking where:
//   slot_datetime <= NOW() + 30 minutes
//   AND status = "pending"
//   AND reminder_2h_sent = TRUE

// Action:
//   status = "released"
//   released_at = NOW()
//   Notify waitlist if exists
```

---

## 4. Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NOSHOW_DEPOSIT_PERCENT` | 25 | Default deposit % |
| `NOSHOW_MIN_DEPOSIT` | 1000 | Min deposit in cents ($10) |
| `NOSHOW_REMINDER_24H` | true | Enable 24h reminder |
| `NOSHOW_REMINDER_2H` | true | Enable 2h reminder |
| `NOSHOW_AUTO_RELEASE` | true | Auto-release unconfirmed |
| `NOSHOW_RELEASE_BUFFER` | 30 | Minutes before slot |

---

## 5. Testing

| Step | Action | Verify |
|------|--------|--------|
| 1 | Create test booking | Row in DB, status=pending |
| 2 | Click confirm link | Status changes to confirmed |
| 3 | Wait for T-24h window | Reminder email sent |
| 4 | Click cancel link | Status changes to cancelled |
| 5 | Don't confirm | Auto-release fires at T-30min |

---

## 6. Critical Constraints

| Constraint | Detail |
|------------|--------|
| **Token uniqueness** | Confirmation tokens must be cryptographically random |
| **Deduplication** | Check `reminder_sent` flags before sending |
| **Time zone** | All times in America/Chicago |
| **Deposit handling** | Deposits are holds, not charges — credited toward total |

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
