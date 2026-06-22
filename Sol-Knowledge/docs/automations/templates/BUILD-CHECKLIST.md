# Automation Build Checklist

**Purpose:** Before starting ANY automation build, complete this checklist.  
**Source:** AGENTS.md RULE 6B + RULE 6C (Pre-Deployment + Top 10 Pitfalls)  
**Rule:** No build starts without this checklist completed.

---

## Pre-Build Checklist

### 1. Memory Search
- [ ] Search MEMORY.md for past failures with this system type
- [ ] Search for "pitfall", "lesson", "gotcha" related to technology stack
- [ ] Check TOOLS.md for credential status
- [ ] Verify no existing similar automation already built

### 2. Technology Stack Validation
- [ ] n8n version compatible? (currently need 1.50+)
- [ ] All credentials available and active?
- [ ] API limits known and documented?
- [ ] Local-only fallback available if cloud fails?

### 3. Client/Requirement Validation
- [ ] Client need validated (not assumed)?
- [ ] ROI estimate calculated?
- [ ] Success metrics defined?
- [ ] Client approval obtained?

### 4. Documentation Setup
- [ ] Doc file created from template?
- [ ] Automation ID assigned?
- [ ] Status set to `draft`?

---

## Build Phase Checklist

### 5. Architecture
- [ ] Flow diagram created?
- [ ] All triggers defined?
- [ ] Data flow documented?
- [ ] Failure scenarios identified?

### 6. Configuration
- [ ] Environment variables documented?
- [ ] Credentials referenced (not hardcoded)?
- [ ] Retry policy set (5 attempts)?
- [ ] Error workflow connected?

### 7. Testing
- [ ] Test payload prepared?
- [ ] Happy path tested?
- [ ] Error path tested?
- [ ] Edge cases considered?

---

## Pre-Deployment Checklist (MANDATORY — HARD STOP)

### 8. Code Quality
- [ ] `node -c` on EVERY .js file changed → syntax errors = deployed bugs
- [ ] grep for duplicate const declarations → SyntaxError = broken page
- [ ] Verify ALL image/file paths exist → 404s = broken UI
- [ ] No hardcoded API keys in JSON files → git leak = permanent exposure

### 9. n8n-Specific (if applicable)
- [ ] IMAP node: format="resolved" → shallow parsing = missed attachments
- [ ] IF node: check mimeType NOT fileName → "Phone bill .pdf" fails endsWith
- [ ] Binary key: attachment_0 NOT attachment_ → wrong key = invisible attachments
- [ ] No ES6 spread (...) in Code nodes → n8n sandbox doesn't support it
- [ ] Webhook validates actual form fields → field name mismatch = all orders fail
- [ ] Webhook responds AFTER processing → respond first = lost orders

### 10. Git Safety
- [ ] git diff reviewed for secrets
- [ ] No credentials in commit history
- [ ] .env files in .gitignore
- [ ] git log --all --grep='password|key|token|secret' checked

### 11. Live Test
- [ ] Test webhook with curl
- [ ] Test email delivery
- [ ] Test payment flow (if applicable)
- [ ] Verify database writes

### 12. Documentation
- [ ] All template sections filled?
- [ ] Client handoff section complete?
- [ ] Runbook operational?
- [ ] Quick reference card ready?

---

## Post-Deployment

### 13. Monitoring
- [ ] First 24h: check every 2 hours
- [ ] First week: daily check
- [ ] Ongoing: weekly check

### 14. Client Handoff
- [ ] Client documentation delivered
- [ ] Client training completed (if needed)
- [ ] Support escalation path communicated
- [ ] "What not to touch" clearly stated

---

## Sign-Off

**Builder:** _________________  
**Date:** _________________  
**Build ID:** _________________  

**Reviewer:** _________________  
**Date:** _________________  

**Deploy Approved:** [ ] Yes  
**Notes:** _________________

---

## HARD STOPS (Never Violate)

1. **Never push if any commit contains real credentials**
2. **Never deploy if node -c fails**
3. **Never deploy n8n workflow with placeholder credential IDs**
4. **Never use shell variable expansion for API keys** (use Python file I/O)
5. **Never edit n8n SQLite database directly** (use MCP or UI)

Violation of any hard stop has caused production failures documented in MEMORY.md and PESSI-PITFALLS.md.

---

**Last Updated:** 2026-06-11  
**Version:** 1.0  
**Source:** AGENTS.md RULE 6B + 6C
