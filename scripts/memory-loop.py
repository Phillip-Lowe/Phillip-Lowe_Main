#!/usr/bin/env python3
"""
Memory Loop — Automatic feedback system
Every output flows back to memory in real-time or batch.

Config (from Green 2026-05-28):
- Scope: plans, agents, n8n workflows, manual actions
- Storage: daily logs + SQLite
- Detail: full but space-conscious
- Timing: real-time for high-leverage/errors, batch for routine
"""

import sqlite3
import json
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# ── PATHS ──────────────────────────────────────────────────────
MEMORY_DIR = Path.home() / ".openclaw" / "workspaces" / "sol" / "memory"
PLANS_DIR = MEMORY_DIR / "plans"
DAILY_LOG = MEMORY_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"
DB_PATH = Path.home() / "Documents" / "SOL-System" / "05-Logs" / "fleet_observability.db"
ARTIFACTS_DIR = Path.home() / ".openclaw" / "workspaces" / "sol" / "artifacts"

# ── SPACE CONSCIOUSNESS ────────────────────────────────────────
MAX_DAILY_LOG_SIZE_MB = 5  # Rotate/truncate if exceeded
MAX_ARTIFACT_AGE_DAYS = 30  # Archive old artifacts
MAX_DB_ROWS_PER_TABLE = 10000  # Prune old rows

