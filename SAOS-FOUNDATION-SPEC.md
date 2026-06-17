# SAOS Foundation Spec — Agent Operating System for Systack

**Version:** 1.0
**Date:** 2026-06-05
**Source:** ORACLE session + Percy deployment learnings
**Status:** Architecture defined, implementation pending

---

## What is SAOS?

The **Systack Agent Operating System** is the foundation layer every Systack agent runs on. It handles deployment, model management, monitoring, failure recovery, and recursive self-improvement — so client agents "just work" without Systack manually babysitting each one.

---

## Core Architecture: Recursive Self-Improvement Loop

From ORACLE research: All functioning RSI systems converge to a 4-layer loop.

```
Generate → Evaluate → Modify → Validate → Commit → Repeat
```

### Layer 1 — Execution
Agents perform tasks. Inputs → outputs.

### Layer 2 — Observation (Instrumentation)
Capture: inputs, outputs, decisions, errors, timing.

### Layer 3 — Evaluation (Verifier)
Score performance: rules, metrics, human feedback.

### Layer 4 — Improvement Engine
Propose changes → test → promote only winners.

---

## Fleet Role Mapping (GVU Architecture)

### Canonical Fleet (Internal System Truth): 10 Agents

| Tier | Function | Agent | Scope |
|------|----------|-------|-------|
| **Execution** | Generator (create outputs) | SOL + all agents | Client-facing execution |
| **Execution** | Build Engine | CODY | Skills, builds, scaffolding |
| **Execution** | Deployment | ASSEMBLY | Promote changes, rollback |
| **Quality/Risk** | Verifier (quality scoring) | VALI | Every output scored |
| **Quality/Risk** | Risk analysis | PESSI | Failure patterns, edge cases |
| **Intelligence** | Improvement design | ORACLE | Architecture, prompts, strategy |
| **Intelligence** | Knowledge capture | ATLAS | Structured memory, lessons |
| **Engagement** | Communication | CHATTY | Onboarding, social, support |
| **Engagement** | Creative | GENI | Images, video, visual assets |
| **Compliance** | Legal/Compliance | JURIS | Contracts, regulatory, risk clearance |

### External Presentation (Tiered Exposure)

**Core System (7):** SOL, ORACLE, ATLAS, VALI, PESSI, ASSEMBLY, JURIS
- What clients must understand
- Stable, proven mental model

**Extended Capabilities (+3):** Introduced as augmentation modules
- **CODY → Build Engine** (generates system components)
- **CHATTY → Communication Layer** (onboarding, messaging)
- **GENI → Creative Layer** (visual + content assets)

> Principle: We do not reduce the system to fit perception. We structure perception to absorb the system.

---

## Fleet System Loop (Canonical)

```
ORACLE → Design
  ↓
CODY → Build
  ↓
ASSEMBLY → Deploy
  ↓
VALI → Validate
  ↓
PESSI → Stress-test
  ↓
SOL → Execute / Orchestrate
  ↓
CHATTY → Communicate
  ↓
GENI → Visualize
  ↓
ATLAS → Store knowledge
  ↓
JURIS → Validate legal/compliance
  ↓
[Loop repeats]
```

### Operational Sequence

| Step | Agent | Action |
|------|-------|--------|
| 1 | **ORACLE** | Generates improvement proposal / architecture spec |
| 2 | **CODY** | Builds/codegens any needed components |
| 3 | **ASSEMBLY** | Deploys changes to staging/production |
| 4 | **VALI** | Validates output quality against spec |
| 5 | **PESSI** | Stress-tests for edge cases, risks, failures |
| 6 | **SOL** | Executes workflow in production context |
| 7 | **CHATTY** | Prepares client-facing messaging, onboarding |
| 8 | **GENI** | Produces visual assets if needed |
| 9 | **ATLAS** | Logs structured findings, lessons, version history |
| 10 | **JURIS** | Clears legal/regulatory compliance requirements |
| 11 | **ORACLE** | Evaluates loop performance, designs next iteration |

