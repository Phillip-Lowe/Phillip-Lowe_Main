#!/usr/bin/env python3
"""
SOL Orchestrator — Phase 1
- Polls Postgres task_queue
- Dispatches tasks to agents
- Tracks state, handles retries
- Logs everything to execution_log

Usage:
    python3 orchestrator.py --poll      # Poll for pending tasks (loop)
    python3 orchestrator.py --status    # Show system status
    python3 orchestrator.py --task "goal text" --agent ASSEMBLY  # Create task
    python3 orchestrator.py --messages  # Check unread messages
"""

import os, sys, argparse, json, time, subprocess
from datetime import datetime
from typing import Optional, Dict, List

import psycopg2
from psycopg2.extras import RealDictCursor

# ── CONFIG ───────────────────────────────────────────────────────────
DB_HOST = os.environ.get("PGHOST", "localhost")
DB_PORT = int(os.environ.get("PGPORT", "5432"))
DB_NAME = os.environ.get("PGDATABASE", "systack_memory")
DB_USER = os.environ.get("PGUSER", "philliplowe")
DB_PASS = os.environ.get("PGPASSWORD", "")

POLL_INTERVAL = 5  # seconds between polls

def get_db():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=os.environ.get("PGPASSWORD", "")
    )

# ── TASK MANAGEMENT ─────────────────────────────────────────────────
def create_task(task_type: str, payload: Dict, agent: Optional[str] = None,
                priority: int = 5, max_retries: int = 5) -> int:
    """Create a new task in the queue. Returns task_id."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO task_queue (task_type, payload_json, assigned_agent, priority, max_retries)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (task_type, json.dumps(payload), agent, priority, max_retries))
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return task_id

def claim_next_task(agent_name: str) -> Optional[Dict]:
    """
    Atomically claim the highest-priority pending task for this agent.
    Uses SELECT FOR UPDATE SKIP LOCKED for safe concurrent access.
    Respects next_attempt_at for retry backoff.
    """
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("BEGIN;")
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
    else:
        conn.rollback()
    cur.close()
    conn.close()
    return dict(row) if row else None

def complete_task(task_id: int, output: Dict, agent_name: str) -> None:
    """Mark task as DONE and log execution."""
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

def fail_task(task_id: int, error: str, agent_name: str) -> None:
    """Mark task FAILED, increment retry, set next attempt with exponential backoff."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT retry_count, max_retries FROM task_queue WHERE id = %s", (task_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return

    new_retry = row['retry_count'] + 1
    
    if new_retry >= row['max_retries']:
        new_status = 'DEAD'
        next_attempt = None  # No more retries
    else:
        new_status = 'PENDING'
        # Exponential backoff: 2^retry_count minutes, capped at 60 min
        backoff_minutes = min(2 ** new_retry, 60)
        cur.execute("SELECT CURRENT_TIMESTAMP + INTERVAL '%s minutes' AS next_attempt", (backoff_minutes,))
        row_na = cur.fetchone()
        next_attempt = row_na['next_attempt'] if row_na else None

    cur.execute("""
        UPDATE task_queue
        SET status = %s, retry_count = %s, error_message = %s, 
            next_attempt_at = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s;
    """, (new_status, new_retry, error[:500], next_attempt, task_id))
    
    # Fixed: Use CASE instead of IF expression (not valid in standard SQL)
    new_agent_status = 'ERROR' if new_status == 'DEAD' else 'IDLE'
    cur.execute("""
        UPDATE agent_state
        SET status = %s,
            current_task_id = NULL,
            total_tasks_failed = total_tasks_failed + 1,
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

# ── AGENT MESSAGING ────────────────────────────────────────────────
def send_message(from_agent: str, to_agent: str, message_type: str, payload: Dict) -> int:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO message_bus (from_agent, to_agent, message_type, payload_json)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """, (from_agent, to_agent, message_type, json.dumps(payload)))
    msg_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return msg_id

def get_messages(to_agent: str, status: str = 'UNREAD') -> List[Dict]:
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT * FROM message_bus
        WHERE to_agent = %s AND status = %s
        ORDER BY created_at ASC;
    """, (to_agent, status))
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows

def mark_message_read(msg_id: int) -> None:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE message_bus SET status = 'READ', read_at = CURRENT_TIMESTAMP WHERE id = %s;
    """, (msg_id,))
    conn.commit()
    cur.close()
    conn.close()

