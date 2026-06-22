#!/usr/bin/env python3
"""
Daily Learning Orchestrator
- Reads ORACLE-CURRICULUM.md
- Creates tasks for today's agent
- Puts them in the task_queue for the orchestrator

Usage:
    python3 daily_learning_orchestrator.py --dry-run   # Preview
    python3 daily_learning_orchestrator.py            # Create real tasks
"""

import os, sys, argparse, json
from datetime import datetime
from pathlib import Path

# Import our orchestrator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orchestrator import create_task

# Day → Agent mapping
AGENT_ROTATION = {
    "Monday": ("SOL", "Error Alerting System"),
    "Tuesday": ("ASSEMBLY", "n8n Credential Management"),
    "Wednesday": ("PESSI", "Webhook Idempotency"),
    "Thursday": ("CHATTY", "Client Onboarding Automation"),
    "Friday": ("GENI", "ComfyUI Model Activation"),
    "Saturday": ("VALI", "Payment Gateway Testing"),
    "Sunday": ("SOL", "Synthesis + GAP State Updates"),
}

def get_today_agent():
    day_name = datetime.now().strftime("%A")
    return AGENT_ROTATION.get(day_name, ("SOL", "General Task"))

def main():
    parser = argparse.ArgumentParser(description="Daily Learning Task Creator")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()

    agent, topic = get_today_agent()
    print(f"📅 Today is {datetime.now().strftime('%A, %B %d')}")
    print(f"🤖 Agent: {agent}")
    print(f"🎯 Topic: {topic}")

    # Create 3 tasks: research → build → validate
    tasks = [
        {
            "type": "RESEARCH",
            "priority": 8,
            "payload": {
                "goal": f"Research {topic}",
                "context": f"Agent {agent} researching {topic} per ORACLE curriculum",
                "output": "memory/learning/{}.md".format(datetime.now().strftime('%Y-%m-%d') + '-' + agent.lower())
            }
        },
        {
            "type": "BUILD",
            "priority": 9,
            "payload": {
                "goal": f"Build/test {topic}",
                "sandbox": True,
                "depends_on": "research"
            }
        },
        {
            "type": "VALIDATE",
            "priority": 7,
            "payload": {
                "goal": f"Validate {topic} output",
                "checklist": ["sandbox tested", "documented", "production ready"]
            }
        }
    ]

    print(f"\n📋 Creating {len(tasks)} tasks:")
    for i, t in enumerate(tasks, 1):
        print(f"  {i}. [{t['type']}] {t['payload']['goal']} (priority={t['priority']})")

    if args.dry_run:
        print("\n🏃 DRY RUN — no tasks created")
        return

    print("\n✅ Creating tasks...")
    created = []
    for t in tasks:
        task_id = create_task(t['type'], t['payload'], agent, t['priority'])
        created.append(task_id)
        print(f"   Task #{task_id}: {t['type']} → {agent}")

    print(f"\n🚀 Done! {len(created)} tasks queued for {agent}")
    print(f"   Run: python3 orchestrator.py --poll --agent {agent}")

if __name__ == "__main__":
    main()