---

## Critical Architecture Rules

### Rule 1 — Versioned Memory
- Snapshot every system version
- Rollback on degradation
- Never overwrite blindly

### Rule 2 — Isolated Test Environment
- All improvements tested in sandbox
- Must pass validation
- Must prove measurable gain

### Rule 3 — Metric-Driven
Every loop optimizes: accuracy, latency, completion rate, revenue.

### Rule 4 — Human Authority (GREEN)
Final approval layer. Fully autonomous RSI is unsafe without oversight.

---

## True Recursion: Improve the Improver

Most systems fail here — they improve outputs, not the improvement system itself.

SAOS must also improve:
- **The evaluation system** (better scoring, validators)
- **The improvement generator** (better ORACLE prompts)
- **The loop speed** (faster testing cycles)

```
Improve(task execution) AND Improve(improvement system)
```

---

## Deployment Tiers

| Tier | Name | RAM | Model | Context | Deployment | Monthly |
|------|------|-----|-------|---------|------------|---------|
| **Bronze** | Starter | 4GB | qwen2.5:3b | 16K | Cloud VPS | $70/mo |
| **Silver** | Professional | 8GB | qwen2.5:7b | 32K | Cloud VPS + Tailscale | $140/mo |
| **Gold** | Business | 16GB | qwen2.5:14b | 64K | Cloud VPS + Tailscale | $220/mo |
| **Platinum** | Enterprise | 8-16GB | Custom | 32-64K | On-premise server | $300+/mo |
| **Custom** | Air-gapped | Variable | Custom | Variable | No external network | $500+/mo |

### What's included in Systack monthly:
- Agent deployment and configuration
- Identity file creation (SOUL, AGENTS, USER, etc.)
- 24/7 monitoring and health checks
- Monthly improvement reviews
- Priority support (response within 4 hours)
- Optional: weekly strategy sessions ($100/mo add-on)

### Setup fee: $200-500 one-time (beta: free for early clients)

---

## Data Sensitivity Tiers

### Tier 1 — Public
- **Data:** Public info, general knowledge
- **Deployment:** Cloud VPS OK
- **Model:** Cloud or local
- **Examples:** Public-facing chatbot, FAQ agent

### Tier 2 — Internal
- **Data:** Business schedules, employee info, non-sensitive docs
- **Deployment:** Cloud VPS + Tailscale
- **Model:** Local only (no cloud APIs)
- **Examples:** Jacqueline/Percy, office manager agent

### Tier 3 — Confidential
- **Data:** Financials, client lists, contracts
- **Deployment:** On-premise server or strict VPN
- **Model:** Local only, air-gapped
- **Examples:** Accounting firm, legal practice

### Tier 4 — Restricted
- **Data:** HIPAA, attorney-client privilege, classified
- **Deployment:** Air-gapped, no external network
- **Model:** Local only, no remote updates without approval
- **Examples:** Healthcare, defense, government

---

## Infrastructure Requirements Matrix

| Requirement | Bronze | Silver | Gold | Platinum | Custom |
|-------------|--------|--------|------|----------|--------|
| Internet | 10 Mbps | 25 Mbps | 50 Mbps | N/A (local) | None |
| OS | Any (VPS) | Any (VPS) | Any (VPS) | Linux/Windows Server | Linux |
| Access | Public | Tailscale | Tailscale | Tailscale + VPN | Physical only |
| Updates | Auto | Auto | Manual | Client-controlled | Offline USB |
| Backup | Cloud (Vultr) | Cloud + Local | Cloud + Local | Client-owned | Physical media |
| Support SLA | 24h | 4h | 1h | 30m | Custom |

---

## Client Discovery Questionnaire

**Mandatory before quoting:**

