# SAOS Personal — Real Cost Analysis

## Problem: $49/mo Doesn't Cover Infrastructure

For SAOS Personal to work, the user needs:
1. **VPS** to run the agent 24/7
2. **LLM** for inference (even small models need GPU or CPU)
3. **n8n** for workflows
4. **Storage** for memory/database

## VPS Cost Reality

| Provider | Specs | Monthly Cost | Notes |
|----------|-------|------------|-------|
| **Hetzner** | 2 vCPU, 4GB RAM | ~$7/mo | Cheapest, EU only |
| **Hetzner** | 4 vCPU, 8GB RAM | ~$15/mo | Recommended minimum |
| **DigitalOcean** | 2 vCPU, 4GB RAM | $24/mo | US-based |
| **DigitalOcean** | 4 vCPU, 8GB RAM | $48/mo | Better performance |
| **Linode** | 2 vCPU, 4GB RAM | $24/mo | Good support |
| **AWS Lightsail** | 2 vCPU, 4GB RAM | $24/mo | Easy but expensive |
| **RunPod** | 4 vCPU, 8GB, RTX A4000 | $62/mo | GPU for fast inference |
| **Lambda Labs** | 4 vCPU, 8GB, RTX A10 | ~$80/mo | GPU, good for LLMs |

**Minimum viable:** 4GB RAM, 2 vCPU = **$15-24/mo**
**Recommended:** 8GB RAM, 4 vCPU = **$24-48/mo**
**GPU (fast inference):** 8GB VRAM = **$62-80/mo**

## Cost Per User (Systack's Margins)

### Scenario A: Self-Hosted VPS (User brings their own)

| Item | Cost to User | Cost to Systack | Margin |
|------|-------------|----------------|--------|
| VPS | $15-24/mo | $0 | N/A |
| SAOS software | $49/mo | $0 (software) | $49/mo |
| Support | Included | ~$10/mo | ~$39/mo |
| **Total to user** | **$64-73/mo** | | **~$39/mo profit** |

**Problem:** User pays $64-73/mo total. That's steep for "personal assistant."

### Scenario B: Systack-Hosted VPS (We provide)

| Item | Cost to Systack | Markup | Price to User |
|------|----------------|--------|---------------|
| VPS (4GB) | $15/mo | 2x | $30/mo |
| Software license | $0 | | Included |
| Support/maintenance | $10/mo | | Included |
| **Total** | **$25/mo** | | **$49/mo** |

**Margin:** $24/mo per user ($288/yr)
**Problem:** Thin margin. If user needs support, we lose money.

### Scenario C: Shared Infrastructure (Multi-tenant)

One VPS hosts multiple Personal agents:

| Item | Cost | Users per VPS | Cost per user |
|------|------|--------------|---------------|
| VPS (16GB RAM, 8 vCPU) | $60/mo | 10 users | $6/user |
| GPU (optional) | $80/mo | 10 users | $8/user |
| **Total infra cost** | **$140/mo** | | **$14/user** |
| Software | $0 | | Included |
| Support | ~$5/user | | Included |
| **Total cost** | | | **$19/user** |
| **Price to user** | | | **$49/mo** |
| **Margin** | | | **$30/user/mo ($360/yr)** |

**This works.** 10 users on one VPS = $30/mo margin each.

## Recommended Pricing

### SAOS Personal (Shared VPS, Self-Managed)

| Tier | Price | What's Included | VPS |
|------|-------|----------------|-----|
| **Personal Basic** | $49/mo | Agent software, shared VPS, community support | Shared (10 users/VPS) |
| **Personal Pro** | $99/mo | Agent software, dedicated VPS, email support | Dedicated 4GB |
| **Personal+** | $149/mo | Agent software, GPU VPS, priority support | Dedicated 8GB + GPU |

### Why These Prices

| Tier | Cost to Systack | Price | Margin | Notes |
|------|----------------|-------|--------|-------|
| Basic | ~$14/mo | $49 | $35/mo | Shared infra, thin margin but scales |
| Pro | ~$35/mo | $99 | $64/mo | Dedicated VPS, better experience |
| Personal+ | ~$80/mo | $149 | $69/mo | GPU, fast inference, premium |

## The Realistic Minimum

**$49/mo is possible IF:**
- Shared infrastructure (multi-tenant VPS)
- Minimal support (community/forum)
- Small models (3B parameters, not 70B)
- No GPU (CPU inference, slower but cheaper)

**$49/mo is NOT possible IF:**
- Each user gets dedicated VPS
- We provide GPU for fast inference
- We offer 1-on-1 support
- We use large models (llama3-70b)

## Recommendation

### Option 1: Shared Infrastructure ($49-99/mo)
- Multiple users per VPS
- CPU inference (slower, cheaper)
- Community support
- **Best for:** Price-sensitive individuals

### Option 2: Dedicated VPS ($99-149/mo)
- One user per VPS
- Optional GPU add-on
- Email support
- **Best for:** Power users, small business owners

### Option 3: Bring Your Own VPS ($29/mo software only)
- User provides their own VPS
- Systack provides software + updates
- **Best for:** Technical users who already have infrastructure

## Percy's Place

**Percy = Personal+ tier ($149/mo)**
- Dedicated 8GB VPS
- GPU for fast inference
- Priority support
- Full feature set

**This is what we demo.** Show Percy, sell Personal+.

## Final Pricing

| Product | Price | Includes | Target |
|---------|-------|----------|--------|
| **SAOS Personal Basic** | $49/mo | Shared VPS, CPU inference, community | Students, tight budgets |
| **SAOS Personal Pro** | $99/mo | Dedicated 4GB VPS, CPU, email support | Professionals, freelancers |
| **SAOS Personal+** | $149/mo | Dedicated 8GB+GPU, priority, full features | Power users, Percy reference |
| **SAOS Business Fleet** | $299/mo | Team features, Slack, multi-agent | Small teams |
| **SAOS Enterprise Fleet** | $799/mo | On-premise, HIPAA, white-glove | Large orgs |

## Bottom Line

**$49/mo is only viable with shared infrastructure.** If we promise dedicated resources, minimum is $99/mo.

Be transparent: "Personal Basic runs on shared servers. Personal Pro gets your own server."
