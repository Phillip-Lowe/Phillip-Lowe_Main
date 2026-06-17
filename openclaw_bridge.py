#!/usr/bin/env python3
"""
OpenClaw Session Bridge for Orchestrator — Phase 2
- Spawns real isolated sub-agents via OpenClaw sessions_spawn
- Manages token budgets to prevent overload
- Returns structured output back to orchestrator

Token Safety Rules:
- qwen2.5-coder:7b: 32K context — limit prompts to 8K tokens
- llama3.2:3b: 128K context — limit to 16K tokens
- Never exceed 50% of model capacity
- Strip unnecessary context before spawning

Usage:
    from openclaw_bridge import spawn_agent_task
    result = spawn_agent_task(task, agent_name="ASSEMBLY")
"""

import os, sys, json, time, subprocess, textwrap, argparse
from typing import Dict, Optional, List

# ── CONFIG ─────────────────────────────────────────────────────────
OPENCLAW_WORKSPACE = os.path.expanduser("~/.openclaw/workspaces/sol")
TASKS_DIR = f"{OPENCLAW_WORKSPACE}/tasks"

# Token limits (conservative — never exceed 50% of model capacity)
MODEL_LIMITS = {
    "qwen2.5-coder:7b": {"context": 32768, "prompt_limit": 8000, "output_limit": 4000},
    "llama3.2:3b": {"context": 131072, "prompt_limit": 16000, "output_limit": 8000},
    "llama3.1:8b": {"context": 131072, "prompt_limit": 16000, "output_limit": 8000},
    "qwen3.5:9b": {"context": 262144, "prompt_limit": 16000, "output_limit": 8000},
    "gemma-2-9b": {"context": 8192, "prompt_limit": 3000, "output_limit": 2000},
}

# Default model for sub-agents (small, fast, reliable)
DEFAULT_SUBAGENT_MODEL = "llama3.2:3b"  # 3.2B, 128K context, 2GB RAM

# ── TOKEN ESTIMATION ───────────────────────────────────────────────
def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~1.3 tokens per word for English."""
    words = len(text.split())
    return int(words * 1.3)

def strip_context(prompt: str, max_tokens: int) -> str:
    """Strip prompt to fit within token budget."""
    current = estimate_tokens(prompt)
    if current <= max_tokens:
        return prompt
    
    # Truncate from the middle (keep beginning and end)
    lines = prompt.splitlines()
    if len(lines) > 20:
        # Keep first 10 lines and last 10 lines
        kept = lines[:10] + ["\n... [context truncated for token budget] ...\n"] + lines[-10:]
        prompt = "\n".join(kept)
    
    # If still too long, truncate brutally
    current = estimate_tokens(prompt)
    if current > max_tokens:
        max_chars = int(max_tokens / 1.3 * 0.9)  # 10% safety margin
        prompt = prompt[:max_chars] + "\n... [truncated]"
    
    return prompt

# ── SUB-AGENT SPAWNING ─────────────────────────────────────────────
def spawn_agent_task(task: Dict, agent_name: str = "SOL",
                     model: str = DEFAULT_SUBAGENT_MODEL,
                     timeout_seconds: int = 300) -> Dict:
    """
    Spawn an isolated OpenClaw sub-agent to execute a task.
    Uses sessions_spawn for clean, tracked execution.
    
    Returns: {"status": "ok|error", "output": str, "artifacts": [...]}
    """
    task_type = task.get("task_type", "GENERIC")
    payload = task.get("payload_json", {})
    goal = payload.get("goal", task_type)
    task_id = task.get("id", 0)
    
    # Get model limits
    limits = MODEL_LIMITS.get(model, MODEL_LIMITS[DEFAULT_SUBAGENT_MODEL])
    
    # Build stripped-down task prompt
    base_prompt = f"""You are {agent_name}, executing Task #{task_id}.

