---
name: automator-runbook-generator
description: "Generate complete automation runbooks from build notes: internal implementation guide, client service manual, technical architecture, and troubleshooting guide."
---

# Automator Runbook Generator

Transform build notes into complete documentation suite: internal guide, client manual, architecture doc, troubleshooting guide. One build → four docs.

## When to Use
- Automation build is complete and deployed
- Client needs service manual for their system
- Internal team needs implementation reference
- Troubleshooting guide needed for support
- QA/testing documentation required

## Output Suite

For each automation, generate:

1. **`internal/[automation]-internal-implementation-guide.md`**
   - What was built
   - Technical architecture
   - n8n workflow details
   - Database schemas
   - API endpoints
   - Environment variables

2. **`client/[business]-[automation]-client-service-manual.md`**
   - What the system does
   - How to use it
   - What to expect
   - How to get help
   - Cost/value proposition

3. **`internal/[automation]-technical-architecture.md`**
   - System diagram
   - Data flow
   - Component interactions
   - Security model
   - Scalability notes

4. **`internal/[automation]-troubleshooting-guide.md`**
   - Common problems
   - Diagnostic steps
   - Quick fixes
   - When to escalate
   - Emergency procedures

## Generation Process

```
Build complete →
    ├── Extract key facts
    │   ├── What: [system description]
    │   ├── How: [architecture]
    │   ├── Where: [deployment details]
    │   ├── When: [triggers, schedule]
    │   └── Why: [business value]
    │
    ├── Generate internal guide
    │   └── Technical details, credentials, configs
    │
    ├── Generate client manual
    │   └── Business-friendly, no tech jargon
    │
    ├── Generate architecture doc
    │   └── Diagrams, data flow, security
    │
    └── Generate troubleshooting guide
        └── Symptoms → Diagnosis → Fix
```

## Template Structure

### Internal Implementation Guide

```markdown
# [Automation Name] — Internal Implementation Guide

## Overview
What this automation does and why.

## Architecture
- Frontend: [HTML/JS/React]
- Backend: [n8n/Python/API]
- Database: [SQLite/Postgres]
- Hosting: [Netlify/Vultr/Local]

## Components
| Component | File | Purpose |
|-----------|------|---------|
| Webhook | `webhook-url` | Receives form data |
| Workflow | `workflow-id` | Processes data |
| Database | `table-name` | Stores records |
| API | `api-port` | Serves dashboard |

## Configuration
```
WEBHOOK_URL=https://...
DATABASE_PATH=...
API_PORT=9001
```

## Deployment Steps
1. Import n8n workflow
2. Configure credentials
3. Test webhook
4. Activate workflow

## Maintenance
- Monthly: Review error logs
- Quarterly: Update credentials
- Annually: Review architecture
```

### Client Service Manual

```markdown
# [Business Name] — [Automation Name] Service Manual

## What This Does
[Plain English description]

## How It Works
1. Customer [does X]
2. System [does Y]
3. You receive [Z]

## What to Expect
- Response time: [X minutes/hours]
- Notifications: [email/SMS/dashboard]
- Reports: [daily/weekly/monthly]

## Getting Help
- Email: support@systack.net
- Slack: [workspace invite]
- Emergency: [phone number]

## Pricing
- Included in: [tier name]
- Overage: [cost per extra unit]
```

## File Locations

```
docs/automations/
├── [automation-name]/
│   ├── [automation]-docs.md                    # Overview
│   ├── internal/
│   │   ├── [automation]-internal-guide.md      # Tech details
│   │   ├── [automation]-workflow-walkthrough.md
│   │   ├── [automation]-technical-architecture.md
│   │   └── [automation]-troubleshooting-guide.md
│   └── client/
│       └── [business]-[automation]-client-manual.md
```

## Automation Catalog

| Automation | Status | Client Manual | Internal Guide | Architecture | Troubleshooting |
|-----------|--------|--------------|----------------|--------------|-----------------|
| Order System | ✅ | ✅ | ✅ | ✅ | ✅ |
| Invoice Parser | ✅ | ✅ | ✅ | ✅ | ✅ |
| Catering Lead | ✅ | ✅ | ✅ | ✅ | ⏳ |
| Booking System | ✅ | ✅ | ✅ | ✅ | ⏳ |
| Meal Prep | ✅ | ✅ | ✅ | ⏳ | ⏳ |
| No-Show Prevention | ✅ | ✅ | ✅ | ⏳ | ⏳ |
| CRM Lite | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| Review System | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| Referral Engine | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| Subscription | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| Upsell Intelligence | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| Smart Rebooking | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| Scheduling Optimizer | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| Missed Lead Recovery | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |

## Validation Checklist

Before marking documentation complete:
- [ ] All technical details verified against actual deployment
- [ ] Client manual reviewed for clarity (no jargon)
- [ ] Architecture diagram matches actual system
- [ ] Troubleshooting steps tested
- [ ] File paths and URLs confirmed live
- [ ] Credential references use placeholder format
- [ ] Version/date stamped

## Reference

- Template: `docs/automations/templates/automation-doc-template.md`
- Build checklist: `docs/automations/templates/BUILD-CHECKLIST.md`
- Full catalog: `docs/automations/AUTOMATION-CATALOG.md`
- Master plan: `docs/automations/MASTER-PLAN.md`
