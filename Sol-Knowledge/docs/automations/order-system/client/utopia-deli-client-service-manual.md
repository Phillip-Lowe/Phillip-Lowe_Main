# Utopia Deli — Online Ordering System
## Client Service Manual

**Document ID:** `UD-CSM-001`  
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
| Headers, CTAs | Navy | `#001a2d` |
| Navy Light | Navy Light | `#002845` |
| Secondary accents | Teal | `#007da9` |
| Primary buttons, links | Cyan | `#00a1db` |
| Gradients | Cyan Bright | `#00c5e0` |
| Backgrounds | Gray 50 | `#f8fafc` |
| Cards | Gray 100 | `#f1f5f9` |
| Borders | Gray 200 | `#e2e8f0` |
| Muted text | Gray 400 | `#94a3b8` |
| Body text | Gray 600 | `#475569` |
| Headings | Gray 800 | `#1e293b` |
| Success | Green | `#22c55e` |
| Error | Red | `#ef4444` |
| Accent highlights | Purple | `#8b5cf6` |

---

## 1. Overview

The Utopia Deli Online Ordering System allows customers to:

- Place orders directly from your website
- Select menu items and modifiers (extras, changes, etc.)
- Choose a pickup time
- Pay securely through Square
- Receive confirmation after payment

This system enables faster ordering, reduces manual work, and eliminates third‑party delivery fees.

---

## 2. How the System Works

### Step 1 — Customer Places Order

Customers visit:
**[https://order.theutopiadeli.com/pickup-order/](https://order.theutopiadeli.com/pickup-order/)**

They:

- Select items from the menu
- Add modifiers (e.g., extra mayo)
- Choose a pickup time
- Enter contact information

---

### Step 2 — Order Processing

The system automatically:

- Validates the order
- Calculates subtotal, tax, and total
- Generates a unique Order ID

**Example:**
```
UD-20260616-143022-4782
```

---

### Step 3 — Payment Redirect

- The system generates a secure Square payment link
- The customer remains on the order page
- The customer is redirected to Square to complete payment

**No email is sent at this stage.**

---

### Step 4 — Payment Completion

- Customer completes payment in Square
- Square sends confirmation to the system

---

### Step 5 — Order Fulfillment Trigger

After payment is confirmed:

- Kitchen receives the order notification
- Customer receives a confirmation email

**No order is sent to the kitchen before payment is complete.**

---

## 3. What You See

### New Order Notification (Kitchen)

Example:

```
NEW ORDER: UD-20260616-143022-4782
Customer: John Smith
Phone: 555-123-4567
Pickup: 2:30 PM
Items:
• Italian Sub (x1)
• Chips (x2)
Total: $11.49
Notes: Extra mayo
```

---

### Customer Confirmation Email

Customer receives:

- Order number
- Pickup time
- Itemized order list
- Total paid

There is no order status or tracking button.

---

## 4. Order Lifecycle

| Stage | Description |
|-------|-------------|
| **Order Submitted** | Customer completes form |
| **Payment Redirect** | Customer is sent to Square |
| **Payment Completed** | Square confirms payment |
| **Kitchen Notification** | Sent after payment only |
| **Confirmation Email** | Sent to customer |

**Invariant:** Orders are only created after payment is complete.

---

## 5. Business Hours Logic

Operating hours:

- Monday–Saturday: 12:30 PM – 7:30 PM
- Sunday: Closed

System behavior:

- "ASAP" orders are automatically set to current time + 30 minutes
- Orders outside business hours are blocked

---

## 6. Key Benefits

- Reduced processing fees (approximately 3.2%)
- Faster order completion (average under 60 seconds)
- Full ownership of customer data
- No dependency on third-party delivery platforms

---

## 7. Common Questions

### What if a customer does not pay?

- The order is not created
- The kitchen receives nothing
- The process stops at the payment stage

---

### Can orders be edited?

- Not automatically
- Customers must call in changes

---

### Where are orders stored?

Orders may be stored in:

- Local databases (SQLite or file-based storage)
- Google Sheets
- PostgreSQL

Storage depends on system configuration.

---

### What if a customer says they paid but no confirmation was received?

Steps:

1. Check the payment in Square
2. If payment is confirmed:
   - The system may be delayed
   - The notification may arrive late

Known issue:

- Square outages or webhook delays can delay or prevent notifications

Action:

- Treat confirmed payment as valid
- Notify kitchen manually if necessary

---

## 8. Troubleshooting

### Not receiving orders

- Check email inbox and spam folder
- Check kitchen notification device (SMS or tablet)

---

### Payment completed but no order received

Possible cause:

- Square webhook delay or outage

Resolution:

1. Verify payment in Square
2. Notify kitchen manually
3. Complete order fulfillment

---

### Incorrect order details

- Usually caused by customer input
- Review menu and form configuration if issues persist

---

## 9. Support

| Channel | Detail |
|---------|--------|
| **Email** | support@systack.net |
| **Phone** | (501) 274-6231 |

---

## 10. Summary

The Utopia Deli Online Ordering System provides:

- Direct online ordering
- Secure payment processing
- Automated order handling
- Reduced operational overhead
- Improved customer experience

Orders are only created after payment is complete, ensuring accuracy and eliminating unpaid or invalid orders.

---

*Document prepared by Systack for Utopia Deli.*  
*© 2026 Systack. All rights reserved.*
