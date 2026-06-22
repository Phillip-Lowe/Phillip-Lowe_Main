# Systack Automation Documentation System

**Rule:** Every automation we build MUST have documentation in this format. 
**Purpose:** (1) Client deliverable, (2) Internal build reference, (3) Future employee/agent onboarding.
**Status:** MANDATORY — no automation ships without docs.

---

## 📋 Documentation Template

### File Naming
`docs/automations/{automation-id}/{automation-id}-docs.md`

Example: `docs/automations/noshow-prevention/noshow-prevention-docs.md`

---

## Template Structure

```markdown
# {Automation Name} — System Documentation

**Automation ID:** `{id}`  
**Version:** `{version}`  
**Status:** `{draft|building|testing|live|deprecated}`  
**Built:** `{date}`  
**Last Updated:** `{date}`  
**Owner:** `{client or internal}`  
**Builder:** `{agent/person}`  

---

## 1. Executive Summary

### What It Does
{One paragraph — what problem this solves and how}

### Business Value
| Metric | Before | After |
|--------|--------|-------|
| {e.g., No-show rate} | {X%} | {Y%} |
| {e.g., Labor hours/week} | {N} | {N} |

### ROI Estimate
- Time saved: {hours/week}
- Revenue protected/captured: {$/month}
- Payback period: {time}

---

## 2. System Architecture

### Flow Diagram
{Mermaid or ASCII flow}

### Components
| Component | Technology | Purpose |
|-----------|------------|---------|
| {e.g., Trigger} | {n8n Webhook} | {Captures booking attempt} |
| {e.g., Database} | {SQLite/Postgres} | {Stores lead state} |
| {e.g., Email} | {n8n Email Node} | {Sends reminders} |

### Data Flow
1. {Step 1}
2. {Step 2}
3. {Step 3}

---

## 3. Technical Specifications

### Triggers
| Trigger | Type | Schedule/Condition |
|---------|------|-------------------|
| {Name} | {Webhook/Cron/Manual} | {Details} |

### Inputs
| Field | Type | Required | Source |
|-------|------|----------|--------|
| {email} | {string} | {Yes} | {Booking form} |
| {phone} | {string} | {No} | {Booking form} |

### Outputs
| Destination | Format | Frequency |
|-------------|--------|-----------|
| {Email} | {HTML} | {Per event} |
| {Google Sheet} | {Row} | {Per event} |

### Dependencies
| System | Version | Credential ID |
|--------|---------|---------------|
| {n8n} | {1.50+} | {—} |
| {Square} | {API v2} | {cred_xxx} |
| {Gmail} | {IMAP} | {cred_yyy} |

---

## 4. Configuration

### Environment Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `{N8N_WEBHOOK_URL}` | {Webhook endpoint} | `https://...` |
| `{EMAIL_FROM}` | {Sender address} | `support@...` |

### n8n Workflow Settings
| Setting | Value |
|---------|-------|
| {Execution mode} | {Sequential/Parallel} |
| {Error workflow} | {ID or "None"} |
| {Timeout} | {Seconds} |

### Retry Policy
| Condition | Action | Max Attempts |
|-----------|--------|--------------|
| {HTTP fail} | {Exponential backoff} | {5} |
| {Email bounce} | {Log + alert} | {3} |

---

## 5. Operational Runbook

### Startup / Shutdown
- **Activate:** {Steps to turn on}
- **Deactivate:** {Steps to pause safely}
- **Emergency stop:** {How to kill immediately}

### Daily Checks
- [ ] {Check A}
- [ ] {Check B}

### Monitoring
| Metric | Expected | Alert If |
|--------|----------|----------|
| {Executions/day} | {N} | {< N-5} |
| {Error rate} | {< 2%} | {> 5%} |

### Failure Scenarios
| Scenario | Symptom | Response |
|----------|---------|----------|
| {API down} | {Workflow stops} | {Check status page, retry in 5m} |
| {Auth expired} | {401 errors} | {Refresh credential in n8n UI} |

---

## 6. Build Log

### Phase {N}: {Name}
- **Date:** {YYYY-MM-DD}
- **What:** {What was built}
- **Blockers:** {Any issues}
- **Decisions:** {Key choices made}

---

## 7. Client Handoff

### What the Client Sees
{Screenshots, URLs, or description of client-facing elements}

### What They Need to Know
- {Point 1}
- {Point 2}

### What They Should NOT Touch
- {Config X} — changing this breaks {Y}
- {Credential Z} — managed by Systack

### Support Escalation
| Issue | First Response | Escalate To |
|-------|---------------|-------------|
| {Stop working} | {Check n8n status} | {Systack — within 4h} |
| {Want changes} | {Document request} | {Systack — next business day} |

---

## 8. Future Enhancements

| Priority | Idea | Effort | Impact |
|----------|------|--------|--------|
| {P1} | {Add SMS} | {Low} | {High} |
| {P2} | {AI routing} | {Medium} | {Medium} |

---

## 9. References

### Related Documentation
- {Link to other system docs}
- {Link to skill file}

### Source Code
- {n8n workflow ID: `xxx`}
- {Frontend file: `path/to/file`}
- {API endpoint: `https://...`}

### Test Data
- {Sample payloads}
- {Test credentials (sanitized)}

---

## Appendix: Quick Reference Card

```
START:     {How to start}
STOP:      {How to stop}
CHECK:     {How to verify it's working}
FIX:       {Common fix for most common failure}
ESCALATE:  {When to call for help}
```
```

---

## 📁 Directory Structure

```
docs/
├── automations/
│   ├── order-system/
│   │   ├── order-system-docs.md
│   │   ├── order-system-runbook.md
│   │   └── screenshots/
│   ├── invoice-parser/
│   │   ├── invoice-parser-docs.md
│   │   └── ...
│   ├── noshow-prevention/
│   ├── smart-rebooking/
│   ├── review-system/
│   ├── missed-lead-recovery/
│   ├── referral-engine/
│   ├── crm-lite/
│   ├── upsell-intelligence/
│   ├── scheduling-optimizer/
│   └── revenue-dashboard/
├── templates/
│   └── automation-doc-template.md      # This file
├── clients/
│   └── {client-name}/
│       └── {automation-id}/
└── internal/
    └── build-checklists/
```

---

## 🔧 How to Use This Template

### For New Automations
1. Copy this template to `docs/automations/{id}/{id}-docs.md`
2. Fill in all sections during build
3. Update status as you progress: `draft` → `building` → `testing` → `live`
4. Client handoff section must be complete before delivery

### For Existing Automations (Retrofit)
1. Create docs for each live system using this template
2. Mark status as `live`
3. Fill in what you know, mark unknowns as `TODO`
4. Backfill build logs from memory files

### For Oracle / Planning Phase
1. Create doc with status `draft`
2. Fill sections 1, 2, 3, 8 (summary, architecture, specs, enhancements)
3. Use for client proposals and internal planning
4. Upgrade to `building` when approved

---

## 📝 Status Definitions

| Status | Meaning | Can Client See? |
|--------|---------|-----------------|
| `draft` | Planning/proposal phase | Yes — as proposal |
| `building` | Under active development | No — internal only |
| `testing` | Built, being validated | No — internal only |
| `live` | Production, actively running | Yes — full docs |
| `deprecated` | Replaced or shutting down | Yes — with migration guide |

---

**Last Updated:** 2026-06-11  
**Template Version:** 1.0  
**Rule Source:** User directive — "documentation templates for each build"  
**Enforcement:** AGENTS.md RULE 6B — Pre-deployment checklist includes "docs complete"