# ── HELPERS ────────────────────────────────────────────────────
def ensure_db():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS memory_loop (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            category TEXT,
            source TEXT,
            event TEXT,
            detail TEXT,
            leverage TEXT,  -- high | medium | low
            status TEXT,    -- success | failure | info
            plan_id TEXT,
            agent TEXT,
            size_bytes INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_size(text):
    return len(text.encode("utf-8"))

def truncate_if_needed(filepath, max_mb=MAX_DAILY_LOG_SIZE_MB):
    if not filepath.exists():
        return
    size_mb = filepath.stat().st_size / (1024 * 1024)
    if size_mb > max_mb:
        # Keep last 50% of file
        lines = filepath.read_text().splitlines()
        half = len(lines) // 2
        filepath.write_text("\n".join(lines[half:]) + "\n")
        log_event("system", "memory", "daily_log_truncated", 
                  f"Truncated {filepath.name} at {size_mb:.1f}MB", "low", "info")

def log_event(category, source, event, detail, leverage="medium", status="info", plan_id=None, agent=None):
    """Write to both SQLite and daily log."""
    ensure_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    detail_text = json.dumps(detail) if isinstance(detail, (dict, list)) else str(detail)
    size = get_size(detail_text)
    
    # ── SQLite ──────────────────────────────────────────────
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""
        INSERT INTO memory_loop (timestamp, category, source, event, detail, leverage, status, plan_id, agent, size_bytes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (now, category, source, event, detail_text[:2000], leverage, status, plan_id, agent, size))
    
    # Prune old rows if needed
    c.execute("SELECT COUNT(*) FROM memory_loop")
    count = c.fetchone()[0]
    if count > MAX_DB_ROWS_PER_TABLE:
        c.execute("DELETE FROM memory_loop WHERE id IN (SELECT id FROM memory_loop ORDER BY timestamp ASC LIMIT ?)",
                  (count - MAX_DB_ROWS_PER_TABLE,))
    
    conn.commit()
    conn.close()
    
    # ── Daily Log (space-conscious) ─────────────────────────
    DAILY_LOG.parent.mkdir(parents=True, exist_ok=True)
    truncate_if_needed(DAILY_LOG)
    
    # Format based on leverage
    if leverage == "high":
        header = f"## [{now}] 🔴 HIGH-LEVERAGE: {event}"
    elif leverage == "medium":
        header = f"## [{now}] 🟡 {event}"
    else:
        header = f"## [{now}] {event}"
    
    # Condense detail if too long
    detail_str = detail_text[:500] + "... (truncated)" if len(detail_text) > 500 else detail_text
    
    entry = f"""
{header}
- **Category:** {category}
- **Source:** {source}
- **Status:** {status}
- **Plan:** {plan_id or "N/A"}
- **Agent:** {agent or "N/A"}
- **Detail:** {detail_str}

---
"""
    with open(DAILY_LOG, "a", encoding="utf-8") as f:
        f.write(entry)
    
    return True

# ── TRIGGERS ─────────────────────────────────────────────────
def on_plan_state_change(plan_id, old_state, new_state, agent=None, summary=""):
    """Trigger: Plan state changes (especially DONE or FAILED)."""
    leverage = "high" if new_state in ("DONE", "FAILED_FINAL") else "medium"
    status = "success" if new_state == "DONE" else ("failure" if "FAIL" in new_state else "info")
    
    log_event(
        category="plan",
        source="plan_registry",
        event=f"plan_{new_state.lower()}",
        detail={
            "plan_id": plan_id,
            "old_state": old_state,
            "new_state": new_state,
            "summary": summary[:200]  # Space-conscious
        },
        leverage=leverage,
        status=status,
        plan_id=plan_id,
        agent=agent
    )

def on_agent_completion(agent, task, result, errors=None):
    """Trigger: Agent finishes a task."""
    has_errors = errors and len(errors) > 0
    leverage = "high" if has_errors else "medium"
    status = "failure" if has_errors else "success"
    
    log_event(
        category="agent",
        source=agent,
        event="task_complete",
        detail={
            "task": task[:200],
            "result": result[:300],
            "errors": errors[:3] if errors else []  # Space-conscious: max 3 errors
        },
        leverage=leverage,
        status=status,
        agent=agent
    )

def on_n8n_execution(workflow_name, execution_id, status, output_summary, error=None):
    """Trigger: n8n workflow runs."""
    leverage = "high" if error or status == "error" else "low"
    
    log_event(
        category="workflow",
        source="n8n",
        event=f"workflow_{status}",
        detail={
            "workflow": workflow_name,
            "execution_id": execution_id,
            "output": output_summary[:200],
            "error": error[:200] if error else None
        },
        leverage=leverage,
        status="failure" if error else "success"
    )

def on_manual_action(action_type, description, result=None):
    """Trigger: Green (or SOL) takes a manual action."""
    log_event(
        category="manual",
        source="green" if "green" in action_type.lower() else "sol",
        event=action_type,
        detail={
            "description": description[:300],
            "result": result[:200] if result else None
        },
        leverage="high",  # Manual actions are high-leverage by default
        status="info"
    )

# ── BATCH DIGEST ─────────────────────────────────────────────
def generate_digest():
    """Generate end-of-day summary from SQLite."""
    ensure_db()
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    
    c.execute("""
        SELECT category, status, COUNT(*) 
        FROM memory_loop 
        WHERE timestamp LIKE ? 
        GROUP BY category, status
    """, (f"{today}%",))
    stats = c.fetchall()
    
    c.execute("""
        SELECT timestamp, category, event, detail, leverage, status, plan_id, agent
        FROM memory_loop
        WHERE timestamp LIKE ? AND leverage IN ('high', 'medium')
        ORDER BY timestamp DESC
        LIMIT 50
    """, (f"{today}%",))
    highlights = c.fetchall()
    conn.close()
    
    digest = f"""# Daily Digest — {today}

## Stats
| Category | Status | Count |
|----------|--------|-------|
"""
    for cat, stat, count in stats:
        digest += f"| {cat} | {stat} | {count} |\n"
    
    digest += "\n## Highlights (High/Medium Leverage)\n\n"
    for row in highlights:
        ts, cat, evt, det, lev, stat, pid, agt = row
        digest += f"- **{ts}** — `{cat}` — {evt} — {stat.upper()}"
        if pid:
            digest += f" — Plan: `{pid}`"
        if agt:
            digest += f" — Agent: `{agt}`"
        digest += f"\n  Detail: {det[:100]}...\n\n"
    
    return digest

# ── CLI ──────────────────────────────────────────────────────
def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: memory-loop.py [digest|test|status]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "digest":
        digest = generate_digest()
        print(digest)
        # Also write to daily log
        with open(DAILY_LOG, "a", encoding="utf-8") as f:
            f.write("\n" + digest + "\n")
        print(f"\nDigest appended to {DAILY_LOG}")
    
    elif cmd == "test":
        print("Testing memory loop...")
        on_plan_state_change("PLAN-TEST-001", "ACTIVE", "DONE", agent="CODY", summary="Test completion")
        on_agent_completion("CODY", "Build test feature", "Success", errors=[])
        on_n8n_execution("Utopia Deli Orders", "exec_123", "success", "2 orders processed")
        on_manual_action("config_change", "Updated n8n webhook URL", "Verified working")
        print("Test events logged. Check SQLite and daily log.")
    
    elif cmd == "status":
        ensure_db()
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute("SELECT COUNT(*), SUM(size_bytes) FROM memory_loop")
        count, size = c.fetchone()
        c.execute("SELECT COUNT(DISTINCT date(timestamp)) FROM memory_loop")
        days = c.fetchone()[0]
        conn.close()
        
        log_size = DAILY_LOG.stat().st_size / 1024 if DAILY_LOG.exists() else 0
        print(f"Memory Loop Status:")
        print(f"  Total events: {count}")
        print(f"  Total size: {size / 1024:.1f} KB (SQLite)")
        print(f"  Days covered: {days}")
        print(f"  Today's log: {log_size:.1f} KB")
        print(f"  Daily log path: {DAILY_LOG}")
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
