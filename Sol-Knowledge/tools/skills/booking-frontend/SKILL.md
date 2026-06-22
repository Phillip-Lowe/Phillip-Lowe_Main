---
name: booking-frontend
description: "Build responsive HTML booking/catering/order forms with Square payment integration, webhook submission to n8n, config-driven menu systems, and mobile-first design."
---

# Booking Frontend

Build complete HTML booking/order/catering forms with payment integration. Config-driven menu → form validation → webhook to n8n → confirmation page.

## When to Use
- Client needs online ordering (restaurant, retail, services)
- Appointment/calendar booking system
- Catering/event inquiry form with scoring
- Any "fill form → pay → confirm" workflow

## Architecture

```
index.html
  ├── config.js — Menu data, prices, modifiers, hours
  ├── menu-data.js — Category/items structure
  ├── order-form.js — Validation + cart + checkout
  └── webhook POST → n8n → Square payment link → confirmation
```

## Config-Driven Menu

```javascript
// config.js
window.CONFIG = {
  businessName: "Utopia Deli",
  logo: "../images/logo.png",
  squareLocationId: "L...",
  webhookUrl: "https://api.systack.net/webhook/order",
  pickupHours: {
    mon: { open: "07:00", close: "21:00" },
    tue: { open: "07:00", close: "21:00" },
    // ... etc
  },
  // Global gate: block ordering outside hours
  hoursGateEnabled: true,
  // Payment
  paymentMethod: "square", // or "stripe", "manual"
  taxRate: 0.08,
  // Modifiers
  modifiers: {
    "sandwich": ["white bread", "wheat bread", "lettuce", "tomato", "onion", "pickles", "mayo", "mustard"],
    "salad": ["ranch", "italian", "balsamic", "caesar"],
    "sides": ["fries", "chips", "fruit cup"],
    // ... etc
  }
};

// menu-data.js
const MENU_DATA = [
  {
    category: "Signature Sandwiches",
    items: [
      { name: "The Ultimate Club", price: 12.99, description: "Turkey, ham, bacon...", image: "club.jpg" },
      { name: "Grilled Chicken", price: 11.99, modifiers: ["sandwich", "sides"] },
    ]
  },
  {
    category: "Fresh Salads",
    items: [
      { name: "Caesar Salad", price: 9.99, modifiers: ["salad"] },
    ]
  }
];
```

## Hours Gate Pattern

```javascript
function isWithinPickupHours() {
  const now = new Date();
  const days = ['sun','mon','tue','wed','thu','fri','sat'];
  const day = days[now.getDay()];
  const hours = CONFIG.pickupHours[day];
  if (!hours) return false;
  
  const [openH, openM] = hours.open.split(':').map(Number);
  const [closeH, closeM] = hours.close.split(':').map(Number);
  const current = now.getHours() * 60 + now.getMinutes();
  const open = openH * 60 + openM;
  const close = closeH * 60 + closeM;
  
  return current >= open && current <= close;
}
```

## Form Validation

```javascript
// Required fields
const required = ['customer_name', 'customer_phone', 'pickup_time'];
for (let field of required) {
  if (!document.getElementById(field).value.trim()) {
    showError(`${field} is required`);
    return false;
  }
}

// Phone format
const phone = document.getElementById('customer_phone').value.replace(/\D/g,'');
if (phone.length !== 10) {
  showError('Please enter a valid 10-digit phone number');
  return false;
}

// Cart not empty
if (cart.items.length === 0) {
  showError('Please add items to your cart');
  return false;
}
```

## Webhook POST

```javascript
async function submitOrder(orderData) {
  const response = await fetch(CONFIG.webhookUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...orderData,
      source: window.location.hostname,
      timestamp: new Date().toISOString()
    })
  });
  
  if (!response.ok) {
    throw new Error(`Webhook failed: ${response.status}`);
  }
  
  const result = await response.json();
  window.location.href = result.paymentLink || result.redirectUrl || '/success.html';
}
```

## Square Payment Integration

```javascript
// Generate Square payment link via n8n
// n8n receives order → calculates total → creates Square Checkout URL → returns to frontend

// Frontend receives:
// { paymentLink: "https://checkout.square.site/...", orderId: "ORD-001" }

// Redirect customer:
window.location.href = result.paymentLink;

// Customer pays on Square → Square webhook → n8n → confirmation email
```

## Catering Form (Multi-Step)

```javascript
// 5-step catering form with lead scoring
const CATERING_STEPS = [
  { id: 'contact', fields: ['name', 'email', 'phone'] },
  { id: 'event', fields: ['event_type', 'guest_count', 'event_date'] },
  { id: 'menu', fields: ['service_style', 'budget_per_person'] },
  { id: 'details', fields: ['dietary_restrictions', 'special_requests'] },
  { id: 'review', fields: [] } // Summary + submit
];

// Lead scoring
function scoreLead(data) {
  let score = 0;
  if (data.guest_count >= 50) score += 20;
  if (data.budget_per_person >= 15) score += 15;
  if (data.event_date && new Date(data.event_date) > new Date()) score += 10;
  if (data.dietary_restrictions) score += 5; // Detail-oriented client
  return score;
}
```

## Common Gotchas

| Issue | Fix |
|-------|-----|
| Logo 404 after moving page to subdirectory | Use `../images/logo.png` relative path |
| Hours gate blocking legitimate orders | Check timezone (America/Chicago default) |
| Payment link not generating | Verify Square credentials in n8n |
| Cart items disappearing on refresh | Use `localStorage` for cart persistence |
| Modifier selections not saving | Store per-item in cart array |
| Mobile layout broken | Use viewport meta + responsive CSS |

## File Structure

```
pickup-order/
  ├── index.html          # Main order page
  ├── config-v2.js        # Business config (hours, prices, webhooks)
  ├── menu-data.js        # Menu categories and items
  ├── order-form.js       # Cart, validation, checkout logic
  └── privacy.html        # Privacy policy

catering/
  ├── index.html          # 5-step catering form
  └── catering-form.js    # Lead scoring + webhook
```

## Testing Checklist

- [ ] Form submits successfully
- [ ] Validation blocks incomplete submissions
- [ ] Payment link redirects correctly
- [ ] Confirmation page displays order details
- [ ] n8n receives webhook payload
- [ ] Email sent with correct order details
- [ ] Mobile responsive (iPhone SE width)
- [ ] Hours gate works (test after hours)
- [ ] Logo and images load correctly

## Reference

- Full catering system: `CATERING-DEPLOYMENT-STATUS.md`
- Order system: `docs/automations/order-system/`
- n8n workflows: `SOL n8n templates/`
