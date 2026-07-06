# SAOS SOP Library

*Standard Operating Procedures for every recurring Systack task.*

**Version:** 1.0  
**Last Updated:** 2026-07-06  
**Owner:** SOL 🛰️  
**Classification:** Internal — Systack Operations

---

## Table of Contents

1. [SOP-001: Daily Health Check](#sop-001-daily-health-check)
2. [SOP-002: Weekly Backup Verification](#sop-002-weekly-backup-verification)
3. [SOP-003: Client Onboarding](#sop-003-client-onboarding)
4. [SOP-004: New Agent Deployment](#sop-004-new-agent-deployment)
5. [SOP-005: Security Incident Response](#sop-005-security-incident-response)
6. [SOP-006: Service Degradation Response](#sop-006-service-degradation-response)
7. [SOP-007: Client Offboarding](#sop-007-client-offboarding)
8. [SOP-008: SSL Certificate Renewal](#sop-008-ssl-certificate-renewal)
9. [SOP-009: Database Maintenance](#sop-009-database-maintenance)
10. [SOP-010: Fleet Agent Rotation](#sop-010-fleet-agent-rotation)

---

## SOP-001: Daily Health Check

### Purpose
Verify all SAOS services are operational before the business day begins.

### Frequency
Daily, 7:00 AM CDT

### Owner
LOKI 🏠 (automated) + SOL 🛰️ (review)

### Steps

| Step | Action | Expected Result | Time |
|------|--------|-----------------|------|
| 1 | Run `curl https://portal.systack.net/api/health` | `{"status":"ok"}` | 5s |
| 2 | Run `curl https://command.systack.net/api/health` | `{"status":"ok"}` | 5s |
| 3 | Run `curl https://invoice.systack.net/api/summary` | JSON with counts | 5s |
| 4 | Check `tailscale status` | All nodes connected | 10s |
| 5 | Review Command Center Alerts tab | Zero critical alerts | 30s |
| 6 | Review backup_log table for last 24h | At least one successful backup | 10s |
| 7 | Check disk space: `df -h` | All partitions <80% | 10s |
| 8 | Check memory: `free -h` | Available >2GB | 5s |

### Success Criteria
- All 8 services respond green
- No critical alerts in last 24 hours
- Backup completed successfully
- Disk and memory within thresholds

### Failure Response
- If any service fails → SOP-006: Service Degradation Response
- If backup failed → Run manual backup, investigate root cause
- If disk >80% → Clean logs, archive old backups

### Documentation
- Log results in Command Center
- iMessage alert to Green if any failure

---

## SOP-002: Weekly Backup Verification

### Purpose
Ensure backups are valid and can be restored within RTO.

### Frequency
Weekly, Sundays at 3:00 AM CDT (automated via cron)

### Owner
LOKI 🏠 (automated) + SOL 🛰️ (review results)

### Steps

| Step | Action | Expected Result | Time |
|------|--------|-----------------|------|
| 1 | Verify automated backup ran | Entry in backup_log with status=success | 5s |
| 2 | Check backup file size | Within 10% of previous backup | 5s |
| 3 | Verify SHA-256 checksum | Matches backup_log entry | 10s |
| 4 | Test restore on staging VPS | Database restored successfully | 5 min |
| 5 | Verify restored data integrity | Spot-check 10 random records | 5 min |
| 6 | Record verification in backup_log | Update verified_at timestamp | 10s |

### Success Criteria
- Backup completes successfully
- File size is reasonable (not zero, not 10x normal)
- Checksum matches
- Restore test passes
- Sample data verified

### Failure Response
- If backup fails → Investigate immediately, run manual backup
- If restore fails → This is CRITICAL — escalate to Green immediately
- If data integrity fails → Do not proceed with any changes until resolved

### Documentation
- Results logged in backup_log table
- Weekly summary emailed to Green

---

## SOP-003: Client Onboarding

### Purpose
Standardize every new client setup for consistency and speed.

### Frequency
Per new client

### Owner
SOL 🏠 + DOOBY 🤖 (technical execution)

### Steps

#### Phase 1: Pre-Deployment (Sales Complete → Day 1)

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | Confirm contract signed and payment received | Green | — |
| 2 | Gather client requirements: services, integrations, contacts | SOL | 30 min |
| 3 | Create client folder in workspace: `clients/{client-id}/` | SOL | 5 min |
| 4 | Generate temporary PIN using onboard_client.py | DOOBY | 2 min |
| 5 | Schedule kickoff call (within 5 business days) | SOL | 10 min |

#### Phase 2: Provisioning (Day 1-3)

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 6 | Provision VPS (Vultr, 16GB, Dallas) | DOOBY | 10 min |
| 7 | Install Tailscale, add to tailnet | DOOBY | 15 min |
| 8 | Install PostgreSQL, run schema migrations | DOOBY | 20 min |
| 9 | Deploy Customer Portal (port 8768) | DOOBY | 15 min |
| 10 | Deploy Command Center (port 8770) | DOOBY | 15 min |
| 11 | Configure environment variables | DOOBY | 10 min |
| 12 | Set up Cloudflare DNS (if custom domain) | DOOBY | 10 min |

#### Phase 3: Configuration (Day 2-7)

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 13 | Configure email integration (invoices, notifications) | DOOBY | 30 min |
| 14 | Set up form endpoints (leads, support) | DOOBY | 20 min |
| 15 | Import client data (vendor list, contact list) | DOOBY | 30 min |
| 16 | Configure report templates and schedules | DOOBY | 30 min |
| 17 | Set up n8n workflows for client's services | DOOBY | 1 hour |

#### Phase 4: Testing (Day 8-14)

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 18 | Run acceptance tests per VALI standards | VALI | 2 hours |
| 19 | Test end-to-end with sample data | VALI | 1 hour |
| 20 | Client validation call | Green + Client | 1 hour |
| 21 | Fix any issues identified | DOOBY | Varies |

#### Phase 5: Go-Live (Day 15)

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 22 | Switch to production data flow | DOOBY | 30 min |
| 23 | Activate monitoring and alerts | LOKI | 15 min |
| 24 | Client training session (video call) | Green | 1 hour |
| 25 | Deliver Standard Launch Kit | ASSEMBLY | 10 min |
| 26 | Schedule 30-day check-in | SOL | 5 min |

### Success Criteria
- Client can log in with Client ID + PIN
- Dashboard shows real data
- At least one invoice processed end-to-end (if applicable)
- At least one lead scored and alerted (if applicable)
- All acceptance tests pass
- Client confirms satisfaction

### Failure Response
- If VPS provisioning fails → Retry with different region, notify Vultr support
- If deployment fails → Check logs, fix, redeploy
- If acceptance tests fail → Fix before go-live, never deploy failing tests

### Documentation
- Client record in Command Center
- Deployment checklist completed and signed
- Training session recording saved

---

## SOP-004: New Agent Deployment

### Purpose
Add a new AI agent to the SAOS fleet safely.

### Frequency
Per new agent request

### Owner
ASSEMBLY 🛠️ (design) + DOOBY 🤖 (implementation)

### Steps

| Step | Action | Expected Result | Time |
|------|--------|-----------------|------|
| 1 | Define agent purpose, scope, and boundaries | ASSEMBLY | 1 hour |
| 2 | Create agent configuration file | DOOBY | 30 min |
| 3 | Set up dedicated workspace directory | DOOBY | 10 min |
| 4 | Configure model and parameters | DOOBY | 15 min |
| 5 | Define tool permissions (what it can/can't do) | ASSEMBLY | 30 min |
| 6 | Create system prompt and identity | DOOBY | 30 min |
| 7 | Test in isolated environment | VALI | 1 hour |
| 8 | Review for safety and scope compliance | CODY | 30 min |
| 9 | Deploy to production fleet | DOOBY | 15 min |
| 10 | Monitor for 48 hours | PESSI | 2 days |
| 11 | Document in AGENTS.md | SOL | 15 min |

### Success Criteria
- Agent responds correctly to test prompts
- Agent respects boundaries and permissions
- No errors in logs for 48 hours
- Documentation updated

### Failure Response
- If agent misbehaves → Roll back, adjust prompt, redeploy
- If safety review fails → Redesign, never deploy without CODY approval

---

## SOP-005: Security Incident Response

### Purpose
Handle security incidents (breaches, unauthorized access, data exposure) systematically.

### Frequency
As needed

### Owner
PESSI ⚠️ (detection) + SOL 🛰️ (coordination) + JURIS ⚖️ (compliance)

### Severity Levels

| Level | Definition | Examples | Response Time |
|-------|-----------|----------|---------------|
| P1 | Critical | Data breach, unauthorized admin access, ransomware | Immediate |
| P2 | High | Failed login spike, suspicious API activity | 1 hour |
| P3 | Medium | Single unauthorized access attempt, expired cert | 4 hours |
| P4 | Low | Policy violation, minor misconfiguration | 24 hours |

### Steps (P1 Critical)

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | **CONTAIN** — Isolate affected systems | PESSI | 5 min |
| 2 | **ASSESS** — Determine scope of breach | PESSI | 15 min |
| 3 | **NOTIFY** — Alert Green immediately | SOL | 2 min |
| 4 | **NOTIFY** — If client data affected, notify client | JURIS | 30 min |
| 5 | **PRESERVE** — Capture logs, don't delete evidence | PESSI | 10 min |
| 6 | **INVESTIGATE** — Determine root cause | PESSI + CODY | 2 hours |
| 7 | **REMEDIATE** — Fix vulnerability, rotate credentials | DOOBY | 1 hour |
| 8 | **VERIFY** — Confirm breach is contained | VALI | 30 min |
| 9 | **DOCUMENT** — Incident report in incident_log | SOL | 1 hour |
| 10 | **REVIEW** — Post-mortem, process improvements | SOL | 1 day |

### Documentation
- incident_log table entry with full timeline
- Client notification (if applicable)
- Post-mortem document
- Process updates if gaps found

---

## SOP-006: Service Degradation Response

### Purpose
Restore service when any SAOS component is down or degraded.

### Frequency
As needed

### Owner
PESSI ⚠️ (detection) + DOOBY 🤖 (technical fix)

### Steps

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | Detect degradation (monitoring alert or health check fail) | PESSI | Immediate |
| 2 | Verify degradation (run health check 3x) | PESSI | 1 min |
| 3 | Check dependency status (DB, Tailscale, VPS) | PESSI | 2 min |
| 4 | If dependency issue → Fix dependency first | DOOBY | Varies |
| 5 | If service issue → Restart service | DOOBY | 2 min |
| 6 | Verify service recovery (health check 3x) | VALI | 2 min |
| 7 | If not recovered → Escalate to Green | SOL | 2 min |
| 8 | Document incident and resolution | SOL | 15 min |
| 9 | If pattern emerges → Schedule root cause analysis | ASSEMBLY | 1 week |

### Escalation
- Service not recovered in 15 minutes → Green notified
- Service not recovered in 1 hour → All-hands response
- Critical service (portal or Command Center) → Immediate Green notification

---

## SOP-007: Client Offboarding

### Purpose
Remove a client cleanly, securely, and professionally.

### Frequency
Per client cancellation

### Owner
SOL 🛰️ + DOOBY 🤖 (technical) + JURIS ⚖️ (compliance)

### Steps

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | Confirm cancellation notice received | JURIS | 5 min |
| 2 | Verify payment status (all invoices paid) | JURIS | 5 min |
| 3 | Export client data (JSON, CSV, SQLite) | DOOBY | 30 min |
| 4 | Verify data export completeness | VALI | 15 min |
| 5 | Send data export to client | SOL | 10 min |
| 6 | Wait 30 days (retention period) | — | 30 days |
| 7 | Archive client database records (don't delete, mark inactive) | DOOBY | 10 min |
| 8 | Deprovision VPS (if dedicated) | DOOBY | 15 min |
| 9 | Remove from Command Center | DOOBY | 5 min |
| 10 | Update client status to "inactive" | SOL | 5 min |
| 11 | Schedule exit interview (if applicable) | Green | 30 min |
| 12 | Document learnings in churn analysis | SOL | 30 min |

### Success Criteria
- Client has full data export
- No active billing
- Resources deprovisioned
- Records archived (not deleted)

---

## SOP-008: SSL Certificate Renewal

### Purpose
Maintain valid SSL certificates for all SAOS domains.

### Frequency
Every 60 days (Cloudflare auto-renewal)

### Owner
DOOBY 🤖 + LOKI 🏠 (monitoring)

### Steps

| Step | Action | Expected Result | Time |
|------|--------|-----------------|------|
| 1 | Check cert expiry: `openssl s_client -connect portal.systack.net:443` | Valid >30 days | 10s |
| 2 | Verify auto-renewal is configured in Cloudflare | Enabled | 5 min |
| 3 | Check Cloudflare notification settings | Alerts enabled | 2 min |
| 4 | If manual cert: Run certbot renewal | Success message | 5 min |
| 5 | Verify renewed cert | Valid for 90 days | 10s |
| 6 | Test all endpoints | No SSL errors | 2 min |

### Failure Response
- If auto-renewal fails → Manual certbot run
- If certbot fails → Check DNS, firewall, ACME challenges
- If unresolved in 1 hour → Escalate to Green

---

## SOP-009: Database Maintenance

### Purpose
Keep PostgreSQL healthy and performant.

### Frequency
Monthly

### Owner
DOOBY 🤖 + LOKI 🏠

### Steps

| Step | Action | Expected Result | Time |
|------|--------|-----------------|------|
| 1 | Check table sizes: `\dt+` in psql | No unexpected bloat | 1 min |
| 2 | Check slow queries: `pg_stat_statements` | No queries >1s avg | 5 min |
| 3 | Vacuum analyze: `VACUUM ANALYZE;` | Complete without errors | 10 min |
| 4 | Check replication lag (if replicated) | <5 seconds | 1 min |
| 5 | Review connection count | <80% of max | 1 min |
| 6 | Check for missing indexes | Query plans use indexes | 10 min |

### Failure Response
- If vacuum fails → Check disk space, resolve, retry
- If slow queries found → Optimize or add indexes
- If connections maxed → Check for connection leaks, restart if needed

---

## SOP-010: Fleet Agent Rotation

### Purpose
Manage cloud model usage within Ollama Pro tier limits.

### Frequency
Weekly (or as needed based on usage)

### Owner
SOL 🛰️

### Steps

| Step | Action | Expected Result | Time |
|------|--------|-----------------|------|
| 1 | Review current model usage | Within 50% target allocation | 5 min |
| 2 | Check active agents (`ollama ps`) | Only expected models running | 10s |
| 3 | Verify no local model conflicts | Only one local model at a time | 10s |
| 4 | Schedule next week's agent rotation | Calendar invites sent | 10 min |
| 5 | Review compute budget vs. actual | On track for monthly target | 5 min |

### Weekly Compute Budget

| Agent | Model | Target % | When |
|-------|-------|----------|------|
| SOL | kimi-k2.6:cloud | 50% | Daily |
| ATLAS | kimi-k2.6:cloud | 20% | Rotating weeks |
| CHATTY | kimi-k2.6:cloud | 15% | Rotating weeks |
| CODY | kimi-k2.6:cloud | 10% | Default |
| PESSI | deepseek-v4-pro:cloud | 3% | Launches only |
| JURIS | kimi-k2.6:cloud | 2% | Contracts only |
| DOOBY | qwen3.5:9b local | On-demand | Coding tasks |
| LOKI | qwen3.5:9b local | Cron only | Background tasks |
| VALI | qwen3.5:9b local | On-demand | QA bursts |

### Failure Response
- If over budget → Pause non-critical agents, defer research/outreach
- If model conflict → Kill conflicting instance, respawn correct one

---

*SOP Library Version 1.0. Update as processes evolve.*
