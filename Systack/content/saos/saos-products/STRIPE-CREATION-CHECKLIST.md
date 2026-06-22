# Stripe Product Creation Checklist

## Products to Create (in Stripe Dashboard)

### SAOS Fleet (Self-Managed)

| # | Product Name | Price | Type | Billing |
|---|-------------|-------|------|---------|
| 1 | **SAOS Personal+ Monthly** | $199/mo | Recurring | Monthly |
| 2 | **SAOS Personal+ Annual** | $1,999/yr | Recurring | Yearly |
| 3 | **SAOS Business Fleet Monthly** | $299/mo | Recurring | Monthly |
| 4 | **SAOS Enterprise Fleet Monthly** | $799/mo | Recurring | Monthly |

### Systack Services (Done-For-You)

| # | Product Name | Price | Type | Billing |
|---|-------------|-------|------|---------|
| 5 | **Systack Accelerate 10K Monthly** | $249/mo | Recurring | Monthly |
| 6 | **Systack Accelerate 25K Monthly** | $349/mo | Recurring | Monthly |
| 7 | **Systack Private Monthly** | $799/mo | Recurring | Monthly |
| 8 | **Systack Accelerate Setup** | $2,500 | One-time | Immediate |
| 9 | **Systack Private Setup** | $4,500 | One-time | Immediate |

## Existing Products (Keep)

| Button ID | Product | Price | Action |
|-----------|---------|-------|--------|
| `buy_btn_1TfU3M1WicviTxiilXTJNolL` | SAOS Business Fleet | $299/mo | ✅ Keep |
| `buy_btn_1TfU1m1WicviTxiikPepeQO4` | SAOS Enterprise Fleet | $799/mo | ✅ Keep |

## Deprecated (Replace)

| Button ID | Old Product | New Product | Action |
|-----------|------------|------------|--------|
| `buy_btn_1TfU451WicviTxiig1l8JYjR` | SAOS Solo $149 | SAOS Personal+ $199 | ❌ Replace |

## Publishable Key

```
pk_live_51Tckdx1WicviTxii6uKLsxzQENJqWDNxt8Zqmst9YKBQ4F0KSn7VpuR7PZTGRQXJMv42NwimR1kcIdOxElznzIsM000DBc6pKp
```

## Steps to Create in Stripe

1. Go to https://dashboard.stripe.com/products
2. Click "Add product"
3. Fill in:
   - Name: [Product Name]
   - Description: [from below]
   - Price: [Amount]
   - Billing period: [Monthly/Yearly/One-time]
4. Click "Save product"
5. Create Payment Link
6. Copy Payment Link URL and Buy Button ID
7. Paste into this doc

## Product Descriptions

### SAOS Personal+ Monthly ($199)
> Your own AI agent on a 16GB dedicated server. Local models, your data never leaves. Includes email triage, calendar management, task reminders, document summarization, multi-device sync, voice interaction, and local dashboard.

### SAOS Personal+ Annual ($1,999)
> Same as Personal+ Monthly. Save $389 when billed annually.

### SAOS Business Fleet ($299)
> Multi-agent team for your business. Everything in Personal+ plus team Slack workspace, invoice processing, lead qualification, customer support drafting. Up to 5 team members.

### SAOS Enterprise Fleet ($799)
> Full private automation suite. On-premise deployment, HIPAA-grade privacy, dedicated hardware (Mac Studio or RTX 4090), white-glove setup, unlimited n8n runs.

### Systack Accelerate 10K ($249)
> Managed automation for small business. Cloud VPS, up to 10K automation runs/month, custom workflows, Slack + Google integration, same-day support.

### Systack Accelerate 25K ($349)
> Higher volume managed automation. Up to 25K runs/month.

### Systack Private ($799)
> On-premise managed automation. Dedicated hardware in your building, air-gapped, HIPAA/PCI ready, 24K model (llama3:70b), 4-hour support SLA.

### Setup Fees
- Accelerate Setup ($2,500): One-time remote setup + integration + training
- Private Setup ($4,500): One-time hardware install + network config + model setup

## Naming Convention for Stripe

Format: `[BRAND] [TIER] [BILLING]`

Examples:
- `SAOS Personal+ — Monthly`
- `SAOS Business Fleet — Monthly`
- `Systack Private — Monthly`
- `Systack Accelerate Setup — One-time`

## After Creating

Paste the new Payment Link URLs and Buy Button IDs here:

| Product | Payment Link | Buy Button ID | Status |
|---------|-------------|---------------|--------|
| SAOS Personal+ Monthly | | | ⬜ |
| SAOS Personal+ Annual | | | ⬜ |
| Systack Accelerate 10K | | | ⬜ |
| Systack Accelerate 25K | | | ⬜ |
| Systack Private | | | ⬜ |
| Systack Accelerate Setup | | | ⬜ |
| Systack Private Setup | | | ⬜ |

---

*Next: Update site with new buy button IDs*
