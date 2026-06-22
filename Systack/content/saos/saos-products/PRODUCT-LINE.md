# SAOS Product Line — Personal + Business Tiers

## Philosophy

**"AI that works for you, not the other way around."**

SAOS agents handle the boring stuff so you can focus on what matters.
Two tracks: **Personal** (life) and **Business** (work).

---

## PERSONAL TRACK — Life Assistance

### 1. SAOS Personal Agent — $49/mo

**For:** Individuals, freelancers, side-hustlers, anyone who needs help staying organized

**What it does:**
- Email triage and drafting
- Calendar management and scheduling
- Task reminders and follow-ups
- Document summarization
- Research assistance
- Note-taking and organization

**How it works:**
- Runs on your device (laptop, home server)
- No cloud AI — local models only
- Your data stays on your machine
- Accessible via web dashboard or SMS

**Perfect for:**
- Busy professionals who need an executive assistant
- Students managing classes and deadlines
- Caregivers coordinating schedules
- Anyone who says "I need help staying on top of things"

**Pricing:**
- $49/mo (no setup fee, self-install)
- $499/yr (save $89)

---

### 2. SAOS Personal+ — $99/mo

**For:** Power users who want more capability

**Everything in Personal, plus:**
- Multi-device sync (phone, laptop, tablet)
- Voice interaction (local Whisper)
- Automated expense tracking
- Travel planning and booking assistance
- Social media scheduling (local only, no cloud APIs)
- Custom integrations (local apps)

**Pricing:**
- $99/mo
- $999/yr (save $189)

---

## BUSINESS TRACK — Work Automation

### 3. SAOS Business Fleet — $299/mo

**For:** Small teams (2-10 people)

**What it does:**
- Invoice processing
- Lead qualification
- Customer support drafting
- Team collaboration via Slack
- Document classification
- Report generation

**Infrastructure:**
- Cloud VPS managed by Systack
- Client-owned Slack + Google accounts
- Local AI processing
- Systack handles maintenance

---

### 4. SAOS Enterprise Fleet — $799/mo

**For:** Large teams (10+ people), regulated industries

**Everything in Business, plus:**
- On-premise deployment option
- HIPAA-grade privacy
- Dedicated hardware
- White-glove setup
- Priority support

---

## Comparison

| Feature | Personal $49 | Personal+ $99 | Business $299 | Enterprise $799 |
|---------|-------------|--------------|---------------|----------------|
| **Target** | Individual | Power user | Small team | Large team |
| **Email triage** | ✅ | ✅ | ✅ | ✅ |
| **Calendar mgmt** | ✅ | ✅ | ✅ | ✅ |
| **Invoice processing** | ❌ | ❌ | ✅ | ✅ |
| **Team Slack** | ❌ | ❌ | ✅ | ✅ |
| **On-premise** | ❌ | ❌ | ❌ | ✅ |
| **HIPAA** | ❌ | ❌ | ❌ | ✅ |
| **Devices** | 1 | Unlimited | Team | Team |
| **Setup** | Self-install | Self-install | Remote | White-glove |
| **Support** | Community | Email | Same-day | 4-hour SLA |

---

## Percy's Place

**Percy = SAOS Personal+ reference implementation**

Percy is the agent we built for ourselves. It demonstrates:
- Multi-device sync
- Voice interaction
- Memory system (daily logs → long-term)
- Local dashboard
- n8n integration
- Ollama models

**Percy is not sold** — it's the open-source reference. But we can sell **"Percy-powered Personal Agents"** as a configured service.

---

## Why Separate Personal from Business?

| Personal | Business |
|----------|----------|
| "Help me stay organized" | "Automate my company's workflows" |
| One person | Multiple people |
| Life tasks | Revenue tasks |
| $49-99/mo | $299-799/mo |
| Self-install | Systack manages |
| No compliance needs | HIPAA/SOC2 |

---

## Stripe Products to Create

### Personal Track

| # | Product | Price | Billing | Type |
|---|---------|-------|---------|------|
| 11 | **SAOS Personal Monthly** | $49/mo | Monthly | Recurring |
| 12 | **SAOS Personal Annual** | $499/yr | Yearly | Recurring |
| 13 | **SAOS Personal+ Monthly** | $99/mo | Monthly | Recurring |
| 14 | **SAOS Personal+ Annual** | $999/yr | Yearly | Recurring |

### Business Track (Existing)

| # | Product | Price | Billing | Type |
|---|---------|-------|---------|------|
| 8 | **SAOS Business Fleet** | $299/mo | Monthly | Recurring |
| 9 | **SAOS Enterprise Fleet** | $799/mo | Monthly | Recurring |

---

## Naming Convention

```
SAOS-PER-M  → SAOS Personal Monthly ($49)
SAOS-PER-A  → SAOS Personal Annual ($499)
SAOS-PER+-M → SAOS Personal+ Monthly ($99)
SAOS-PER+-A → SAOS Personal+ Annual ($999)
SAOS-BIZ-M  → SAOS Business Fleet Monthly ($299)
SAOS-ENT-M  → SAOS Enterprise Fleet Monthly ($799)
```

---

## Marketing Angles

### Personal: "Your AI Sidekick"
> "Imagine having a personal assistant who never sleeps, never forgets, and never judges your inbox. That's SAOS Personal."

### Business: "Automation That Actually Works"
> "Stop paying for AI that sends your data to OpenAI. SAOS runs locally. Your invoices, your customers, your data — all private."

---

*Next: Update service-packages.md with Personal tiers*
