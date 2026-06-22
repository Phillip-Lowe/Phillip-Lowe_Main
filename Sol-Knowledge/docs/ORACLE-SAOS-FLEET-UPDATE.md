# ORACLE-SAOS-FLEET-UPDATE — Revived Agents

**Date:** 2026-06-17  
**Status:** AGENTS ADDED TO SAOS  
**Agents Updated:** CODY, CHATTY, GENI

---

## ⚠️ CRITICAL CONTEXT FOR ORACLE

SAOS has expanded from the 7-agent fleet described in original handoff (2026-06-16) to a **full 10-agent fleet**.

**Original 7:** SOL, VALI, PESSI, ORACLE, ATLAS, ASSEMBLY, JURIS
**Added 3:** CODY, CHATTY, GENI

These 3 agents were originally seeded in the PostgreSQL orchestrator database (2026-06-09) but were **removed from the SAOS website/client-facing fleet** to simplify messaging. They are now **restored to active duty** per client directive.

---

## 🔧 CODY — Code Generation & Build Agent

**Role:** Automated code generation, skill building, voice/streaming development

**What CODY Does:**
- Generates new skills, plugins, automation components
- Builds voice skill development and streaming integrations
- Produces code artifacts that ASSEMBLY deploys
- Iterates build phases (Phase 1, Phase 2, etc.)

**Workflow Pattern:**
```
ORACLE designs → CODY codes → ASSEMBLY deploys → VALI validates
```

**Current Status:** 🔄 REVIVING
- Dormant since May 31, 2026
- Build cron jobs were failing (assigned to SOL instead)
- Reactivation in progress

**Scheduled Jobs:**
| Job | Schedule | Last Run | Status |
|-----|----------|----------|--------|
| BUILD-VOICE-SKILL-Phase1 | 23:00 CDT | Jun 5 | ✅ Complete |
| BUILD-CUSTOM-SKILLS | 01:00 CDT | Jun 5 | ✅ Complete |

**Deliverables Produced:**
- Voice streaming skill (`plugin.json` + source)
- Custom skills (4 builds on Jun 5)
- `PHASE1-REPORT.md` documenting build phases

---

## 💬 CHATTY — Communication & Onboarding Agent

**Role:** Client communication, onboarding flows, content generation, social media

**What CHATTY Does:**
- Crafts client-facing messages, emails, announcements
- Manages onboarding sequences for new SAOS deployments
- Generates social media content (LinkedIn marketing)
- Handles customer support responses and escalation
- Maintains brand voice consistency

**When to Invoke:**
| Trigger | Example |
|---------|---------|
| New client onboarded | Welcome sequence, setup guide, first contact |
| LinkedIn post needed | Draft, review, schedule business content |
| Support ticket | Compose response or escalate with context |

**Current Status:** 🔄 REVIVING
- Originally active in orchestrator prototype
- Not yet in production SAOS fleet
- Needs formal activation and scheduling

**Brand Voice:**
- Friendly but professional
- Technical accuracy without jargon overload
- Action-oriented (clear next steps)
- Human-first, AI-assisted tone

---

## 🎨 GENI — Creative & Visual Agent

**Role:** Image generation, video creation, visual asset production

**What GENI Does:**
- Generates marketing visuals, social media assets
- Produces video content from text descriptions
- Creates branded templates and design systems
- Optimizes prompts for local/cloud generation tools

**Tools Available:**
| Tool | Purpose |
|------|---------|
| Kling AI | Image generation via web interface |
| ComfyUI | Local image/video generation |
| pandoc + pyppeteer | Branded PDF generation |
| SVG/HTML | Diagrams, whiteboards, web graphics |

**Current Status:** 🔄 REVIVING
- Seeded in orchestrator DB (2026-06-09)
- Tools exist (Kling, ComfyUI) but agent role not yet formalized

**Collaboration:**
- CHATTY provides copy, captions, content direction
- ORACLE ensures visuals align with system architecture
- ATLAS archives approved assets for reuse

---

## 📁 FILES CREATED

| File | Location | Status |
|------|----------|--------|
| `fleet/cody.md` | `~/.openclaw/workspaces/sol/fleet/cody.md` | ✅ Created |
| `fleet/chatty.md` | `~/.openclaw/workspaces/sol/fleet/chatty.md` | ✅ Created |
| `fleet/geni.md` | `~/.openclaw/workspaces/sol/fleet/geni.md` | ✅ Created |
| `SAOS-FOUNDATION-SPEC.md` | Updated fleet table + loop | ✅ Edited |

---

## 🎯 IMPACT ON ORACLE'S WORK

If Oracle is generating SAOS documentation, fleet diagrams, or client-facing materials:

1. **Use the 10-agent fleet**, not the 7-agent version
2. **CODY is part of the architecture** — mention in build/development sections
3. **CHATTY is the client voice** — include in onboarding/communication docs
4. **GENI is the creative engine** — include in marketing/visual asset sections

**Correct fleet diagram:**
```
┌─────────────────────────────────────────────┐
│              SAOS AGENT FLEET               │
├─────────────────────────────────────────────┤
│                                             │
│  EXECUTION LAYER                            │
│  ├── SOL (Generator)                        │
│  ├── CODY (Code Builder)         ← RESTORED  │
│  └── ASSEMBLY (Deployment)                  │
│                                             │
│  QUALITY/RISK LAYER                         │
│  ├── VALI (Verifier)                        │
│  └── PESSI (Risk Analyst)                   │
│                                             │
│  INTELLIGENCE LAYER                         │
│  ├── ORACLE (Designer)                      │
│  └── ATLAS (Knowledge)                      │
│                                             │
│  ENGAGEMENT LAYER                           │
│  ├── CHATTY (Communication)      ← RESTORED  │
│  └── GENI (Creative)             ← RESTORED  │
│                                             │
│  COMPLIANCE LAYER                           │
│  └── JURIS (Legal)                          │
│                                             │
└─────────────────────────────────────────────┘
```

---

## ❓ QUESTIONS FOR ORACLE

1. Should service manuals differentiate between **core 7** and **extended 10** fleet tiers?
2. Do CHATTY/GENI need separate pricing pages or are they bundled?
3. Should CODY appear in technical documentation as the "build engine"?
4. Are there naming/branding concerns with expanding from 7→10 agents publicly?

---

## ✅ ACTION ITEMS

- [x] Create role spec files for all 3 agents
- [x] Update SAOS-FOUNDATION-SPEC.md fleet table
- [x] Update SAOS-FOUNDATION-SPEC.md system loop
- [ ] Inform Oracle Systems of fleet expansion
- [ ] Update systack.net/saos/ page (when website refresh happens)
- [ ] Reactivate CODY build cron jobs
- [ ] Activate CHATTY (create first onboarding flow)
- [ ] Activate GENI (produce first SAOS marketing asset)

---

**Prepared by:** SOL  
**Date:** 2026-06-17 03:59 CDT  
**Priority:** MEDIUM — Oracle should incorporate into ongoing documentation work
