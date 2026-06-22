---
name: ai-consultation-orchestrator
description: "Structured escalation to M365 Copilot or other AI consultants when confidence is low, attempts fail, or the problem domain is novel. Captures responses, synthesizes insights, and saves to memory."
---

# AI Consultation Orchestrator

Structured escalation to M365 Copilot or other AI consultants. For when confidence is low, local attempts fail, or the problem domain is novel.

## When to Use (Triggers)

Consult Copilot when ANY of these conditions met:
1. **Confidence < 0.75** on proposed solution
2. **2+ failed attempts** on same problem
3. **Unknown domain** — novel problem never seen before
4. **High risk** — PESSI flagged as risky/irreversible
5. **Detected reasoning loop** — cyclic tool calls, going in circles
6. **System architecture decision** — designing new component
7. **New API integration** — unknown patterns, authentication
8. **Security-sensitive** — involves credentials, access, compliance

## Process

```
1. Try local solution first
   ├── memory_search
   ├── skills lookup
   └── reasoning

2. If stuck → Open Copilot via browser automation
   └── URL: https://m365.cloud.microsoft/chat/

3. Ask structured question
   └── Include context pack:
       ├── Problem statement
       ├── What was tried
       ├── Error messages
       └── Expected vs actual behavior

4. Capture full response

5. Synthesize:
   ├── Extract key points
   ├── Compare with local knowledge
   ├── Validate feasibility
   └── Create plan

6. Save to memory:
   ├── Raw response (memory/YYYY-MM-DD-copilot-*.md)
   ├── Curated insights (extracted patterns)
   └── Applied solution (document what worked)

7. Apply to task, document solution
```

## Context Pack Format

```
PROBLEM:
[Clear 1-2 sentence description]

WHAT I TRIED:
1. [Attempt 1] → [Result]
2. [Attempt 2] → [Result]

ERROR:
[Exact error message or unexpected behavior]

EXPECTED:
[What should happen]

ACTUAL:
[What actually happened]

ENVIRONMENT:
- OS: [e.g., macOS 15, Ubuntu 22.04]
- Tools: [e.g., n8n, Python 3.11, Node 20]
- Version: [e.g., n8n 1.45, OpenClaw 0.65.4]

QUESTION:
[Specific question for Copilot]
```

## Credential Access

```bash
# Retrieve password if needed
security find-generic-password -s "m365-copilot-81777" -w

# Account: 81777@office365proplus.co
# Browser: Brave (profile: openclaw-managed)
# URL: https://m365.cloud.microsoft/chat/
```

## Response Capture

Save Copilot responses with full context:

```markdown
# Copilot Consultation — 2026-06-20

## Question
[What was asked]

## Copilot Response
[Full response]

## Key Insights
1. [Insight 1]
2. [Insight 2]

## Comparison with Local Knowledge
- Confirms: [what we knew]
- Contradicts: [what we had wrong]
- Adds: [new information]

## Decision
- Applied: [what we did]
- Outcome: [result]
- Saved to: [memory location]
```

## Integration with Fleet

- **ORACLE** — Design questions, architecture validation
- **VALI** — Validation approaches, test strategies
- **PESSI** — Risk assessment, security questions
- **CODY** — Implementation details, code patterns
- **SOL** — Orchestration, coordination decisions

## Documentation

Consultation archives stored in:
- `memory/YYYY-MM-DD-copilot-[topic].md`
- Pattern library updated with validated solutions

## Critical Rules

1. **Try local first** — Don't default to Copilot
2. **Capture everything** — Raw + curated + patterns
3. **Validate before applying** — Copilot can be wrong
4. **Document the solution** — So we don't need Copilot next time
5. **Save to memory** — Makes future consultations faster

## Reference

- Full protocol: `COPILOT-CONSULTATION-RULES.md`
- Architecture doc: `memory/2026-06-04-copilot-insight-escalation-architecture.md`
- API analysis: `memory/2026-06-04-copilot-api-options.md`
