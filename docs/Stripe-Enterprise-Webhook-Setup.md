# Stripe Enterprise Webhook Setup Guide

**Status:** ⚠️ REQUIRES MANUAL STEPS
**Created:** 2026-06-19
**Workflow ID:** 77b76TUhNvZyAu5U

---

## What's Already Done ✅

| Task | Status |
|------|--------|
| Stripe product created | ✅ `prod_UjXtLBNuOjpGRF` |
| Prices configured | ✅ Monthly $799, Annual $7,990 |
| Payment links generated | ✅ Direct checkout URLs |
| n8n workflow created | ✅ Extracts data, queues DEPLOY task |
| Postgres credentials | ✅ Connected to Systack Postgres |

---

## Manual Steps Required

### Step 1: Activate n8n Workflow

1. Open: https://n8n.systack.net/workflow/77b76TUhNvZyAu5U
2. Click the **"Inactive"** toggle in top-right corner → switches to **"Active"**
3. The webhook URL becomes live: `https://n8n.systack.net/webhook/stripe-enterprise-checkout`

### Step 2: Configure Stripe Webhook Endpoint

1. Go to: https://dashboard.stripe.com/webhooks
2. Click **"Add endpoint"**
3. Endpoint URL: `https://n8n.systack.net/webhook/stripe-enterprise-checkout`
4. Events to listen to:
   - ✅ `checkout.session.completed`
5. Click **"Add endpoint"**
6. Copy the **Signing secret** (starts with `whsec_`)

### Step 3: Set Environment Variable

```bash
# Add to ~/.zshrc or ~/.bash_profile
export STRIPE_WEBHOOK_SECRET="whsec_your_signing_secret_here"

# Reload shell
source ~/.zshrc
```

### Step 4: Verify Webhook Works

```bash
# Test with curl
curl -X POST https://n8n.systack.net/webhook/stripe-enterprise-checkout \
  -H "Content-Type: application/json" \
  -d '{
    "type": "checkout.session.completed",
    "data": {
      "object": {
        "id": "test_session",
        "customer_details": {"email": "test@example.com", "name": "Test Corp"},
        "metadata": {"tier": "enterprise", "client_id": "TEST", "billing": "monthly"},
        "subscription": "sub_test"
      }
    }
  }'
```

Expected response:
```json
{"status": "success", "message": "Provisioning queued", "task_id": 123}
```

---

## Payment Links (Ready to Use Now)

| Plan | URL |
|------|-----|
| **Monthly** | https://buy.stripe.com/9B6fZafZL0FN7oIff887K0e |
| **Annual** | https://buy.stripe.com/dRm14gcNz74beRa7MG87K0f |

Embed on your website:
```html
<a href="https://buy.stripe.com/9B6fZafZL0FN7oIff887K0e" class="btn-primary">
  Subscribe Monthly — $799/mo
</a>
<a href="https://buy.stripe.com/dRm14gcNz74beRa7MG87K0f" class="btn-secondary">
  Pay Annually — $7,990/yr (2 months free)
</a>
```

---

## End-to-End Flow After Setup

```
Customer clicks payment link
        │
        ▼
Stripe Checkout (hosted by Stripe)
        │
        ▼
Payment complete → Stripe POSTs webhook
        │
        ▼
n8n receives checkout.session.completed
        │
        ▼
Extracts customer data + metadata
        │
        ▼
Queues DEPLOY task in Postgres
        │
        ▼
Bridge polls every 30s → picks up task
        │
        ▼
Vultr API creates VPS
        │
        ▼
Cloud-init installs services
        │
        ▼
VPS ready → webhook to n8n
        │
        ▼
Customer receives credentials email
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Webhook returns 404 | Workflow not active — toggle in n8n UI |
| Webhook returns 400 | Check Stripe signature header |
| Task not queued | Verify Postgres credentials in n8n node |
| Bridge doesn't pick up | Check bridge logs: `tail -f logs/saos-bridge.log` |

---

*Setup guide generated 2026-06-19. For issues, check memory/2026-06-19-enterprise-stripe-integration.md*
