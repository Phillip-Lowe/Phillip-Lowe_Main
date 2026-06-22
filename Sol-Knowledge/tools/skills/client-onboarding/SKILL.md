---
name: client-onboarding
description: "Structured client discovery questionnaire, service agreement generation, and SAOS tier recommendation based on business data sensitivity and compliance needs."
---

# Client Onboarding

Systematic client intake: discovery questionnaire → compliance assessment → tier recommendation → service agreement → deployment scheduling.

## When to Use
- New prospect expresses interest in SAOS
- Existing client upgrading tiers
- Annual renewal / compliance re-assessment
- Building a proposal for a specific business

## Discovery Questionnaire

### Mandatory Questions (Before Quote)

1. **Data Types** — What will the agent handle?
   - [ ] Public info (general knowledge)
   - [ ] Internal (schedules, employee info)
   - [ ] Confidential (financials, client lists)
   - [ ] Restricted (HIPAA, legal privilege)

2. **Premises Requirement** — Does any data need to stay on-site?
   - [ ] Yes → Recommend on-premise + VPN
   - [ ] No → Cloud VPS OK
   - [ ] Not sure → Schedule follow-up

3. **Compliance Requirements**
   - [ ] HIPAA
   - [ ] SOX
   - [ ] GDPR
   - [ ] None

4. **User Count**
   - [ ] 1 user
   - [ ] 2-5 users
   - [ ] 6-20 users
   - [ ] 20+ users

5. **Conversation Volume**
   - [ ] Light (< 50/day)
   - [ ] Moderate (50-200/day)
   - [ ] Heavy (200+/day)

### SAOS Data Sensitivity Tiers

| Tier | Data | Deployment | Model | Cost |
|------|------|-----------|-------|------|
| **Public** | General knowledge | Cloud VPS | Cloud or local | Lowest |
| **Internal** | Employee info, docs | Cloud VPS + Tailscale | Local only | Medium |
| **Confidential** | Financials, contracts | On-premise or VPN | Local only | High |
| **Restricted** | HIPAA, legal | Air-gapped, no network | Local only, no updates | Premium |

### Tier Recommendation Logic

```
IF data == Restricted → SAOS Enterprise + compliance audit
IF data == Confidential → SAOS Enterprise (VPN/air-gap)
IF users > 20 OR volume == Heavy → SAOS Enterprise
IF compliance != None → SAOS Business minimum
ELSE → SAOS Starter or Business
```

## Service Agreement Generation

Based on tier, generate:
- `SYSTACK-SERVICE-AGREEMENT-TEMPLATE.md` — Main agreement
- `DATA-PROCESSING-ADDENDUM.md` — GDPR/HIPAA addendum
- `AUTOMATION-SERVICE-AGREEMENT.md` — Scope of work
- `BUSINESS-SYSTEMS-AGREEMENT.md` — System access terms

### Key Terms
- **Monthly fee**: Based on tier
- **Setup fee**: One-time provisioning cost
- **Data retention**: 30 days chat, 7 years financial (configurable)
- **Termination**: 30-day notice, data export provided
- **Support**: SLA based on tier

## Onboarding Sequence

1. **Discovery call** → Fill questionnaire
2. **Compliance check** → JURIS reviews data sensitivity
3. **Proposal** → Tier + pricing + timeline
4. **Agreement signed** → Deposit collected
5. **Provisioning** → VPS creation (see vps-provisioning skill)
6. **Training** → 1-hour kickoff call
7. **30-day check** → Health review + feedback

## Files Generated

- `CLIENT-DISCOVERY-TEMPLATE.md` — Questionnaire
- `clients/<id>/client-record.json` — Discovery answers
- `clients/<id>/deployment-record.json` — Technical specs
- `legal/SYSTACK-SERVICE-AGREEMENT-TEMPLATE.md` — Contract

## Compliance Checklist (JURIS)

Before deployment:
- [ ] Data sensitivity tier assigned
- [ ] Retention policy documented
- [ ] Breach response procedure acknowledged
- [ ] Data destruction policy signed
- [ ] Access controls configured

## Pricing

| Tier | Monthly | Users | Includes |
|------|---------|-------|----------|
| Starter | $299 | 1-3 | Core system (7 agents) |
| Growth | $599 | 4-10 | + Engagement Engine (CHATTY, GENI) |
| Business | $799 | 11-25 | + Advanced automations |
| Enterprise | Custom | 25+ | Full customization, compliance |

## Reference

- Full spec: `SAOS-FOUNDATION-SPEC.md`
- Fleet docs: `fleet/` directory
- Compliance framework: `entities/systack-compliance.md`
