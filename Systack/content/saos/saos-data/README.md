# SAOS — Systack Agent Operating System

**10-agent fleet orchestration, provisioning, and automation.**

## Fleet Agents

| Agent | Emoji | Role |
|-------|-------|------|
| SOL | 🛰️ | Command & Orchestration |
| CODY | 💻 | Build Engine |
| ASSEMBLY | 🛠️ | Deployment |
| VALI | ✅ | Quality Verification |
| PESSI | ⚠️ | Risk Analysis |
| ORACLE | 🔮 | Design & Architecture |
| ATLAS | 🗺️ | Knowledge & Memory |
| CHATTY | 💬 | Communication |
| GENI | 🎨 | Creative & Visual |
| JURIS | ⚖️ | Legal & Compliance |

## Components

- `orchestrator-daemon.py` — Persistent fleet loop (launchd)
- `orchestrator.py` — Core task queue + dispatch
- `openclaw_bridge.py` — Agent session bridge
- `dashboard/` — Fleet status API + UI
- `scripts/` — Identity generator, provisioners
- `fleet/` — Agent definitions (markdown)
- `n8n/` — Workflow templates

## Quick Start

```bash
# Start orchestrator daemon
python3 orchestrator-daemon.py --daemon

# View fleet status
python3 orchestrator-daemon.py --status

# Start dashboard API
cd dashboard && python3 api.py --port 8765
```

## License

Proprietary — Systack Systems
