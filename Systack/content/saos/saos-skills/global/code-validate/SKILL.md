---
name: code-validate
description: "Validate code changes for stability and correctness. Use before any commit, push, or deploy involving code."
---

# Code Change Validation

## Trigger
Any code modification: scripts, HTML, CSS, JS, Python, n8n workflow changes.

## Workflow

1. **Identify affected components** — Map change to all dependent files/systems
2. **Run relevant tests** — Unit tests, integration tests, or manual validation
3. **Validate logic manually** — Walk through changed code line-by-line
4. **Check integrations** — API contracts, webhook formats, database schema
5. **Confirm no regressions** — Test adjacent functionality

## Verification Gate (AGENTS.md RULE 6B)
**FAIL IF:**
- [ ] No tests run (manual or automated)
- [ ] Risk unassessed
- [ ] Changes unverified against live system
- [ ] `node -c` fails on any changed `.js` file
- [ ] Duplicate const declarations exist (grep check)
- [ ] Image/file paths unverified

## Pre-Deployment Checklist (Mandatory)
```bash
# Run before ANY deploy
node -c <changed.js files>
grep -n "const " <changed files> | sort | uniq -d
ls -la <referenced image paths>
```

## n8n-Specific Gates
- IMAP node: format="resolved" (not shallow)
- IF node: check mimeType NOT fileName
- Binary key: attachment_0 NOT attachment_
- No ES6 spread (...) in Code nodes
- Webhook validates actual form field names

## Output
```
Files Changed: <list>
Tests: <results>
Manual Validation: ✅ | ❌ <details>
Risk Level: low | medium | high
Regressions: none | <list>
Ready to Deploy: YES | NO — <blockers>
```

## Escalation
SOL → ORACLE when:
- Change touches production data or payment flows
- Risk level = high
- No tests exist for changed component