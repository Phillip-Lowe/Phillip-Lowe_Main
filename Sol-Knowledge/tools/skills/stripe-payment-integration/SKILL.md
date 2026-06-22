---
name: stripe-payment-integration
description: "Integrate Stripe Checkout and Payment Links with n8n workflows, handle webhooks for payment confirmation, and manage product catalogs for SAAS and one-time purchases."
---

# Stripe Payment Integration

Connect Stripe payments to n8n workflows. Product catalog → Checkout → Webhook → Confirmation → Fulfillment.

## When to Use
- Client needs to collect payments online
- SAOS tier upgrades or addon purchases
- One-time service fees (setup, consultation)
- Subscription billing for ongoing services
- Any "pay before we proceed" workflow

## Payment Flow

```
Customer clicks "Pay Now"
    ↓
Stripe Checkout (hosted page)
    ↓
Customer completes payment
    ↓
Stripe webhook → n8n
    ↓
n8n confirms payment
    ↓
Trigger fulfillment:
    ├── Send confirmation email
    ├── Activate service
    ├── Update database
    └── Notify admin
```

## Product Catalog Setup

### Via Stripe Dashboard
1. Products → Add product
2. Name: "SAOS Starter Monthly"
3. Price: $299.00
4. Recurring: Monthly (optional)
5. Save → Copy price ID (looks like `price_1ABC...`)

### Via API
```bash
curl https://api.stripe.com/v1/products \
  -u sk_live_...: \
  -d name="SAOS Business" \
  -d description="AI automation suite for businesses"

curl https://api.stripe.com/v1/prices \
  -u sk_live_...: \
  -d product=prod_ABC... \
  -d unit_amount=79900 \
  -d currency=usd \
  -d "recurring[interval]"=month
```

## Payment Link Generation

### Static (Stripe Dashboard)
- Product → More options → Create payment link
- Copy URL: `https://buy.stripe.com/test_abc123`

### Dynamic (n8n/API)
```javascript
// n8n Code node
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

const session = await stripe.checkout.sessions.create({
  payment_method_types: ['card'],
  line_items: [{
    price: $json.price_id,
    quantity: 1
  }],
  mode: 'payment', // or 'subscription'
  success_url: 'https://systack.net/success?session_id={CHECKOUT_SESSION_ID}',
  cancel_url: 'https://systack.net/cancel',
  metadata: {
    customer_email: $json.email,
    service_type: $json.service
  }
});

return [{ json: { payment_url: session.url } }];
```

## Webhook Handling

### n8n Webhook Configuration
```json
{
  "trigger": "Webhook",
  "path": "stripe-webhook",
  "method": "POST",
  "responseMode": "responseNode"
}
```

### Stripe Webhook Setup
1. Stripe Developers → Webhooks → Add endpoint
2. URL: `https://api.systack.net/webhook/stripe`
3. Events: `checkout.session.completed`, `invoice.paid`, `payment_intent.succeeded`
4. Copy signing secret

### Webhook Processing
```javascript
// Verify signature first (security)
const sig = $request.headers['stripe-signature'];
const event = stripe.webhooks.constructEvent($request.body, sig, webhookSecret);

// Route by event type
switch(event.type) {
  case 'checkout.session.completed':
    // Activate service, send welcome email
    return [{ json: { status: 'paid', customer: event.data.object.customer_email }}];
  case 'invoice.paid':
    // Subscription renewed
    return [{ json: { status: 'renewed' }}];
  case 'payment_intent.payment_failed':
    // Alert admin, retry logic
    return [{ json: { status: 'failed', error: event.data.object.last_payment_error }}];
}
```

## SAOS Tier Pricing

| Tier | Monthly | Setup Fee | Users | Payment Link |
|------|---------|-----------|-------|--------------|
| Starter | $299 | $199 | 1-3 | `price_starter` |
| Growth | $599 | $299 | 4-10 | `price_growth` |
| Business | $799 | $399 | 11-25 | `price_business` |
| Enterprise | Custom | Custom | 25+ | Contact sales |

## Critical Rules

1. **Webhook validates before responding** — Never respond 200 before processing
2. **Sequential flow** — Process → Validate → Email → THEN respond
3. **Store event IDs** — Prevent duplicate processing (idempotency)
4. **Test with Stripe CLI** — `stripe listen --forward-to localhost:5678`
5. **Live vs Test keys** — Test mode for development, live for production

## Testing

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Listen to webhooks locally
stripe listen --forward-to http://localhost:5678/webhook/stripe

# Trigger test event
stripe trigger checkout.session.completed

# Test payment
stripe open https://buy.stripe.com/test_abc123
```

## Enterprise Integration

For high-volume clients:
- Stripe Connect (platform payouts)
- Custom invoicing via API
- Metered billing (usage-based)
- ACH / bank transfer

## Files

- `saos-products/STRIPE-CATALOG.md` — Full product catalog
- `saos-products/STRIPE-CREATION-CHECKLIST.md` — Setup steps
- `saos/stripe-payment-links-workflow.json` — n8n workflow
- `stripe_enterprise_integration.py` — Enterprise API wrapper

## Gotchas

| Issue | Fix |
|-------|-----|
| Webhook 400 errors | Verify signing secret, check event type |
| Payment not activating | Check n8n workflow is ACTIVE |
| Duplicate charges | Check event ID not already processed |
| Test key in production | Use environment variables, validate key prefix |
| Currency mismatch | Ensure USD for US customers |

## Reference

- Stripe docs: https://stripe.com/docs
- Test cards: https://stripe.com/docs/testing
- API ref: https://stripe.com/docs/api
