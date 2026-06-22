# Utopia Deli — No-Show Prevention System
## Current State Documentation

**Document ID:** `UD-NSHOW-STATE-001`  
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

## 1. System Overview

The No-Show Prevention System reduces revenue loss from customers who book but don't show up. It combines deposit collection, automated reminders, and confirmation requirements to ensure slots are either used or released for resale.

**Status:** 🚧 PARTIAL — Core deposit + reminder infrastructure operational. Auto-release and frontend booking form not yet built.

---

## 2. What's Working ✅

### Branch 1: Booking Creation + Database Insert

- **Status:** ✅ Live
- **What it does:** Captures new booking, inserts into `systack_noshow` database
- **Database:** PostgreSQL (`bookings` table, 15 columns)
- **Auth:** Trust (localhost)

---

### Branch 2: Confirmation Email with Token

- **Status:** ✅ Live
- **What it does:** Sends confirmation email with unique token link
- **Token:** Validated on click, updates booking status
- **Email delivery:** Gmail SMTP (Support@systack.net) — delivering reliably

---

### Branch 3: Confirmation Webhook Handler

- **Status:** ✅ Live
- **What it does:** Processes customer confirmation clicks
- **Webhook:** `GET /systack-confirm-booking`
- **Action:** Validates token, updates booking status to "confirmed"

---

### Branch 4: T-24h Reminder Scheduler

- **Status:** ✅ Tested — works
- **What it does:** Sends reminder email 24 hours before booking
- **Trigger:** Schedule trigger (5-minute interval for testing)
- **Content:** Reminder + "Confirm or Cancel" button

---

### Branch 5: T-2h Urgent Reminder

- **Status:** 📋 Built, needs testing
- **What it does:** Sends final reminder 2 hours before booking
- **Trigger:** Schedule trigger (5-minute interval for testing)
- **Content:** Urgent reminder + "I'm on my way" button

---

## 3. What's Not Built 🚧

### Branch 6: Auto-Release Unconfirmed Slots

- **Status:** 📋 Queued — NOT BUILT
- **What it needs to do:**
  - Check confirmation status at T-30min before booking
  - If unconfirmed: release slot for resale
  - Notify waitlist if exists
  - Flag for follow-up

---

### Frontend Booking Form

- **Status:** 📋 Queued — NOT BUILT
- **What it needs:**
  - Customer-facing booking page at `systack.net/book`
  - Test form at `systack.net/test-book` (internal)
  - Deposit notice: "A 25% deposit is required to hold your slot"
  - Integration with Square for deposit collection

---

## 4. Technical Details

### Database

| Field | Detail |
|-------|--------|
| **Name** | `systack_noshow` |
| **Type** | PostgreSQL |
| **Host** | localhost (Phillip's MacBook) |
| **Auth** | Trust (no password for local) |
| **Table** | `bookings` (15 columns) |

---

### n8n Workflows

| Workflow | Trigger | Status |
|----------|---------|--------|
| Create Booking | `POST /systack-create-booking` | Active |
| Confirm Handler | `GET /systack-confirm-booking` | Active |
| 24h Reminder | Schedule (5 min test) | Active |
| 2h Reminder | Schedule (5 min test) | Active (needs test) |

---

### Deposit Rules (Configured)

| Service Value | Deposit % | Min Deposit | Max Deposit |
|---------------|-----------|-------------|-------------|
| < $50 | 100% | $10 | $50 |
| $50–$150 | 50% | $20 | $75 |
| > $150 | 25% | $37.50 | No max |

---

## 5. Completion Criteria

- [x] Booking created in database
- [x] Confirmation email sent
- [x] Confirmation link works (token validated)
- [x] T-24h reminder sends
- [ ] T-2h reminder tested with real booking window
- [ ] Auto-release logic built and tested
- [ ] Frontend booking form deployed
- [ ] Test/prod environment separation

---

## 6. Known Gaps

| Gap | Impact | Priority |
|-----|--------|----------|
| No auto-release | Unconfirmed slots not freed for resale | P1 |
| No frontend form | Can't accept customer bookings yet | P1 |
| T-2h untested | Final reminder reliability unknown | P2 |
| No test/prod separation | Testing affects production data | P2 |
| No waitlist system | Released slots not offered to waitlist | P3 |

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
