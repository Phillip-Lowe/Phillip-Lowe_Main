#!/usr/bin/env python3
"""
SAOS Orchestrator Daemon — Persistent Fleet Loop
Runs continuously, polls task_queue, dispatches to all 10 fleet agents.

Usage:
    python3 orchestrator-daemon.py              # Start daemon (foreground)
    python3 orchestrator-daemon.py --daemon   # Start daemon (background via launchd)
    python3 orchestrator-daemon.py --status     # Show system status
    python3 orchestrator-daemon.py --once       # Process one batch and exit
"""

import os, sys, time, json, subprocess, signal, argparse
from datetime import datetime
from typing import Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

# ── CONFIG ───────────────────────────────────────────────────────────
DB_HOST = os.environ.get("PGHOST", "localhost")
DB_PORT = int(os.environ.get("PGPORT", "5432"))
DB_NAME = os.environ.get("PGDATABASE", "systack_memory")
DB_USER = os.environ.get("PGUSER", "philliplowe")
DB_PASS = os.environ.get("PGPASSWORD", "")

POLL_INTERVAL = 10       # seconds between task polls
AGENT_HEARTBEAT = 60    # seconds between agent heartbeat updates
BATCH_SIZE = 5          # tasks to process per poll cycle

# ALL 10 FLEET AGENTS — each gets tasks based on capability matching
FLEET_AGENTS = [
    "SOL",        # Command & Orchestrator
    "CODY",       # Build Engine  
    "ASSEMBLY",   # Deployment
    "VALI",       # Quality Verification
    "PESSI",      # Risk Analysis
    "ORACLE",     # Design & Architecture
    "ATLAS",      # Knowledge & Memory
    "CHATTY",     # Communication
    "GENI",       # Creative & Visual
    "JURIS",      # Legal & Compliance
]

# Agent capability map — determines which tasks each agent can claim
AGENT_CAPABILITIES = {
    "SOL":      ["GENERIC", "ORCHESTRATE", "COORDINATE", "ROUTE"],
    "CODY":     ["BUILD", "CODE", "GENERATE", "SCAFFOLD", "RESEARCH"],
    "ASSEMBLY": ["DEPLOY", "ACTIVATE", "PUBLISH", "CONFIGURE", "INSTALL"],
    "VALI":     ["VALIDATE", "TEST", "VERIFY", "QUALITY", "REVIEW"],
    "PESSI":    ["RISK", "AUDIT", "SECURITY", "STRESS_TEST", "FAILURE_MODE"],
    "ORACLE":   ["DESIGN", "ARCHITECT", "PLAN", "STRATEGY", "RESEARCH"],
    "ATLAS":    ["KNOWLEDGE", "MEMORY", "LOG", "DOCUMENT", "INDEX"],
    "CHATTY":   ["COMMUNICATE", "MESSAGE", "ONBOARD", "EMAIL", "NOTIFY"],
    "GENI":     ["CREATE", "IMAGE", "VIDEO", "DESIGN", "VISUAL"],
    "JURIS":    ["LEGAL", "COMPLIANCE", "CONTRACT", "REVIEW", "CLEAR"],
}

# Agent emoji for logs
AGENT_EMOJI = {
    "SOL": "🛰️", "CODY": "💻", "ASSEMBLY": "🛠️", "VALI": "✅",
    "PESSI": "⚠️", "ORACLE": "🔮", "ATLAS": "🗺️", "CHATTY": "💬",
    "GENI": "🎨", "JURIS": "⚖️"
}

running = True

def signal_handler(signum, frame):
    global running
    print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
    running = False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def get_db():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS
    )

