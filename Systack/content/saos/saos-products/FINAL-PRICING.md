# SAOS Final Pricing — No Pro Tier, Model Costs Included

## Decision: Kill Pro, Start with Personal+ ($199)

**Why:**
- 4GB doesn't work (Jacqueline proved it)
- 8GB is bare minimum but tight
- 16GB is where it actually works
- We need margin for cloud LLM costs if they want Claude/ChatGPT
- We don't want support nightmares from slow agents

---

## New Product Line

### SAOS Personal+ — $199/mo
**"Your agent, your server, works properly"**

**Includes:**
- 16GB VPS (DigitalOcean/Linode) — $96/mo cost
- Local models (Ollama) — qwen2.5:7b or gemma-2-9b
- 32K context
- Email support
- Multi-device sync
- Voice interaction (local Whisper)
- Local dashboard
- n8n workflows (up to 5,000 runs/mo)

**Target:** Individuals who want a working agent, not a science project

---

### SAOS Business Fleet — $299/mo
**"Team automation that actually works"**

**Includes:**
- 16GB VPS — $96/mo cost
- Everything in Personal+
- Team collaboration (shared Slack workspace)
- Up to 5 team members
- Invoice processing pipeline
- Lead qualification
- Customer support drafting
- 10,000 n8n runs/mo

**Target:** Small teams (2-10 people)

---

### SAOS Enterprise Fleet — $799/mo
**"Private infrastructure, zero exposure"**

**Includes:**
- On-premise deployment (we ship hardware)
- Dedicated Mac Studio or Linux + RTX 4090
- llama3:70b or command-r-plus
- HIPAA-grade privacy
- White-glove setup
- Priority support (4-hour SLA)
- Unlimited n8n runs

**Target:** Regulated industries, 10+ people

---

## Model Cost Reality

### Local Models (Included in Price)

| Model | Size | RAM | Speed | Quality |
|-------|------|-----|-------|---------|
| qwen2.5:7b | 4.7GB | 8GB min | ~3s | Good for most tasks |
| gemma-2-9b | 5.8GB | 12GB min | ~4s | Better reasoning |
| llama3:8b | 4.9GB | 8GB min | ~3s | General purpose |
| mistral-7b | 4.8GB | 8GB min | ~3s | Fast, efficient |

**Cost to us:** $0 (runs on their VPS)
**Included in:** All tiers

### Cloud LLM API (Optional Add-On)

If they want Claude/ChatGPT instead of local models:

| Provider | Cost | Notes |
|----------|------|-------|
| **Claude API** | ~$8-20/mo | 100K-500K tokens/mo typical usage |
| **ChatGPT API** | ~$5-15/mo | GPT-4o, cheaper than Claude |
| **Together AI** | ~$3-10/mo | Mixtral, Llama via API |
| **Groq** | ~$2-8/mo | Fast inference, cheap |

**We pass this cost through:**
- User pays us $199/mo (base)
- PLUS whatever API they use (we bill separately or they pay provider directly)
- OR they use local models (included, no extra cost)

---

## Cost Breakdown (Personal+ $199)

| Item | Cost to Us | Notes |
|------|-----------|-------|
| 16GB VPS (DigitalOcean) | $96/mo | $48 for 8GB is too tight |
| Support (email) | $20/mo | Estimated per user |
| n8n hosting | $0 | Runs on same VPS |
| Ollama hosting | $0 | Runs on same VPS |
| Dashboard hosting | $0 | Runs on same VPS |
| **Total cost** | **~$116/mo** | |
| **Price** | **$199/mo** | |
| **Margin** | **$83/mo ($996/yr)** | |

**This works.** $83/mo margin per user.

---

## Why No Cheaper Tier?

| Tier We Considered | Why It Doesn't Work |
|-------------------|---------------------|
| $49 Basic (shared) | 4GB RAM, unusable, support nightmare |
| $99 Pro (8GB) | Works but tight, no headroom, still slow |
| $149 (8GB+GPU) | GPU adds $60/mo, margin too thin |
| **$199 Personal+ (16GB)** | ✅ Comfortable, works, margin |

**The minimum viable product is $199.** Anything less = broken experience.

---

## What We Tell Prospects

> "Our agents need 16GB RAM to work properly. We learned this the hard way. We don't sell anything below $199 because anything less doesn't work — it's slow, buggy, and you'll hate it."

> "You can use local models (included) or add cloud LLM like Claude. Local is free. Cloud is pay-as-you-go. Your choice."

---

## Percy's Place

**Percy = Personal+ ($199/mo)**
- 16GB VPS
- qwen2.5:7b + whisper
- Full dashboard
- Multi-device
- This is what we demo
- This is what we sell

---

## Files to Update

1. `systack-site/services/service-packages.md` — Remove Pro, fix Personal+ pricing
2. `saos-products/STRIPE-CATALOG.md` — Remove Pro, update prices
3. `saos-products/PRODUCT-LINE.md` — Simplify to 3 tiers
4. `memory/2026-06-06-pricing-alignment.md` — Document decision

---

## Stripe Products to Create

| # | Product | Price | Button Name |
|---|---------|-------|-------------|
| 1 | **SAOS Personal+ Monthly** | $199/mo | `saos-personal-plus` |
| 2 | **SAOS Personal+ Annual** | $1,999/yr | `saos-personal-plus-annual` |
| 3 | **SAOS Business Fleet** | $299/mo | `saos-business-fleet` |
| 4 | **SAOS Enterprise Fleet** | $799/mo | `saos-enterprise-fleet` |
| 5 | **Systack Private Monthly** | $799/mo | `systack-private` |
| 6 | **Systack Accelerate 10K** | $249/mo | `systack-accelerate` |

---

## Cloud LLM Add-On (Separate Billing)

| Provider | Typical Monthly | How We Bill |
|----------|----------------|-------------|
| Claude API | $8-20/mo | User pays provider directly OR we bill +10% |
| ChatGPT API | $5-15/mo | Same |
| Together AI | $3-10/mo | Same |
| Groq | $2-8/mo | Same |

**We don't mark up API costs.** We pass them through. Our margin is in the infrastructure.

---

*Decision made: 2026-06-06 19:20 CDT*  
*Rationale: Jacqueline's 4GB failure + model cost reality*