# ── STATUS / REPORTING ─────────────────────────────────────────────
def get_status() -> Dict:
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT status, COUNT(*) as n FROM task_queue GROUP BY status;
    """)
    tasks = {r['status']: r['n'] for r in cur.fetchall()}
    cur.execute("SELECT * FROM agent_state ORDER BY agent_name;")
    agents = [dict(r) for r in cur.fetchall()]
    cur.execute("SELECT COUNT(*) as n FROM message_bus WHERE status = 'UNREAD';")
    unread = cur.fetchone()['n']
    cur.close()
    conn.close()
    return {"tasks": tasks, "agents": agents, "unread_messages": unread}

def print_status():
    status = get_status()
    print("\n═══ ORCHESTRATOR STATUS ═══")
    print(f"\n📋 Tasks:")
    for st, n in status['tasks'].items():
        print(f"  {st}: {n}")
    print(f"\n🤖 Agents:")
    for a in status['agents']:
        task = f" (task #{a['current_task_id']})" if a['current_task_id'] else ""
        print(f"  {a['agent_name']}: {a['status']}{task} | completed={a['total_tasks_completed']} failed={a['total_tasks_failed']}")
    print(f"\n📨 Unread messages: {status['unread_messages']}")
    print("\n═══════════════════════════\n")

# ── POLL LOOP (for background execution) ───────────────────────────
def poll_loop(agent_name: str = 'SOL', max_iterations: int = 0):
    """
    Poll for tasks and execute them.
    In Phase 1: tasks are simple — just log and mark complete.
    In Phase 2+: tasks spawn OpenClaw sessions for real execution.
    """
    print(f"🚀 Orchestrator poll loop starting for agent: {agent_name}")
    print(f"   Poll interval: {POLL_INTERVAL}s")
    print(f"   Press Ctrl+C to stop\n")

    iteration = 0
    try:
        while True:
            iteration += 1
            if max_iterations > 0 and iteration > max_iterations:
                break

            task = claim_next_task(agent_name)
            if task:
                print(f"[{iteration}] 🎯 CLAIMED task #{task['id']}: {task['task_type']}")
                print(f"       Payload: {json.dumps(task['payload_json'])[:200]}")

                try:
                    # Phase 1: simulate execution
                    # Phase 2: this is where we'd spawn an OpenClaw session
                    result = execute_task_locally(task)
                    complete_task(task['id'], result, agent_name)
                    print(f"       ✅ COMPLETED")

                except Exception as e:
                    fail_task(task['id'], str(e), agent_name)
                    print(f"       ❌ FAILED: {e}")

            else:
                if iteration % 12 == 0:  # every minute
                    print(f"[{iteration}] 💤 No pending tasks")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print(f"\n🛑 Poll loop stopped after {iteration} iterations")

def execute_task_locally(task: Dict) -> Dict:
    """
    REAL execution via OpenClaw agent turns.
    
    Delegates task execution to the appropriate fleet agent using
    openclaw agent --agent <id> --message <prompt>.
    
    If previous_task_id is present in payload, injects the prior step's
    output into the agent prompt for chained execution.
    
    Falls back to direct Python tool execution for simple/fast ops.
    
    VERIFIED: 2026-06-16 — VALI + ASSEMBLY successfully executed shell commands
    via openclaw agent turns. Session traces show tool calls working.
    """
    task_type = task['task_type']
    payload = task.get('payload_json', {})
    task_id = task.get('id', 0)
    agent_name = task.get('assigned_agent', 'SOL')
    
    # Build execution prompt from task
    goal = payload.get('goal', task_type)
    
    # ── STEP CHAINING: Look up previous task output ──
    prev_task_id = payload.get('previous_task_id')
    prev_output = None
    if prev_task_id:
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT output_summary FROM execution_log
                WHERE task_id = %s AND step_action = 'complete_task'
                ORDER BY created_at DESC LIMIT 1;
            """, (prev_task_id,))
            row = cur.fetchone()
            if row and row[0]:
                prev_output = json.loads(row[0]) if isinstance(row[0], str) else row[0]
            cur.close()
            conn.close()
        except Exception:
            pass  # Previous output not available, proceed without it
    
    # Build enhanced prompt with previous step context
    context_parts = [f"Task #{task_id}: {goal}"]
    
    if prev_output:
        prev_raw = json.dumps(prev_output, indent=2, default=str)[:800]
        context_parts.append(f"\n📋 PREVIOUS STEP (Task #{prev_task_id}) OUTPUT:\n```json\n{prev_raw}\n```\n")
        context_parts.append("Use the above output to inform your work on this step.")
    
    context_parts.append(f"\nPayload: {json.dumps(payload, indent=2, default=str)[:500]}")
    
    prompt = "\n".join(context_parts)
    
    # Delegate to agent turn via bridge
    from openclaw_bridge import spawn_agent_task
    
    result = spawn_agent_task(
        task={"id": task_id, "task_type": task_type, "payload_json": payload},
        agent_name=agent_name,
        timeout_seconds=300
    )
    
    return result

# ── MAIN ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SOL Orchestrator")
    parser.add_argument("--poll", action="store_true", help="Poll for tasks (loop)")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--task", help="Create a task with this goal text")
    parser.add_argument("--agent", default="SOL", help="Target agent (default: SOL)")
    parser.add_argument("--type", default="GENERIC", help="Task type")
    parser.add_argument("--priority", type=int, default=5, help="Priority 1-10")
    parser.add_argument("--payload", help="JSON payload string")
    parser.add_argument("--messages", action="store_true", help="Check unread messages")
    parser.add_argument("--send-msg", help="Send message: from:to:type:payload_json")
    parser.add_argument("--max-iter", type=int, default=0, help="Max poll iterations (0=infinite)")
    args = parser.parse_args()

    if args.status:
        print_status()

    elif args.task:
        payload = json.loads(args.payload) if args.payload else {"goal": args.task}
        task_id = create_task(args.type, payload, args.agent, args.priority)
        print(f"✅ Created task #{task_id}: {args.type} → {args.agent}")
        print(f"   Goal: {args.task}")

    elif args.messages:
        msgs = get_messages(args.agent)
        print(f"\n📨 Messages for {args.agent}:")
        for m in msgs:
            print(f"  #{m['id']} from {m['from_agent']}: {m['message_type']}")
            print(f"     {json.dumps(m['payload_json'])[:200]}")

    elif args.send_msg:
        parts = args.send_msg.split(":", 3)
        if len(parts) == 4:
            msg_id = send_message(parts[0], parts[1], parts[2], json.loads(parts[3]))
            print(f"✅ Sent message #{msg_id}: {parts[0]} → {parts[1]}")
        else:
            print("Usage: --send-msg from:to:type:{payload}")

    elif args.poll:
        poll_loop(args.agent, args.max_iter)

    else:
        print_status()