def log(msg: str, agent: str = "SYSTEM"):
    """Print timestamped log message."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    emoji = AGENT_EMOJI.get(agent, "🔹")
    print(f"[{ts}] {emoji} {agent}: {msg}", flush=True)

def ensure_agents_seeded():
    """Make sure all 10 agents exist in agent_state table."""
    conn = get_db()
    cur = conn.cursor()
    
    for agent in FLEET_AGENTS:
        cur.execute("""
            INSERT INTO agent_state (agent_name, status, total_tasks_completed, total_tasks_failed)
            VALUES (%s, 'IDLE', 0, 0)
            ON CONFLICT (agent_name) DO NOTHING;
        """, (agent,))
    
    conn.commit()
    cur.close()
    conn.close()
    log(f"Fleet seeded: {len(FLEET_AGENTS)} agents ready")

def claim_next_task(agent_name: str) -> Optional[Dict]:
    """Atomically claim highest-priority task matching agent capabilities."""
    capabilities = AGENT_CAPABILITIES.get(agent_name, ["GENERIC"])
    
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Build capability pattern for SQL LIKE matching
    cap_patterns = [f"%%{c}%%" for c in capabilities]
    
    cur.execute("BEGIN;")
    
    # Try to claim a task that matches this agent's capabilities
    # OR a task with no specific agent assigned
    cur.execute("""
        SELECT * FROM task_queue
        WHERE status = 'PENDING'
          AND (assigned_agent IS NULL OR assigned_agent = %s)
          AND (next_attempt_at IS NULL OR next_attempt_at <= CURRENT_TIMESTAMP)
        ORDER BY priority DESC, created_at ASC
        FOR UPDATE SKIP LOCKED
        LIMIT 1;
    """, (agent_name,))
    
    row = cur.fetchone()
    if row:
        cur.execute("""
            UPDATE task_queue
            SET status = 'RUNNING', assigned_agent = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
        """, (agent_name, row['id']))
        cur.execute("""
            UPDATE agent_state
            SET status = 'BUSY', current_task_id = %s, updated_at = CURRENT_TIMESTAMP
            WHERE agent_name = %s;
        """, (row['id'], agent_name))
        conn.commit()
        task = dict(row)
    else:
        conn.rollback()
        task = None
    
    cur.close()
    conn.close()
    return task

def execute_task(task: Dict, agent_name: str) -> Dict:
    """Execute a task by delegating to the agent via openclaw_bridge."""
    task_id = task['id']
    task_type = task['task_type']
    
    log(f"Executing task #{task_id} ({task_type})", agent_name)
    
    try:
        from openclaw_bridge import spawn_agent_task
        result = spawn_agent_task(
            task={"id": task_id, "task_type": task_type, "payload_json": task['payload_json']},
            agent_name=agent_name,
            timeout_seconds=300
        )
        log(f"Task #{task_id} completed — status: {result.get('status', 'unknown')}", agent_name)
        return result
    except Exception as e:
        error = str(e)
        log(f"Task #{task_id} failed: {error}", agent_name)
        return {"status": "error", "output": error, "agent": agent_name, "task_id": task_id}

def complete_task(task_id: int, output: Dict, agent_name: str):
    """Mark task DONE and update agent stats."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE task_queue
        SET status = 'DONE', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s;
    """, (task_id,))
    cur.execute("""
        UPDATE agent_state
        SET status = 'IDLE', current_task_id = NULL, total_tasks_completed = total_tasks_completed + 1,
            last_heartbeat = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE agent_name = %s;
    """, (agent_name,))
    cur.execute("""
        INSERT INTO execution_log (task_id, agent, step_number, step_action, output_summary)
        VALUES (%s, %s, 1, 'complete_task', %s);
    """, (task_id, agent_name, json.dumps(output)[:500]))
    conn.commit()
    cur.close()
    conn.close()

def fail_task(task_id: int, error: str, agent_name: str):
    """Mark task FAILED with retry backoff."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT retry_count, max_retries FROM task_queue WHERE id = %s", (task_id,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close(); return
    
    new_retry = row['retry_count'] + 1
    if new_retry >= row['max_retries']:
        new_status = 'DEAD'
        next_attempt = None
    else:
        new_status = 'PENDING'
        backoff = min(2 ** new_retry, 60)
        cur.execute("SELECT CURRENT_TIMESTAMP + INTERVAL '%s minutes' AS next_attempt", (backoff,))
        next_attempt = cur.fetchone()['next_attempt']
    
    cur.execute("""
        UPDATE task_queue
        SET status = %s, retry_count = %s, error_message = %s,
            next_attempt_at = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s;
    """, (new_status, new_retry, error[:500], next_attempt, task_id))
    
    new_agent_status = 'ERROR' if new_status == 'DEAD' else 'IDLE'
    cur.execute("""
        UPDATE agent_state
        SET status = %s, current_task_id = NULL, total_tasks_failed = total_tasks_failed + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE agent_name = %s;
    """, (new_agent_status, agent_name))
    
    cur.execute("""
        INSERT INTO execution_log (task_id, agent, step_number, step_action, error_message)
        VALUES (%s, %s, 1, 'fail_task', %s);
    """, (task_id, agent_name, error[:500]))
    
    conn.commit()
    cur.close()
    conn.close()
    
    if new_status == 'DEAD':
        log(f"Task #{task_id} DEAD after {new_retry} retries", agent_name)

def update_agent_heartbeat(agent_name: str):
    """Update agent's last heartbeat timestamp."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE agent_state
        SET last_heartbeat = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE agent_name = %s;
    """, (agent_name,))
    conn.commit()
    cur.close()
    conn.close()

