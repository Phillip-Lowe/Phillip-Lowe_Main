---
name: deli-workflow-validation
description: "End-to-end validation of Utopia Deli order and catering workflows. Use before any deli system change or periodic audit."
---

# RUNBOOK: Utopia Deli Workflow Validation

## Trigger
- Code change to deli frontend or n8n workflow
- Periodic health check (weekly recommended)
- Reported bug or user complaint
- Before any deployment to deli production

## Roles
| Step | Agent | Skill |
|------|-------|-------|
| Code Check | SOL | code-validate |
| Workflow Test | SOL | (n8n API / webhook test) |
| UI QA | SOL | browser-qa |
| Email Confirm | SOL | (inbox check / n8n execution log) |
| Publish Verify | SOL | publish-verify (if UI affected) |

## Execution Flow

### Phase 1: Code Validation (SOL)
1. Identify all changed files in deli repo
2. Run **code-validate**:
   - `node -c` on all JS files
   - Check config-v2.js for correct logo paths (subdirectory awareness)
   - Verify webhook URL matches active n8n workflow
   - Check form field names match n8n webhook expectations
3. Output: Code validation report

### Phase 2: Workflow Execution Test (SOL)
1. Trigger test order via `curl` or browser
2. Verify n8n execution:
   - Webhook received (check n8n executions)
   - Scoring calculated correctly
   - SQLite database updated
   - Email sent (check inbox / n8n log)
3. For catering: verify lead scoring + auto-reply email
4. Output: Execution trace + PASS/FAIL per node

### Phase 3: Browser QA (SOL)
1. Run **browser-qa** on:
   - https://order.theutopiadeli.com/pickup-order/
   - https://order.theutopiadeli.com/catering/
2. Test full user flows:
   - Order flow: menu → cart → checkout → confirmation
   - Catering flow: form → submit → confirmation page
3. Mobile viewport mandatory
4. Output: QA screenshots + issue log

### Phase 4: Email Confirmation (SOL)
1. Submit test order with known email
2. Verify received:
   - Order confirmation (if configured)
   - Catering lead auto-reply (catering flow)
   - No duplicate sends
3. Check spam folder
4. Output: Email delivery report

### Phase 5: Publish Verification (If UI Changed)
1. Run **publish-verify** on affected URLs
2. Confirm: content live, metadata correct, load time <3s
3. Output: Verification report

## Known Pitfalls (Check Every Time)
| Pitfall | Check |
|---------|-------|
| Logo path broken in subdirectory | `config-v2.js` uses `../images/logo.png` |
| Webhook URL mismatch | Matches active n8n workflow ID |
| Form field name drift | `subtotal_cents` not `subtotal` |
| IMAP credential revoked | Test email receipt live |
| n8n shallow MIME parsing | IMAP node uses `"format": "resolved"` |
| ES6 spread in Code node | Verify no `{...obj}` syntax |

## Quality Bar
- [ ] Order completes end-to-end
- [ ] Payment link valid (if applicable)
- [ ] Email sent and received correctly
- [ ] UI verified on mobile
- [ ] No console errors
- [ ] Database updated

## Failure Handling
- ANY phase FAIL → Full stop, no deploy
- SOL diagnoses: code issue, config issue, or n8n issue
- Escalate to ORACLE if root cause unclear
- Document failure in MEMORY.md with date + symptom

## Output
- Complete validation report
- Screenshots
- Execution trace
- GO / NO-GO decision