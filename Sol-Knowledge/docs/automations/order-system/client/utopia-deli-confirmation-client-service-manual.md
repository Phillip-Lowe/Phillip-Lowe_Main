# Utopia Deli — Confirmation Email System
## Client Service Manual

**Document ID:** `UD-CONF-CSM-001`  
**Version:** 1.0  
**Status:** Live  
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

The Confirmation Email System handles what happens after a customer completes payment. When payment is confirmed through Square, the customer sees a branded success page and receives an itemized receipt email. This system ensures every paid order is acknowledged and documented.

---

## 2. How the System Works

### Step 1 — Payment Completed

Customer completes payment on Square.

---

### Step 2 — Success Page Displayed

Square redirects the customer to a branded confirmation page:

- **Pickup Orders:** `https://order.theutopiadeli.com/payment-confirmed/`
- **Meal Prep Orders:** `https://order.theutopiadeli.com/payment-confirmed-meal-prep/`

The success page shows:

- ✅ Payment Confirmed
- ✅ Order Status: Paid & Received
- Pickup time estimate (25–30 minutes for regular orders)
- Order policy (no modifications after payment)
- Contact information
- Buttons to return to homepage or order again

---

### Step 3 — Confirmation Webhook Fires

The success page automatically sends the order ID to the confirmation system.

---

### Step 4 — Receipt Email Sent

The system looks up the order details and sends an itemized receipt email containing:

- Utopia Deli branding
- Payment received confirmation
- Order ID
- Itemized list of items purchased
- Subtotal, tax, and total
- Pickup information

---

## 3. What Customers See

### Success Page (Pickup Orders)

**URL:** `https://order.theutopiadeli.com/payment-confirmed/`

Displays:

- "Payment Confirmed" heading
- Order status: Paid & Received
- Pickup time: 25–30 minutes
- Order policy reminder
- Contact information
- Homepage and Order Again buttons

---

### Success Page (Meal Prep)

**URL:** `https://order.theutopiadeli.com/payment-confirmed-meal-prep/`

Displays:

- "Payment Confirmed" heading
- Order status: Paid & Received
- Pickup: Thursday 12:30 PM – 7:30 PM
- Order policy reminder
- Contact information
- Homepage and Order Again buttons

---

### Receipt Email

Customer receives:

- Utopia Deli branded header
- "Payment received ✅" confirmation
- Order ID
- Itemized cart table with quantities and prices
- Subtotal, tax, and total
- Footer with deli address and phone

---

## 4. Confirmation Lifecycle

| Stage | Description |
|-------|-------------|
| **Payment Completed** | Customer finishes Square payment |
| **Success Page** | Branded confirmation displayed |
| **Webhook Fired** | Order ID sent to confirmation system |
| **Order Lookup** | System retrieves order from database |
| **Email Sent** | Itemized receipt delivered to customer |

---

## 5. Key Benefits

- **Immediate confirmation** — customer knows payment was received
- **Professional receipt** — itemized email for customer records
- **Deduplication** — system prevents duplicate receipt emails
- **Dual trigger** — works from both Square webhooks and frontend page load
- **No manual work** — fully automated after payment

---

## 6. Common Questions

### What if the customer doesn't see the success page?

The success page displays automatically after Square redirects. If the customer closes the browser too quickly, the receipt email still serves as confirmation.

---

### Will the customer get duplicate emails?

No — the system tracks whether a receipt has been sent and prevents duplicates.

---

### What if the receipt email doesn't arrive?

1. Check spam folder
2. Verify the email address entered at checkout was correct
3. Contact Systack support if issue persists

---

### Can the success page be customized?

Yes — contact Systack to update messaging, branding, or buttons.

---

## 7. Troubleshooting

### Success page not loading

- Check internet connection
- Verify URL is correct
- Contact Systack if persistent

---

### Receipt email not received

Possible causes:

- Email entered incorrectly at checkout
- Email in spam folder
- SMTP delivery delay

Resolution:

1. Check spam folder
2. Verify order exists in system
3. Contact Systack for manual resend if needed

---

## 8. Support

| Channel | Detail |
|---------|--------|
| **Email** | support@systack.net |
| **Phone** | (501) 274-6231 |

---

## 9. Summary

The Confirmation Email System ensures every paid order receives:

- A branded success page immediately after payment
- An itemized receipt email for customer records
- Reliable, deduplicated delivery

Customers leave with confidence that their order is confirmed and their payment was received.

---

*Document prepared by Systack for Utopia Deli.*  
*© 2026 Systack. All rights reserved.*
