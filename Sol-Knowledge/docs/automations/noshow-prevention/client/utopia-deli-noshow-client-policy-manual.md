# Utopia Deli — No-Show Prevention System
## Client Policy Manual

**Document ID:** `UD-NSHOW-POLICY-001`  
**Version:** 1.0  
**Status:** Live (Policies Active)  
**Prepared for:** Utopia Deli, Little Rock, AR  
**Prepared by:** Systack (systack.net)  
**Date:** 2026-06-16  
**Support:** support@systack.net | (501) 274-6231

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

## 1. Overview

This document defines the deposit, cancellation, and confirmation policies for Utopia Deli bookings. These policies are enforced by the No-Show Prevention System to protect revenue and ensure fair slot allocation.

---

## 2. Deposit Policy

### Deposit Requirement

A deposit is required to secure all bookings. The deposit amount is calculated based on the total service value.

### Deposit Schedule

| Service Value | Deposit Percentage | Minimum Deposit | Maximum Deposit |
|---------------|-------------------|-----------------|-----------------|
| Under $50 | 100% of total | $10.00 | Full amount |
| $50 – $150 | 50% of total | $20.00 | $75.00 |
| Over $150 | 25% of total | $37.50 | No maximum |

### Deposit Collection

- Deposits are collected via **Square** at the time of booking
- The deposit is a **hold on the card**, not a separate charge
- The full service amount is charged at fulfillment
- Deposit amount is credited toward the final total

### Deposit Disclosure

Customers see the following at booking:

> "A deposit is required to hold your slot. The deposit amount is credited toward your final total. See cancellation policy for refund terms."

---

## 3. Cancellation Policy

### Cancellation Windows

| Cancellation Timing | Deposit Refund | Reschedule Option |
|---------------------|---------------|-------------------|
| More than 24 hours before | **Full refund** | Available |
| Less than 24 hours before | **Deposit forfeited** | Can reschedule (deposit transfers) |
| No-show (no cancellation) | **Deposit forfeited** | No reschedule |

### How to Cancel

Customers can cancel through:

- **Confirmation email:** Click "Cancel" button in any reminder or confirmation email
- **Phone:** Call (501) 551-5944
- **Email:** order@theutopiadeli.com

### Automatic Cancellation

If a customer does not confirm their booking:

- **T-24h reminder:** Sent 24 hours before booking with "Confirm or Cancel" button
- **T-2h reminder:** Sent 2 hours before booking with "I'm on my way" button
- **T-30min auto-release:** If still unconfirmed 30 minutes before the booking, the slot is automatically released

---

## 4. Confirmation Policy

### Confirmation Requirement

Customers must confirm their booking to keep their slot:

1. **Booking confirmation email:** Sent immediately after deposit is collected
2. **T-24h reminder:** Sent 24 hours before the booking — customer must confirm
3. **T-2h final reminder:** Sent 2 hours before — last chance to confirm

### What Happens If Not Confirmed

| Stage | Action |
|-------|--------|
| After booking | Slot is "pending" — held for customer |
| T-24h no confirm | Reminder sent — slot still held |
| T-2h no confirm | Final reminder sent — slot still held |
| T-30min no confirm | **Slot auto-released** — available for others |

### How to Confirm

Customers confirm by clicking the **"Confirm"** button in any reminder or confirmation email. The button links to a unique token that validates their booking.

---

## 5. Refund Policy

### Deposit Refunds

| Scenario | Refund |
|----------|--------|
| Cancel > 24h before | Full deposit refunded |
| Cancel < 24h before | Deposit forfeited |
| No-show | Deposit forfeited |
| Deli cancels | Full deposit refunded + apology |
| Reschedule > 24h before | Deposit transfers to new date |
| Reschedule < 24h before | Deposit transfers (one-time courtesy) |

### Refund Processing

- Refunds are processed through Square
- Typically appear on customer's card within 5–10 business days
- Confirmation email sent when refund is initiated

---

## 6. Customer Communication

### What Customers See at Booking

> "By booking, you agree to our deposit and cancellation policy. A [amount] deposit will be collected to hold your slot. Cancel more than 24 hours ahead for a full deposit refund."

### What Reminder Emails Say

**T-24h:**
> "Your booking is tomorrow! Please confirm you'll be there or cancel if your plans have changed. Cancel > 24 hours ahead for a full deposit refund."

**T-2h:**
> "Your booking is in 2 hours! Click 'I'm on my way' to confirm. Unconfirmed slots may be released."

---

## 7. Policy Exceptions

### Deli-Initiated Cancellations

If Utopia Deli must cancel a booking:

- Full deposit refund (no forfeiture)
- Apology email with reschedule offer
- Priority slot for rescheduled booking

### Emergency Exceptions

Case-by-case review for:

- Medical emergencies
- Severe weather
- Family emergencies

Contact Systack to process exception refunds.

---

## 8. Policy Changes

### How to Update Policies

1. Document requested changes
2. Systack reviews impact on system configuration
3. Update environment variables (deposit percentages, time windows)
4. Update customer-facing policy text
5. Deploy changes

### Configuration Variables

| Variable | Current Value | Description |
|----------|--------------|-------------|
| `NOSHOW_DEPOSIT_PERCENT` | 25 | Default deposit percentage |
| `NOSHOW_MIN_DEPOSIT` | 1000 ($10.00) | Minimum deposit in cents |
| `NOSHOW_REMINDER_24H` | true | Enable 24h reminder |
| `NOSHOW_REMINDER_2H` | true | Enable 2h reminder |
| `NOSHOW_AUTO_RELEASE` | true | Auto-release unconfirmed |
| `NOSHOW_RELEASE_BUFFER` | 30 | Minutes before slot to release |

---

## 9. Summary

| Policy | Key Point |
|--------|-----------|
| **Deposit** | Required for all bookings, credited toward total |
| **Cancellation** | Full refund > 24h, forfeited < 24h or no-show |
| **Confirmation** | Required at booking, T-24h, and T-2h |
| **Auto-Release** | Unconfirmed slots released 30min before booking |
| **Exceptions** | Case-by-case for emergencies |

These policies protect the deli's revenue while giving customers clear, fair terms.

---

*Document prepared by Systack for Utopia Deli.*  
*© 2026 Systack. All rights reserved.*
