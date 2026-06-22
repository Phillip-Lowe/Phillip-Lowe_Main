---
name: mod1-content-pipeline
description: "End-to-end content production workflow for MOD 1 clients. Orchestrates research, writing, image gen, build, QA, and publish verification."
---

# RUNBOOK: MOD 1 Content Pipeline

## Trigger
New MOD 1 client needs product page, content refresh, or marketing asset.

## Roles
| Step | Agent | Skill |
|------|-------|-------|
| Research | SOL | research-live |
| Writing | SOL | writing-voice |
| Image Gen | GENI | local-image-gen |
| Page Build | CODY | (coding agent) |
| QA | SOL | browser-qa |
| Publish Verify | SOL | publish-verify |
| Stakeholder Update | CHATTY | (communication) |

## Execution Flow

### Phase 1: Input & Research (SOL)
1. Receive client brief + product specs
2. Run **research-live** — Verify all factual claims (pricing, features, competitors)
3. Output: Research brief with citations + confidence levels

### Phase 2: Content Creation (SOL + GENI)
1. Run **writing-voice** — Produce product copy in Systack voice
2. Handoff to GENI — Generate hero image + supporting visuals
3. Output: Copy doc + image assets

### Phase 3: Build (CODY)
1. CODY receives copy + assets + page requirements
2. Builds HTML/CSS/JS page per Systack site standards
3. Output: Built page files

### Phase 4: Validation (SOL)
1. Run **code-validate** — Check all changed files
2. Run **browser-qa** — Desktop + mobile + console check
3. Output: QA report with PASS/FAIL

### Phase 5: Publish & Verify (SOL)
1. Deploy to production (GitHub Pages / VPS)
2. Run **publish-verify** — Confirm live, metadata correct, links valid
3. Output: Live URL + verification report

### Phase 6: Communication (CHATTY)
1. CHATTY drafts stakeholder update
2. Include: live URL, QA summary, any caveats
3. Output: Sent or queued message

## Quality Bar
- [ ] Research verified (2+ sources)
- [ ] Voice consistent (generic-detection pass)
- [ ] UI tested (desktop + mobile)
- [ ] Page live and confirmed
- [ ] All links reachable

## Failure Handling
- Any skill FAIL → Halt pipeline, return to SOL
- SOL decides: retry skill, escalate to ORACLE, or abort
- ORACLE assesses: fix skill, adjust runbook, or change scope

## Output
- Published page URL
- Complete QA + verification report
- Stakeholder notification sent