---
name: fleet-orchestrator
description: "Coordinate multi-agent task execution across the SAOS fleet with task creation, agent assignment, status tracking, and inter-agent messaging via the orchestrator daemon."
---

# Fleet Orchestrator

Coordinate work across the SAOS agent fleet. Task creation → agent assignment → execution tracking → completion handling.

## When to Use
- Multi-step project spanning multiple agents
- Need background task execution (non-blocking)
- Inter-agent communication required
- Long-running tasks with progress updates
- Parallel execution of independent subtasks

## Fleet Agents

| Agent | Role | Typical Tasks |
|-------|------|-------------|
| **SOL** | Orchestrator | Task routing, execution, status |
| **CODY** | Build Engine | Code, scripts, technical implementation |
| **ASSEMBLY** | Deployment | Deploy, configure, verify |
| **VALI** | Validation | Test, audit, verify correctness |
| **PESSI** | Risk Analysis | Assess risks, flag pitfalls |
| **ORACLE** | Design/Architecture | System design, patterns |
| **ATLAS** | Knowledge | Memory, documentation, research |
| **CHATTY** | Communication | Messages, social media, outreach |
| **GENI** | Creative | Images, design, visual assets |
| **JURIS** | Legal/Compliance | Contracts, compliance, policies |

## System Loop

```
ORACLE → Design → CODY → Build → ASSEMBLY → Deploy → VALI → Validate →
PESSI → Stress-test → SOL → Execute → CHATTY → Communicate → GENI → Visualize →
ATLAS → Store → JURIS → Legal → [Loop]
```

## Task Creation

```python
# orchestrator.py
from orchestrator import TaskManager, MessageBus

tm = TaskManager()

# Create task
task = tm.create_task(
    goal="Build invoice dashboard for Utopia Deli",
    assigned_agent="CODY",
    priority=8,  # 1-10
    task_type="BUILD",
    context={
        "client": "utopia-deli",
        "deadline": "2026-06-21",
        "requirements": [...]
    }
)

# Assign to CODY
tm.assign(task.id, agent="CODY")

# Poll for status
status = tm.get_status(task.id)
```

## Inter-Agent Messaging

```python
# Message bus for agent communication
bus = MessageBus()

# CODY sends status update
bus.send(
    sender="CODY",
    recipient="SOL",
    type="TASK_PROGRESS",
    payload={"task_id": "123", "progress": 0.5, "status": "building_frontend"}
)

# VALI reports test results
bus.send(
    sender="VALI",
    recipient="SOL",
    type="VALIDATION_COMPLETE",
    payload={"task_id": "123", "passed": True, "notes": "All tests green"}
)

# PESSI flags risk
bus.send(
    sender="PESSI",
    recipient="SOL",
    type="RISK_ALERT",
    payload={"level": "MEDIUM", "issue": "No error handling on API endpoint"}
)
```

## Task States

```
CREATED → ASSIGNED → IN_PROGRESS → REVIEW → COMPLETE
              ↓           ↓
          PAUSED     FAILED → RETRY → IN_PROGRESS
              ↓           ↓
          CANCELLED   ESCALATED → ORACLE
```

## Command Line Interface

```bash
# Check system status
python3 orchestrator.py --status

# Create a task
python3 orchestrator.py --task "Build invoice dashboard" --agent CODY --type BUILD --priority 8

# Poll for tasks (background)
python3 orchestrator.py --poll --agent SOL

# Check messages
python3 orchestrator.py --messages --agent SOL

# List all tasks
python3 orchestrator.py --list

# Get task details
python3 orchestrator.py --get-task <task-id>
```

## Integration with OpenClaw

```python
# Execute task via OpenClaw CLI bridge
from openclaw_bridge import spawn_agent_session

result = spawn_agent_session(
    agent_id="cody",
    task="Implement error handling on API endpoint",
    timeout=600
)

# Parse result
if result["status"] == "success":
    tm.complete_task(task_id, result["artifacts"])
else:
    tm.fail_task(task_id, result["error"])
```

## Task Types

| Type | Description | Example |
|------|-------------|---------|
| BUILD | Code/script development | "Build order form" |
| DEPLOY | Infrastructure deployment | "Deploy to Netlify" |
| VALIDATE | Testing and verification | "Run payment flow test" |
| RESEARCH | Information gathering | "Find competitor pricing" |
| DESIGN | Architecture planning | "Design booking system" |
| CONTENT | Writing/creative | "Write LinkedIn post" |
| AUDIT | Security/compliance review | "Audit credential storage" |
| COMMUNICATION | External messaging | "Send client update" |

## Retry Logic

```python
def execute_with_retry(task, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = execute_task_locally(task)
            return result
        except TemporaryError as e:
            if attempt < max_retries - 1:
                delay = 2 ** attempt * 30  # 30s, 60s, 120s
                time.sleep(delay)
            else:
                raise
        except PermanentError as e:
            # No retry — escalate
            escalate_to_oracle(task, e)
            raise
```

## Daily Learning Job

Orchestrator powers the daily learning system:

```bash
# Cron job runs daily
0 6 * * * cd ~/.openclaw/workspaces/sol && python3 daily_learning_orchestrator.py
```

- **Model**: ollama/qwen2.5-coder:7b
- **Timeout**: 900s (15 min)
- **Context**: Light (essential only)

## Safety

- **No infinite loops**: Max 5 retries, then fail
- **Timeout enforcement**: Kill stuck tasks
- **Resource limits**: Max 3 concurrent tasks per agent
- **Escalation**: ORACLE handles architecture questions
- **Approval gate**: PESSI flags risky actions

## Files

- `saos/orchestrator.py` — Main orchestrator
- `saos/orchestrator-daemon.py` — Background daemon
- `saos/openclaw_bridge.py` — OpenClaw CLI integration
- `saos/scripts/agent-return-schema.py` — Result schema
- `saos/scripts/fleet-drift-lint.py` — Fleet health checker
- `ORCHESTRATOR-STATUS.md` — Current status

## Gotchas

| Issue | Fix |
|-------|-----|
| Task stuck in IN_PROGRESS | Check agent session still alive |
| Messages lost | MessageBus is in-memory — use disk persistence |
| Agent overlap | Assign unique task IDs, check before spawning |
| Memory leak | Limit concurrent tasks, enforce timeouts |
| Bridge failure | Fallback to direct OpenClaw session |

## Reference

- Architecture: `docs/ORACLE-SUPPLEMENTAL-DATA.md`
- Full spec: `ORACLE-FUNNEL-HANDOFF-SUMMARY.md`
- Deployment plan: `SAOS-PROVISIONING-BUILD-PLAN.md`
- Fleet docs: `fleet/` directory
