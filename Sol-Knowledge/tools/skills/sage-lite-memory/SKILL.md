---
name: sage-lite-memory
description: "Lightweight persistent memory system for agent workspaces using flat-file JSON and periodic sync to long-term stores. Enables cross-session continuity without heavy infrastructure."
---

# SAGE Lite Memory

Lightweight persistent memory for agent workspaces. Flat-file JSON storage with periodic sync to long-term (SQLite/Postgres). Cross-session continuity without heavy infrastructure.

## When to Use
- Agent workspace needs memory that persists across reboots
- Daily log accumulation for weekly distillation
- Short-term recall (last 7 days) without embedding overhead
- Bridge between session chat and long-term MEMORY.md

## Architecture

```
Active Session
    ↓ (write)
memory/dreaming/light/YYYY-MM-DD.md  — daily raw logs
memory/dreaming/rem/YYYY-MM-DD.md   — compressed REM cycle
memory/dreaming/deep/YYYY-MM-DD.md  — deep consolidation
    ↓ (periodic sync)
memory/YYYY-MM-DD.md                 — human-readable daily log
    ↓ (weekly)
MEMORY.md                            — distilled rules/decisions
```

## File Types

| Layer | File | Purpose | Retention |
|-------|------|---------|-----------|
| **Light** | `light/YYYY-MM-DD.md` | Raw session events | 7 days |
| **REM** | `rem/YYYY-MM-DD.md` | Compressed highlights | 30 days |
| **Deep** | `deep/YYYY-MM-DD.md` | Consolidated patterns | 90 days |
| **Daily** | `memory/YYYY-MM-DD.md` | Human-readable log | 1 year |
| **Long** | `MEMORY.md` | Distilled rules | Permanent |

## Daily Log Format

```markdown
# 2026-06-20

## Morning
- Built catering lead system
- Fixed logo path bug

## Afternoon
- Deployed invoice pipeline
- Tested n8n webhook

## Decisions
- Use Postgres for invoice DB (SQLite caused locking issues)

## Gotchas
- Never use shell variable expansion for API keys
```

## Memory Sync Scripts

```python
# sage-lite-sync.py
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

MEM_DIR = Path("~/.openclaw/workspaces/sol/memory").expanduser()
LIGHT_DIR = MEM_DIR / "dreaming" / "light"

class SageLiteMemory:
    def write_event(self, event_text, category="general"):
        """Write event to today's light log."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = LIGHT_DIR / f"{today}.md"
        
        timestamp = datetime.now().strftime("%H:%M")
        entry = f"- [{timestamp}] ({category}) {event_text}\n"
        
        with open(log_file, "a") as f:
            f.write(entry)
    
    def distill_week(self):
        """Distill 7 days of light logs into MEMORY.md sections."""
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            log_file = LIGHT_DIR / f"{date}.md"
            if log_file.exists():
                # Extract decisions, gotchas, key events
                pass
```

## Heartbeat Integration

At each heartbeat poll:
```
1. Review recent light/ logs
2. Identify patterns (repeated issues, decisions)
3. Promote to MEMORY.md if important
4. Archive old light/ logs (> 7 days)
```

## Memory Query

```python
# memory_query.py — semantic-ish search
import re
from pathlib import Path

def memory_search(query_terms, days_back=7):
    """Search recent daily logs for keywords."""
    results = []
    mem_dir = Path("~/.openclaw/workspaces/sol/memory").expanduser()
    
    for log_file in sorted(mem_dir.glob("2026-*.md"))[-days_back:]:
        with open(log_file) as f:
            content = f.read()
            for term in query_terms:
                if term.lower() in content.lower():
                    # Extract surrounding context
                    idx = content.lower().find(term.lower())
                    start = max(0, idx - 100)
                    end = min(len(content), idx + 200)
                    snippet = content[start:end]
                    results.append({
                        "file": log_file.name,
                        "term": term,
                        "snippet": snippet.strip()
                    })
    
    return results
```

## Promotion Rules

Promote to MEMORY.md when:
- Decision affects future behavior ("Always do X before Y")
- Gotcha caused a failure (document so it doesn't repeat)
- System rule changed ("From now on...")
- Tool configuration finalized
- Credential or API endpoint changed

## Scripts

- `saos/scripts/sage-lite-init.py` — Initialize memory structure
- `saos/scripts/sage-lite-ingest.py` — Write event to light log
- `saos/scripts/sage-lite-reader.py` — Read/query recent memory
- `saos/scripts/sage-lite-writer.py` — Write distilled entry
- `memory_sync.py` — Full sync to long-term
- `memory_query.py` — Keyword search across logs

## Schema

```json
// memory/dreaming/daily-ingestion.json
{
  "schema": "sage-lite-v1",
  "date": "2026-06-20",
  "events": [
    {
      "timestamp": "03:41:00",
      "category": "skill_creation",
      "event": "Created 12 skills from project patterns",
      "agents_involved": ["SOL"],
      "files_created": ["skills/*/SKILL.md"]
    }
  ],
  "decisions": [],
  "gotchas": []
}
```

## Gotchas

- **Disk space**: Light logs accumulate fast. Auto-archive after 7 days.
- **Locking**: Don't hold file open. Write-append, close immediately.
- **Corruption**: Keep backup. JSON is append-only, easy to recover.
- **Query speed**: Flat files slow after 100MB. Archive quarterly.

## Reference

- Schema: `schemas/sage-lite-schema.md`
- Full system: `HYBRID-MEMORY-SYSTEM.md`
- Dream diary: `memory/dream-diary-2026-06-04.md`
