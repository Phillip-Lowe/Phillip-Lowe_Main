# Systack + SAOS — Final Stripe Product Catalog

## Decision: Minimum $199 (16GB RAM)

**Why:** 4GB doesn't work (Jacqueline proved it). 8GB is tight. 16GB is where agents actually work.

---

## Products to Create

### SAOS Fleet (Self-Managed)

| # | SKU | Product Name | Price | Billing | Description |
|---|-----|-------------|-------|---------|-------------|
| 1 | **SAOS-PER+-M** | SAOS Personal+ Monthly | $199/mo | Monthly | 16GB VPS, local models, dashboard |
| 2 | **SAOS-PER+-A** | SAOS Personal+ Annual | $1,999/yr | Yearly | Save $389 |
| 3 | **SAOS-BIZ-M** | SAOS Business Fleet Monthly | $299/mo | Monthly | Team features, 10K runs |
| 4 | **SAOS-ENT-M** | SAOS Enterprise Fleet Monthly | $799/mo | Monthly | On-premise, HIPAA |

### Systack Services (Done-For-You)

| # | SKU | Product Name | Price | Billing | Description |
|---|-----|-------------|-------|---------|-------------|
| 5 | **SYST-ACC-10K-M** | Systack Accelerate 10K Monthly | $249/mo | Monthly | Managed automation, 10K runs |
| 6 | **SYST-ACC-25K-M** | Systack Accelerate 25K Monthly | $349/mo | Monthly | Managed automation, 25K runs |
| 7 | **SYST-ACC-S** | Systack Accelerate Setup | $2,500 | One-time | Remote setup + training |
| 8 | **SYST-PRV-M** | Systack Private Monthly | $799/mo | Monthly | On-premise, managed |
| 9 | **SYST-PRV-S** | Systack Private Setup | $4,500 | One-time | Hardware install + setup |

### Cloud LLM Add-On (Optional, Pass-Through)

| Provider | Typical Cost | Billing |
|----------|-------------|---------|
| Claude API | $8-20/mo | User pays directly |
| ChatGPT API | $5-15/mo | User pays directly |
| Together AI | $3-10/mo | User pays directly |
| Groq | $2-8/mo | User pays directly |

**No markup.** We pass costs through. Our margin is in infrastructure.

---

## Existing Buttons (Keep or Deprecate)

| Button ID | Current Product | Status |
|-----------|----------------|--------|
| `buy_btn_1TfU451WicviTxiig1l8JYjR` | SAOS Solo $149 | **DEPRECATED** — replaced by Personal+ $199 |
| `buy_btn_1TfU3M1WicviTxiilXTJNolL` | SAOS Business $299 | **KEEP** — rename to Business Fleet |
| `buy_btn_1TfU1m1WicviTxiikPepeQO4` | SAOS Enterprise $799 | **KEEP** — rename to Enterprise Fleet |

---

## Publishable Key

```
pk_live_51Tckdx1WicviTxii6uKLsxzQENJqWDNxt8Zqmst9YKBQ4F0KSn7VpuR7PZTGRQXJMv42NwimR1kcIdOxElznzIsM000DBc6pKp
```

---

## Pricing Rationale

| Tier | VPS Cost | Support | Total Cost | Price | Margin |
|------|----------|---------|------------|-------|--------|
| Personal+ ($199) | $96 (16GB) | $20 | $116 | $199 | $83/mo |
| Business ($299) | $96 (16GB) | $40 | $136 | $299 | $163/mo |
| Enterprise ($799) | ~$200 (hardware) | $100 | ~$300 | $799 | ~$499/mo |

---

## Naming Convention

```
SAOS-PER+-M  → SAOS Personal+ Monthly ($199)
SAOS-PER+-A  → SAOS Personal+ Annual ($1,999)
SAOS-BIZ-M   → SAOS Business Fleet Monthly ($299)
SAOS-ENT-M   → SAOS Enterprise Fleet Monthly ($799)

SYST-ACC-10K-M → Systack Accelerate 10K ($249)
SYST-ACC-25K-M → Systack Accelerate 25K ($349)
SYST-ACC-S     → Systack Accelerate Setup ($2,500)
SYST-PRV-M     → Systack Private Monthly ($799)
SYST-PRV-S     → Systack Private Setup ($4,500)
```

---

## Recommended Priority

1. **SAOS Personal+ Monthly** ($199) — new product, highest volume potential
2. **SAOS Business Fleet** ($299) — keep existing button, rename
3. **SAOS Enterprise Fleet** ($799) — keep existing button, rename
4. **Systack Accelerate** ($249) — new product
5. **Setup fees** ($2,500 / $4,500) — one-time revenue

---

*Updated: 2026-06-06 19:25 CDT*  
*Decision: Kill Basic/Pro, start at Personal+ ($199)*
