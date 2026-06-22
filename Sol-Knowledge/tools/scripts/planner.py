#!/usr/bin/env python3
"""
Planner — Converts user intent into structured execution plans
Uses local Ollama (qwen2.5-coder:7b) for intent interpretation

Usage:
    python3 planner.py "Build n8n credential management"
    python3 planner.py --intent-file goal.txt --output plan.json
"""

import os, sys, argparse, json, re
from typing import Dict, List, Optional

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
PLANNER_MODEL = "qwen2.5-coder:7b"


def get_plan(intent: str, available_tools: List[str] = None) -> Dict:
    """
    Convert natural language intent into structured execution plan.
    Returns: {"goal": str, "steps": [{"action": str, "tool": str, "params": dict}]}
    """
    if available_tools is None:
        available_tools = [
            "rag_retrieve", "postgres_query", "n8n_api", "openclaw_session",
            "shell_exec", "file_read", "file_write", "browser_automation"
        ]

    system_prompt = f"""You are a task planner for an AI agent system. Convert user intent into structured execution plans.

Available tools: {', '.join(available_tools)}

Rules:
- Output ONLY valid JSON
- Each step must have: action (what to do), tool (which tool to use), params (inputs)
- Steps should be sequential and logical
- Include validation steps where appropriate
- Max 10 steps

Output format:
{{
  "goal": "brief description",
  "steps": [
    {{"action": "retrieve context", "tool": "rag_retrieve", "params": {{"query": "..."}}}},
    {{"action": "analyze", "tool": "openclaw_session", "params": {{"prompt": "..."}}}},
    {{"action": "execute", "tool": "shell_exec", "params": {{"command": "..."}}}},
    {{"action": "validate", "tool": "openclaw_session", "params": {{"prompt": "verify..."}}}}
  ]
}}"""

    user_prompt = f"Intent: {intent}\n\nGenerate the execution plan as JSON only."

    import urllib.request
    payload = json.dumps({
        "model": PLANNER_MODEL,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.3}
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
        raw = data.get("response", "")

    # Extract JSON from response (handle markdown wrappers)
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        # Remove ```json and ``` lines
        filtered = [l for l in lines if not l.strip().startswith("```")]
        raw = "\n".join(filtered)

    try:
        plan = json.loads(raw.strip())
        # Validate structure
        if "goal" not in plan or "steps" not in plan:
            return fallback_plan(intent)
        return plan
    except json.JSONDecodeError:
        return fallback_plan(intent)


def fallback_plan(intent: str) -> Dict:
    """Simple fallback when LLM fails to produce valid JSON."""
    return {
        "goal": intent,
        "steps": [
            {"action": "research context", "tool": "rag_retrieve", "params": {"query": intent}},
            {"action": "analyze and plan", "tool": "openclaw_session", "params": {"prompt": f"Plan: {intent}"}},
            {"action": "execute", "tool": "shell_exec", "params": {"command": "echo 'execute plan here'"}},
            {"action": "validate", "tool": "openclaw_session", "params": {"prompt": f"Validate: {intent}"}}
        ]
    }


def print_plan(plan: Dict) -> None:
    print(f"\n🎯 GOAL: {plan['goal']}\n")
    print("📋 STEPS:")
    for i, step in enumerate(plan.get('steps', []), 1):
        print(f"  {i}. [{step.get('tool', '?')}] {step.get('action', 'unknown')}")
        params = step.get('params', {})
        for k, v in params.items():
            vstr = str(v)[:60] + "..." if len(str(v)) > 60 else str(v)
            print(f"     {k}: {vstr}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Planner for SOL orchestrator")
    parser.add_argument("intent", nargs="?", help="Natural language intent")
    parser.add_argument("--intent-file", help="Read intent from file")
    parser.add_argument("--output", help="Write plan to JSON file")
    parser.add_argument("--tools", help="Comma-separated tool list")
    args = parser.parse_args()

    intent = args.intent
    if args.intent_file:
        with open(args.intent_file, 'r') as f:
            intent = f.read().strip()

    if not intent:
        print("Usage: python3 planner.py 'intent text' or --intent-file file.txt")
        sys.exit(1)

    tools = args.tools.split(",") if args.tools else None
    plan = get_plan(intent, tools)

    print_plan(plan)

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(plan, f, indent=2)
        print(f"✅ Plan saved to {args.output}")
