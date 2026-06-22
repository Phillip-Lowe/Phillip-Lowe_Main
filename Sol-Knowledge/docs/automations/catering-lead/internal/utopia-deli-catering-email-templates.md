# Utopia Deli — Catering Lead System
## Email Template Library

**Document ID:** `UD-CAT-EMAIL-001`  
**Version:** 1.0  
**Status:** Internal — Systack Only  
**Source System:** Utopia Deli (Live since 2026-06-08)  
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

## Template Rules (n8n HTML Email Node)

1. HTML field MUST start with `=` (expression evaluation)
2. Use REAL HTML tags — never escaped entities
3. Utopia Deli branding: burgundy header + gold accents
4. Variables: `{{ $json.field_name }}`

---

## Template 1: High Score (80+)

**Subject:** Your Utopia Deli Catering Inquiry — Let's Talk!

**Trigger:** Lead score ≥ 80

```html
=`
<!DOCTYPE html>
<html>
<head><style>
  body { font-family: -apple-system, sans-serif; color: #1F2937; background: #FBFCFE; }
  .header { background: #590B3F; color: #ffffff; padding: 24px; text-align: center; }
  .header h1 { color: #ffffff; margin: 0; }
  .accent { color: #D59F5C; }
  .content { background: #ffffff; padding: 24px; max-width: 600px; margin: 0 auto; }
  .highlight { background: #f5e6d0; padding: 16px; border-radius: 8px; margin: 16px 0; }
  .cta { display: inline-block; background: #AF3D4B; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; margin: 16px 0; }
  .footer { background: #590B3F; color: #f5e6d0; padding: 16px; text-align: center; font-size: 12px; }
</style></head>
<body>
  <div class="header">
    <h1>Utopia Deli Catering</h1>
    <p>It's just good food</p>
  </div>
  <div class="content">
    <h2>Thank you, {{ $json.customer_name }}!</h2>
    <p>We're excited about your <strong>{{ $json.event_type }}</strong> for <strong>{{ $json.guest_count }} guests</strong> on <strong>{{ $json.event_date }}</strong>.</p>
    
    <div class="highlight">
      <h3 class="accent">Your Event at a Glance</h3>
      <p><strong>Service:</strong> {{ $json.service_type }}</p>
      <p><strong>Guests:</strong> {{ $json.guest_count }}</p>
      <p><strong>Date:</strong> {{ $json.event_date }}</p>
      {{ $json.budget ? '<p><strong>Budget:</strong> $' + $json.budget + '</p>' : '' }}
    </div>
    
    <h3>Sample Pricing</h3>
    <p>For events of your size, catering typically ranges from <strong>$18–32 per person</strong> depending on menu selections and service style.</p>
    
    <h3>Next Steps</h3>
    <p>We'd love to discuss your event in detail. Click below to schedule a call:</p>
    <a href="https://calendly.com/utopia-deli/catering-consultation" class="cta">Schedule a Consultation</a>
    
    <h3>Payment Policy</h3>
    <p>A <strong>50% deposit</strong> secures your date. The balance is due 2 weeks before your event.</p>
    
    <p>Questions? Reply to this email or call us at (501) 551-5944.</p>
  </div>
  <div class="footer">
    Utopia Deli | Little Rock, AR | (501) 551-5944 | theutopiadeli.com
  </div>
</body>
</html>
`
```

---

## Template 2: Medium Score (50–79)

**Subject:** Your Utopia Deli Catering Inquiry — Here's What We Offer

**Trigger:** Lead score 50–79

```html
=`
<!DOCTYPE html>
<html>
<head><style>
  body { font-family: -apple-system, sans-serif; color: #1F2937; background: #FBFCFE; }
  .header { background: #590B3F; color: #ffffff; padding: 24px; text-align: center; }
  .content { background: #ffffff; padding: 24px; max-width: 600px; margin: 0 auto; }
  .cta { display: inline-block; background: #AF3D4B; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; margin: 16px 0; }
  .footer { background: #590B3F; color: #f5e6d0; padding: 16px; text-align: center; font-size: 12px; }
</style></head>
<body>
  <div class="header">
    <h1>Utopia Deli Catering</h1>
    <p>It's just good food</p>
  </div>
  <div class="content">
    <h2>Thank you, {{ $json.customer_name }}!</h2>
    <p>We received your inquiry about a <strong>{{ $json.event_type }}</strong> for <strong>{{ $json.guest_count }} guests</strong>.</p>
    
    <h3>Our Catering Services</h3>
    <ul>
      <li><strong>Full Service:</strong> On-site setup, service staff, and cleanup</li>
      <li><strong>Drop-off:</strong> Delivered ready to serve in disposable packaging</li>
      <li><strong>Custom Menus:</strong> Tailored to your event and dietary needs</li>
    </ul>
    
    <h3>Would You Like More Details?</h3>
    <p>We can provide a customized quote based on your specific needs. Click below to request one:</p>
    <a href="https://order.theutopiadeli.com/catering/" class="cta">Request Detailed Quote</a>
    
    <p>Or reply to this email with any questions. We're happy to help!</p>
  </div>
  <div class="footer">
    Utopia Deli | Little Rock, AR | (501) 551-5944 | theutopiadeli.com
  </div>
</body>
</html>
`
```

---

## Template 3: Low Score (<50)

**Subject:** Thank You for Your Utopia Deli Catering Inquiry

**Trigger:** Lead score < 50

```html
=`
<!DOCTYPE html>
<html>
<head><style>
  body { font-family: -apple-system, sans-serif; color: #1F2937; background: #FBFCFE; }
  .header { background: #590B3F; color: #ffffff; padding: 24px; text-align: center; }
  .content { background: #ffffff; padding: 24px; max-width: 600px; margin: 0 auto; }
  .footer { background: #590B3F; color: #f5e6d0; padding: 16px; text-align: center; font-size: 12px; }
</style></head>
<body>
  <div class="header">
    <h1>Utopia Deli Catering</h1>
    <p>It's just good food</p>
  </div>
  <div class="content">
    <h2>Thank you for reaching out, {{ $json.customer_name }}!</h2>
    <p>We received your inquiry and appreciate your interest in Utopia Deli Catering.</p>
    
    <p>We offer catering for events of all sizes — from intimate gatherings to large celebrations. Our menu features the same quality ingredients and flavors you know from our deli.</p>
    
    <p><strong>When your plans are firmer, we'd love to provide a detailed quote.</strong> Just reach out anytime:</p>
    <ul>
      <li>Visit: order.theutopiadeli.com/catering/</li>
      <li>Call: (501) 551-5944</li>
      <li>Email: order@theutopiadeli.com</li>
    </ul>
    
    <p>We look forward to working with you when the time is right!</p>
  </div>
  <div class="footer">
    Utopia Deli | Little Rock, AR | (501) 551-5944 | theutopiadeli.com
  </div>
</body>
</html>
`
```

---

## Template Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `{{ $json.customer_name }}` | Customer full name | Jane Smith |
| `{{ $json.customer_email }}` | Customer email | jane@example.com |
| `{{ $json.customer_phone }}` | Customer phone | 555-123-4567 |
| `{{ $json.event_type }}` | Type of event | Corporate Lunch |
| `{{ $json.guest_count }}` | Number of guests | 120 |
| `{{ $json.event_date }}` | Event date | June 28, 2026 |
| `{{ $json.service_type }}` | Service style | Full Service |
| `{{ $json.budget }}` | Budget amount (if provided) | 3500 |
| `{{ $json.special_requests }}` | Special notes | Vegetarian options |
| `{{ $json.lead_score }}` | Calculated score | 85 |

---

## Customization Notes

- **Calendar link:** Replace Calendly URL with actual scheduling link
- **Pricing ranges:** Update as menu and pricing change
- **Phone numbers:** Verify before deployment
- **Branding:** Burgundy (`#590B3F`) header, gold (`#D59F5C`) accents, rust red (`#AF3D4B`) CTAs

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
