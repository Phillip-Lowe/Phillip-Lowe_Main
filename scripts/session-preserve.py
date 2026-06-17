#!/usr/bin/env python3
"""
Session Preservation System
Saves active session context before the 4 AM reset, restores on reconnect.
"""

import json
import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path.home() / ".openclaw" / "workspaces" / "sol" / "memory" / "session_state.db"
MEMORY_DIR = Path.home() / ".openclaw" / "workspaces" / "sol" / "memory"

def ensure_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS session_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_key TEXT,
            plan_id TEXT,
            context TEXT,
            last_user_message TEXT,
            pending_tasks TEXT,
            created_at TEXT,
            expires_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_checkpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            active_plans TEXT,
            last_topic TEXT,
            next_actions TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_checkpoint():
    """Save current operational state before 4 AM reset."""
    ensure_db()
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Find active plans
    plans_dir = MEMORY_DIR / "plans"
    active_plans = []
    if plans_dir.exists():
        for f in plans_dir.glob("PLAN-*.md"):
            text = f.read_text(encoding="utf-8", errors="ignore")
            if "**State:** ACTIVE" in text or "STATE: ACTIVE" in text:
                active_plans.append(f.stem)
    
    # Find today's memory for context
    today_file = MEMORY_DIR / f"{today}.md"
    last_topic = ""
    if today_file.exists():
        lines = today_file.read_text().splitlines()
        for line in reversed(lines):
            if line.strip() and not line.startswith("#"):
                last_topic = line.strip()[:200]
                break
    
    c.execute("""
        INSERT OR REPLACE INTO daily_checkpoints 
        (date, active_plans, last_topic, next_actions, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        today,
        json.dumps(active_plans),
        last_topic,
        "Pending: inspect UI, fix MCP, validate plan",
        now
    ))
    
    conn.commit()
    conn.close()
    print(f"[{now}] Checkpoint saved: {len(active_plans)} active plans, topic: {last_topic[:60]}...")

def get_recovery_context():
    """Retrieve last checkpoint for session recovery."""
    ensure_db()
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("""
        SELECT active_plans, last_topic, next_actions, created_at 
        FROM daily_checkpoints 
        WHERE date = ?
    """, (today,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "active_plans": json.loads(row[0]),
            "last_topic": row[1],
            "next_actions": row[2],
            "saved_at": row[3]
        }
    return None

def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "save":
        save_checkpoint()
    elif len(sys.argv) > 1 and sys.argv[1] == "recover":
        ctx = get_recovery_context()
        if ctx:
            print(json.dumps(ctx, indent=2))
        else:
            print("No checkpoint found for today.")
    else:
        print("Usage: session-preserve.py [save|recover]")

if __name__ == "__main__":
    main()
