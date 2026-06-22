---
name: systack-email-brander
description: "Generate SyStack-branded HTML emails with navy/cyan gradient palette, responsive layout, and dynamic variable substitution for any automation workflow."
---

# SyStack Email Brander

Generate branded HTML emails for any SyStack automation. Consistent navy header, cyan CTA, gray body, navy footer. Used across all client emails — booking confirmations, invoices, alerts, marketing, onboarding.

## When to Use
- Building ANY email node in n8n or API
- Client needs branded transactional emails
- Creating email templates for new automations
- Updating existing email branding to match SyStack palette

## Brand Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Navy | `#001a2d` | Header background, footer |
| Navy Light | `#002845` | Gradient end |
| Teal | `#007da9` | Accent elements |
| Cyan | `#00a1db` | Primary CTA button |
| Cyan Bright | `#00c5e0` | Hover states |
| Gray Body | `#f8fafc` | Email body background |
| Text Dark | `#1e293b` | Body text |
| Text Muted | `#475569` | Secondary text |

## Template Structure

```html
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f8fafc;font-family:Arial,sans-serif;">
  <!-- NAVY HEADER -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#001a2d 0%,#002845 100%);">
    <tr><td align="center" style="padding:30px 20px;">
      <img src="https://systack.net/images/logo-white.png" alt="SyStack" style="height:40px;"/>
    </td></tr>
  </table>
  
  <!-- BODY -->
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td align="center" style="padding:30px 20px;">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
        <tr><td style="padding:40px 30px;">
          <h1 style="color:#001a2d;font-size:24px;margin:0 0 20px;">{{ headline }}</h1>
          <p style="color:#475569;font-size:16px;line-height:1.6;margin:0 0 20px;">{{ body_text }}</p>
          
          <!-- CYAN CTA -->
          <a href="{{ cta_url }}" style="display:inline-block;background:linear-gradient(135deg,#00a1db 0%,#00c5e0 100%);color:#ffffff;text-decoration:none;padding:14px 32px;border-radius:6px;font-weight:600;font-size:16px;">{{ cta_text }}</a>
        </td></tr>
      </table>
    </td></tr>
  </table>
  
  <!-- NAVY FOOTER -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#001a2d;">
    <tr><td align="center" style="padding:20px;color:#94a3b8;font-size:12px;">
      © {{ year }} SyStack. Built for your business.<br/>
      <a href="{{ unsubscribe_url }}" style="color:#94a3b8;">Unsubscribe</a>
    </td></tr>
  </table>
</body>
</html>
```

## Critical Rules

1. **HTML field must start with `=`** — n8n expression evaluation: `={{ $json.html_body }}`
2. **Real HTML tags only** — Never escaped entities (`&lt;div&gt;` breaks rendering)
3. **Inline styles only** — Email clients strip `<style>` blocks
4. **Table-based layout** — Divs fail in Outlook/Gmail
5. **600px max width** — Desktop readability, mobile scales down

## Variable Substitution

n8n uses `{{ $json.field_name }}` syntax:

```javascript
// In n8n Code node, build email HTML:
const html = `
<h1>Hello {{ $json.customer_name }}</h1>
<p>Your {{ $json.service }} is scheduled for {{ $json.appointment_time }}</p>
<a href="{{ $json.confirm_link }}">Confirm Appointment</a>
`;
return [{ json: { html_body: html } }];
```

## Common Templates

### Booking Confirmation
- Headline: "Your appointment is confirmed"
- Body: Service, date/time, location, what to expect
- CTA: "View Details" / "Reschedule"

### Invoice Received
- Headline: "New invoice from {{ vendor }}"
- Body: Amount, due date, items summary
- CTA: "View Invoice" / "Pay Now"

### Payment Confirmed
- Headline: "Payment received — thank you!"
- Body: Amount, transaction ID, next steps
- CTA: "View Receipt"

### Welcome / Onboarding
- Headline: "Welcome to SyStack"
- Body: What happens next, timeline, contact info
- CTA: "Book Setup Call"

## Testing

Always send test email before marking complete:
1. Use test recipient (your own email)
2. Check Gmail, Outlook, Apple Mail
3. Verify on mobile
4. Confirm links work

## Reference

Full template fleet: `memory/2026-06-11-systack-email-template-fleet-reference.md`
