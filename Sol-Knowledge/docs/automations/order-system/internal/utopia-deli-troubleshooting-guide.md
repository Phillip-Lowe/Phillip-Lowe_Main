# Utopia Deli — Online Ordering System
## Troubleshooting Guide

**Document ID:** `UD-TS-001`  
**Version:** 1.0  
**Status:** Internal — Systack Only  
**Source System:** Utopia Deli (Live since 2026-06-03)  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

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

## 1. No Orders Received

**Cause:**

- Webhook not firing
- Frontend issue

**Fix:**

- Test webhook manually with curl
- Check CORS headers on webhook response
- Verify frontend POST URL matches webhook path
- Check n8n workflow is Active

---

## 2. Payment Link Not Working

**Cause:**

- Square API failure

**Fix:**

- Verify Square API credentials in n8n
- Check `SQUARE_ACCESS_TOKEN` is valid
- Check `SQUARE_LOCATION_ID` is correct
- Regenerate link by resubmitting order
- Check Square API status: squareup.com/status

---

## 3. Payment Completed but No Order

**Cause:**

- Square webhook delay or outage

**Fix:**

1. Verify payment in Square Dashboard
2. Manually notify kitchen with order details
3. Retry webhook if possible
4. Check n8n confirmation workflow is Active
5. Check Square webhook subscription is configured

---

## 4. Email Not Sending

**Cause:**

- SMTP issue

**Fix:**

- Check SMTP credentials in n8n
- Verify Gmail access (app password may be revoked)
- Check spam folder for missing emails
- Test SMTP connection from n8n
- Verify email node configuration (HTML field starts with `=`)

---

## 5. Incorrect Totals

**Cause:**

- Schema mismatch (cents vs dollars)

**Fix:**

- Ensure cents conversion in Normalize node
- Validate tax calculation (9.52% AR rate)
- Check floating point tolerance (±$0.02)
- Verify Square receives amounts in cents

---

## 6. System Crashes in Code Node

**Cause:**

- Unsupported JavaScript syntax

**Fix:**

- Remove ES6 spread operators (`...obj`)
- Replace with `Object.assign({}, obj1, obj2)`
- Use simple function expressions (no arrow functions in some contexts)
- Wrap `JSON.parse` in try/catch
- Check n8n Code node for syntax errors in execution log

---

## 7. Attachments Not Found (Invoice Crossover Issue)

**Cause:**

- Wrong binary key reference

**Fix:**

- Use `attachment_0` (NOT `attachment_`)
- Verify binary key matches n8n node output
- Check IMAP format is "resolved" (not shallow)

---

## Quick Reference

| Symptom | First Check | Escalate If |
|---------|------------|-------------|
| No orders | n8n workflow Active? | > 1 hour during business hours |
| Payment fails | Square credentials valid? | > 3 consecutive failures |
| No confirmation | SMTP credentials valid? | > 5 failed sends |
| Page down | DNS resolving? GitHub Pages up? | > 30 min downtime |
| Wrong totals | Cents conversion working? | Every occurrence |

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