1. **Data type:** What data will the agent handle? (Public / Internal / Confidential / Restricted)
2. **Local-only?** Does any data need to stay on-premises? (Yes / No / Not sure)
3. **Compliance:** Any regulatory requirements? (HIPAA / SOX / GDPR / PCI / None)
4. **Users:** How many users? (1 / 2-5 / 6-20 / 20+)
5. **Volume:** Expected daily conversations? (Light <10 / Moderate 10-50 / Heavy 50+)
6. **Hardware:** Existing servers we can use? (Yes / No)
7. **Budget:** Monthly range? ($50-100 / $100-200 / $200-500 / Enterprise)
8. **Timeline:** When do you need it live? (ASAP / Within 1 month / Within 3 months)

---

## Agent Identity File Standards

| VPS Size | Model | Max Context | Max System Prompt | Identity Files |
|----------|-------|-------------|-------------------|----------------|
| 4GB | qwen2.5:3b | 16K | ~6,000 tokens | ~8KB total |
| 8GB | qwen2.5:7b | 32K | ~14,000 tokens | ~20KB total |
| 16GB | qwen2.5:14b | 64K | ~28,000 tokens | ~40KB total |
| 2GB | qwen2.5:1.5b | 8K | ~2,000 tokens | ~3KB total |

---

## Standard Config Templates

### Bronze (4GB VPS)
```json
{
  "models": {
    "providers": {
      "ollama": {
        "models": [{
          "id": "qwen2.5:3b",
          "name": "qwen2.5:3b",
          "contextWindow": 16384,
          "maxTokens": 8192,
          "params": { "num_ctx": 16384 }
        }]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": "ollama/qwen2.5:3b",
      "compaction": { "reserveTokensFloor": 8192 }
    }
  }
}
```

### Silver (8GB VPS)
```json
{
  "models": {
    "providers": {
      "ollama": {
        "models": [{
          "id": "qwen2.5:7b",
          "name": "qwen2.5:7b",
          "contextWindow": 32768,
          "maxTokens": 8192,
          "params": { "num_ctx": 32768 }
        }]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": "ollama/qwen2.5:7b",
      "compaction": { "reserveTokensFloor": 16384 }
    }
  }
}
```

---

## RSI Implementation: n8n Workflow Spec

### Pilot: Utopia Deli (live system, real transactions)

**Instrumentation nodes:**
1. Order Received → log input payload
2. Order Processed → log output + decision steps
3. Error → capture type, pattern, severity

**Evaluation nodes:**
4. Daily Score: completion rate, errors, latency
5. Weekly Report: trends, regressions

**Improvement loop:**
6. ORACLE triggered when: error rate > 5% OR 3+ same-error
7. Proposal generated → sandbox test → VALI approval → deploy

**Retry:** Max 5 attempts per issue, escalate to GREEN if no improvement.

---

## Deployment Playbook Updates Required

- [ ] Add data sensitivity classification step (before server provisioning)
- [ ] Add RAM/context sizing calculator (automated)
- [ ] Add local-only deployment checklist (no cloud dependencies)
- [ ] Add cost estimate template with all line items
- [ ] Add compliance checklist (HIPAA, SOX, etc.)

---

## Files That Need Creation/Update

| File | Action | Priority |
|------|--------|----------|
| `SAOS-FOUNDATION-SPEC.md` | ✅ This file — created | Done |
| `CLIENT-DISCOVERY-TEMPLATE.md` | Create questionnaire | Next |
| `DEPLOYMENT-PLAYBOOK.md` | Add sensitivity + RAM sections | Next |
| `SYSTACK-PRODUCTION-PLAN.md` | Update pricing tiers | After |
| `systack-site/services/personal-agent.html` | Add tiers to site | After |
| `clients/mcdonalds-gm/` | Add sensitivity classification | After |

---

*Architected by ORACLE, synthesized by SOL*
*This is the North Star — build toward it, don't rush it*