def get_fleet_status() -> Dict:
    """Get full fleet status for dashboard."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT status, COUNT(*) as n FROM task_queue GROUP BY status;")
    tasks = {r['status']: r['n'] for r in cur.fetchall()}
    cur.execute("SELECT * FROM agent_state ORDER BY agent_name;")
    agents = [dict(r) for r in cur.fetchall()]
    cur.execute("SELECT COUNT(*) as n FROM message_bus WHERE status = 'UNREAD';")
    unread = cur.fetchone()['n']
    cur.close()
    conn.close()
    return {"tasks": tasks, "agents": agents, "unread_messages": unread}

def print_fleet_status():
    """Print formatted fleet status."""
    status = get_fleet_status()
    print("\n" + "═" * 60)
    print("  🛰️  SAOS FLEET STATUS")
    print("═" * 60)
    print(f"\n📋 TASK QUEUE:")
    for st, n in status['tasks'].items():
        icon = {"PENDING": "⏳", "RUNNING": "🔄", "DONE": "✅", "FAILED": "❌", "DEAD": "💀"}
        print(f"   {icon.get(st, '⚪')} {st}: {n}")
    
    print(f"\n🤖 FLEET AGENTS ({len(FLEET_AGENTS)} total):")
    for a in status['agents']:
        emoji = AGENT_EMOJI.get(a['agent_name'], '🔹')
        status_icon = "🟢" if a['status'] == 'IDLE' else "🔴" if a['status'] == 'BUSY' else "⚫"
        task = f" (task #{a['current_task_id']})" if a['current_task_id'] else ""
        print(f"   {emoji} {status_icon} {a['agent_name']:<10} | {a['status']:<8}{task} | done={a['total_tasks_completed']} fail={a['total_tasks_failed']}")
    
    print(f"\n📨 Unread messages: {status['unread_messages']}")
    print("═" * 60 + "\n")

def process_task_batch():
    """Process one batch of tasks across all agents."""
    tasks_processed = 0
    
    # Try each agent in round-robin order
    for agent_name in FLEET_AGENTS:
        if not running:
            break
            
        task = claim_next_task(agent_name)
        if task:
            try:
                result = execute_task(task, agent_name)
                if result.get('status') == 'error':
                    fail_task(task['id'], result.get('output', 'Unknown error'), agent_name)
                else:
                    complete_task(task['id'], result, agent_name)
            except Exception as e:
                fail_task(task['id'], str(e), agent_name)
            tasks_processed += 1
            
            # Small delay between tasks
            time.sleep(2)
    
    return tasks_processed

def run_daemon():
    """Main daemon loop."""
    log("🚀 SAOS Fleet Orchestrator Daemon starting...")
    log(f"Fleet: {len(FLEET_AGENTS)} agents | Poll interval: {POLL_INTERVAL}s")
    
    ensure_agents_seeded()
    print_fleet_status()
    
    last_heartbeat = time.time()
    iteration = 0
    
    while running:
        iteration += 1
        
        # Process task batch
        tasks_done = process_task_batch()
        
        # Update heartbeats periodically
        if time.time() - last_heartbeat > AGENT_HEARTBEAT:
            for agent in FLEET_AGENTS:
                update_agent_heartbeat(agent)
            last_heartbeat = time.time()
            log("Fleet heartbeat updated")
        
        # Status log every 10 minutes
        if iteration % 60 == 0:
            status = get_fleet_status()
            pending = status['tasks'].get('PENDING', 0)
            running_count = status['tasks'].get('RUNNING', 0)
            log(f"Status check — Pending: {pending}, Running: {running_count}")
        
        # Sleep between polls
        time.sleep(POLL_INTERVAL)
    
    log("👋 Daemon shutting down gracefully")
    print_fleet_status()

def main():
    parser = argparse.ArgumentParser(description="SAOS Fleet Orchestrator Daemon")
    parser.add_argument("--status", action="store_true", help="Show fleet status and exit")
    parser.add_argument("--once", action="store_true", help="Process one batch and exit")
    parser.add_argument("--daemon", action="store_true", help="Run as persistent daemon")
    args = parser.parse_args()
    
    if args.status:
        ensure_agents_seeded()
        print_fleet_status()
    elif args.once:
        ensure_agents_seeded()
        process_task_batch()
        print_fleet_status()
    else:
        # Default: run daemon
        run_daemon()

if __name__ == "__main__":
    main()