GOAL: {goal}"""
    
    # ── STEP CHAINING: Inject previous step output ──
    prev_task_id = payload.get('previous_task_id')
    if prev_task_id:
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=os.environ.get("PGHOST", "localhost"),
                port=int(os.environ.get("PGPORT", "5432")),
                dbname=os.environ.get("PGDATABASE", "systack_memory"),
                user=os.environ.get("PGUSER", "philliplowe"),
                password=os.environ.get("PGPASSWORD", "")
            )
            cur = conn.cursor()
            cur.execute("""
                SELECT output_summary FROM execution_log
                WHERE task_id = %s AND step_action = 'complete_task'
                ORDER BY created_at DESC LIMIT 1;
            """, (prev_task_id,))
            row = cur.fetchone()
            if row and row[0]:
                prev = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                prev_output = prev.get('output', str(prev)[:500])
                base_prompt += f"\n\n📋 PREVIOUS STEP (Task #{prev_task_id}) RESULT:\n```\n{prev_output[:600]}\n```\n\n↪ Build on the above result. Do NOT ignore it."
            cur.close()
            conn.close()
        except Exception:
            base_prompt += f"\n\n[Previous step Task #{prev_task_id} output unavailable]"
    
    base_prompt += """

RULES:
- Execute to completion in one turn
- Use file read/write, exec, web_search tools as needed
- Document what you did
- Return a structured summary
- Be concise — you have limited context window

OUTPUT FORMAT:
Return a JSON-like summary with:
- status: "completed" or "blocked"
- actions_taken: list of what you did
- files_created: list of paths
- result: brief outcome description
- next_steps: what should happen next (if anything)
"""
    
    # Add payload context (stripped)
    payload_json = json.dumps(payload, indent=2, default=str)
    context_section = f"\nPAYLOAD:\n```json\n{payload_json}\n```\n"
    
    full_prompt = base_prompt + context_section
    
    # Strip to token budget
    safe_prompt = strip_context(full_prompt, limits["prompt_limit"])
    prompt_tokens = estimate_tokens(safe_prompt)
    
    # Write task artifact (for reference)
    timestamp = int(time.time())
    artifact_dir = f"{TASKS_DIR}/{agent_name.lower()}"
    os.makedirs(artifact_dir, exist_ok=True)
    
    artifact_path = f"{artifact_dir}/task-{task_id}-{timestamp}.md"
    with open(artifact_path, 'w') as f:
        f.write(f"# Task #{task_id}: {goal}\n\n")
        f.write(f"**Agent:** {agent_name}\n")
        f.write(f"**Model:** {model}\n")
        f.write(f"**Prompt tokens:** {prompt_tokens} / {limits['prompt_limit']}\n")
        f.write(f"**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Prompt (Sent to Sub-Agent)\n\n")
        f.write(f"```\n{safe_prompt}\n```\n\n")
    
    # Spawn sub-agent via OpenClaw CLI
    # Using sessions_spawn through exec since sessions_spawn tool is for agent use
    try:
        result = _spawn_via_openclaw(
            prompt=safe_prompt,
            agent_name=agent_name,
            model=model,
            timeout=timeout_seconds,
            task_id=task_id
        )
        
        # Log result to artifact
        with open(artifact_path, 'a') as f:
            f.write("## Result\n\n")
            f.write(f"```json\n{json.dumps(result, indent=2, default=str)}\n```\n")
        
        return {
            "status": result.get("status", "unknown"),
            "output": result.get("output", ""),
            "artifacts": [artifact_path],
            "agent": agent_name,
            "task_id": task_id,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "task_type": task_type
        }
        
    except Exception as e:
        error_msg = str(e)
        with open(artifact_path, 'a') as f:
            f.write(f"## ERROR\n\n{error_msg}\n")
        
        return {
            "status": "error",
            "output": error_msg,
            "artifacts": [artifact_path],
            "agent": agent_name,
            "task_id": task_id,
            "task_type": task_type
        }


def _spawn_via_openclaw(prompt: str, agent_name: str, model: str,
                        timeout: int, task_id: int) -> Dict:
    """
    Execute task by running a real agent turn via OpenClaw CLI.
    
    HOW IT WORKS:
    1. Runs: openclaw agent --agent <agent> --message <prompt> --json
    2. Parses the resulting session JSONL to extract tool outputs
    3. Returns structured result
    
    VERIFIED: 2026-06-16 — VALI successfully executed 'echo hello-from-vali'
    via this exact mechanism. Session file at:
    ~/.openclaw/agents/vali/sessions/
    """
    import uuid
    
    # Normalize agent name
    agent_id = agent_name.lower()
    valid_agents = ['sol', 'assembly', 'pessi', 'chatty', 'geni', 'vali', 'cody', 'atlas']
    if agent_id not in valid_agents:
        agent_id = 'sol'  # Fallback to SOL for unknown agents
    
    # Build the prompt to encourage tool usage and structured output
    wrapped_prompt = f"""Execute this task and return your result as structured text.

