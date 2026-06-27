# SAOS Compute Pause State — June 27, 2026

**Status:** ⏸️ PAUSED — Safe to leave as-is. Everything is preserved.

## What Was Running (Before Pause)

| Process | State Before | Action Taken | How to Re-enable |
|---------|-------------|--------------|------------------|
| Orchestrator Daemon | Running (PID 1076), spawned every 10s | Killed + LaunchAgent unloaded | `launchctl load ~/Library/LaunchAgents/net.systack.orchestrator.plist` |
| n8n Email Dispatcher | Active, polled every 60s | Disabled in DB (active=0) | `sqlite3 ~/.n8n/database.sqlite "UPDATE workflow_entity SET active=1 WHERE id='eylye0Me5zyoXMc2';"` |
| 14 pending test tasks | PENDING in task_queue | Marked DONE (IDs 325-336) | N/A — these were test artifacts |

## Still Running (Unchanged)

| Service | Port | Status |
|---------|------|--------|
| OpenClaw Gateway | 18789 | ✅ Running |
| n8n Main | 5678 | ✅ Running |
| Customer Dashboard API | 8768 | ✅ Running |
| Old Dashboard API | 8765 | ✅ Running |
| SAOS Webhook Bridge | 8767 | ✅ Running |
| Invoice Parser API | 9001 | ✅ Running |
| Invoice Dashboard API | 8766 | ✅ Running |
| Cloudflare Tunnels | — | ✅ Running |

## n8n SAOS Workflows Status

| Workflow | ID | Active | Notes |
|----------|-----|--------|-------|
| SAOS Lead Capture + Score + Log | `rnsOGACoyXh0TXFm` | ✅ 1 | Webhook-based, safe |
| SAOS Client Provisioning Pipeline | `8567a376-...` | ✅ 1 | Webhook-based, safe |
| SAOS VPS Ready Notification | `yiMN48g5lFc7NpIm` | ✅ 1 | Webhook-based, safe |
| SAOS Enterprise — Stripe Checkout Webhook | `77b76TUhNvZyAu5U` | ✅ 1 | Webhook-based, safe |
| SAOS Enterprise — Configure Fleet | `cAVqSVhMojNEa3hb` | ✅ 1 | Webhook-based, safe |
| SAOS Email Notification Dispatcher | `eylye0Me5zyoXMc2` | ⏸️ **0** | **Disabled — was polling every 60s** |

## Quick Restore Commands

### Restore Orchestrator Daemon
```bash
launchctl load ~/Library/LaunchAgents/net.systack.orchestrator.plist
```

### Restore n8n Email Dispatcher
```bash
sqlite3 ~/.n8n/database.sqlite "UPDATE workflow_entity SET active = 1 WHERE id = 'eylye0Me5zyoXMc2';"
```

### Check Orchestrator Status
```bash
ps aux | grep orchestrator-daemon | grep -v grep
launchctl list | grep orchestrator
```

## Why This Happened

The orchestrator daemon (built June 17) was designed to poll the task_queue and spawn agents. After a workspace reorganization on June 22, credential paths broke, causing the daemon to fail tasks and retry in a loop. On June 24, the daemon was stopped and fixed, but the LaunchAgent was never unloaded — so it restarted on boot.

14 test `client_request` tasks (IDs 325-336) from June 23 were left in PENDING state. The daemon kept finding them and spawning SOL sessions with the "TASK: You are SOL..." prompt pattern.

The n8n Email Notification Dispatcher was polling `localhost:8768` (wrong port — should be 8765), causing ~1,440 failed executions per day.

## Prevention Checklist

- [ ] Before re-enabling daemon: verify credential paths in `scripts/provision_vps.py`
- [ ] Before re-enabling daemon: clear task_queue of old test tasks
- [ ] Before re-enabling email dispatcher: fix API port from 8768 to 8765
- [ ] Add circuit breaker: if >50% tasks fail, daemon should pause itself
- [ ] Add pre-flight check: daemon verifies credentials before starting loop

---
*File created by SOL — June 27, 2026*
*Source: session conversation + process audit*
