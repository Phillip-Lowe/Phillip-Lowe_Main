#!/usr/bin/env python3
"""
Plan Executor — Connects planner output to orchestrator task queue.

Reads a plan JSON and creates one task per step in the orchestrator queue.
Handles agent assignment based on tool type.

Usage:
    python3 planner.py "Build a file logger" | python3 plan_executor.py --plan - --execute
    python3 plan_executor.py --plan plan.json --execute
    python3 plan_executor.py --intent "Research invoice parsers" --execute
"""

import os, sys, argparse, json
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orchestrator import create_task

# Map tools to agents
TOOL_AGENT_MAP = {
    "shell_exec": "ASSEMBLY",
    "file_read": "SOL",
    "file_write": "ASSEMBLY",
    "postgres_query": "ASSEMBLY",
    "rag_retrieve": "ATLAS",
    "n8n_api": "ASSEMBLY",
    "openclaw_session": "SOL",
    "browser_automation": "SOL",
    "web_search": "SOL",
    "web_fetch": "SOL",
}

# Map step action keywords to task types
ACTION_TYPE_MAP = {
    "research": "RESEARCH",
    "retrieve": "RESEARCH",
    "analyze": "RESEARCH",
    "build": "BUILD",
    "generate": "BUILD",
    "create": "BUILD",
    "execute": "EXECUTE_SHELL",
    "run": "EXECUTE_SHELL",
    "deploy": "DEPLOY_WORKFLOW",
    "validate": "VALIDATE_OUTPUT",
    "test": "VALIDATE_OUTPUT",
    "verify": "VALIDATE_OUTPUT",
    "check": "RISK_CHECK",
    "risk": "RISK_CHECK",
}


def resolve_agent(step: Dict) -> str:
    """Determine which agent should execute this step."""
    tool = step.get("tool", "openclaw_session")
    return TOOL_AGENT_MAP.get(tool, "SOL")


def resolve_task_type(step: Dict) -> str:
    """Determine task type from step action."""
    action = step.get("action", "").lower()
    for keyword, task_type in ACTION_TYPE_MAP.items():
        if keyword in action:
            return task_type
    return "GENERIC"


def resolve_priority(step_index: int, total_steps: int) -> int:
    """Higher priority for earlier steps and validation steps."""
    base = 5
    # Earlier steps = higher priority (dependency order)
    if step_index == 0:
        base = 9
    elif step_index == total_steps - 1:
        base = 8  # Validation is important
    elif step_index < total_steps / 2:
        base = 7
    return base


def step_to_payload(step: Dict, plan_goal: str, step_index: int, total_steps: int) -> Dict:
    """Convert a planner step into orchestrator payload."""
    params = step.get("params", {})
    tool = step.get("tool", "openclaw_session")
    action = step.get("action", "")
    
    payload = {
        "goal": f"{plan_goal} — Step {step_index + 1}/{total_steps}: {action}",
        "step_index": step_index,
        "total_steps": total_steps,
        "original_tool": tool,
        "original_action": action,
    }
    
    # Merge params based on tool type
    if tool == "shell_exec" and "command" in params:
        payload["command"] = params["command"]
    elif tool == "file_read" and "path" in params:
        payload["command"] = f"cat {params['path']}"
    elif tool == "file_write" and "path" in params:
        payload["command"] = f"cat > {params['path']}"
        payload["content"] = params.get("content", "")
    elif tool == "postgres_query" and "query" in params:
        payload["command"] = f"psql -c \"{params['query']}\""
    elif tool == "rag_retrieve":
        payload["query"] = params.get("query", plan_goal)
    elif tool == "n8n_api":
        payload["workflow"] = params.get("workflow", "")
    elif tool == "openclaw_session":
        payload["prompt"] = params.get("prompt", action)
    elif tool in ("web_search", "web_fetch"):
        payload["query"] = params.get("query", plan_goal)
        payload["url"] = params.get("url", "")
    
    return payload


def execute_plan(plan: Dict, dry_run: bool = False, chain_steps: bool = True) -> List[int]:
    """
    Create orchestrator tasks for each step in the plan.
    Returns list of created task IDs.
    
    If chain_steps=True, each task payload includes previous_task_id
    so the orchestrator can inject prior step output into the agent prompt.
    """
    goal = plan.get("goal", "Unnamed plan")
    steps = plan.get("steps", [])
    total = len(steps)
    
    print(f"🎯 PLAN: {goal}")
    print(f"📋 {total} steps")
    print()
    
    if total == 0:
        print("❌ No steps in plan")
        return []
    
    task_ids = []
    
    for i, step in enumerate(steps):
        agent = resolve_agent(step)
        task_type = resolve_task_type(step)
        priority = resolve_priority(i, total)
        payload = step_to_payload(step, goal, i, total)
        
        # Chain steps: reference previous task if available
        if chain_steps and i > 0:
            payload["previous_task_id"] = task_ids[i - 1]
            payload["previous_step_index"] = i - 1
            payload["depends_on"] = task_ids[i - 1]
        
        print(f"  Step {i + 1}/{total}: [{task_type}] {step.get('action', '?')} → {agent} (priority={priority})")
        if chain_steps and i > 0:
            print(f"    ← Depends on Task #{task_ids[i - 1]} (Step {i})")
        
        if not dry_run:
            task_id = create_task(task_type, payload, agent, priority)
            task_ids.append(task_id)
            print(f"    → Task #{task_id} created")
        else:
            print(f"    → (dry run — not created)")
    
    print()
    if dry_run:
        print(f"🏃 DRY RUN — {total} tasks would be created")
    else:
        print(f"✅ {len(task_ids)} tasks created")
        if chain_steps and len(task_ids) > 1:
            print(f"   Steps chained: Task {task_ids[0]} → ... → Task {task_ids[-1]}")
        print(f"   Run: python3 orchestrator.py --poll --agent ASSEMBLY")
    
    return task_ids


def plan_from_intent(intent: str) -> Dict:
    """Generate plan from intent using planner module."""
    from planner import get_plan
    return get_plan(intent)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plan Executor for SAOS Orchestrator")
    parser.add_argument("--plan", help="Path to plan JSON file, or - for stdin")
    parser.add_argument("--intent", help="Generate plan from intent string")
    parser.add_argument("--execute", action="store_true", help="Create real tasks (default: dry run)")
    args = parser.parse_args()
    
    plan = None
    
    if args.plan:
        if args.plan == "-":
            plan = json.load(sys.stdin)
        else:
            with open(args.plan, 'r') as f:
                plan = json.load(f)
    elif args.intent:
        plan = plan_from_intent(args.intent)
    else:
        print("Usage: --plan <file.json> | --intent 'goal text'")
        print("       Add --execute to create real tasks")
        sys.exit(1)
    
    execute_plan(plan, dry_run=not args.execute)