TASK: {prompt}

RULES:
- Use tools (exec, read, write, etc.) to accomplish the task
- Return a clear summary of what you did
- If you use exec, capture the output
- Be concise — state the result clearly

YOUR RESPONSE SHOULD INCLUDE:
- What action you took
- The output or result
- Any files created or modified
"""
    
    try:
        cmd = [
            "openclaw", "agent",
            "--agent", agent_id,
            "--message", wrapped_prompt[:4000],
            "--json",
            "--timeout", str(min(timeout, 300))
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=min(timeout, 300) + 30
        )
        
        if result.returncode != 0:
            return {
                "status": "error",
                "output": f"Agent turn failed (rc={result.returncode}): {result.stderr[:1000]}",
                "stdout": result.stdout[:500],
                "method": "agent_turn_failed"
            }
        
        # Parse JSON output to get session ID
        try:
            json_output = json.loads(result.stdout)
            meta = json_output.get("result", {}).get("meta", {})
            session_file = meta.get("agentMeta", {}).get("sessionFile", "")
            session_id = meta.get("agentMeta", {}).get("sessionId", "")
            tool_summary = meta.get("toolSummary", {})
            
            # Extract tool results from session JSONL
            tool_outputs = []
            if session_file and os.path.isfile(session_file):
                tool_outputs = _extract_tool_results_from_session(session_file)
        
        except json.JSONDecodeError:
            session_file = ""
            session_id = ""
            tool_summary = {}
            tool_outputs = []
        
        # Determine status from tool usage
        tool_calls = tool_summary.get("calls", 0)
        tool_failures = tool_summary.get("failures", 0)
        
        if tool_calls > 0 and tool_failures == 0:
            status = "completed"
        elif tool_calls > 0 and tool_failures > 0:
            status = "partial"
        else:
            status = "completed"  # Agent completed without needing tools
        
        # Compile output from tool results
        if tool_outputs:
            output_text = "\n".join([
                f"[{o['tool']}]: {o['output'][:500]}"
                for o in tool_outputs[:5]
            ])
        else:
            # Fallback: parse the assistant's text response from JSONL
            output_text = _extract_assistant_text(session_file) if session_file else "Agent completed (no tools used)"
        
        return {
            "status": status,
            "output": output_text[:2000],
            "tool_calls": tool_calls,
            "tool_failures": tool_failures,
            "tool_outputs": tool_outputs[:5],
            "session_id": session_id,
            "session_file": session_file,
            "method": "agent_turn",
            "agent": agent_id,
            "rc": result.returncode
        }
        
    except FileNotFoundError:
        return {
            "status": "blocked",
            "output": "OpenClaw CLI not available",
            "method": "cli_unavailable"
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "blocked",
            "output": f"Agent turn timed out after {min(timeout, 300)}s",
            "method": "agent_timeout"
        }
    except Exception as e:
        return {
            "status": "error",
            "output": f"Agent turn error: {str(e)}",
            "method": "agent_exception"
        }


def _extract_tool_results_from_session(session_file: str) -> List[Dict]:
    """
    Parse agent session JSONL to extract tool call results.
    
    Looks for messages of type "toolResult" and extracts:
    - toolName
    - content (the tool output)
    - status/exitCode
    """
    results = []
    if not os.path.isfile(session_file):
        return results
    
    try:
        with open(session_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    if msg.get("type") == "message" and msg.get("message", {}).get("role") == "toolResult":
                        content_blocks = msg.get("message", {}).get("content", [])
                        content_text = ""
                        for block in content_blocks:
                            if block.get("type") == "text":
                                content_text += block.get("text", "")
                        
                        details = msg.get("message", {}).get("details", {})
                        results.append({
                            "tool": msg.get("message", {}).get("toolName", "unknown"),
                            "output": content_text,
                            "exit_code": details.get("exitCode"),
                            "status": details.get("status"),
                            "timestamp": msg.get("timestamp")
                        })
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        results.append({"tool": "parse_error", "output": str(e), "error": True})
    
    return results


def _extract_assistant_text(session_file: str) -> str:
    """Extract the final assistant text response from session JSONL."""
    if not os.path.isfile(session_file):
        return "Session file not found"
    
    texts = []
    try:
        with open(session_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    if msg.get("type") == "message" and msg.get("message", {}).get("role") == "assistant":
                        content = msg.get("message", {}).get("content", [])
                        for block in content:
                            if block.get("type") == "text":
                                text = block.get("text", "")
                                if text and text != "NO_REPLY":
                                    texts.append(text)
                except json.JSONDecodeError:
                    continue
    except Exception:
        return "Failed to read session"
    
    # Return last assistant text
    return texts[-1] if texts else "No assistant response captured"


def _execute_direct_tools(prompt: str, agent_name: str, task_id: int) -> Optional[Dict]:
    """
    FALLBACK: Parse the task prompt and execute directly using Python libraries.
    Only used when agent turn is unavailable or for simple/fast operations.
    
    This is NOT the preferred path — agent turns are preferred per architecture.
    """
    import re
    
    prompt_lower = prompt.lower()
    
    # ── SHELL_EXEC (direct fallback) ──
    shell_match = re.search(r'["\']?command["\']?\s*[:=]\s*["\']([^"\']+)["\']', prompt, re.I)
    if not shell_match:
        shell_match = re.search(r'run[:\s]+(.+?)(?:\n|$)', prompt, re.I)
    
    if shell_match or 'shell_exec' in prompt_lower:
        cmd = shell_match.group(1).strip() if shell_match else None
        if cmd:
            dangerous = ['rm -rf /', 'rm -rf ~', 'drop ', 'delete from ', 
                        'shutdown', 'reboot', 'mkfs', 'dd if=', '> /dev/null']
            if any(d in cmd.lower() for d in dangerous):
                return {
                    "status": "blocked",
                    "output": f"SAFETY: Command '{cmd}' rejected",
                    "method": "direct_shell_blocked"
                }
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                return {
                    "status": "completed",
                    "output": result.stdout[:2000],
                    "stderr": result.stderr[:1000],
                    "rc": result.returncode,
                    "method": "direct_shell_exec",
                    "command": cmd
                }
            except Exception as e:
                return {"status": "error", "output": f"Shell error: {e}", "method": "direct_shell_error"}
    
    # ── FILE_READ (direct fallback) ──
    read_match = re.search(r'(?:read|cat|show)\s+(?:file\s+)?["\']?([^"\']+\.\w+)["\']?', prompt, re.I)
    if read_match or 'file_read' in prompt_lower:
        filepath = read_match.group(1).strip() if read_match else None
        if filepath and os.path.isfile(filepath):
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                return {"status": "completed", "output": content[:3000], "method": "direct_file_read", "file": filepath}
            except Exception as e:
                return {"status": "error", "output": f"Read error: {e}", "method": "direct_file_error"}
    
    # ── FILE_WRITE (direct fallback) ──
    write_match = re.search(r'(?:write|save|create)\s+(?:to\s+)?["\']?([^"\']+\.\w+)["\']?', prompt, re.I)
    if write_match or 'file_write' in prompt_lower:
        content_match = re.search(r'(?:content|body)[:\s]+(.+?)(?:\n#|$)', prompt, re.S | re.I)
        if not content_match:
            content_match = re.search(r'```(?:\w+)?\s*(.+?)```', prompt, re.S)
        filepath = write_match.group(1).strip() if write_match else None
        if filepath and content_match:
            content = content_match.group(1).strip()
            try:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w') as f:
                    f.write(content)
                return {"status": "completed", "output": f"Written {len(content)} chars to {filepath}", "method": "direct_file_write", "file": filepath}
            except Exception as e:
                return {"status": "error", "output": f"Write error: {e}", "method": "direct_write_error"}
    
    # ── POSTGRES_QUERY (direct fallback) ──
    if 'postgres_query' in prompt_lower or ('select ' in prompt_lower and 'from ' in prompt_lower):
        sql_match = re.search(r'```sql\s*(.+?)```', prompt, re.S | re.I)
        if not sql_match:
            sql_match = re.search(r'(?:query|sql)[:\s]+(.+?)(?:\n\n|$)', prompt, re.S | re.I)
        if sql_match:
            query = sql_match.group(1).strip()
            if query.lower().startswith('select') or query.lower().startswith('with'):
                try:
                    conn = psycopg2.connect(
                        host=os.environ.get("PGHOST", "localhost"),
                        port=int(os.environ.get("PGPORT", "5432")),
                        dbname=os.environ.get("PGDATABASE", "systack_memory"),
                        user=os.environ.get("PGUSER", "philliplowe"),
                        password=os.environ.get("PGPASSWORD", "")
                    )
                    cur = conn.cursor()
                    cur.execute(query)
                    rows = cur.fetchall()
                    colnames = [desc[0] for desc in cur.description] if cur.description else []
                    cur.close(); conn.close()
                    return {"status": "completed", "output": {"columns": colnames, "rows": rows[:50]}, "method": "direct_postgres_query", "query": query}
                except Exception as e:
                    return {"status": "error", "output": f"Query error: {e}", "method": "direct_postgres_error"}
            else:
                return {"status": "blocked", "output": "Non-SELECT queries require approval", "method": "direct_postgres_safety"}
    
    # No direct tool matched — agent will handle it
    return None


# ── WEB DASHBOARD DATA ─────────────────────────────────────────────
def get_dashboard_data() -> Dict:
    """Return current system state for web dashboard."""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=int(os.environ.get("PGPORT", "5432")),
        dbname=os.environ.get("PGDATABASE", "systack_memory"),
        user=os.environ.get("PGUSER", "philliplowe"),
        password=os.environ.get("PGPASSWORD", "")
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Task stats
    cur.execute("SELECT status, COUNT(*) as n FROM task_queue GROUP BY status")
    tasks = {r['status']: r['n'] for r in cur.fetchall()}
    
    # Recent tasks
    cur.execute("""
        SELECT id, task_type, status, assigned_agent, priority, created_at, updated_at
        FROM task_queue ORDER BY updated_at DESC LIMIT 20
    """)
    recent_tasks = [dict(r) for r in cur.fetchall()]
    
    # Agent status
    cur.execute("SELECT * FROM agent_state ORDER BY agent_name")
    agents = [dict(r) for r in cur.fetchall()]
    
    # Messages
    cur.execute("SELECT COUNT(*) as n FROM message_bus WHERE status = 'UNREAD'")
    unread = cur.fetchone()['n']
    
    # Execution log (recent)
    cur.execute("""
        SELECT task_id, agent, step_action, error_message, created_at
        FROM execution_log ORDER BY created_at DESC LIMIT 10
    """)
    recent_log = [dict(r) for r in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tasks": tasks,
        "recent_tasks": recent_tasks,
        "agents": agents,
        "unread_messages": unread,
        "recent_log": recent_log,
        "models": {k: {"context": v["context"], "prompt_limit": v["prompt_limit"]}
                   for k, v in MODEL_LIMITS.items()}
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenClaw Bridge")
    parser.add_argument("--test", action="store_true", help="Test spawn with dummy task")
    parser.add_argument("--dashboard", action="store_true", help="Output dashboard JSON")
    parser.add_argument("--task-id", type=int, help="Test with specific task ID")
    args = parser.parse_args()
    
    if args.dashboard:
        data = get_dashboard_data()
        print(json.dumps(data, indent=2, default=str))
    elif args.test:
        test_task = {
            "id": args.task_id or 999,
            "task_type": "TEST",
            "payload_json": {"goal": "Test OpenClaw bridge spawn", "test": True}
        }
        result = spawn_agent_task(test_task, "TEST_AGENT")
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Usage: --test | --dashboard")
        print(f"Models configured: {list(MODEL_LIMITS.keys())}")
