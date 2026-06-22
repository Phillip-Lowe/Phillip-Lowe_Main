# SKILL.md — Auto-Research

## Description
Autonomous research skill for AI agents. Given a topic or question, the agent searches sources, extracts findings, synthesizes a structured report, and self-evaluates completeness.

## When to Use
- User asks "research X" or "find out about Y"
- Agent encounters an unknown tool, API, or concept
- Agent needs to verify a claim before acting on it
- Scheduled research tasks (competitor monitoring, trend tracking)

## Protocol

### Phase 1: Query Clarification
1. Identify the core question
2. Determine scope (how deep, how broad, what timeframe)
3. Identify source preferences (docs, news, academic, etc.)

### Phase 2: Source Discovery
1. Search web for relevant sources (web_search)
2. Fetch primary sources (web_fetch, browser)
3. Search internal memory (memory_search, wiki_search)
4. Check local files/docs if applicable (read, dir_list)

### Phase 3: Extraction
1. Read each source
2. Extract key facts, claims, data points
3. Note source credibility and recency
4. Flag contradictions between sources

### Phase 4: Synthesis
1. Organize findings by theme
2. Write structured summary with citations
3. Include confidence levels (verified / probable / uncertain)
4. Note gaps in knowledge

### Phase 5: Self-Evaluation
1. Did I answer the original question?
2. Are the sources credible and recent?
3. Are there contradictions I haven't resolved?
4. Should I search for more sources?
5. Loop back to Phase 2 if gaps remain (max 3 iterations)

### Phase 6: Output
1. Write findings to a file in `memory/research/YYYY-MM-DD-<topic>.md`
2. Include: question, sources, findings, confidence, gaps, next steps
3. Update MEMORY.md or wiki if findings reveal durable knowledge

## Verification Requirements (Binding)
- [ ] At least 2 independent sources consulted
- [ ] Primary source fetched (not just search results)
- [ ] Findings written to file before reporting to user
- [ ] Confidence levels assigned to all claims
- [ ] Contradictions explicitly noted, not hidden

## Failure Modes to Avoid
- **Single-source dependency** — never rely on one source
- **Confidence inflation** — don't mark uncertain claims as verified
- **Search-and-report** — don't just list search results, synthesize
- **Tool failure blindness** — if web_search/web_fetch fails, report it and try alternatives

## Example Invocation
```
research "What is the current pricing for Brave Search API?"
→ Search → Fetch brave.com → Check memory → Synthesize → Write file → Report
```
