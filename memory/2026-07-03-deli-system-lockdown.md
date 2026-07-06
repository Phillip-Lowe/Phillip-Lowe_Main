# DELI SYSTEM LOCKDOWN — PERMANENT RULE

**Date:** 2026-07-03
**Status:** ✅ ACTIVE — Never Expires
**Code Phrase:** "ORACLE OVERRIDE"

## Rule

- **Never touch Utopia Deli frontend, backend, n8n workflows, or any code unless EXPLICITLY prompted by Green**
- **Core deli architecture is OFF LIMITS without the code phrase: "KUDU-7"**
- **This includes:** `order.theutopiadeli.com`, `utopia-deli` repo, n8n deli workflows, Square integration, menu data, pricing

## Reason

Week of 2026-06-30 to 2026-07-03 spent fixing broken deli deployments. Multiple production days lost. Autonomous changes to deli system caused cascading failures including:
- Broken payload structures
- Missing HTML elements causing JS crashes
- GitHub Pages deployment failures
- Customer unable to place orders

## Scope

**OFF LIMITS (require "ORACLE OVERRIDE"):**
- `The Utopia Deli/` directory
- `utopia-deli/` repo
- `utopia-deli-temp/` directory
- n8n workflows with "deli", "utopia", "meal-prep", "catering" in name
- Square integration for deli
- Any file path containing "deli", "utopia", "meal-prep", "catering"

**ALLOWED (informational only):**
- Answering questions about deli system
- Checking status/logs
- Providing advice when asked

## Enforcement

If asked to work on deli system without code phrase:
1. Refuse politely
2. Remind user of lockdown rule
3. Ask them to say "ORACLE OVERRIDE" if they want to proceed

---

*This rule is binding. Violation = immediate halt + notification to Green.*
