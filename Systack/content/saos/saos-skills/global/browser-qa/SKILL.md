---
name: browser-qa
description: "Validate real-world UI behavior. Use after any deploy, page change, or user flow modification."
---

# Browser QA Verification

## Trigger
- UI changes deployed
- New pages or user flows
- Bug fix claims
- Cross-browser / mobile concerns

## Tools
- browser (snapshot + act)
- Mobile viewport simulation

## Workflow

1. **Open live page** — Use actual URL, not localhost unless specified
2. **Check console** — Errors, warnings, CSP issues
3. **Test desktop** — 1440px viewport minimum
4. **Test mobile** — 375px viewport minimum
5. **Execute user flow** — Click through complete path
6. **Capture evidence** — Screenshot on pass AND fail

## Verification Gate
**DO NOT PASS UNLESS:**
- [ ] Mobile viewport tested
- [ ] No console errors (warnings flagged but not blocking)
- [ ] Screenshots captured
- [ ] User flow completes end-to-end

## Output
```
Status: PASS | FAIL
URL: <tested URL>
Viewport: desktop | mobile | both
Console: clean | <N> errors | <N> warnings
Screenshots: <paths>
Issues: <none or list>
```

## Escalation
SOL → ORACLE when:
- Test requires authentication not available
- Failure is environmental (CDN, DNS, SSL) not code
- Multi-step flow exceeds browser tool reliability