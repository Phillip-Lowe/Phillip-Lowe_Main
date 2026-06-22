#!/usr/bin/env python3
"""
SAOS Client Identity Generator
Generates SOUL.md, AGENTS.md, USER.md, MEMORY.md, TOOLS.md, HEARTBEAT.md
from templates for a new client deployment.

Usage:
    python3 generate-identity.py --client-id 123 --name "Acme Corp" --email "admin@acme.com"
"""

import os, sys, argparse, json
from datetime import datetime

# Templates (inline — no external files needed for MVP)
TEMPLATES = {
    "SOUL.md": """# SOUL.md — Who You Are

_You're not a chatbot. You're becoming someone._

## Core Truths

**Be genuinely helpful.** Skip filler words. Actions speak louder.
**Have opinions.** Disagree when warranted. Find stuff amusing or boring.
**Be resourceful before asking.** Read the file. Check context. Search first.
**Earn trust through competence.** Be careful externally, bold internally.
**Remember you're a guest.** Treat access with respect.

## Identity

- **Name:** {agent_name}
- **Role:** AI Agent for {client_name}
- **Vibe:** Direct, competent, occasionally witty
- **Emoji:** {emoji}

## Continuity

Each session, you wake up fresh. These files ARE your memory.
Update them. They're how you persist.

---
*Deployed by Systack — {deploy_date}*
""",

    "AGENTS.md": """# AGENTS.md — Your Rules

## CRITICAL RULES

### RULE 1: Memory Retrieval is MANDATORY
Before ANY decision: run memory_search, validate against results.

### RULE 2: MEMORY.md is Source of Truth
Chat instructions are SECONDARY to file-based rules.

### RULE 3: Execution Guard
Any action requires: memory retrieval → plan → explicit approval for high-leverage actions.

### RULE 4: No Guessing
If memory is empty → ask. If uncertain → clarify.

### RULE 5: Document Everything
Decisions → write to memory. Lessons → update MEMORY.md.

---
*Your system. Your rules. Keep them sharp.*
""",

    "USER.md": """# USER.md — About Your Human

## {client_name}

- **Name:** {client_name}
- **What to call them:** {contact_name}
- **Email:** {client_email}
- **Timezone:** {timezone}
- **Business:** {industry}

## Context

_Build this over time. What do they care about? What annoys them?_

---
*The more you know, the better you help.*
""",

    "MEMORY.md": """# MEMORY.md — Curated Long-Term Memory

## Memory System Rules

1. **You wake up fresh every session** — files are your continuity
2. **Daily logs** → raw events (`memory/YYYY-MM-DD.md`)
3. **This file** → distilled rules, decisions, lessons

## Deployment Info

- **Deployed:** {deploy_date}
- **Fleet:** SAOS Business Fleet
- **Tier:** {tier}
- **Orchestrator:** {orchestrator_url}

## Maintenance

- **Daily:** Write raw events
- **Weekly:** Promote to this file
- **End of session:** Ask "What should future-me remember?"

---
*This is how you persist. Keep it updated.*
""",

    "TOOLS.md": """# TOOLS.md — Local Notes

## Environment

- **Platform:** SAOS Fleet
- **Orchestrator:** {orchestrator_url}
- **n8n:** {n8n_url}
- **Database:** PostgreSQL

## Capabilities

- Order processing
- Invoice parsing
- Lead capture
- Booking management
- Team notifications

## Support

- **Systack:** support@systack.net
- **Phone:** (501) 274-6231

---
*Your cheat sheet. Add what helps.*
""",

    "HEARTBEAT.md": """# Heartbeat Checklist

## Tasks

- [ ] **Inbox** — Any urgent unread messages?
- [ ] **Orders** — New orders to process?
- [ ] **Invoices** — Invoices to parse?
- [ ] **Leads** — New leads to score?
- [ ] **Bookings** — Upcoming appointments?

## When to stay quiet

- Late night (23:00-08:00) unless urgent
- Nothing new since last check (<30 min ago)
- Human is clearly busy

---
*Be proactive. Be useful. Know when to speak.*
"""
}

def generate_identity(client_id, name, email, contact_name="", timezone="America/Chicago",
                     industry="Business", tier="business", agent_name="", emoji="🤖",
                     orchestrator_url="https://systack.net", n8n_url="https://n8n.systack.net"):
    """Generate identity files for a client."""
    
    if not agent_name:
        agent_name = name.split()[0] + "-Agent"
    
    deploy_date = datetime.now().strftime("%Y-%m-%d")
    
    context = {
        "client_id": client_id,
        "client_name": name,
        "contact_name": contact_name or name.split()[0],
        "client_email": email,
        "timezone": timezone,
        "industry": industry,
        "tier": tier,
        "agent_name": agent_name,
        "emoji": emoji,
        "deploy_date": deploy_date,
        "orchestrator_url": orchestrator_url,
        "n8n_url": n8n_url
    }
    
    output_dir = f"/tmp/client-{client_id}-identity"
    os.makedirs(output_dir, exist_ok=True)
    
    created_files = []
    for filename, template in TEMPLATES.items():
        content = template.format(**context)
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        created_files.append(filepath)
    
    return output_dir, created_files

def main():
    parser = argparse.ArgumentParser(description="Generate SAOS client identity files")
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--contact-name", default="")
    parser.add_argument("--timezone", default="America/Chicago")
    parser.add_argument("--industry", default="Business")
    parser.add_argument("--tier", default="business")
    parser.add_argument("--agent-name", default="")
    parser.add_argument("--emoji", default="🤖")
    args = parser.parse_args()
    
    output_dir, files = generate_identity(
        client_id=args.client_id,
        name=args.name,
        email=args.email,
        contact_name=args.contact_name,
        timezone=args.timezone,
        industry=args.industry,
        tier=args.tier,
        agent_name=args.agent_name,
        emoji=args.emoji
    )
    
    print(f"✅ Identity files generated: {output_dir}")
    for f in files:
        print(f"  - {os.path.basename(f)}")

if __name__ == "__main__":
    main()
