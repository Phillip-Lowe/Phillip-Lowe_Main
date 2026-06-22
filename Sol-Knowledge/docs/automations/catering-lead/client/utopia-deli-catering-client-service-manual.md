# Utopia Deli — Catering Lead System
## Client Service Manual

**Document ID:** `UD-CAT-CSM-001`  
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

The Utopia Deli Catering Lead System captures event and catering inquiries through a 5-step form on your website. Each submission is automatically scored, categorized, and responded to — so high-value leads get immediate attention while standard inquiries receive appropriate follow-up information.

This system eliminates the back-and-forth of phone and email lead qualification, responding to every inquiry within minutes.

---

## 2. How the System Works

### Step 1 — Customer Submits Inquiry

Customers visit:
**[https://order.theutopiadeli.com/catering/](https://order.theutopiadeli.com/catering/)**

They complete a 5-step form:

| Step | Information Collected |
|------|----------------------|
| 1 | Event type and details |
| 2 | Guest count and event date |
| 3 | Service style preference |
| 4 | Contact information (name, email, phone) |
| 5 | Special requests and budget |

---

### Step 2 — Automatic Lead Scoring

The system immediately scores each lead based on:

- **Guest count** (40% weight) — larger events score higher
- **Date proximity** (30% weight) — sooner events score higher
- **Service type** (20% weight) — full-service scores higher than drop-off
- **Budget mentioned** (10% weight) — bonus for providing budget

**Score thresholds:**

| Score | Category | Response |
|-------|----------|----------|
| 80+ | High | Detailed quote + calendar link |
| 50–79 | Medium | Standard info + follow-up offer |
| Below 50 | Low | Basic info + "let us know if dates change" |

---

### Step 3 — Automatic Email Response

Within minutes of submission, the customer receives an email tailored to their lead score:

- **High-score leads:** Detailed catering information, sample pricing, and a link to schedule a call
- **Medium-score leads:** Standard catering overview with an offer to follow up
- **Low-score leads:** Basic information with encouragement to reach out when plans are firmer

---

### Step 4 — Internal Notification

The deli receives an internal notification for every lead, with high-score leads flagged for priority personal follow-up.

---

### Step 5 — Lead Storage

All leads are stored in a database for:

- Future reference and follow-up
- Tracking conversion rates
- Identifying repeat inquiries

---

## 3. What You See

### High-Score Lead Notification

Example:

```
NEW CATERING LEAD (HIGH SCORE: 85)
Customer: Jane Smith
Email: jane@example.com
Phone: 555-123-4567
Event: Corporate Lunch
Guests: 120
Date: June 28, 2026
Service: Full Service
Budget: $3,500
Notes: Vegetarian options needed
```

---

### Customer Auto-Response (High Score)

Customer receives:

- Personalized greeting
- Catering menu overview
- Sample pricing for their guest count
- Link to schedule a consultation call
- Contact information

---

## 4. Lead Lifecycle

| Stage | Description |
|-------|-------------|
| **Form Submitted** | Customer completes 5-step catering form |
| **Lead Scored** | System calculates score based on event details |
| **Auto-Response Sent** | Tailored email sent within minutes |
| **Internal Notification** | Deli notified with score and details |
| **Personal Follow-Up** | High-score leads flagged for direct contact |

---

## 5. Payment Policy

For catering bookings:

- **50% deposit** required to secure the event date
- **Balance due** 2 weeks before the event
- **Events within 2 weeks:** Full payment required upfront

This policy is communicated in the auto-response email for high and medium-score leads.

---

## 6. Key Benefits

- **Immediate response** — every lead gets a reply within minutes, not hours or days
- **Automatic prioritization** — high-value leads are flagged instantly
- **Consistent follow-up** — no leads fall through the cracks
- **Reduced manual work** — no phone tag or email back-and-forth for basic info
- **Complete lead history** — all inquiries stored for reference

---

## 7. Common Questions

### How quickly does the customer get a response?

Typically within 2–5 minutes of submitting the form.

---

### Can I see all catering leads?

Yes — leads are stored in the system database. Contact Systack for access or a regular report.

---

### What if a lead score seems wrong?

Scoring is based on the information the customer provides. If a lead seems misclassified:

1. Review the submitted details
2. Follow up personally regardless of score
3. Report persistent issues to Systack

---

### Can I customize the auto-response emails?

Yes — email templates can be updated. Contact Systack with requested changes.

---

### What happens if the form stops working?

1. Check the catering page at https://order.theutopiadeli.com/catering/
2. Contact Systack support immediately
3. Leads submitted during downtime may need manual follow-up

---

## 8. Troubleshooting

### Not receiving lead notifications

- Check email inbox and spam folder
- Verify notification settings with Systack

---

### Auto-responses not sending

Possible cause:

- n8n workflow issue
- Email credential expired

Resolution:

1. Contact Systack support
2. Manually follow up with any leads received during the outage

---

### Form not submitting

- Check internet connection
- Verify all required fields are completed
- Try a different browser
- Contact Systack if persistent

---

## 9. Support

| Channel | Detail |
|---------|--------|
| **Email** | support@systack.net |
| **Phone** | (501) 274-6231 |

---

## 10. Summary

The Utopia Deli Catering Lead System provides:

- Automated lead capture from your website
- Instant scoring and prioritization
- Tailored auto-responses within minutes
- Complete lead history and tracking
- Reduced manual qualification work

Every catering inquiry gets an immediate, appropriate response — high-value opportunities are never missed.

---

*Document prepared by Systack for Utopia Deli.*  
*© 2026 Systack. All rights reserved.*
