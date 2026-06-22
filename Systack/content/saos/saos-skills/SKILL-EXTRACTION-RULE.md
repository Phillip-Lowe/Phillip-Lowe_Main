# Skill Extraction Loop (System Rule)

## When to Run
At end of every session that involves repeated workflows.

## Process

1. **Identify repeated pattern**
   - What trigger appeared 3+ times?
   - What steps were consistently followed?
   - What verification was used?

2. **Validate for skill candidacy**
   - [ ] Clear trigger? (WHEN TO USE is unambiguous)
   - [ ] Defined steps? (Reproducible sequence)
   - [ ] Verification gate? (PASS/FAIL criteria)
   - [ ] Tool match? (Existing OpenClaw tools cover it)

3. **Decision**
   - IF all YES → Convert to skill per skill-creator format
   - IF any NO → Discard or refine; document in session log why

4. **Store**
   - Save to `saos-skills/global/<skill-name>/SKILL.md`
   - Update this file with extraction date + skill name
   - Reference in MEMORY.md under "SAOS Skills Inventory"

## Extraction Log
| Date | Skill Extracted | Source Session | Pattern |
|------|-----------------|----------------|---------|
| 2026-06-19 | research-live | ORACLE system design | Repeated web search + cross-check |
| 2026-06-19 | writing-voice | ORACLE system design | Voice rules from SOUL.md + MEMORY.md |
| 2026-06-19 | browser-qa | ORACLE system design | Post-deploy UI validation pattern |
| 2026-06-19 | publish-verify | ORACLE system design | Post-publish confirmation pattern |
| 2026-06-19 | code-validate | ORACLE system design | Pre-deploy code check pattern |

## Retry Policy
- Each new skill tested 5 iterations minimum before promotion to "stable"
- Failure triggers: unclear triggers, weak verification, inconsistent output
- Failed skill → `saos-skills/staging/` not `global/`