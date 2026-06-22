---
name: research-live
description: "Live research with source verification. Use for any fact-based, time-sensitive, or externally verifiable claim."
---

# Research — Live Verified

## Trigger
Any output requiring external validation: market data, pricing, tools, news, competitor info, technical specs.

## Anti-Triggers
- Creative writing (voice skill instead)
- Internal system logic (check MEMORY.md first)

## Workflow

1. **Identify claims** — Tag every assertion needing proof
2. **Search live** — web_search minimum 2 queries
3. **Cross-check** — Compare 2+ sources; flag conflicts
4. **Extract** — Key facts + publication dates
5. **Flag uncertainty** — Confidence level per claim

## Verification Gate
**DO NOT COMPLETE UNLESS:**
- [ ] Minimum 2 independent sources
- [ ] Publication dates verified (reject ">2 years old" without flag)
- [ ] No unstated assumptions remain

## Output
```
Claim: <what you found>
Sources: <URLs with dates>
Confidence: high | medium | low
Caveats: <what might be wrong/missing>
```

## Retry Policy
- 3 search iterations minimum before low-confidence
- If sources conflict → escalate to ORACLE with conflict summary

## Escalation
SOL → ORACLE when:
- Sources irreconcilably conflict
- Domain is novel / no reliable sources exist
- Financial/legal/regulatory claim without authoritative source