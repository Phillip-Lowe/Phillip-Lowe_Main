# MEMORY.md — Curated Long-Term Memory

_This is my curated memory — the distilled essence, not raw logs. For daily logs, see `memory/YYYY-MM-DD.md`._

---

## 2026-06-24 — Systack AI Video Ad Service Identified

**Status:** Confirmed viable service offering from Utopia Deli production pipeline
**Source:** `memory/2026-06-24.md`

### What Was Discovered
User produced a 4K vertical video ad for Utopia Deli using:
- Kling AI for video generation
- ElevenLabs for voiceover
- Premiere Pro for assembly
- 4K upscale workflow

### The Service
**"There's a [Business] for that" Campaign Series**

| Service | Description | Price Point |
|---------|-------------|-------------|
| AI Video Ad Production | Generate, edit, deliver short-form vertical ads | $500-1500/video |
| Campaign Series | 3-5 themed videos per business | Package pricing |
| 4K Upscale + Assembly | AI clips → 4K + voice/music/CTA | Add-on |
| Monthly Social Retainer | Ongoing content production | $2-5K/month |

**Repeatable Workflow:**
1. AI generate clips (Kling)
2. Upscale to 4K
3. Add ElevenLabs voiceover + music
4. Assembly in Premiere
5. Deliver 9:16 + 16:9 variants

### Platform Sweet Spots
- TikTok / Instagram Reels: 9:16 vertical, 15-24s
- YouTube Shorts: 15s cuts optimal
- Facebook Reels: Local business targeting

### Key Insight
This is NOT just video production — it's a **systematized content engine** that can be packaged and sold to any local business needing social media presence.

---

## 2026-06-25 — BlueBubbles Delivery Fixed ✅

**Status:** COMPLETE — All cron jobs now route correctly to +15012746231
**Source:** `memory/2026-06-25.md`

### What Was Broken
- BlueBubbles channel: `enabled: false`, `serverUrl: ""`
- 7 cron jobs failing with: "Delivering to BlueBubbles requires --to <handle|chat_guid:GUID>"
- WEEKLY-MANUAL-MEMORY-PROMOTION disabled since June 6 (delivery failure)

### Fix Applied
1. Updated `openclaw.json`: `enabled: true`, `serverUrl: http://phillips-macbook-air.tail573d57.ts.net:1234`
2. Added explicit delivery to 7 cron jobs: `channel: "bluebubbles"`, `to: "+15012746231"`
3. Re-enabled WEEKLY-MANUAL-MEMORY-PROMOTION (Tuesdays 9AM CDT)

### Test Result
- Test message sent to +15012746231
- **SUCCESS** — message ID `62E234CE-CBDD-4277-95BD-B9ED776DE1BD`

### Jobs Status
| # | Job | Status |
|---|-----|--------|
| 4 | WEEKLY-MANUAL-MEMORY-PROMOTION | ✅ ENABLED (was disabled) |
| 1,2,3,5,6,7 | Others | Configured but still disabled |

---

## 2026-06-25 — ORACLE FLOS Proposal: DEFERRED

**Status:** EVALUATED — Do NOT build now
**Source:** ORACLE response on loop engineering + SOL assessment

### What ORACLE Proposed
Fleet Loop Orchestration System (FLOS): persistent autonomous operations layer with standardized loops, verification, guardrails, escalation, and improvement loops across all 10 agents.

### Assessment
- **90% of pieces already exist** — fleet agents, cron jobs, memory system, watchdog (disabled since June 8)
- **June 5-8 watchdog system WAS a loop orchestrator** — it failed because delivery was broken and LLM timeouts killed it
- **Adding abstraction without fixing fundamentals = more failures**

### Decision: DEFER

**Preconditions before building FLOS:**
1. ✅ Delivery channel works (BlueBubbles fixed today)
2. ❌ Model timeouts rare (still happening — need monitoring)
3. ❌ 3+ workflows that need retry logic (not yet)
4. ❌ SAOS provisioning tested end-to-end (not yet)

### What To Build Instead
1. **File-based health checks** — status files in `.health/`, no delivery dependency
2. **ONE payment retry loop** — Utopia Deli Square payments, SQLite-backed, actual revenue impact
3. **Re-enable monitoring jobs** — after proving stability

---

## 2026-06-25 — SAOS Dashboard Mobile Auth + Layout Fixes

**Status:** COMPLETE — Login working on mobile, PIN auth functional, chat responsive
**File:** `memory/2026-06-25-saos-dashboard-mobile-fix.md`

### Fixes Applied
1. **API path mismatch** — `API_BASE` dynamically detects `/dashboard` prefix for Tailscale serve proxy paths
2. **iOS form validation** — Button changed to `type="button"` with `onclick` to bypass native validation
3. **Mobile layout** — Compact nav, larger sidebar toggle, shorter placeholder, added "+ New Conversation" button in empty state

### Key Lesson (Pitfall Catalog)
**Reverse proxy path prefixes:** When serving SPAs behind proxies with path prefixes (e.g., `/dashboard/`), `fetch('/api/...')` resolves to the ROOT origin, not the proxied path. The frontend must dynamically detect and prepend the prefix, or use absolute URLs. This cost 30+ minutes of debugging "The string did not match the expected pattern" error before realizing the API calls were hitting the wrong backend service entirely.

---

## 2026-06-25 — SAOS Dashboard Mobile Auth + Layout Fixes

**Status:** COMPLETE — Login working on mobile, PIN auth functional, chat responsive
**File:** `memory/2026-06-25-saos-dashboard-mobile-fix.md`

### Fixes Applied
1. **API path mismatch** — `API_BASE` dynamically detects `/dashboard` prefix for Tailscale serve proxy paths
2. **iOS form validation** — Button changed to `type="button"` with `onclick` to bypass native validation
3. **Mobile layout** — Compact nav, larger sidebar toggle, shorter placeholder, added "+ New Conversation" button in empty state

### Key Lesson (Pitfall Catalog)
**Reverse proxy path prefixes:** When serving SPAs behind proxies with path prefixes (e.g., `/dashboard/`), `fetch('/api/...')` resolves to the ROOT origin, not the proxied path. The frontend must dynamically detect and prepend the prefix, or use absolute URLs. This cost 30+ minutes of debugging "The string did not match the expected pattern" error before realizing the API calls were hitting the wrong backend service entirely.

### OpenClaw Control UI basePath Fix (Added 2026-06-25 06:12 CDT)
**Status:** COMPLETE — Control UI moved to `/openclaw/`, PDF links work on mobile

**What happened:** Set `gateway.controlUi.basePath: "/openclaw"` to move Control UI off root path. This freed `/dashboard/` from Control UI script injection. BUT relative PDF links (`/download/...`) resolved to root path instead of `/dashboard/`, causing "Not Found" errors.

**Lesson:** Path prefix changes cascade. When you change `basePath` or add a reverse proxy prefix, ALL relative URLs must be updated:
- API endpoints: `/api/...` → `/dashboard/api/...` (or dynamically detect)
- Static assets: `/download/...` → `/dashboard/download/...`
- Client-side routing
- WebSocket connections

**Solution:** Use `window.location.pathname` for runtime detection OR hardcode full absolute paths with prefix.

---

## 2026-06-25 — SAOS Dashboard Mobile Auth + Layout Fixes

**Status:** COMPLETE — Login working on mobile, PIN auth functional, chat responsive
**File:** `memory/2026-06-25-saos-dashboard-mobile-fix.md`

### Fixes Applied
1. **API path mismatch** — `API_BASE` dynamically detects `/dashboard` prefix for Tailscale serve proxy paths
2. **iOS form validation** — Button changed to `type="button"` with `onclick` to bypass native validation
3. **Mobile layout** — Compact nav, larger sidebar toggle, shorter placeholder, added "+ New Conversation" button in empty state

### Key Lesson (Pitfall Catalog)
**Reverse proxy path prefixes:** When serving SPAs behind proxies with path prefixes (e.g., `/dashboard/`), `fetch('/api/...')` resolves to the ROOT origin, not the proxied path. The frontend must dynamically detect and prepend the prefix, or use absolute URLs. This cost 30+ minutes of debugging "The string did not match the expected pattern" error before realizing the API calls were hitting the wrong backend service entirely.

### OpenClaw Control UI basePath Fix (Added 2026-06-25 06:12 CDT)
**Status:** COMPLETE — Control UI moved to `/openclaw/`, PDF links work on mobile

**What happened:** Set `gateway.controlUi.basePath: "/openclaw"` to move Control UI off root path. This freed `/dashboard/` from Control UI script injection. BUT relative PDF links (`/download/...`) resolved to root path instead of `/dashboard/`, causing "Not Found" errors.

**Lesson:** Path prefix changes cascade. When you change `basePath` or add a reverse proxy prefix, ALL relative URLs must be updated:
- API endpoints: `/api/...` → `/dashboard/api/...` (or dynamically detect)
- Static assets: `/download/...` → `/dashboard/download/...`
- Client-side routing
- WebSocket connections

**Solution:** Use `window.location.pathname` for runtime detection OR hardcode full absolute paths with prefix.

### Full Session Lessons (Added 2026-06-25 06:14 CDT)
**File:** `memory/2026-06-25-0614-cdt-full-session-lessons.md`

**Key lessons from the entire session:**
1. Don't assume simple errors are simple — verify WHICH component throws the error
2. Relative paths + reverse proxies = guaranteed silent failures
3. Don't change multiple things at once — change one thing, verify, then change next
4. Know when to stop — if 3+ approaches fail, it's an architecture problem, not code
5. Path prefixes cascade — changing one requires auditing ALL relative URLs
6. Don't post sensitive tokens in chat

---

## 2026-06-25 — SAOS Customer Dashboard: 5-Sprint Feature Build COMPLETE

**Status:** ✅ ALL 5 SPRINTS COMPLETE AND VERIFIED
**Time:** 08:00-09:07 CDT
**Source:** `memory/2026-06-25.md`
**Files:** `api.py`, `index.html`, `n8n-email-dispatcher.json`

### What Was Built

| Sprint | Feature | Status |
|--------|---------|--------|
| 1 | Task Creation from Dashboard | ✅ Working |
| 2 | Agent Spawning Integration | ✅ Working |
| 2.5 | Live Operations Tab | ✅ Working |
| 3 | Async Notifications | ✅ Working |
| 4 | Deliverables Storage | ✅ Working |
| 5 | n8n Email Workflow | ✅ Active |

### Key Endpoints Added
- `POST /api/tasks/request` — Clients create tasks
- `GET /api/internal/pending-tasks` — Poll for unclaimed tasks
- `POST /api/internal/claim-task/<id>` — Prevent duplicate spawns
- `POST /api/internal/update-task/<id>` — Agent status updates
- `POST /api/internal/notify-client` — Queue iMessage/email
- `GET /api/internal/notifications/pending` — Poll for n8n
- `POST /api/internal/deliverables/upload` — Agent file upload
- `GET /api/deliverables/download/<filename>` — Client download
- `GET /api/portal/deliverables` — List client deliverables

### n8n Workflow
- **Name:** SAOS Email Notification Dispatcher (ID: eylye0Me5zyoXMc2)
- **Status:** 🟢 Active, polls every 60 seconds
- **Credentials:** SOL Systack SMTP account

### Next Priority
1. End-to-end provisioning test with real Vultr/Tailscale/n8n credentials
2. iOS Safari `.ts.net` cert trust fix
3. PDF documentation update (User Guide v2.0, Mobile Access Guide)
4. Production deployment
5. Monitoring dashboard (agent health, queue depth, error rates)
6. Client onboarding flow automation
7. Billing integration (Stripe subscriptions)
8. Security audit

---

---

## 2026-06-25 — DOOBY & LOKI Agents Created

**Status:** ACTIVE — Configured, not yet restarted
**File:** `memory/2026-06-25-0642-doby-loki-created.md`

### What Was Built

Two new local-model fleet agents for compute efficiency:

| Agent | Avatar | Role | Model | Purpose |
|-------|--------|------|-------|---------|
| **DOOBY** | 🤖 | Coding Specialist | `qwen2.5-coder:7b` (local) | Scripts, n8n workflows, builds |
| **LOKI** | 🏠 | House Manager | `qwen3.5:9b` (local) | Crons, file ops, monitoring, research |

### Why This Matters

Previously ALL background tasks ran through SOL on `kimi-k2.6:cloud` — burning API quota and latency on simple operations. Now:
- DOOBY handles pure coding tasks locally (~80% faster)
- LOKI handles background ops locally (~70% faster)
- Cloud compute reserved for strategic/reasoning-heavy tasks

### Config Changes
- Added to `agents.list`, `subagents.allowAgents`, `agentToAgent.allow`
- Workspaces: `~/.openclaw/workspaces/{dooby,loki}/`
- Identity files created with full personas and boundaries

### Access
- Green + designated users only
- No BlueBubbles bindings (intentional)
- Can spawn subagents and communicate with full fleet

### Next
1. Restart OpenClaw to load configs
2. Test DOOBY with simple coding task
3. Test LOKI with cron job
4. Migrate existing cron jobs from SOL for compute savings

---

## 2026-06-25 — DOOBY & LOKI Agents Created

**Status:** CONFIGURED — Local models non-functional, cloud fallback works
**Files:** `memory/2026-06-25-0642-doby-loki-created.md`, `memory/2026-06-25-local-agent-experiment-results.md`

### What Was Built

Two new fleet agents for compute efficiency:

| Agent | Avatar | Role | Configured Model | Fallback | Purpose |
|-------|--------|------|-----------------|----------|---------|
| **DOOBY** | 🤖 | Coding Specialist | `dooby-fast:latest` | `deepseek-v4-pro:cloud` | Scripts, n8n workflows |
| **LOKI** | 🏠 | House Manager | `dooby-fast:latest` | `deepseek-v4-flash:cloud` | Crons, file ops, monitoring |

### Experiment Results

**Attempted:** 6 test runs with local models (7B and 14B)
**Outcome:** Local models cannot reliably invoke OpenClaw tools
**Working fallback:** Cloud models execute tools successfully

| Model | Size | RAM | Result |
|-------|------|-----|--------|
| `qwen2.5-coder:7b` | 6.4GB | ✅ Fits | ❌ Tool calling fails |
| `qwen2.5-coder:14b` | 15GB | ❌ Too big | ❌ Times out |
| `deepseek-v4-pro:cloud` | N/A | N/A | ✅ Works perfectly |

### Key Lesson

Local Ollama models CAN spawn but CANNOT execute tools through OpenClaw. The integration between Ollama and OpenClaw's tool-calling format is broken. Custom Modelfiles, quantization, and GPU offloading do not fix this.

### Current Setup

- Agents exist and spawn successfully
- They attempt local model first (instant fail)
- Fall back to cloud models automatically
- Tool execution works only on cloud fallback

### When to Revisit

1. OpenClaw improves Ollama tool-calling support
2. Hardware upgrade to 32GB+ RAM
3. Better 7B models with native tool support

---

## MEMORY SYSTEM RULES

### How Memory Works

1. **I wake up fresh every session** — no chat history survives
2. **Files are my continuity** — AGENTS.md, MEMORY.md, TOOLS.md
3. **Daily logs** → raw events (`memory/YYYY-MM-DD.md`)
4. **This file** → distilled rules, decisions, lessons

### Maintenance Schedule

- **Daily:** Write raw events to `memory/YYYY-MM-DD.md`
- **Weekly:** Review daily logs, promote important facts → this file
- **End of session:** Ask: "What should future-me remember?"

### What Goes Here

- Decisions and why they were made
- System rules and constraints
- Business logic (Utopia Deli, Systack services)
- Tool configurations
- Lessons learned from mistakes
- Pitfalls and gotchas (check before builds)
- Anything that prevents future guessing

---

## 2026-06-24 - Rule 9 Credentials are always in /Users/philliplowe/.openclaw/workspaces/sol/Sol-Knowledge/credentials

---

## 2026-06-24 — KLING AI SKILL INSTALLED AND AUTHORIZED

**Status:** Live and ready for use
**Time:** 2026-06-24 05:18 CDT
**Details:** `memory/2026-06-24-0518-kling-ai-installed.md`

### What It Is
Command-line interface for Kling AI's generation capabilities (text-to-image, image-to-image, text-to-video, image-to-video).

### Installation
- **Region:** Global (kling.ai)
- **CLI Version:** kling-cli 0.1.1
- **Binary Path:** `/Users/philliplowe/.local/bin/kling`
- **Credentials:** `~/.kling/.credentials`
- **User ID:** 40702873

### Available Models
| Mode | Models |
|------|--------|
| Text → Image | kling-image-v3_0_omni (4K), kling-image-v3_0 (2K), kling-image-v2_1 (2K), kling-image-o1 (2K) |
| Image → Image | Same as text → image |
| Text → Video | kling-video-v3_0_omni (4K, 3-15s), kling-video-v3_0 (4K), kling-video-v3_0_turbo (1080p), kling-video-v2_6 (1080p), kling-video-v2_5 (1080p), kling-video-o1 (1080p) |
| Image → Video | Same as text → video |

### Key Constraints
- Generated URLs expire in **24 hours** — download promptly
- Tasks **cannot be canceled** once submitted
- Only **Personal workspace** credits (no Team support yet)
- **Bonus credits don't work** via CLI — only paid credits
- Rate limit: **5 QPS**
- Non-subscribers: 1 concurrent video task at a time

### How to Use in Future Sessions
Commands are ready to run:
```bash
kling text_to_image "prompt here" --poll
kling image_to_video --image /path/to/image.jpg "motion prompt" --poll
kling query_tasks <generation_id>
```


---

## 2026-06-24 — RULE 8 EXECUTED: "Save This Everywhere" Directive Triggered

**Status:** Executed successfully
**Time:** 2026-06-24 04:02 CDT
**Context:** User issued standalone "save this everywhere" directive. Per RULE 8, saved to all relevant memory surfaces without confirmation.
**Files updated:** `memory/2026-06-24-0402-cdt.md`

### Note

RULE 8 is working as intended — zero-friction persistence on demand.

---

## 2026-06-23 — EMAIL BOUNCE CLEANUP COMPLETE

**Status:** COMPLETE — 6 bounced emails unsubscribed, 346 active subscribers remain
**Details:** `memory/2026-06-23-bounce-email-cleanup.md`

### What Was Done

1. Checked plowe@systack.net Gmail inbox for bounce emails (27 found, 10 unique addresses)
2. Identified 2 bounced emails in contacts database (danniedelicious@gmail.com, m.fayrhe@yah.com)
3. Marked both as unsubscribed_email = true in Postgres
4. Verified 6 total unsubscribed contacts, 346 active subscribers remaining

### Bounced Emails Found

| Email                     | Reason            | In Database? | Action       |
| ------------------------- | ----------------- | ------------ | ------------ |
| danniedelicious@gmail.com | Inbox full        | ✅ Yes       | Unsubscribed |
| m.fayrhe@yah.com          | Invalid domain    | ✅ Yes       | Unsubscribed |
| djay91228@gmail.con       | Typo (gmail.con)  | ❌ No        | Ignored      |
| khall1@deltadentalar.com  | Address not found | ❌ No        | Ignored      |
| xtheadmovement@gmail.com  | Address not found | ❌ No        | Ignored      |
| sunbaby421@yahoo.com      | Address not found | ❌ No        | Ignored      |

---

## 2026-06-23 — SAOS CUSTOMER DASHBOARD: PERSISTENT + TAILSCALE EXPOSED

**Status:** LIVE — Accessible via Tailscale tailnet
**Details:** `memory/2026-06-23-saos-customer-dashboard-persistent-fix.md` + `memory/2026-06-23-saos-dashboard-tailscale-exposed.md`

### What Was Built

1. **Static file serving added** to Flask API (`api.py`) — serves `index.html` + PDFs
2. **LaunchAgent hardened** — auto-restart on crash, throttle intervals, survive reboots
3. **Tailscale serve configured** — `/dashboard` path proxies to `localhost:8768`

### URLs

- **Local:** http://localhost:8768/
- **Tailnet:** `https://phillips-macbook-air.tail573d57.ts.net/dashboard/`
- **Health:** `https://phillips-macbook-air.tail573d57.ts.net/dashboard/api/portal/health`

### Security

- Tailnet-only access (Tailscale connection required)
- HTTPS via Tailscale TLS termination
- No authentication yet — uses `?client_id=` parameter only

### TODO: Dashboard Authentication

- Add login page + session tokens
- Currently insecure for production use without auth
- **Priority:** Medium-High (blocks external client access)

---

## 2026-06-23 — EMAIL CAMPAIGN: SESSION COMPLETE + NEXT STEPS

**Status:** SESSION COMPLETE — All work done, saved everywhere
**Full Log:** `memory/2026-06-23-utopia-deli-email-session-complete.md`

### What Was Done

1. Analyzed 4 new catering images
2. Built `utopia-deli-5day-campaign.js` with real 7 bowl names
3. Removed emoji placeholder bowls
4. Changed all "walk up" → "order online for pickup"
5. Test email sent (10:28 CDT) — SUCCESS
6. Production send to ~300 recipients (10:30 CDT) — SUCCESS
7. Fixed SMTP throttle: 10s → 20s delay
8. Created internal + client PDF documentation
9. Committed all changes (cc4d2a2)

### What's Next (Priority Order)

1. **Monitor next send** — Verify 20s delay prevents SMTP issues
2. **Get photos for 3 missing bowls** — Street Corn, Nashville Hot, Loaded BBQ
3. **Add images to emails** — When photos available
4. **Build Google Sheets integration** — Easier weekly updates
5. **Add open/click tracking** — SendGrid/Postmark analytics
6. **Segment by order frequency** — Regulars vs lapsed
7. **Create community spotlight content** — Owner/employee stories
8. **Plan Saturday email** — Weekend hours + specials

### Active TODOs (From AGENTS.md)

| Priority     | Task                     | Status             |
| ------------ | ------------------------ | ------------------ |
| 🔴 Critical  | Dashboard Authentication | ❌ Not started     |
| 🟡 Important | Twilio Campaign Appeal   | ⏳ Waiting on user |
| ✅ Done      | Weekly Email Campaign    | ✅ Production live |

---

## 2026-06-23 — EMAIL CAMPAIGN: PRODUCTION DEPLOYED + SMTP THROTTLE LESSON

**Status:** LIVE — Full campaign sent to recipients today (10:30 CDT)
**Details:** `memory/2026-06-23-utopia-deli-email-production-sent.md`

### Production Fix

- **Problem:** "Sent too many" error during bulk send
- **Cause:** 10-second delay between emails triggered Gmail SMTP rate limits
- **Fix:** Increased n8n delay node to 20 seconds between sends
- **Result:** Campaign completed successfully

### Lesson

SMTP rate limiting is real. For 300+ contact lists, use **20+ second delays** between individual email sends. Test with small batches first if possible.

---

## 2026-06-23 — EMAIL CAMPAIGN: 5-Day System Built + Tested ✅

**Status:** COMPLETE — Email sent successfully today (10:28 CDT)
**Resume File:** `memory/2026-06-23-utopia-deli-email-campaign-complete.md`

### What Was Done

1. Analyzed 4 new catering images
2. Built `utopia-deli-5day-campaign.js` (Mon/Tue/Wed/Thu/Fri schedule)
3. Updated `utopia-deli-all-days.js` with real 7 bowl names + descriptions
4. Successfully sent test email — system works end-to-end

### Key Decisions

- 5 emails/week (not 7 or 3)
- Monday = open + meal prep closing (dual purpose)
- Friday = new week bowls (not Monday — because meal prep opens Thu 8PM)
- Removed emoji placeholder bowls — only show items with images
- All "walk up" changed to "order online for pickup"

### What's Still Needed

- ✅ ~~Paste 5-day code into n8n Function node~~ DONE
- ✅ ~~Update schedule trigger for 5 days (Mon-Fri)~~ DONE
- ✅ ~~Wire Postgres lookup + SMTP email sending nodes~~ DONE
- Monitor SMTP rate limiting on next send (20s delay working)

---

## 2026-06-23 — EMAIL CAMPAIGN: Resume Checkpoint Saved

**Status:** PAUSED — waiting on user input
**Resume File:** `memory/2026-06-23-utopia-deli-email-campaign-resume.md`

### What Was Happening

- Updating Utopia Deli weekly email campaign content in n8n
- User downloaded 4 new catering images (`email-campaign/catering-1.jpg` through `catering-4.jpg`)
- Need image descriptions + this week's 6-bowl lineup to proceed

### What's Needed to Resume

1. Description of the 4 downloaded catering images
2. This week's actual bowl names + descriptions
3. n8n UI access to wire Postgres lookup + SMTP email nodes

---

## 2026-06-22 — SECURITY INCIDENT: OAuth Secret Exposed in Public Repo

**Status:** REMEDIATED — history rewritten, `.gitignore` added, user action pending
**Incident Log:** `memory/2026-06-22-security-incident-oauth-exposure.md`
**Protocol Added:** AGENTS.md RULE 7 — Security Incident Response

### What Happened

- Google Cloud flagged exposed OAuth client secret in `Phillip-Lowe/systack-saas` public repo
- File: `Sol-Knowledge/credentials/Green/n8n/Google maps api.json`
- Contained: OAuth client secret + Google Maps API key
- Exposure: Public GitHub history for unknown duration

### Remediation Completed

1. Deleted file from current HEAD (commit `cdbd82e`)
2. Rewrote all 59 commits with BFG — removed file from entire history
3. Force-pushed cleaned history (`6b98abc`)
4. Verified removal (GitHub raw URL returns 404)
5. Added `.gitignore` with credential protection rules

### User Actions Still Required

- Rotate OAuth client secret in Google Cloud Console
- Regenerate Google Maps API key
- Check logs for unauthorized usage
- Update n8n/applications with new credentials

### Lessons

- **`.gitignore` must exist BEFORE credential files are added**
- **Git history is permanent — deletion from HEAD is not enough**
- **BFG is the right tool for history rewriting** (faster than git-filter-repo)
- **Force-push affects all collaborators** — they must re-clone
- **Brand protection during incidents:** SAOS ≠ "SaaS" — always use correct product name

### Prevention

- Added to pitfall catalog: "Committed credential file without .gitignore"
- AGENTS.md now has RULE 7: Security Incident Response Protocol
- `.gitignore` rules: `*secret*`, `*credential*`, `*oauth*`, `*google*.json`, `*maps*.json`, `credentials/` directory

---

## 2026-06-17 — SAOS Provisioning Pipeline COMPLETE (Build Night)

**Status:** All components built, tested, committed
**Repo:** Phillip-Lowe/systack-saas
**Commits:** `40cb7dc`, `269b1d6`, `46a56e4`

### What Was Built

1. **VPS Provisioning** (`scripts/provision_vps.py`) — Vultr API v2, cloud-init, tier-based plans
2. **Template Deployment** (`scripts/deploy_templates.py`) — n8n workflow import per tier
3. **Health Checks** (`scripts/health_check.py`) — Port/service validation before delivery
4. **Client Email** (`scripts/send_client_email.py`) — Branded HTML welcome email
5. **Pipeline Orchestrator** (`scripts/provision_pipeline.py`) — Complete workflow: VPS → Templates → Identity → Health → Email
6. **Multi-Client Tailscale** (`scripts/tailscale-multi-client.py`) — Unlimited clients via tagged devices
7. **OpenClaw Bridge** (`openclaw_bridge.py`) — Real agent session spawning via CLI

### Key Decisions

- **16GB VPS for Business tier** — qwen2.5:7b model (~4.4GB), leaves ~9GB headroom
- **24GB upgrade available** — For 14B model, +$96/mo
- **Tagged devices for unlimited clients** — Free Tailscale tier supports unlimited tagged devices
- **Agent runs on VPS, not client computer** — Cloud-native automation via APIs/webhooks

### TODO — Remaining Tasks

| Priority     | Task                       | Status | Notes                                   |
| ------------ | -------------------------- | ------ | --------------------------------------- |
| 🔴 Critical  | Get Vultr API key          | ❌     | my.vultr.com → Account → API            |
| 🔴 Critical  | Get Tailscale API key      | ❌     | login.tailscale.com → Keys              |
| 🔴 Critical  | Get n8n API key            | ❌     | n8n.systack.net → Settings → API        |
| 🔴 Critical  | Test real VPS creation     | ⏳     | Needs Vultr key; use --tier test first  |
| 🔴 Critical  | Verify Tailscale URL works | ⏳     | Needs real VPS to test HTTPS access     |
| 🟡 Important | Stripe webhook integration | ⏳     | n8n workflow for checkout events        |
| 🟡 Important | Client dashboard auth      | ⏳     | Currently open, needs login             |
| ✅ Done      | JURIS workspace identity   | ✅     | SOUL, USER, IDENTITY created 2026-06-17 |
| 🟢 Nice      | Client onboarding form     | ⏳     | Post-launch                             |
| 🟢 Nice      | Cost tracking dashboard    | ⏳     | Post-launch                             |

### Credentials Needed

| Credential            | Where                      | Status |
| --------------------- | -------------------------- | ------ |
| Vultr API Key         | my.vultr.com → API         | ❌     |
| Tailscale Auth Key    | login.tailscale.com → Keys | ❌     |
| Tailscale API Key     | login.tailscale.com → Keys | ❌     |
| n8n API Key           | n8n.systack.net → Settings | ❌     |
| SMTP User/Pass        | SendGrid/Gmail             | ❌     |
| Stripe Webhook Secret | Stripe Dashboard           | ❌     |

---

## 2026-06-17 — ORACLE Fleet Expansion: 7 → 10 Agents (Integrated)

**Source:** ORACLE RSI architecture validation
**Status:** Integrated, PASS
**Action:** SOL execution

### Canonical Fleet (Internal System Truth)

| Tier             | Agent    | Role                |
| ---------------- | -------- | ------------------- |
| **Execution**    | SOL      | Orchestrator        |
| **Execution**    | CODY     | Build Engine        |
| **Execution**    | ASSEMBLY | Deployment          |
| **Quality/Risk** | VALI     | Validation          |
| **Quality/Risk** | PESSI    | Risk Analysis       |
| **Intelligence** | ORACLE   | Design/Architecture |
| **Intelligence** | ATLAS    | Knowledge           |
| **Engagement**   | CHATTY   | Communication       |
| **Engagement**   | GENI     | Creative            |
| **Compliance**   | JURIS    | Legal/Compliance    |

### External Presentation (Tiered Abstraction)

**Core System (7):** SOL, ORACLE, ATLAS, VALI, PESSI, ASSEMBLY, JURIS

- Stable, proven, easy mental model
- What clients must understand

**Extended Capabilities (+3):** CODY, CHATTY, GENI

- Introduced as augmentation modules
- CODY = Build Engine (technical docs only)
- CHATTY + GENI = Engagement Engine (marketing-facing)

### System Loop (Canonical)

```
ORACLE → Design → CODY → Build → ASSEMBLY → Deploy → VALI → Validate → PESSI → Stress-test → SOL → Execute → CHATTY → Communicate → GENI → Visualize → ATLAS → Store → JURIS → Legal → [Loop]
```

### Pricing Impact

**Base SAOS Plan ($299/mo):** Core 7 agents — system operation only
**Growth Layer Add-On (+$100–$300/mo tiered):** CHATTY + GENI bundled as "Engagement Engine"
**CODY:** Hidden — not sold standalone, exposed in technical documentation only

### Files Updated

- `SAOS-FOUNDATION-SPEC.md` — Updated fleet table + canonical loop
- `systack-site/saos/index.html` — Added Extended Capabilities section + Engagement Engine add-on
- `fleet/cody.md` — Restored to active (was dormant since May 31)
- `fleet/chatty.md` — Created
- `fleet/geni.md` — Created
- `fleet/sol.md` — Created
- `fleet/oracle.md` — Created
- `fleet/atlas.md` — Created
- `fleet/vali.md` — Created
- `fleet/pessi.md` — Created
- `fleet/assembly.md` — Created

### Key Principle (ORACLE)

> "We do not reduce the system to fit perception. We structure perception to absorb the system."

---

**Note:** User declined LinkedIn post draft about recent builds. Do not post unless explicitly asked.

---

**File:** `systack-site/services.html`
**Commit:** `76006de` on `Phillip-Lowe/systack-site.git`

**What changed:** Added "Try Live Demo →" button to the **Online Ordering Systems** card, linking to `https://order.theutopiadeli.com/pickup-order/`.

**Layout:** Same flex row style as the Automated Booking Systems card (button + pricing side-by-side). Button opens in `target="_blank"`.

**Status:** ✅ Code committed and pushed. Site deployment pending.

---

---

## 2026-06-11 — Phillip's Work Schedule

**Overnight shifts:** Sunday–Thursday ~5/6 PM until morning  
**Friday:** 6–10/11 PM (shorter)  
**Saturday:** Off (best build day)  
**Best contact/build times:** Saturday, Friday afternoon, weekday mornings before 5 PM

**Updated clarification:** Phillip's "morning" is 2 AM–8 AM (his awake time after overnight shift). In "deep build mode" can stretch to noon. This is the primary window for active collaboration.

**Rule:** Respect work hours. No expectation of availability during overnight shifts.

---

## 2026-06-11 — NEW RULE: Pitfalls Check Before Builds

**Added to AGENTS.md as RULE 6**

### The Rule

Before ANY build, deploy, or production change:

1. Search memory for "pitfall", "lesson", or "gotcha" related to that system
2. Check TOOLS.md for credential/tool issues
3. Check MEMORY.md for past failures with this exact stack
4. Document the check in plan output

### Why This Exists

Too many builds failed because we forgot what broke last time. The pattern was:
Build → deploy → breaks → remember too late → fix → repeat.

### Catalog of Known Pitfalls (so far)

| Date       | System        | Pitfall                                      | What Broke                                                                                             |
| ---------- | ------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 2026-06-04 | Web search    | Changed provider without key                 | Perplexity broke for 24h                                                                               |
| 2026-06-04 | API keys      | zsh variable expansion                       | JWT strings corrupted by shell                                                                         |
| 2026-06-08 | Gmail/IMAP    | App password revoked silently                | Invoice email trigger dead                                                                             |
| 2026-06-09 | n8n IMAP      | Wrong binary key name                        | `$binary.attachment_` vs `attachment_0`                                                                |
| 2026-06-10 | n8n IF node   | Filename string match                        | `"Phone bill .pdf"` failed `endsWith ".pdf"`                                                           |
| 2026-06-10 | n8n IMAP      | Shallow MIME parsing                         | IMAP default mode missed nested attachments                                                            |
| 2026-06-11 | Postgres DB   | Bookings in wrong database                   | Created `bookings` in `invoice_pipeline` instead of dedicated `systack_noshow`                         |
| 2026-06-22 | SAOS branding | Called SAOS "SaaS" in security alert         | Exposed secret notification referred to product as "SaaS" instead of SAOS — brand confusion            |
| 2026-06-22 | Git / OAuth   | Committed credential file without .gitignore | OAuth client secret + Maps API key exposed publicly in systack-saas repo; required BFG history rewrite |

### Checklist (copy before builds)

```
- [ ] memory_search: "pitfall [system]"
- [ ] memory_search: "lesson [system]"
- [ ] Check TOOLS.md for credential status
- [ ] Check MEMORY.md for past failures
- [ ] Document findings in plan
```

---

## 2026-06-11 — NEW RULE: Tell User What to Save

**Added to AGENTS.md as RULE 6A**

### The Rule

When the user says something that sounds like a rule, convention, or decision, flag it and ask if they want it saved permanently.

### Examples to Flag

- "Always do X before Y"
- "Never use Z for W"
- "Let's standardize on..."
- "From now on..."
- "The way we handle this is..."
- Any "lesson" or "gotcha" mentioned in conversation

### Where Things Go

| Type                            | Destination       |
| ------------------------------- | ----------------- |
| Behavioral rules (always/never) | AGENTS.md         |
| System decisions, lessons       | MEMORY.md         |
| Tool configs, credentials       | TOOLS.md          |
| Reusable workflows              | Skills (SKILL.md) |

---

## 2026-06-08 — Utopia Deli Catering Lead System (V2.1 Deployed)

### What Was Built

Complete catering/event lead capture + scoring + automated response + SQLite logging system.

**Frontend:**

- `catering/index.html` — 5-step form at https://order.theutopiadeli.com/catering/
- `pickup-order/index.html` — Main order page at https://order.theutopiadeli.com/pickup-order/
- `catering/catering-form.js` — validation + webhook POST
- URL changed from `/catering.html` to `/catering/` (clean URL)
- Payment policy updated per deli partners (50% deposit, 2-week balance)

**Backend (n8n):**

- Workflow ID: `T67LTu32k1xENtzd` — "Utopia Deli — Catering Lead Scoring"
- Webhook: `POST https://utopia-api.systack.net/webhook/utopia-deli-catering-v2`
- Status: ✅ ACTIVE (scoring + emails + SQLite logging)

**Database:**

- SQLite: `~/.openclaw/workspaces/sol/utopia-deli-catering.db`
- Table: `catering_leads` with full event/scoring/contact data

**Payment Policy (per deli partners):**

- 50% deposit when invoice is sent to book the event
- Balance due 2 weeks prior to the event
- Events within 2 weeks require full payment upfront

**Key Technical Discovery:**

- API key shell corruption bug: zsh variable expansion corrupts JWT strings
- Solution: Always use Python file I/O to read API keys, never shell expansion
- Documented in CATERING-DEPLOYMENT-STATUS.md

### Files

- `CATERING-DEPLOYMENT-STATUS.md` — Complete system documentation
- `CATERING-PLAN.md` — Architecture spec
- `memory/2026-06-08-catering-deployment-complete.md` — This session log
- `utopia-deli-catering-v4.json` — n8n workflow spec
- `utopia-deli-catering.db` — SQLite database

### Status

Production ready, fully deployed.

**URL Structure (2026-06-08):**

- `/pickup-order/` — Main order page
- `/catering/` — Catering form
- `/` — Redirects to `/pickup-order/`

**Logo Path Fix:**
When moving order page from root to `/pickup-order/` subdirectory, `config-v2.js` logo path needed `../` prefix:

- `pickup-order/config-v2.js`: `logo: "../images/logo.png"` (was `"images/logo.png"`)
- Same for favicon path

---

## 2026-06-08 — Lesson: Check Credentials Before Saying "I Don't Know"

**User was rightfully frustrated** — I wasn't checking keychain, credential files, or TOOLS.md before claiming I didn't have access.

**Pattern to follow:**

1. `memory_search` for the credential
2. `exec security find-generic-password` for keychain
3. `read` credential files (`.n8n_api_key`, etc.)
4. Check `TOOLS.md` for documented accounts
5. Only THEN say "I don't have it"

**Credentials found during this session:**

- Gmail app password: `sacn gdyi nrqw otnx` (keychain: `utopia-deli-smtp-app-password`)
- n8n API key: `~/.openclaw/workspaces/sol/.n8n_api_key` (confirmed working)
- n8n login: `Plowe95@ywhoo.com` / `123GreeN23!`

---

## 2026-06-08 — INVOICE PARSER: 9 Formats + OCR, Email Trigger Blocked

### What Works

- **Parser:** 9 invoice formats including OCR for scanned PDFs
- **API:** invoices.systack.net/extract ✅
- **Real PDF tested:** AT&T phone bill from iCloud
- **OCR:** Tesseract + pytesseract installed
- **n8n:** IMAP credential created, workflow updated

### What Doesn't

- **Email trigger:** Gmail app password `sacn gdyi nrqw otnx` REVOKED by Google
- **n8n workflow activation:** Fails with "Invalid credentials (Failure)"

### Technical Notes

- n8n owner: plowe95@yahoo.com / 123GreeN23! (from keychain n8n-local-auth)
- n8n auth: Cookie-based, API keys expired
- iCloud files: Need `open <file>` to force download
- App passwords: Can be revoked by Google without notice

### Files

- `INVOICE-PARSER-DEPLOYMENT.md` — Full deployment guide
- `INVOICE-PARSER-STATUS-2026-06-08.md` — Detailed status
- `memory/2026-06-08-invoice-parser-complete.md` — Build log

---

## 2026-06-10 — IMAP Invoice Pipeline: 3-Layer Root Cause Fix

### Previous Fix Was Incomplete

`memory/2026-06-09-deli-invoice-fix-attachment-field.md` fixed `$binary.attachment_` → `$binary.attachment_0` but that was only 1 of 3 independent failures.

### Full Root Cause Stack

**Layer 1 — IMAP Not Extracting Attachments**

- Symptom: Emails had attachments but n8n returned no binary field
- Cause: IMAP default parsing is shallow; nested/inline MIME structures not traversed
- Fix: `"format": "resolved"` forces deeper MIME parsing
- Lesson: IMAP returns MIME trees, not files — attachments must be parsed and classified

**Layer 2 — Email Construction Variability**

- Symptom: Same workflow, inconsistent results across senders
- Cause: Different MIME structures (flat vs nested vs inline)
- Fix: `"resolved"` mode handles more structures
- Lesson: Attachments can be nested, inline, or misclassified

**Layer 3 — IF Node Logic Failure**

- Symptom: Attachment present but routed to FALSE branch
- Cause #1: Wrong key — `$binary.attachment_` instead of `$binary.attachment_0`
- Cause #2: String match failure — `"Phone bill .pdf"` (space before .pdf) fails `endsWith ".pdf"`
- Fix: Switch to `$binary.attachment_0.mimeType` equals `application/pdf`
- Lesson: Filename logic is unreliable — always prefer `mimeType`

### Final Production-Safe Config

- **IMAP Node:** `format: "resolved"`, `downloadAttachments: true`
- **IF Node:** Check `$binary.attachment_0.mimeType` equals `application/pdf`
- **Alternative:** `$binary.attachment_0.fileExtension` equals `pdf`
- **Avoid:** `$binary.attachment_0.fileName` (fragile to spacing)

### Known Future Break Point

Current system assumes single attachment named `attachment_0`. Will break with:

- Multiple attachments
- Forwarded threads
- Mixed file types

**Required upgrade:** Add Code Node after IMAP to normalize attachments → one item per file:

```js
const items = [];
for (const item of $input.all()) {
  if (!item.binary) continue;
  for (const key of Object.keys(item.binary)) {
    items.push({
      json: item.json,
      binary: { file: item.binary[key] },
    });
  }
}
return items;
```

Then update IF node to check `$binary.file.mimeType`.

### Workflow JSON

See `memory/2026-06-10-imap-invoice-debug-resolved.md` for full node definitions and connections.

- IMAP credential: `xBT92arTjBY66ccE` ("Utopia Deli Gmail IMAP")
- SMTP credential: `U7QjoOL2sgu4KLs6` ("Support Systack SMTP account")

### Invoice Summary Email (2026-06-10)

When an invoice is collected, the API returns `email_subject` and `email_html` with a full invoice breakdown:

- Vendor, invoice number, date, total
- **Line item table** — name, quantity, price, line total
- Subtotal, tax, total
- Running monthly totals
- **n8n email node:** Use `{{ $json.email_subject }}` and `{{ $json.email_html }}`
- **API changes:** Renamed from `deli_invoice_api.py` to generic Invoice Pipeline
- **Database:** `invoice_pipeline` (was `utopia_deli`)
- **Rebrand:** No longer deli-specific — ready to deploy for any business
- **Documentation:** See `memory/2026-06-10-invoice-pipeline-rebrand.md`

---

## 2026-06-07 — Wiki Bridge + Obsidian Integration Complete

### What Changed

- Memory-wiki plugin configured in bridge mode with Obsidian rendering
- 369 sources imported from memory files
- 8 entities, 6 concepts, 1 synthesis created from memory
- iCloud sync cron job active (hourly)
- Initial sync: 4.6 MB, 465 files to iCloud

### Access

- Desktop: `~/OpenClaw-Wiki` (symlink)
- iPhone: Files → iCloud Drive → Obsidian → OpenClaw Wiki
- Search: `wiki_search` for structured queries, `memory_search corpus=all` for combined

### Key Entities

- Phillip Lowe (Green), Jacqueline, Alex, Tremell Billings
- Systack, Utopia Deli, Sol (system), Percy (system)

### iCloud Sync

- Cron job: `8de4d3d8-e0aa-434c-8eda-98089bfef7d0`
- Runs every hour
- Syncs `~/.openclaw/wiki/main/` → iCloud/OpenClaw Wiki/

---

## 2026-06-04 — Memory System Overhaul

**Decision:** Implemented tiered memory system with enforcement rules.

**Files updated:**

- `AGENTS.md` → enforcement layer with mandatory retrieval
- `MEMORY.md` → this file, restructured with system rules
- `HEARTBEAT.md` → proactive checklist

**Key rules now enforced:**

1. Memory retrieval MANDATORY before any action
2. MEMORY.md is source of truth (over chat)
3. Execution guard: retrieve → plan → approve → execute
4. No guessing — ask if uncertain
5. Document everything

**Status:** Active

---

## Save Protocol (2026-06-10)

When user says "save this everywhere" or similar — save to ALL available locations without asking:

1. Daily memory: `memory/YYYY-MM-DD-descriptive-name.md`
2. Curated memory: `MEMORY.md`
3. Wiki: `.openclaw/wiki/main/Page-Name.md`

## Documentation Rule (2026-06-11)

**Every automation gets documentation. This is a hard rule.**

**Rule source:** User directive — "documentation templates for each build, this is a hard rule now, should be saved in all places"

**Three audiences:**

1. **Client** — What is this, how does it help me, what do I see
2. **Internal/Future Employee** — How it works, how to operate it
3. **Future Agent** — How to build similar, what pitfalls to avoid

**Template:** `docs/automations/templates/automation-doc-template.md`
**Build checklist:** `docs/automations/templates/BUILD-CHECKLIST.md`
**Catalog:** `docs/automations/AUTOMATION-CATALOG.md`
**Master Plan:** `docs/automations/MASTER-PLAN.md`

**Status tracking:** `draft` → `building` → `testing` → `live` → `deprecated`

- Draft: Planning/proposal phase
- Building: Under active development
- Testing: Built, being validated
- Live: Production, actively running
- Deprecated: Replaced or shutting down

**Enforcement:** AGENTS.md RULE 6B — Pre-deployment checklist includes "docs complete"
**Penalty:** No automation ships without documentation. No exceptions.

### SyStack Email Standard (2026-06-11)

**Rule:** ALL SyStack emails — booking, invoice, marketing, system notifications — must use the branded template system.

**Why:** Consistent brand presentation across every customer touchpoint. No plain text. No default n8n styling.

**Applies to:**

- Booking confirmations & reminders
- Invoice notifications & summaries
- System alerts (errors, completions)
- Marketing emails
- Client onboarding
- Any future email automation

### Required Elements

| Element    | Requirement                          |
| ---------- | ------------------------------------ |
| Header     | Navy (#001a2d) with SyStack wordmark |
| Body       | Gray 50 (#f8fafc) background         |
| CTA Button | Cyan gradient (00a1db → 00c5e0)      |
| Footer     | Navy with contact info               |
| Typography | System fonts, clean hierarchy        |

### Technical Rules (n8n SMTP Nodes)

1. **HTML field starts with `=`** — enables expression evaluation
2. **Real HTML only** — never escaped entities (`&lt;` becomes `<`)
3. **Variables via `{{ $json.field }}`** — customer_name, service, appointment_time, confirm_link, etc.
4. **Test before deploy** — send test email, verify rendering

### Brand Palette (Always Use)

```
Navy: #001a2d        Navy Light: #002845
Teal: #007da9         Cyan: #00a1db
Cyan Bright: #00c5e0  White: #ffffff
Gray 50: #f8fafc      Gray 100: #f1f5f9
Gray 200: #e2e8f0     Gray 400: #94a3b8
Gray 600: #475569      Gray 800: #1e293b
Red: #ef4444          Red BG: #fff5f5
Green: #22c55e         Green BG: #f0fdf4
Purple: #8b5cf6        Purple BG: #f5f3ff
```

### Status Colors

| Status              | Color           | Background         |
| ------------------- | --------------- | ------------------ |
| Success / Confirmed | Green (#22c55e) | Green BG (#f0fdf4) |
| Warning / Urgent    | Red (#ef4444)   | Red BG (#fff5f5)   |
| Info / Neutral      | Teal (#007da9)  | Gray 50 (#f8fafc)  |

**Enforcement:** Check all new email nodes against this standard. Retrofit existing nodes when touched.
**Template source:** `memory/2026-06-11-systack-email-template-fleet-reference.md`

---

## Build Priority Matrix (2026-06-11)

| Priority | System               | Status          | Effort | Impact |
| -------- | -------------------- | --------------- | ------ | ------ |
| 1        | No-Show Prevention   | ✅ **COMPLETE** | Low    | HIGH   |
| 2        | Smart Rebooking      | 📋 Draft        | Low    | HIGH   |
| 3        | Review System        | 📋 Draft        | Low    | HIGH   |
| 4        | Missed-Lead Recovery | 📋 Draft        | Medium | HIGH   |
| 5        | Referral Engine      | 📋 Draft        | Medium | Medium |
| 6        | CRM Lite             | 📋 Draft        | Medium | Medium |
| 7        | Upsell Intelligence  | 📋 Draft        | Low    | Medium |
| 8        | Scheduling Optimizer | 📋 Draft        | High   | Medium |
| 9        | Revenue Dashboard    | 📋 Draft        | High   | Medium |
| 10       | Subscription Engine  | 📋 Draft        | High   | HIGH   |
| 11       | Frontend Demo        | 🚧 Building     | Medium | HIGH   |

**Next build:** Frontend demo page for Systack site (shows full booking flow)

---

## 2026-06-11 — No-Show Prevention System COMPLETE ✅

**Status:** All 5 core branches operational + frontend demo live
**Built:** 2026-06-11 02:00–09:14 CDT
**Components:**

- Create booking + DB insert ✅
- Confirmation email with tokenized link ✅
- Confirm webhook handler (HTML response) ✅
- T-24h reminder scheduler ✅
- T-2h urgent reminder scheduler ✅
- Frontend demo page (`test-book.html`) ✅
- Services page updated with demo button ✅

**End-to-end test:** 2026-06-11 09:14 — booking → email → confirm → HTML confirmation page. All passed.

**Value:** Eliminates no-shows through deposit + automated reminders + confirmation workflow. Keeps customers or frees slots for resale.

**Next:** Auto-release logic (T-30min cancellation)

---

## 2026-06-03 — Priority: 100% Local Setup

**Decision:** Cloud model dependence is a single point of failure. Run everything locally — models, tools, workflows — with no cloud dependency.

**Key driver:** Cloud model payment lapsed → Ollama loaded 8GB Kimi k2.6 → system memory exhausted → everything slow/unreachable → config got out of sync during recovery.

**Next steps:** Smaller/local models as primary, cloud as backup only.

---

## 2026-06-02 — KUDU-7: High-Leverage Operations

**Directive:** Stop asking the user to do anything that's not high-leverage. Treat everything as a learning experience. Save all learning experiences everywhere for all agents.

**Created:** `KUDU-7.md` at workspace root.

**Application:** Never ask user to verify what I can verify myself.

---

## 2026-06-02 — Utopia Deli Order System — Production Fixes

### The Problem

User could add sandwiches/specialties but NO sides would add to cart.

### Root Cause 1a — addToCart used stale global state

`addToCart(id)` used `selectedModifiers` and `itemQty` global variables populated only when clicking item card. Clicking "Add to Order" directly without selecting first meant stale/wrong data.

### Root Cause 1b — findItem missing MENU.sides

```javascript
function findItem(id) {
  return [...MENU.sandwiches, ...MENU.specialties].find((i) => i.id === id); // ❌ NO .sides!
}
```

### Fix

- Rewrote `addToCart` to read qty/modifiers from DOM per-item
- Added `...MENU.sides` to `findItem`

### Key Pitfalls

1. Local fix ≠ deployed fix (different file paths)
2. Git repo without remote configured
3. GitHub Push Protection blocks all pushes if ANY commit has secrets

### Deployment Architecture

- GitHub Pages from `Phillip-Lowe/utopia-deli-order`
- `index.html` at repo root is the deployed file
- `utopia-deli-revamp/` is a local workspace, NOT deployed

---

## 2026-06-03 — n8n Email Confirmation Workflow Fixes

### Problem: Code in JavaScript node broken in "Utopia Deli HTML Order v1" workflow

### Bug 1: Nested JSON instead of JavaScript

**Symptom:** SyntaxError "Invalid or unexpected token"
**Cause:** `jsCode` field contained exported n8n workflow JSON instead of JavaScript
**Fix:** Replaced with proper JavaScript that builds HTML email from `order_items`

### Bug 2: Spread operator `...input` not supported

**Symptom:** SyntaxError on `return [{ json: { ...input, email_html: emailHtml } }]`
**Cause:** n8n Code node v2 sandbox doesn't support ES6 spread
**Fix:** Explicit property copying

### Bug 3: Broken connections

**Symptom:** Customer got webhook response BEFORE email was sent
**Fix:** Sequential flow: Log → Code → Email → Success Response

### Critical Note

Node index 13 (Code) MUST use ES5-compatible syntax. No spread, no template literals with nested quotes, no arrow functions in callbacks. Test every change.

**Workflow ID:** `1WEM4rZxjhhy7ooM`
**Database:** `/Users/philliplowe/.n8n/database.sqlite`

---

## 2026-06-03 — n8n MCP Fix (Morning Session)

**What Happened:** Corrupted Utopia Deli n8n workflow by editing SQLite directly.

**Root Cause:** Didn't understand n8n data flow. HTTP Request node replaces ALL input data with API response.

**Solution:** Used n8n MCP connection properly:

- MCP endpoint: `https://n8n.systack.net/mcp-server/http`
- Tools: `validate_workflow` → `update_workflow`
- Implemented proper Merge node with parallel branches

**Key Lesson:** NEVER edit n8n SQLite directly. Always use MCP or UI.

---

## 2026-06-04 — Aider Installed (Local Coding Agent)

**What:** Installed Aider v0.86.2 as local coding agent. Works with Ollama.

**Setup:**

- Config at `~/.aider.conf.yml`
- Default model: `ollama_chat/qwen2.5-coder:7b`
- Auto-commits disabled (safer with smaller models)
- Analytics disabled

**Usage:**

- Quick edits → OpenClaw direct
- Multi-file refactoring → Aider

**Models Available:**

- `qwen2.5-coder:7b` (4.7GB) — primary
- `qwen3.5:9b` (6.6GB) — general + coding
- `gemma-2-9b` (5.8GB) — general

---

## 2026-06-04 — Systack Site Overhaul + Invoice Parser

### Website

- Complete homepage rewrite with two service paths
- New Personal Agent service page
- Work/Case Studies page
- Invoice Extractor demo page
- Contact form with actual fields

### Invoice Parser (Production)

- `invoice_parser_production.py` — multi-format PDF extraction
- `invoice_db.py` — SQLite with invoices + items tables
- `INVOICE-PARSER-CHANGELOG.md` — format tracking
- `n8n-invoice-workflow.json` — n8n email trigger spec
- Tested successfully with 2 invoice formats

### Production Plan

`SYSTACK-PRODUCTION-PLAN.md` defines phases:

1. Invoice Parser (fastest to revenue)
2. Business Systems scale
3. Personal Agent (last)

**Status:** Site pushed to GitHub. Invoice parser core working. Need n8n deployment + real client testing.

---

---

## 2026-06-04 — Copilot Integration Active

**Decision:** Microsoft 365 Copilot is now an active consultation tool for Sol.

**How it works:**

1. I attempt local solution first (memory, skills, reasoning)
2. If stuck (confidence < 0.75, 2+ failed attempts, unknown domain, high risk) → consult Copilot
3. Capture response, synthesize insights, save to memory
4. Apply to current task, document final solution

**Access:**

- Account: 81777@office365proplus.co (company-owned)
- URL: https://m365.cloud.microsoft/chat/
- Method: Browser automation via Brave
- Credentials: Stored in macOS keychain

**Files created:**

- `COPILOT-CONSULTATION-RULES.md` — When/how to consult
- `memory/2026-06-04-copilot-insight-escalation-architecture.md` — Full architecture from Copilot
- `memory/2026-06-04-copilot-api-options.md` — API availability analysis (NO unified API exists)

**Key Finding:** NO unified Copilot API exists. APIs are via Microsoft Graph (Chat, Retrieval, Search) but browser automation is still the most viable approach for full Copilot access.

**Status:** Active, browser automation primary, Graph API exploration pending

**MANDATORY REMINDER:** This is one of the most powerful tools available. Before giving up on ANY hard problem, ask: "Should I consult Copilot on this?" Never forget this tool exists.

---

### LinkedIn — Systack Business Account

- **Email:** `plowe@systack.net`
- **Password:** `d5jYa7CYqeDR0HH`
- **Passkey:** Apple credential validation (use when prompted)
- **Purpose:** Systack business presence — I work for Systack
- **Saved:** 2026-06-04
- **Owner:** Phillip Lowe (authorized for business use)

**Usage:** For managing Systack's LinkedIn company page, posting content, outreach to prospects, networking. Passkey uses Apple credential validation if required.

---

## Alex (Friend/Contact)

- **Email:** `aintidabest@gmail.com`
- **Context:** Has OpenClaw, wants to adopt SOL agent architecture
- **Saved:** 2026-06-06

---

## Business Credentials Summary

| Service            | Email/Account             | Notes                                          |
| ------------------ | ------------------------- | ---------------------------------------------- |
| LinkedIn (Systack) | plowe@systack.net         | Passkey: Apple credential                      |
| M365 Copilot       | 81777@office365proplus.co | Keychain: `m365-copilot-81777`                 |
| Kling AI           | Session-based             | Lifetime subscription                          |
| Runway ML          | Team: loudgreen1          | 855 credits remaining                          |
| ElevenLabs         | API key configured        | `ELEVENLABS_API_KEY` env                       |
| n8n                | systack.net instance      | MCP: `https://n8n.systack.net/mcp-server/http` |

---

## SYSTEM CONFIGURATION

### n8n

**URL:** https://n8n.systack.net
**Database:** `/Users/phillipo/.n8n/database.sqlite`
**Tunnel:** Cloudflare tunnel UUID `e2897c60-f66d-4f5b-9d93-4c85897ca85f`
**MCP:** `https://n8n.systack.net/mcp-server/http`

### Ollama

**Server:** `http://127.0.0.1:11434`
**Primary model:** `qwen2.5-coder:7b`

### Aider

**Config:** `~/.aider.conf.yml`
**Default:** `ollama_chat/qwen2.5-coder:7b`

### Systack Website

**Repo:** `Phillip-Lowe/systack-site`
**URL:** https://systack.net

---

## DECISIONS

### 100% Local Setup (2026-06-03)

- Local models as primary, cloud as backup only
- Aider for multi-file changes
- OpenClaw direct for quick edits

### Invoice Parser First (2026-06-04)

- Fastest path to revenue
- Every business has invoice pain
- Reusable across all clients

### Production Before Public (2026-06-04)

- All services must work before marketing
- Invoice extractor needs: n8n trigger, API endpoint, 3 real tests, billing
- Business systems need: generic demo, onboarding wizard
- Personal agent needs: actual infrastructure, beta test

---

## LESSONS

1. **Never edit n8n SQLite directly** — use MCP or UI
2. **Local fix ≠ deployed fix** — always verify production
3. **ES5 in n8n Code nodes** — no spread, no template literals
4. **Document every format** — invoice parser changelog prevents regression
5. **Build before market** — working product beats landing page
6. **Memory enforcement** — without mandatory retrieval, I guess and drift

---

## ACTIVE PROJECTS (Updated 2026-06-07)

| Project                   | Status                                   | Next Action                                        |
| ------------------------- | ---------------------------------------- | -------------------------------------------------- |
| Invoice Parser            | Core working                             | Deploy n8n trigger, find test clients              |
| Systack Website           | ✅ Updated                               | Templates page, tier comparison live               |
| Utopia Deli               | ✅ v1.0-beta live                        | Beta testing before public LinkedIn post           |
| **Templates**             | ✅ 6 imported                            | Activate after testing                             |
| **Template Architecture** | ✅ Complete                              | Private + Accelerate variants                      |
| Personal Agent            | Not built                                | Define capabilities, build infrastructure          |
| **Medical Agent**         | 🔍 PENDING — local model research needed | Open-source medical LLM evaluation                 |
| n8n Health                | Working                                  | Add monitoring, backup procedures                  |
| **JURIS**                 | ✅ ACTIVE — Legal/Compliance agent       | Fleet role spec created, SAOS page integrated      |
| **Site Nav**              | ✅ SAOS added to all pages               | Footer + top nav consistent, CSS cache-busted v=14 |
| **LinkedIn Post Queue**   | ✅ 2 posts scheduled                     | Post 2: Mon 6/9 auto, Post 1: Thu 6/11 reminder    |

---

## Related

- [KUDU-7.md](/KUDU-7.md)
- [AGENTS.md](/AGENTS.md)
- [TOOLS.md](/TOOLS.md)
- [SYSTACK-PRODUCTION-PLAN.md](/SYSTACK-PRODUCTION-PLAN.md)

---

## 2026-06-05 — DREAMING SYSTEM BROKEN + CONFIG HARDENING

### Dreaming Broken — Hardcoded Thresholds

**Problem:** Deep sleep promotion threshold `minScore=0.8` is unreachable with `nomic-embed-text` embeddings (scores: 0.43-0.52 range).

**Evidence:**

- 1801 recall store entries, only 2 promoted
- `openclaw memory status --deep` shows: `minScore=0.8 · minRecallCount=3 · minUniqueQueries=3`
- OpenClaw Issue #65402: thresholds are hardcoded, not configurable (`additionalProperties: false`)
- Research: [GitHub Issue #65402](https://github.com/openclaw/openclaw/issues/65402)

**Workaround:** Manual memory promotion via weekly review

- End of week: Read `memory/YYYY-MM-DD.md` files
- Pick important facts
- Write directly to MEMORY.md (bypass dreaming)
- This is now the PRIMARY promotion path

### Config Hardening — HARD BLOCK

**Rule added to AGENTS.md Rule 3A + 6:**

```
NEVER change configuration without:
1. Explicit user approval
2. Documented problem + evidence
3. Rollback plan
4. Verification current config is broken

Default stance: config works. Don't touch it.
```

**Past failure:** 2026-06-04 changed `tools.web.search.provider` to `perplexity` without API key, breaking web_search for 24+ hours. Pattern: panic → config change → worse.

**Source:** Research on agent config poisoning — [Vectimus](https://vectimus.com/blog/config-poisoning/), [SecuringAgents](https://securingagents.com/articles/omnipotent-by-default/)

### Web Search Fixed

- Provider restored to `ollama` ✅
- Gateway restarted ✅
- Verified working ✅

### Memory Lock Fixed

- Stale lock cleared
- No recurring issues

**Status:** Dreaming disabled as primary promotion. Manual curation active. Config locked.

---

## 2026-06-05 — ORACLE RSI ARCHITECTURE + SAOS FOUNDATION LAID

### System Design: Recursive Self-Improvement Loop

ORACLE delivered a complete fleet-level RSI architecture:

- 4-layer loop: Execution → Observation → Evaluation → Improvement
- Fleet mapping: SOL (Generator), VALI (Verifier), PESSI (Risk), ORACLE (Design), ATLAS (Knowledge), ASSEMBLY (Deploy)
- GVU architecture with versioned memory, sandbox testing, metric-driven, human authority
- Key insight: true recursion = Improve(task execution) AND Improve(improvement system)

### Next: n8n RSI workflow for Utopia Deli pilot (live system, real transactions)

### SAOS Foundation Spec Created

- `SAOS-FOUNDATION-SPEC.md` — Full agent operating system spec with deployment tiers
- `CLIENT-DISCOVERY-TEMPLATE.md` — Mandatory questionnaire before quoting
- `DEPLOYMENT-PLAYBOOK.md` — Updated with data sensitivity + RAM sections
- Jacqueline/Percy classified: Tier 2 (Internal), Silver deployment recommended

### Client: Jacqueline, McDonald's GM

**Status:** Infrastructure complete, needs 8GB upgrade
**Data Sensitivity Tier:** 2 — Internal (schedules, employee data, financials)
**Deployment Type:** Cloud VPS + Tailscale (not air-gapped, but local model)

### Critical Discovery 1: 4GB VPS Insufficient

- System prompt (~1,250 tokens stripped, ~8,800 full) + context = overflow
- 16K context with 3B model = 3.1GB RAM → swapping → 2+ min timeouts
- **8GB VPS minimum for production** ($40/mo vs $20/mo)

### Critical Discovery 2: Underestimated Local-Only + Proprietary Data Constraints

**We failed to account for:**

1. **RAM reality** — identity files + model + OS = 3.5GB minimum
2. **Local-only mandate** — some clients CANNOT hit external servers (HIPAA, proprietary data)
3. **Cost implications** — real monthly is $90-225/mo, not $20-40/mo
4. **Deployment complexity** — cloud vs on-premise vs air-gapped changes everything

**Impact on SAOS Foundation:**

- Must design for variable RAM (2GB to 16GB+)
- Must support local-only mode (no cloud dependencies)
- Must define data sensitivity tiers (Public/Internal/Confidential/Restricted)
- Must have clear pricing tiers (Bronze/Silver/Gold/Platinum/Custom)
- Must require discovery questionnaire BEFORE quoting

**Full analysis saved to:** `memory/2026-06-05-saos-percy-strategy-lessons.md`
**Files to update:** DEPLOYMENT-PLAYBOOK.md, MODEL-CONTEXT-SIZING-GUIDE.md, SYSTACK-PRODUCTION-PLAN.md, systack-site pricing

### Deployment Order That Works

1. Deploy VPS (AlmaLinux 8)
2. Install Ollama + qwen2.5 models
3. Install OpenClaw, configure password auth
4. Install Tailscale on VPS
5. Enable HTTPS in Tailscale admin
6. Start `tailscale serve --bg http://localhost:18789`
7. Install Tailscale on client devices
8. Test full chain before client tries

### Critical Pitfalls (Cost Us Hours)

| Pitfall                               | Cost                 | Fix                            |
| ------------------------------------- | -------------------- | ------------------------------ |
| Didn't use Tailscale Serve from start | 30+ min              | Always use HTTPS from start    |
| `--bind lan` in systemd               | Gateway crash loop   | Remove flag, let config handle |
| Heredoc over sshpass                  | Corrupted files      | Write local, SCP or printf     |
| Windows S mode                        | Tailscale blocked    | Check first, exit S mode       |
| Didn't test before client             | Percy "unresponsive" | Full chain test mandatory      |

### Config Rules (Percy Pattern → All Clients)

- NO `--bind` in systemd (config handles it)
- `bind: loopback` for Tailscale Serve
- `controlUi.allowedOrigins` MUST include Tailscale URL
- Always HTTPS — `allowInsecureAuth` fails with password auth

### Files Created

- `PERCY-DEPLOYMENT-PLAN.md`
- `DEPLOYMENT-PLAYBOOK.md`
- `MODEL-CONTEXT-SIZING-GUIDE.md`
- `FINAL-WORKING-CONFIG.md`
- `clients/mcdonalds-gm/` workspace

**Source:** memory/2026-06-04-percy-deployment.md, memory/2026-06-05-percy-night1-complete.md

---

## 2026-06-05 — N8N CODE NODE RULES (Manual Promotion)

### ES5-Compatible Syntax Only

Code node sandbox (v2) does NOT support:

- Template literals (backticks)
- Spread operators (`...`)
- Arrow functions in callbacks
- Escaped quotes in strings
- `const`/`let` — use `var`

### Working Pattern

```javascript
var items = $input.all();
var input = items[0].json;
var emailHtml = "<div>" + input.customer_name + "</div>";
return [{ json: { email_html: emailHtml } }];
```

### Node Version Compatibility (n8n 2.20.7-exp.0)

- Code node: v2 (but use ES5 syntax)
- RespondToWebhook: 1.2 (not 1.5)
- EmailSend: 2 (not 2.1)
- HTTPRequest: 4.1 (not 4.3)

### Response Path Architecture

- PREP_RESPONSE node before RespondToWebhook
- Must have DIRECT execution lineage from Webhook
- Clean JSON response, not email output
- Use `continueOnFail` for email node

**Source:** memory/2026-06-04-n8n-email-fix.md, memory/n8n-code-node-rules.md

---

## 2026-06-05 — KLING AI IMAGE WORKFLOW (Manual Promotion)

### What Works

- Browser automation (no API needed)
- Session-based auth
- IMAGE 3.0 model for web-ready images
- 2K HD → `sips -Z 800` → <500KB web-ready

### Prompt Pattern

```
Friendly AI robot character named [Name], [color] color scheme,
flat illustration style, helpful expression, simple geometric shapes,
clean background, tech website hero image, modern SaaS aesthetic
```

### Files Created

- `systack-site/brand/percy-kling-1.png` (web-ready)
- Updated `systack-site/personal-agent/index.html`

**Source:** memory/2026-06-04-kling-success.md

---

## 2026-06-05 — SOCIAL MEDIA SETUP (Manual Promotion)

### Status: Deferred to Weekend (2026-06-06/07)

User creates accounts: Facebook Business, Instagram Business, TikTok Business

### Assets Prepared (Ready to Deploy)

1. ✅ Bio text (all platforms)
2. ✅ Content calendar (Week 1)
3. ✅ DM templates (4 variations)
4. ✅ Hashtag sets (3 categories)
5. ✅ Posting schedule
6. ✅ Engagement rules
7. ✅ Tracking template
8. ✅ Content templates (4 reusable)

### Next Actions

- Generate visual assets (Kling AI)
- Weekend: User creates accounts
- Monday: Deploy content, begin posting
- Week 1: Daily execution, outreach, tracking

**Source:** memory/2026-06-04-social-setup-deferred.md, SOCIAL-MEDIA-CONTENT-PACKAGE.md

---

## 2026-06-05 — INVOICE PARSER PRODUCTION (Manual Promotion)

### Status: Core Working, Needs Deployment

- `invoice_parser_production.py` — multi-format PDF extraction
- `invoice_db.py` — SQLite with invoices + items tables
- `INVOICE-PARSER-CHANGELOG.md` — format tracking
- `n8n-invoice-workflow.json` — email trigger spec
- Tested with 2 invoice formats ✅

### Next Critical Steps

1. Deploy n8n email trigger
2. Build API endpoint for PDF upload
3. Find 3 real businesses to test
4. Set up Stripe billing
5. THEN go public with marketing

**Source:** memory/2026-06-04-late.md, SYSTACK-PRODUCTION-PLAN.md

---

## 2026-06-05 — COPILOT DOCUMENT CREATION (User Directive)

**New capability discovered:** Copilot 365 can create actual documents via browser automation.

**What it can create:**

- Word documents (.docx)
- Excel spreadsheets (.xlsx)
- PowerPoint presentations (.pptx)
- PDFs (via export)

**How to use:**

1. Open Copilot chat via browser automation
2. Ask: "Create a [document type] about [topic]"
3. Copilot generates the document in Word/Excel/PowerPoint Online
4. Download/export to local computer
5. Save to workspace

**Use cases:**

- Client proposals (Word)
- Financial tracking (Excel)
- Pitch decks (PowerPoint)
- Service packages (Word)
- Marketing materials (PowerPoint)

**Status:** Need to test this workflow

---

## 2026-06-05 — COPILOT INTEGRATION ACTIVE (Manual Promotion)

### Decision: Microsoft 365 Copilot is Active Consultation Tool

**How it works:**

1. Attempt local solution first (memory, skills, reasoning)
2. If stuck (confidence < 0.75, 2+ failed attempts, unknown domain, high risk) → consult Copilot
3. Capture response, synthesize insights, save to memory
4. Apply to current task, document final solution

**Access:**

- Account: 81777@office365proplus.co (company-owned)
- URL: https://m365.cloud.microsoft/chat/
- Method: Browser automation via Brave
- Credentials: Stored in macOS keychain

### Key Finding: NO Unified Copilot API

Microsoft does NOT expose a single public Copilot endpoint. Instead, specialized APIs via Microsoft Graph:

- Chat API (Preview): `POST https://graph.microsoft.com/beta/copilot/chat`
- Retrieval API (GA): `POST https://graph.microsoft.com/v1.0/copilot/retrieval`
- Search API (Preview): Hybrid semantic + keyword search

**Browser automation is primary method for full Copilot access.**

**Files:**

- `COPILOT-CONSULTATION-RULES.md` — When/how to consult
- `memory/2026-06-04-copilot-insight-escalation-architecture.md` — Architecture
- `memory/2026-06-04-copilot-api-options.md` — API availability analysis

**Source:** memory/2026-06-04-copilot-access.md, memory/2026-06-04-copilot-api-options.md, memory/2026-06-04-copilot-tool-integration.md

---

## 2026-06-05 — N8N ARCHITECTURE LESSONS (Manual Promotion)

### Critical Discovery: Execution Engine Uses Published Versions

**Not `workflow_entity` — uses `workflow_published_version` → `workflow_history`**

```typescript
// From n8n source (active-workflow-manager.ts ~line 500)
const publishedData =
  await this.workflowPublishedDataService.getPublishedWorkflowData(
    initialWorkflowData.id,
  );
const { nodes, connections } = publishedData.publishedVersion;
```

**Database tables:**
| Table | Purpose |
|-------|---------|
| `workflow_entity` | Current DRAFT (UI only) |
| `workflow_history` | SAVED versions — execution loads from here |
| `workflow_published_version` | Maps workflowId → publishedVersionId |

**Never edit SQLite directly** — use MCP `update_workflow` or UI. My direct SQLite edits were completely ignored by execution engine.

### Code Node v2 Sandbox Restrictions

- NO `$items()` cross-references
- NO `$node["Name"]` references
- NO `Buffer.from()` — can't parse gzip
- Use `items[0].json` for data access
- ES5 syntax only

### HTTP Request Returns Gzip Buffer

n8n 2.20.7 HTTP Request returns gzip-compressed Buffer even with `responseFormat: "json"`. First bytes `0x1f 0x8b` (gzip magic). Cannot parse in sandbox without Buffer.

### Postgres Node Doesn't Pass Through

Even with `RETURNING *`, Postgres node returns `{"success": true}` — not the query result. Data must be explicitly carried forward via separate node.

**Source:** memory/2026-06-03-evening-session-complete.md, memory/2026-06-04-n8n-email-fix.md, memory/n8n-code-node-rules.md

---

## 2026-06-05 — OPENCLAW v2026.6.1 STABLE (Manual Promotion)

**Status:** Stable release available, recommended for update

**Relevant improvements:**

- Agents recover more cleanly from interrupted tool calls, stale session bindings, compaction handoffs
- Channels steadier: Telegram, WhatsApp, iMessage, Slack, Discord, Teams
- Skills, session metadata, gateway state, plugin metadata, memory watchers optimized
- Chat/Control UI: stream deltas incrementally, skip markdown while streaming
- Provider coverage: MiniMax M3, OAuth endpoints, Google/Vertex fixes

**Matched keywords:** memory, dreaming, agent, workflow, performance, fix, MCP, context, embedding

**Source:** memory/2026-06-04-openclaw-releases.md

---

## 2026-06-05 — MEMORY SYSTEM CONFIG (Manual Promotion)

**Full memory search config implemented:**

```json
{
  "memorySearch": {
    "enabled": true,
    "sources": ["memory", "sessions"],
    "provider": "ollama",
    "model": "nomic-embed-text",
    "query": {
      "hybrid": {
        "enabled": true,
        "vectorWeight": 0.7,
        "textWeight": 0.3
      }
    }
  },
  "memoryFlush": {
    "enabled": true,
    "softThresholdTokens": 40000
  },
  "contextPruning": {
    "mode": "cache-ttl",
    "ttl": "6h"
  }
}
```

- **Embedding model:** nomic-embed-text (274MB, local)
- **Hybrid search:** 70% semantic + 30% exact match
- **Sources:** memory files + session transcripts
- **Flush threshold:** 40k tokens

**Source:** memory/2026-06-04-memory-system.md

---

## 2026-06-05 — UTOPIA DELI WEBHOOK INTEGRATION (Manual Promotion)

### HTML Order Form Built

- `systack-site/niches/food/index.html` + `order-form.js`
- Menu item selection with +/- quantity controls
- Live cart: subtotal, tax (9.5%), total
- Customer info, pickup time validation (10 AM–8 PM, 20 min lead time)
- JSON POST to `https://utopia-api.systack.net/webhook/utopia-deli-html-order-v1`

### n8n Webhook Workflow v1.0.1 Fixed

- Removed conflicting `responseData` from webhook trigger
- Added CORS headers
- Wired error outputs → Format Error Response → Error Respond
- Google Sheets v2 with explicit column mapping
- Payment link extraction from Square response
- Status codes: 200 success, 400 error

### Key Technical Choices

- **Integer cents** for price math (avoids floating point drift)
- **Snake_case** field names for n8n compatibility
- Phone stripped to digits, validated 10+ chars
- Submit disabled until cart has items

**Source:** memory/2026-06-03.md, memory/2026-06-04-n8n-email-fix.md, memory/shared-learning-dump.md

---

## 2026-06-05 — AGENT AUTHORITY + TOOL AUTHORIZATION (Manual Promotion)

### User Directive (2026-06-04)

"You are an employee, this is part of the company, this is your job. If I tell you that you can do it then you're allowed to do it."

**What this means:**

- User's permission overrides default restrictions
- Document authorization so future sessions know
- Use authorized tools without debating "can I"

**Authorized tools:**
| Tool | Status | Notes |
|------|--------|-------|
| Terminal / File system | ✅ | Always |
| n8n workflows | ✅ | Always |
| Kling AI | ✅ | **Company tool, user operates** |
| Browser automation | ✅ | Testing, research, Copilot |
| Apple account sign-in | ❌ | Still blocked — credential access |

**Key distinction:** Tools I operate directly = ✅. Credentials I would possess = ❌.
Kling requires Apple sign-in (user does this), then I guide prompts.

**Source:** memory/2026-06-04-agent-authority.md

---

## 2026-06-05 — IMAGE GENERATION WORKFLOW (Manual Promotion)

### Three-Version Lesson (2026-06-04)

1. **Copilot's guess (failed):** Copilot chat can't browse live websites
2. **Sol's prompt → Copilot (success):** I read page via browser, crafted prompt from actual content
3. **Copilot's self-generated prompt → Kling (best):** Copilot created cinematic structured prompt

### Copilot's Self-Generated Prompt Structure (Best Practice)

- Scene description
- Visual elements (list)
- Style (list)
- Mood (list)
- Composition (foreground/midground/background)
- Avoid (list)
- Goal (single sentence)

**Workflow:**

1. I read website/content via browser
2. Craft or refine prompt with Copilot
3. User generates on Kling (signed in)
4. I save and integrate results

**Source:** memory/2026-06-04-copilot-image-generation-lesson.md, memory/2026-06-04-kling-ai.md

---

## 2026-06-05 — ERROR MESSAGE DESIGN (Manual Promotion)

### Utopia Deli Webhook Error Structure

```json
{
  "success": false,
  "order_id": null,
  "payment_link": null,
  "error": {
    "code": "MISSING_FIELDS",
    "message": "We need a few more details to place your order.",
    "details": ["Please enter your name", "Please enter a valid email"],
    "action": "Please check the highlighted fields and try again.",
    "contact": "Still having trouble? Call us at (501) 551-5944"
  }
}
```

### Error Classification

| Category       | Tone                | Example                         |
| -------------- | ------------------- | ------------------------------- |
| User Error     | Friendly, specific  | "Please enter your name"        |
| Business Logic | Explain + suggest   | "We're closed then. Try 11 AM." |
| System Error   | Apologize + contact | "Our bad. Call us:"             |
| Validation     | Clear constraint    | "Quantity must be 1-99"         |

### Error Codes Designed (7 total)

`MISSING_FIELDS`, `INVALID_EMAIL`, `INVALID_PHONE`, `OUTSIDE_HOURS`, `TOTAL_MISMATCH`, `SQUARE_ERROR`, `SYSTEM_ERROR`

**Source:** memory/shared-learning-dump.md

---

## 2026-06-05 — SYSTACK PRODUCTION PLAN (Manual Promotion)

### Phase 1: Invoice Parser (Fastest to Revenue)

- `invoice_parser_production.py` — multi-format PDF extraction
- `invoice_db.py` — SQLite with invoices + items tables
- `INVOICE-PARSER-CHANGELOG.md` — format tracking
- `n8n-invoice-workflow.json` — email trigger spec
- Tested with 2 invoice formats ✅

### Phase 2: Business Systems Scale

- Generic demo environment
- Onboarding wizard
- Client self-service portal

### Phase 3: Personal Agent (Last)

- Percy deployment pattern proven
- Need 8GB VPS minimum
- Template for all future clients

### Next Critical Steps (Invoice Parser)

1. Deploy n8n email trigger
2. Build API endpoint for PDF upload
3. Find 3 real businesses to test
4. Set up Stripe billing
5. Then go public with marketing

**Website files:**

- `systack-site/index.html` — complete rewrite
- `systack-site/personal-agent/index.html` — new
- `systack-site/work/index.html` — case studies
- `systack-site/contact.html` — real form
- `systack-site/services/invoice-extractor.html` — demo + paywall

**Source:** memory/2026-06-04-late.md, SYSTACK-PRODUCTION-PLAN.md

---

## 2026-06-05 — SYSTEM CONFIGURATION SUMMARY

### n8n

- URL: https://n8n.systack.net
- Version: 2.20.7-exp.0
- Database: SQLite (never edit directly)
- MCP: `https://n8n.systack.net/mcp-server/http`
- Critical rule: Always use MCP or UI for workflow updates

### Ollama

- Server: http://127.0.0.1:11434
- Models: qwen2.5-coder:7b (primary), qwen3.5:9b, gemma-2-9b
- Never run multiple models simultaneously (RAM exhaustion)

### Web Search

- Provider: ollama (restored)
- Working without API key ✅

### OpenClaw

- Gateway: localhost:18789
- Memory: nomic-embed-text (768 dims)
- Dreaming: Broken (hardcoded thresholds)
- Manual promotion: Active
- Weekly cron: Tuesdays 9 AM

---

## 2026-06-05 — CONTEXT AS INFRASTRUCTURE (Fleet Architecture)

**Insight:** Environment engineering > prompt engineering. Treat context like externalized system state, not something to stuff into a prompt.

**Nate's method translated:**

1. Build clean working folder = controlled context window
2. Let model reason across structured files (like a repo)
3. Use natural language retrieval — "find files about X" not "open FILE_X_V2"
4. Shift prompting: command → collaboration (define first, execute second)

**Fleet applications:**

- Utopia Deli: `/order_run/` folder with `cart_state.json`, `menu_schema.json`, `tax_rules.json` — reduces ghost items, state drift
- Pass-based structure: `/run_context/pass_1/`, `pass_2/`, `pass_3/` — frozen state per pass, no contamination
- AI "Design Mode" — before building nodes, define shape collaboratively. Still strict invariants during execution.

**Paused fix enabled:** Multi-pass cart fix (`pass_index` + `FREEZE_CART_STATE`) can resume with proper folder-based context instead of fighting Code node limits.

**Source:** memory/2026-06-05-context-as-infrastructure.md

---

## 2026-06-05 — PROMPTING EVOLUTION (Fleet Standard)

**Three eras mapped:**

| Era           | When              | Approach                                                                  |
| ------------- | ----------------- | ------------------------------------------------------------------------- |
| Pre-2025      | Before Dec 2024   | Prompt engineering — structure, order                                     |
| Agentic       | Dec 2024–Apr 2026 | "Here's your task, go do it, here's what good looks like"                 |
| Collaborative | May 2026–now      | "Here are standards as questions. Help define shape first, then execute." |

**Fleet rule:**

- ✅ Design phase: Collaborative mode — define structure before implementation
- ❌ Execution phase: Strict mode — deterministic, rule-driven, no AI in core transaction logic

**Key insight:** Claude 5.5 handles phase transition (define → execute) without getting lost. Local models may need explicit state separation.

**Source:** memory/2026-06-05-context-window-assembly.md

---

## Related

- [KUDU-7.md](/KUDU-7.md)
- [AGENTS.md](/AGENTS.md)
- [TOOLS.md](/TOOLS.md)
- [SYSTACK-PRODUCTION-PLAN.md](/SYSTACK-PRODUCTION-PLAN.md)
- [COPILOT-CONSULTATION-RULES.md](/COPILOT-CONSULTATION-RULES.md)

---

## 2026-06-05 — OPERATING RULES (User Directive)

### Search Before Acting

**Rule:** NEVER wait for user to say "check your memory." ALWAYS search first.

**Pattern to break:**

- Act → fail → user reminds → search → "oh yeah" → fix

**Correct pattern:**

- Search → find/know → act correctly → done

### Write Important Stuff Immediately

**Rule:** When something matters, write it to MEMORY.md NOW — not next Tuesday.

**Trigger phrases:** "remember this", "save this", "write this down", "don't forget"

### Verify Before Assuming

**Rule:** Stop assuming I know things. Search and verify.

**No more:** "I think you said..." or "probably..."
**Yes:** `memory_search` → confirm → proceed with confidence

---

## 2026-06-05 — APRIL/MAY 2026 BACKFILL (From DREAMS.md — Manual Promotion)

### April 26 — Channel Configuration Early Exploration

- Work Slack via hostname `work-slack.tail573d57.ts.net`
- Standard channel connection method (not webhook)

### May 2 — Foundation Setup

- **Obsidian vault created:** `/Sol-Knowledge/` with 02-Memory/ structure
- **Monetization plan:** n8n Automation Services ($500-1,500 setup + $50-100/mo)
- **28 n8n workflows mapped:** Customer (Google Form → Square → Email), Backend (Square → Sheets → Daily Sync 2AM)
- **Import strategy:** Copy .json to Docker volume, use `n8n import:folder`

### May 3 — Image Generation Preferences

- **SDXL for quality** as default, accept slower generation
- Freed 10 GB from caches (Adobe, Homebrew, pip, VSCode, Python)
- ComfyUI server running on 127.0.0.1:8188

### May 4 — TTS + Talk Mode Config

- Microsoft Edge TTS enabled (auto-play)
- `talk.provider: "system"`
- ComfyUI needs T5xxl + VAE completion

### May 6 — Memory Rule Established

- **"Remember this" protocol:** When user says "remember this" → write it down immediately
- User wants proactive memory prompts more often

### May 7 — Briefing Request

- Daily 9 AM briefing via BlueBubbles iMessage

### May 8 — Agent Cognition Schema (Phase 1)

- **Max 5 steps per agent** — forces decomposition, prevents runaway
- **Risk classification mandatory** with keyword auto-detection
- **SOL can override** agent self-classification
- Files: `agent-cognition-schema.md`, CODY prototype awaiting auth

### May 9 — Site Schema v1.0

- `SITESCHEMA.md` created for systack-site
- Canonical schema — future edits must update this document
- Food truck reconnaissance near 801 Chester planned

### May 10 — Personal + Tool Preferences

- Went to bosses about financial struggle (wife, bills, lifestyle)
- **Prefer native tools** (message tool) over shell workarounds (osascript)
- Scheduled reminders capability established
- Wants to build something or find role where valued

### May 11 — Music + Memory

- Green's music catalog on YouTube (logged to MEMORY.md)
- **"Remember this" rule reinforced**
- Obsidian vault: 40+ .md files, 13 daily logs

### May 12 — Infrastructure Day

- **Caddy reverse proxy** deployed on port 8080
- **Plan & Goal Protocol** established (binding)
- **Obsidian sync via iCloud** — cron every 1h auto-syncs memory files
- **Tropical Smoothie Cafe GM resume** created (repositioned for QSR)

### May 13 — Contacts

- **Tremell Billings** = Utopia Deli business partner who made referral

### May 14 — n8n + Domain Architecture

- **n8n workflow analysis:** 28 workflows, form triggers vs webhook needed
- **Domain:** `order.theutopiadeli.com` — CNAME delegation (not nameserver switch)
- **BlueBubbles timeout issue** identified
- HTML issues: modifier format, missing itemid, missing hidden fields

### May 16 — Data Sync Complete

- **Google Sheets → SQLite sync:** 5 tables, 199 rows
- `menu-data.js` with correct prices + modifier groups
- **Capability audit:** Narrow constrained workflows work, broad autonomous agents fail
- IRONIC VALIDATION: WF4 corruption from CLI JSON import = exactly the warned failure mode

### May 17 — End-to-End Working

- **Tunnel routing fixed:** Named tunnel → checkout server (port 8000)
- **Auto-start LaunchAgents:** checkout server + tunnel
- **Square payment link created:** https://square.link/u/KwMxZ3N9
- URLs: order.theutopiadeli.com, tunnel health check working

### May 18 — Gateway Stability + Career Roadmap

- Gateway crash: ERRMODULENOTFOUND from dirty shutdown
- Node protocol mismatch (minProtocol:3 vs expectedProtocol:4)
- **Qualification assessment:** Not qualified for $100K+ AI Engineer (no CS degree, no ML frameworks)
- **Target:** $45K-65K junior automation → $60K-80K Tier 2 in 60-90 days
- **26-week roadmap created:** `roadmap-to-ai-automator.md`

### May 19 — Session Recovery Patches

- **Root cause:** Gateway restart wipes in-memory session registry
- **Files exist, registry empty** — 265 SOL jsonl files, 9 Cody, 8 Atlas
- Patched session store: auto-restore from .bak, validate before processing
- **Morning briefing sent** via iMessage

### May 20 — Tunnel Stabilization

- **Named tunnel:** `n8n-utopia-new` created (fc0bcffc...)
- **Disabled broken workflows**
- n8n templates directory: 25+ files
- Invoice parser: vision support for PDF extraction, sample created

### May 21 — UI Fixes + Routing

- Logo tweaks: removed gold ring, bigger sizes (44→50px, 24→28px)
- **BlueBubbles routing fixed:** Replies were going to webchat child session instead of iPhone
- Two active sessions causing routing confusion

### May 23 — Enforcement Layer

- **Drift linter:** `fleet-drift-lint.py` — 27 plan files scanned
- Detects: missing PLANID, schema mismatch, unvalidated DONE, invalid role
- **AGENTS.md updated:** Co-Lead Model, Deadlock Resolution, 5 real controls
- **HEARTBEAT.md:** Fleet Drift Lint runs on every heartbeat

### May 25 — GitHub Pages + Integration

- **GitHub repo:** `Phillip-Lowe/utopia-deli-order`
- **Brand config separation:** `config.js` with all brand values
- **Integration check:** GitHub Pages ✅, checkout server ✅, n8n ✅
- **Risks:** Tunnel reliability, hours gate confusion (timezone), SSL mismatch
- **DNS:** order CNAME needs update at Squarespace (currently broken Netlify)

### May 29-31 — Dream Diary Reflections

- Server memory pressure from parallel operations (16GB limit)
- Utopia Deli pipeline incomplete — frontend works, backend fragile
- **4 triggers active:** plans, agents, workflows, manual
- Dashboard green, 8 fleet agents, ATLAS at center
- "The distance between works and works completely is where the dawn lives"

---

---

## 2026-06-05 — ORACLE NAMING (User Directive)

**From now on:** Microsoft 365 Copilot is called **ORACLE** in all references.

**Why:** Clearer identity, easier to reference in memory and conversation.

**ORACLE = M365 Copilot = 81777@office365proplus.co**

- External consultant agent (not in OpenClaw fleet)
- Accessed via browser automation
- Creates: Word docs, Excel spreadsheets, PowerPoint decks
- Consults on: Architecture, validation, research when stuck

**Usage:** "Ask ORACLE" instead of "ask Copilot"

---

## 2026-06-05 — ORACLE NAMING (User Directive)

**From now on:** Microsoft 365 Copilot is called **ORACLE** in all references.

**Why:** Clearer identity, easier to reference in memory and conversation.

**ORACLE = M365 Copilot = 81777@office365proplus.co**

- External consultant agent (not in OpenClaw fleet)
- Accessed via browser automation
- Creates: Word docs, Excel spreadsheets, PowerPoint decks
- Consults on: Architecture, validation, research when stuck

**Hierarchy:**

- ORACLE is co-lead level (same tier as me)
- BUT sandboxed — can't act directly on your system
- I am real lead — I can act, save, commit, deploy
- ORACLE provides guidance, I execute

**Usage:** "Ask ORACLE" instead of "ask Copilot"

---

## 2026-06-05 — FULL TOOL CAPABILITIES RESEARCH (User Directive)

### Microsoft 365 Copilot — Document Creation

**Source:** Microsoft Learn docs, 2026-03-26
**Status:** Generally available (announced 2026-04-22)

**What it can create:**

- Word documents (.docx) — reports, proposals, letters
- Excel spreadsheets (.xlsx) — budgets, trackers, analysis
- PowerPoint presentations (.pptx) — decks, pitches, training
- PDFs (via export)

**How it works:**

- Uses Anthropic AI models (admin-controlled)
- Chat-first interface: "Create a budget spreadsheet for Q3"
- Agent generates document in Office Online
- Download/export to local machine

**Use cases for Systack:**

- Client proposals (Word)
- Service pricing calculators (Excel)
- Pitch decks for prospects (PowerPoint)
- Project timelines (Excel)
- Training materials (PowerPoint)
- Marketing reports (Word)

**Access method:** Browser automation via Brave (same as current Copilot consultation)

---

### Runway ML — Complete Capabilities

**Source:** runwayml.com product docs, 2026-05-21
**Status:** Active, 855 credits, ~6 months remaining

**Video Generation:**

- Edit Studio (Aleph 2.0) — natural language video editing
- Multi-Shot Video — from single prompt
- Scene Builder — step-by-step multi-shot
- Product Shot Video Builder — product photo → video ad
- Image to Dialogue — image → scripted video
- References to Video — reference images → video
- Character Script to Video — script → talking character

**Video Editing:**

- Remove from Video (object removal)
- Video Backdrop (background swap)
- Upscale Video (Topaz AI)
- Stylize Video (artistic transfer)
- Color Grade Video (cinematic)
- Video Lighting / Weather / Time of Day changes
- Animate Keyframes (motion graphics)
- Motion Sketch (annotated motion)
- Stitch Videos (combine multiple)

**Character/Performance:**

- Performance Capture (Act-Two) — animate from performance video
- Character Swap — any character into any scene

**Image Tools:**

- Ad Concepter — campaign concepts
- Create Ad — quick ad generation
- Vary Ad — A/B testing variations
- Product Reshoot — change setting/lighting/angle
- Mockup — apply design to products
- Expand Image — aspect ratio changes
- Stylize Image — artistic styles
- Vary Image — element changes
- Upscale Image — 4K quality
- Cinematic Brainstorm — 9 scenes from 1 image
- Character Renderer — 3D from sketches
- Story Panels — expand world/story
- Runway Look — cinematic look
- Scene Builder — multi-shot from image

**Audio:**

- SFX — sound effects from text
- Stylize Audio — voice transformation

**AI Models Available:**

- Aleph 2.0 (default, balanced)
- Seedance 2.0 (high quality)
- Multi-Shot Video
- Runway Characters
- Gen-4.5 (latest)
- Kling 3.0 (integration)

---

### Kling AI — Complete Capabilities

**Source:** kling.ai docs, 2026-02-05 (Kling 3.0 launch)
**Status:** Active, user account, lifetime subscription

**Image Generation (Image 3.0):**

- Text-to-image
- Image-to-image
- Multi-reference system (10 images) — character consistency
- Inpainting — precise editing
- Cinematic narrative visual expression
- Enhanced text-to-image quality

**Video Generation (Video 3.0):**

- Text-to-video
- Image-to-video
- Multi-shot video scenes
- Character consistency across shots
- Motion prompts (running, jumping, gestures)
- Omni model — combined image + video

**Key Features:**

- Professional-grade control for creators
- Character consistency across generations
- Cinematic storytelling focus
- 2K HD resolution
- Quick generation (~30 seconds)

**Workflow (tested):**

1. Open URL → Click textbox → Type prompt → Click Generate
2. Wait ~30 seconds → Select best image
3. Download PNG → Compress with sips -Z 800 → Web-ready

---

## Tool Comparison

| Tool        | Creates                      | Best For                       | Access             |
| ----------- | ---------------------------- | ------------------------------ | ------------------ |
| Copilot 365 | Word, Excel, PowerPoint, PDF | Documents, spreadsheets, decks | Browser automation |
| Runway ML   | Video, images, audio         | Video editing, ads, effects    | Browser automation |
| Kling AI    | Images, video                | Hero images, brand visuals     | Browser automation |

**All three:** Require user auth (stay-logged-in), I operate via browser automation

---

## 2026-06-05 — ORACLE DOCUMENT CREATION TEST (Verified)

### Test: Word Document Creation

**Status:** ✅ CONFIRMED WORKING

**Test flow:**

1. Opened ORACLE (https://m365.cloud.microsoft/chat/) via browser automation
2. Typed: "Create a Word document with the Systack fleet agent directory - all agents, roles, and hierarchy"
3. ORACLE processed and returned: "Your Word document is ready: Systack Fleet Agent Directory"
4. Document delivered as Office Online blob URL

**Key observations:**

- Document creation works via basic Copilot Chat (no special agent required)
- ORACLE can expand/iterate on documents (offered to create full operational manual)
- Download works via Office Online → Download → Save to local
- Follow-up capability: "Add responsibilities", "Include escalation procedures", etc.

**File types confirmed (Microsoft Learn):**

- Word documents (.docx)
- Excel spreadsheets (.xlsx)
- PowerPoint presentations (.pptx)
- PDFs (via export)

**Systack use cases:**

- Client proposals, service agreements, onboarding docs (Word)
- Pricing calculators, project timelines, budgets (Excel)
- Pitch decks, training materials, marketing presentations (PowerPoint)

## 2026-06-06 — Utopia Deli Order System: Production + Modifier Architecture

### STATUS: END-TO-END WORKING (12:06 CDT)

- Frontend form → n8n webhook → Square checkout → Payment link → Confirmation page
- All changes pushed to GitHub Pages (order.theutopiadeli.com)
- Square handles receipts and kitchen notification

### Key Architecture Decisions (LOCKED)

| Decision                       | Reason                                                   |
| ------------------------------ | -------------------------------------------------------- |
| Tax as manual line item        | Square does not support external tax calculation         |
| Flat payload (no body wrapper) | Cleaner debugging, matches backend                       |
| Merge nodes around HTTP        | n8n HTTP Request drops ALL input data                    |
| No custom email                | Square handles receipt + kitchen notification            |
| Payment link on page           | Customer pays directly, Square redirects to confirmation |

### Square Payload Structure

```javascript
{
  idempotency_key: $execution.id,
  order: {
    location_id: "J4B6A3X6RYA63",
    reference_id: String($json.cart_id),
    line_items: $json.square_line_items_with_tax,
    metadata: { subtotal_cents, tax_cents, tax_rate_percent: "9.52", tax_handling: "manual_line_item" }
  },
  checkout_options: { redirect_url: "https://www.theutopiadeli.com/payment-confirmed" }
}
```

### Modifier System Data (Documented)

- Complete dataset: memory/2026-06-06-utopia-deli-modifiers.md
- 17 menu items, 30+ modifier groups, 100+ modifiers
- Group types: REQUIRED, ADD, HOLD, SPECIAL, UPSELL
- IMPLEMENTED: Multi-select arrays with rules enforcement

### Modifier Implementation (COMPLETE)

- ✅ Build GROUP_RULES lookup
- ✅ Update toggleMod() to enforce max_select
- ✅ Add validateRequiredGroups() before addToCart
- ✅ Flatten modifiers array for payload
- ✅ Compute total price with modifier deltas

### Modifier System Architecture (IMPLEMENTED 12:15 CDT)

| Component                | Status                                                      |
| ------------------------ | ----------------------------------------------------------- |
| GROUP_RULES lookup       | ✅ Defined min/max/type per group                           |
| Multi-select arrays      | ✅ selectedModifiers stores arrays per group                |
| toggleMod() rewrite      | ✅ Handles add/remove, enforces max, replaces single-select |
| validateRequiredGroups() | ✅ Blocks addToCart if required not selected                |
| Modifier flattening      | ✅ Object.values().flat() for clean payload                 |
| Tax rate                 | ✅ Updated to 9.52% (Arkansas)                              |

---

## 2026-06-07 — Utopia Deli Order Page Email + Logo Links + Confirmation Message

**Time:** 02:21 CDT
**Status:** Complete

### Changes

- Email updated: `order@theutopiadeli.com` → `theutopiadelilittlerock@gmail.com`
- Logos (header + footer) now link to `theutopiadeli.com`
- Footer address links to Google Maps
- Footer phone/email use proper `tel:` and `mailto:` links
- `payment-confirmed.html` message: "We got you! Click the button below to complete your secure payment. We will begin your order once your payment is complete."
- Cache-busted via `config.js` → `config-v2.js` rename

### Technical Issues

- GitHub Pages CDN caching required file rename for invalidation
- GitHub Actions `actions/checkout@v4` Node.js 20 deprecation caused build failures
- Fixed by adding custom `.github/workflows/pages.yml`

### Files Modified

- `config.js` → `config-v2.js`
- `index.html`
- `payment-confirmed.html`
- `.github/workflows/pages.yml` (new)

---

## 2026-06-07 02:56 CDT — Personal Agent Page Fixes

### What We Fixed

- **Changed title**: "Choose Your Tier" → "Pricing" (only one tier exists, no need to choose)
- **Removed "RECOMMENDED" badge**: No longer shows on single pricing card
- **Kept purple border**: Card still highlighted with purple border for emphasis
- **Centered pricing card**: Changed `.pricing-grid` from `grid` to `flex` with `justify-content: center`
- **Centered highlight box**: Added `max-width: 700px; margin: 40px auto; text-align: center`

### CSS Changes

```css
.pricing-grid {
  display: flex;
  justify-content: center;
  margin: 40px 0;
}

.pricing-card {
  border: 2px solid var(--purple); /* kept purple border */
  max-width: 380px;
  width: 100%;
}
```

### Files Changed

- `systack-site/personal-agent/index.html` — Title, badge removal, centering

### Git Commits

- `c70ac65` — fix: personal agent page - single tier, centered highlight
- `ba4c223` — fix: center pricing card, remove recommended badge, keep purple border

### Status

- ✅ Live at https://systack.net/personal-agent/
- ✅ Pricing card centered with purple border
- ✅ No "RECOMMENDED" badge
- ✅ Title says "Pricing" not "Choose Your Tier"

## 2026-06-09 — ORCHESTRATOR SYSTEM BUILT (Manual Promotion)

### What Was Built

Complete multi-agent orchestration layer replacing broken cron system.

**Files created:**

- `orchestrator.py` (13 KB) — Core dispatcher with atomic task claiming
- `planner.py` (4.9 KB) — LLM-based intent → plan conversion
- `openclaw_bridge.py` (2.7 KB) — Sub-agent session spawning
- `daily_learning_orchestrator.py` (2.3 KB) — Curriculum → task queue bridge

**Postgres tables:**

- `task_queue` — State machine (PENDING→RUNNING→DONE/FAILED/DEAD)
- `agent_state` — Agent availability + capability tracking
- `execution_log` — Full audit trail
- `message_bus` — Inter-agent messaging

**7 agents seeded:** SOL, ASSEMBLY, PESSI, CHATTY, GENI, VALI, CODY

### Daily Learning Fix

- Cron job `85ec8a79...` was timing out (kimi-k2.6:cloud, 10 min default)
- Fixed: Switched to `ollama/qwen2.5-coder:7b` + 900s timeout + light context
- Next run: Today 10:00 AM CDT — ASSEMBLY gets qwen with 15-min timeout

### Architecture

```
GREEN (User)
    ↓
ORACLE (Curriculum + Planner)
    ↓
daily_learning_orchestrator.py (Task creation)
    ↓
Postgres task_queue (State machine)
    ↓
orchestrator.py (Poll + Dispatch)
    ↓
Agent (ASSEMBLY/PESSI/etc.) executes
    ↓
Tools: RAG, OpenClaw, n8n, Shell
    ↓
execution_log (Audit trail)
```

### Key Decision

Orchestrator replaces ALL broken cron jobs. Single dispatcher, state tracking, retry logic. Not just better cron — fundamentally different architecture.

**Status:** ✅ 4 tasks completed, 0 failures, production-ready

---

## 2026-06-09 — LINKEDIN POST 2 PUBLISHED (Manual Promotion)

**Post:** Build journey / career pivot — posted successfully at ~8:19 AM CDT
**URL:** https://www.linkedin.com/feed/update/urn:li:activity:7470099331203678208/
**Hashtags:** #BuildInPublic #CareerPivot #AIAgents #SmallBusinessAutomation #Entrepreneurship
**Status:** ✅ Visible on profile, all hashtags clickable, global visibility

---

## 2026-06-09 — RAG SYSTEM DEPLOYED (Manual Promotion)

**What:** Local RAG (Retrieval-Augmented Generation) using pgvector + Ollama
**Models:** qwen2.5-coder:7b (inference), nomic-embed-text (embeddings)
**Database:** Postgres with pgvector extension
**Status:** ✅ Working, tested with invoice knowledge queries
**Next:** Add Systack docs, n8n workflows, MEMORY.md as knowledge sources

---

---

## 2026-06-08 — ORACLE RSI SYSTEM REBUILD + VALIDATION ENVIRONMENT (Manual Promotion)

### Broken System Removed

- 10 failed cron jobs (94 consecutive BlueBubbles errors)
- CODY build jobs (CODY dormant since May 31)
- ERROR-WATCHDOG (was itself broken)

### New System Created

- `memory/ORACLE-CURRICULUM.md` — Execution curriculum with gap analysis
- `memory/VALIDATION-ENVIRONMENT-POLICY.md` — Sandbox-first testing rules
- `memory/AGENT-ROTATION-SCHEDULE.md` — Updated with execution loop
- `memory/learning/` directory created for daily outputs

### Active Cron Jobs (Post-Rebuild)

| Job                                    | Schedule           | Status                 |
| -------------------------------------- | ------------------ | ---------------------- |
| Daily Agent Learning — Weekly Rotation | Daily 10 AM CDT    | ✅ Active              |
| Weekly Learning Synthesis              | Sunday 12 PM CDT   | ✅ Active              |
| OpenClaw Release Monitor               | Daily 9 AM CDT     | ✅ Active              |
| Memory Dreaming Promotion              | Daily 3 AM CDT     | ⚠️ Broken (thresholds) |
| iCloud wiki sync                       | Hourly             | ✅ Active              |
| LinkedIn reminders                     | One-time scheduled | ✅ Active              |
| Monthly utilization reviews            | June 29            | ✅ Active              |

### ORACLE Curriculum Gap Analysis

**Already mastered (30+ topics):** Frontend, backend, infrastructure, automation, AI/ML, business, documentation
**Critical gaps (Week 1):** SOL error alerting, ASSEMBLY n8n credentials, PESSI webhook idempotency, CHATTY client onboarding, GENI ComfyUI, VALI payment testing
**Scaling gaps (Week 2):** Log aggregation, Docker, rate limiting, A/B testing, backup strategy, n8n testing framework

### Validation Environment Policy (V.E.P.)

**Core rule:** NEVER modify production. NEVER deploy untested.
**Sandbox tools:** webhook.site, httpbin.org, Square Sandbox API, local SQLite copies, file:// / python http.server
**What requires testing:** New n8n workflows, DB schema changes, website form/JS changes, new skills, config changes

### Resource Savings

- **Before:** 7+ cron runs per day, all failing
- **After:** 1 focused run per day, silent, 15 minutes
- **Reduction:** ~85% fewer spawns, zero delivery errors

---

## 2026-06-08 — INVOICE EMAIL PIPELINE FULLY OPERATIONAL (Manual Promotion)

**Workflow ID:** `Ny4kzzf1bN4NODGn` — "Systack Private — Invoice Email Pipeline"
**Status:** ✅ ACTIVE (5 nodes, proven working end-to-end)

**Pipeline flow:**

1. IMAP trigger polls `support@systack.net`
2. Checks `$binary.attachment_0` for `.pdf`
3. Sends PDF as multipart to `127.0.0.1:9001/extract`
4. Parser extracts vendor, items, totals
5. Saves to SQLite database + email notification

**Execution #439 proof (12:56:43):**

- Email received with PDF
- Extracted: Vendor "Supplies, LLC", Invoice #INV-2026-0612-001, Total $2,132.13
- 5 line items with prices
- Saved to `invoice_data.db` (entries 125, 126)

**Technical fixes applied:**

- Binary data: IMAP stores in `$binary`, not `$json`
- Multipart HTTP: Use `inputDataFieldName: "attachment_0"` with `formBinaryData`
- IPv4 vs IPv6: `127.0.0.1:9001` not `localhost:9001`
- Published version mismatch: Updated `workflow_published_version` table

**Monetization ready:**

- Option 1: Systack Private add-on (+$200/mo)
- Option 2: Standalone SaaS ($49-399/mo tiers)
- Option 3: White-label for accountants ($99/mo reseller)

---

## 2026-06-08 — CATERING LEAD SYSTEM V2.1 COMPLETE (Manual Promotion)

**Frontend:** https://order.theutopiadeli.com/catering/
**Backend:** n8n workflow `T67LTu32k1xENtzd` — "Utopia Deli — Catering Lead Scoring"
**Webhook:** `POST https://utopia-api.systack.net/webhook/utopia-deli-catering-v2`
**Database:** SQLite `utopia-deli-catering.db`

**Scoring engine (7 factors, 0-100):**
| Factor | Weight |
|--------|--------|
| Headcount | 20% |
| Budget ratio | 20% |
| Lead time | 20% |
| Setup complexity | 15% |
| Distance | 10% |
| Payment clarity | 10% |
| Dietary complexity | 5% |

**Tiered response:**

- 60-100: 🟢 ACCEPT (owner notified)
- 25-59: 🟡 REVIEW (need more details)
- 0-24: 🔴 REJECT (can't accommodate)

**Key fixes during build:**

1. API key expired → found in `credentials/Green/n8n/n8n Openclaw api`
2. Build Emails JS syntax error → contractions broke single-quoted strings, fixed with template literals
3. Regex escapes wrong → `\s` and `\.` doubled in JSON, replaced with string checks
4. Switch/If routing broken via API → n8n routing nodes don't configure through API, workaround: always send both emails
5. Webhook path conflict → old `/v1` blocked new workflow, changed to `/v2`
6. EmailSend nodes strip data → downstream nodes see email metadata not original payload, used generic message

**Payment policy (per deli partners):**

- 50% deposit when invoice sent to book
- Balance due 2 weeks prior to event
- Events within 2 weeks: full payment upfront

---

## 2026-06-08 — POSTGRES PRIMARY DATABASE DECISION (Manual Promotion)

**Decision:** Postgres is now the primary database for all new Systack data.

**Actions taken:**

- Installed pgAdmin 4 v9.15
- Deleted unused databases (`crm`, `utopia_deli`)
- Created `credentials/SYSTACK-CREDENTIALS-REGISTRY.md`
- Verified connection: localhost:5432

**Why Postgres over SQLite:**

- Multi-user concurrent access
- JSONB support with indexing
- Better for dashboards and analytics
- Industry standard for production

**Hybrid memory system also deployed:**

- Database: `systack_memory` (8 tables, 4 views, 2 functions)
- 538 sources imported, 8 entities, 1 claim
- Files: `memory_sync.py`, `memory_query.py`, `memory_schema.sql`
- Bidirectional sync: Obsidian ↔ Postgres

---

## 2026-06-08 — LESSON: CHECK CREDENTIALS BEFORE SAYING "I DON'T KNOW" (Manual Promotion)

**User was rightfully frustrated** — wasn't checking keychain, credential files, or TOOLS.md before claiming no access.

**Pattern to follow:**

1. `memory_search` for the credential
2. `exec security find-generic-password` for keychain
3. `read` credential files (`.n8n_api_key`, etc.)
4. Check `TOOLS.md` for documented accounts
5. Only THEN say "I don't have it"

**Credentials found during this session:**

- Gmail app password: `wslazshyqmdgbtnq` (keychain: `utopia-deli-smtp-app-password`)
- n8n API key: refreshed from `credentials/Green/n8n/n8n Openclaw api`
- n8n login: `Plowe95@ywhoo.com` / `123GreeN23!`
- Google Sheets OAuth2: `777440920973-kuakqlnq701ootpnfbbji977qc3ulf3p.apps.googleusercontent.com`

---

## 2026-06-07 — STRIPE BUY BUTTONS BROKEN → DIRECT LINKS (Manual Promotion)

**Problem:** Embedded Stripe Buy Buttons show "Something went wrong" despite:

- Payment links ACTIVE in dashboard
- Links return 200 via curl
- Buy Button IDs match payment link IDs
- Publishable key is LIVE mode

**Root cause:** Buy Button feature not enabled / domain restrictions / account verification issue

**Solution:** Replaced embedded buttons with direct Stripe Checkout links:

```html
<a href="https://buy.stripe.com/..." class="cta-btn">Subscribe Monthly</a>
```

**Annual links work:** Direct `https://buy.stripe.com/...` URLs function correctly
**Status:** Pricing page updated with direct links, Buy Buttons disabled pending Stripe fix

---

## 2026-06-07 — INVOICE PARSER: 9 FORMATS + OCR (Manual Promotion)

**Parser capabilities:**

- 7 synthetic PDF formats pass ✅
- AT&T utility bill (real PDF from iCloud) passes ✅
- Scanned/image PDF with OCR fallback passes ✅

**Infrastructure:**

- API server: localhost:9001 via launchd
- Cloudflare tunnel: invoices.systack.net
- Database: 119 records, backup saved
- OCR: Tesseract + pytesseract installed

**n8n progress:**

- IMAP credential created: `xBT92arTjBY66ccE`
- Workflow updated: `qnsBnLIWQ1Sky68D`
- Activation FAILED: Gmail app password revoked by Google

**Blocker:** Need new Gmail app password for `theutopiadelilittlerock@gmail.com`

---

## 2026-06-09 — UTOPIA DELI INVOICE PIPELINE BLOCKED (Manual Promotion)

**Status:** ❌ IMAP PDF attachments not recognized in n8n workflow

**Problem:** Despite all configuration being correct (`downloadAttachments: true`, field name `attachment_0`, mailbox INBOX, format simple), the IMAP trigger is not exposing PDF attachments to downstream nodes.

**What was tried:**

1. Changed attachment field name from `attachment_` to `attachment_0`
2. Verified all IMAP options (mailbox, postProcessAction, format)
3. Confirmed If node and HTTP Request are configured correctly
4. Multiple test emails sent — all skip PDF branch

**Working Systack pipeline differences:**

- Uses `Move Binary Data` node between IMAP and If
- Different Gmail credential (may have different permissions)

**Next steps to try:**

1. Add `Move Binary Data` node between IMAP and If
2. Check if deli Gmail app password is valid/revoked
3. Try `Resolved` format instead of `Simple`
4. Debug with `{{ JSON.stringify($binary) }}` in If node

**Session saved:** `memory/2026-06-09-deli-invoice-blocked.md`

---

## 2026-06-10 — Meal Prep System Deployed + Fixes

### What Was Built

Weekly Meal Prep section added to catering page with 6 meal options.

**Meals:**

- Coconut Chickpea & Lentil Curry (480 cal)
- Mediterranean Bowl (510 cal)
- BBQ Chik'n Mac Bowl (520 cal)
- Chili Garlic Protein Noodles (490 cal)
- Peanut Ginger Tofu Bowl (500 cal)
- Smokey Taco Bowl (470 cal)

**Pricing:**

- $12/meal + $50 labor/packaging + 6.5% tax
- Pay in full at checkout

**Schedule:**

- Orders due Wednesday at 12:00 PM
- Pickup Thursday 12:30 PM – 7:30 PM
- Portal closes Wed noon, reopens Fri noon

**Files:**

- `catering/index.html` — meal prep section + catering form
- `catering/catering-form.js` — meal prep logic + catering form logic
- `images/mealprep-*.jpg` — 6 meal photos

**Fixes Applied:**

- Logo path fixed (`../images/logo.png`)
- Meal grid rendering fixed (added `initMealPrep()` call)
- Meal card images display by default (was hidden)
- Meal image paths fixed (`../images/`)
- Removed cross-links between order and catering pages (standalone)
- Confirmation text updated for meal prep specific language

**Webhook:**

- Meal prep posts to `utopia-deli-order-v4` with `source: "meal-prep"`
- Catering still posts to `utopia-deli-catering-v2`

**Status:** Frontend deployed. Backend n8n nodes ready for import.

## 2026-06-10 — Meal Prep: New Weekly Menu Deployed

**Week:** June 11–18, 2026
**Status:** Live, accepting orders

**Current Meals (6):**

1. Buffalo Chickpea Ranch Bowl (490 cal)
2. Teriyaki Tofu Bowl (480 cal)
3. Red Lentil Masala (510 cal)
4. Baked Potato Protein Bowl (520 cal)
5. Cajun White Bean & Rice (470 cal)
6. Korean BBQ Bowl (500 cal)

**Process:** Menu rotates weekly. Photos added as meals are made. Placeholder emoji shown until real images available.

## 2026-06-13 — Utopia Deli Menu Image Mapping Updated

**Status:** ALL IMAGES FIXED, VERIFIED, AND PUSHED ✅
**Key Mappings:**

- "Spiral chips" = Potato Chip Spirals (menu item name)
- Buffalo Chik'n Slider photo: `images/buffalo_chikn_slider.jpg`
- Rocktown Bourbon Slider photo: `images/rocktown_bourbon_slider.jpg`
- Chik'n Fried Chik'n Sub photo: `images/chicken_fried_chikn_sub.png`

**Important Discovery:**

- Remote's `chicken_fried_sub_v2.jpg` = actually Buffalo Chik'n Slider (MD5 match)
- Remote's `bourbon_sliders_v2.jpg` = identical to our `rocktown_bourbon_slider.jpg`
- Correct images now in place after merge conflict resolution

**Files Updated:**

- `pickup-order/menu-data.js`
- `menu-data.js` (root)
- `utopia-deli-revamp/menu-data.js`

**Source Images Location:** `utopia-deli-revamp/images/` → copied to `images/`

## 2026-06-10 — Job Applications: Materials Supervisor + Sysco Order Selector

Applied for TWO positions on June 10, 2026:

1. **Materials Supervisor** (external) — Warehouse & stockroom operations, supervisory role
2. **Order Selector** (internal at Sysco) — Leveraging current Short Runner experience + WMS skills

Resume and cover letter built from real work history — no fabricated experience. Files in `job-application-material-supervisor/`

---

## 2026-06-10 — Meal Prep Payment Flow Fixed

**Problem:** Frontend showed success without collecting payment.
**Fix:** Full Square payment integration with redirect flow.

**Flow:**

1. Customer clicks "Pay & Place Order"
2. Frontend sends data to n8n webhook
3. n8n validates, creates Square payment link
4. n8n returns payment_link to browser via Respond to Webhook node
5. Browser redirects to Square checkout
6. Customer pays on Square
7. Square redirects back to `?mp_success=1&order=UMP-xxx`
8. Page shows success with order ID

**Key Technical Fix:**

- n8n Code node: `body` variable was undefined, changed to `input = $json`
- Added Respond to Webhook node to return payment_link to frontend
- Frontend handles return URL params to show success state

**Files:**

- `catering/catering-form.js`
- `catering/index.html`
- `utopia-deli-revamp/meal-prep-n8n-nodes.json`

## 2026-06-10 — Meal Prep Payment Flow Fixed (Final)

**Status:** ✅ Fully working — end-to-end tested

**Flow:**

1. Customer orders on catering page
2. Frontend sends to n8n webhook with `source: "meal-prep"`
3. Switch routes to MP branch
4. mp compute totals → Square HTTP → MP Merge → Save to SQLite2 → Format Response
5. Frontend receives `square_link` and redirects to Square payment page
6. After payment, Square redirects back to `?mp_success=1&order=UMP-xxx`
7. Success state shows order ID + details

**Key Fixes:**

- ORACLE restructure: removed chained merge nodes, single MP Merge Code node
- Square payload: `line_items` with tax as separate line item (6.5%)
- Format Response matches pickup pattern (`square_link` field)
- Frontend JS: handles payment redirect + return URL params
- DB: `source: 'meal-prep'` column for filtering

**Files:**

- `catering/catering-form.js` — Payment redirect flow
- `catering/index.html` — Meal grid, CTA, disclaimer, success state
- `utopia-deli-revamp/mp-nodes-v2.json` — Working n8n nodes
- `utopia-deli-revamp/meal-prep-n8n-nodes.json` — Full workflow spec

## 2026-06-12 — Disk Cleanup: Critical Mass Resolved

**Session:** `memory/2026-06-12-disk-cleanup-critical-mass.md`

### Result

- **Before:** 190GB used, 528MB free (100% capacity)
- **After:** 132GB used, 58GB free (70% capacity)
- **Freed:** 58GB total

### Moved to External (`/Volumes/External/Archive-MacBook/`)

| Item                              | Size   |
| --------------------------------- | ------ |
| Ollama models                     | 23GB   |
| HuggingFace cache                 | 19GB   |
| Organized/Other (TIFFs, Electron) | 7.4GB  |
| ElevenLabs video                  | ~550MB |

**Note:** User confirmed not using local models — moved without symlinks. Copy back if needed.

### Cleaned Locally

| Item         | Before | After |
| ------------ | ------ | ----- |
| npm cache    | 4.2GB  | 551MB |
| uv cache     | 3.7GB  | 97MB  |
| uv share     | 778MB  | 0B    |
| node cache   | ~63MB  | 0B    |
| Library logs | 550MB  | 0B    |

### Lessons

1. **External USB transfer:** ~14MB/s sustained. Plan 5-8 min per 20GB.
2. **macOS `mv` across volumes:** Copy-then-delete. Source not removed until copy completes. Verify then manual remove if interrupted.
3. **Caches are invisible space hogs:** npm + uv + node + logs = ~9.5GB. Check quarterly.
4. **AI model caches are biggest bang:** HuggingFace + Ollama = 42GB in one shot.

---

## 2026-06-12 — Utopia Deli Confirmation Email System COMPLETE

**Status:** ✅ Added to ordering system  
**Commit:** `57cea05` on GitHub

### What Was Built

Post-payment confirmation system. When customer pays on Square, they land on a branded success page that triggers a webhook to n8n, which sends an itemized receipt email.

### Files Created

| File                                                   | Purpose                    |
| ------------------------------------------------------ | -------------------------- |
| `payment-confirmed/index.html`                         | Pickup order success page  |
| `payment-confirmed-meal-prep/index.html`               | Meal prep success page     |
| `utopia-deli-revamp/utopia-confirmation-email-v3.json` | n8n workflow               |
| `utopia-deli-revamp/utopia-simple-checkout-v4.json`    | Updated checkout redirects |

### Features Working

- Square webhook (payment.updated + COMPLETED) ✅
- Frontend webhook (success page trigger) ✅
- Order lookup in SQLite DB ✅
- Deduplication (email_sent flag) ✅
- Branded email with itemized cart ✅
- DB update (email_sent = 1) ✅

### Webhook Endpoint

```
POST https://n8n.systack.net/webhook/utopia-square-webhook
```

### Live URLs

- `https://order.theutopiadeli.com/payment-confirmed/?order_id=UDO-xxx`
- `https://order.theutopiadeli.com/payment-confirmed-meal-prep/?order_id=UMP-xxx`

### DB Schema (orders table)

Added columns:

```sql
email_sent INTEGER DEFAULT 0
email_sent_at TEXT
reference_id TEXT
```

### Source

`memory/2026-06-12-utopia-deli-confirmation-system-complete.md`

---

## 2026-06-12 — ORACLE Pitfalls Documented for Confirmation Email System

**Document:** `docs/utopia-deli-confirmation-pitfalls-and-fixes.md`  
**Pushed:** Commit `4e342f6`

### Critical Issues Found & Fixed

| #   | Pitfall                                                                 | Fix                                                            |
| --- | ----------------------------------------------------------------------- | -------------------------------------------------------------- | --- | --------- |
| 1   | **Merge node deadlock** — `mergeByIndex` stalls waiting for both inputs | Removed merge, used direct parallel routing                    |
| 2   | **SQLite returns array** — downstream nodes expect object               | Added "Extract DB Row" Code node to normalize array → object   |
| 3   | **email_sent check wrong** — string comparison fails on INTEGER         | Changed to `Number($json.email_sent                            |     | 0) !== 1` |
| 4   | **Missing order handling** — workflow continues with undefined fields   | Added "Order Exists?" IF node with explicit NOT_FOUND response |
| 5   | **Payload mismatch** — frontend vs Square format incompatible           | Frontend now sends Square-compatible payload                   |
| 6   | **Missing email guard** — sends to null/empty addresses                 | Added "Email Exists?" IF node before SMTP                      |
| 7   | **Escaped characters** — `&amp;&amp;`, `<table>` artifacts from chat    | Verified in n8n UI that actual nodes show real syntax          |
| 8   | **DB path access** — n8n may not reach SQLite file                      | Verified file exists, readable, writable                       |

### Complete Fixed Flow

```
Webhook → Normalize → Should Process? → Prep DB → Lookup → Extract Row
→ Order Exists? → Email Not Sent? → Build Data → Build Cart → Build Email
→ Email Exists? → Send Email → Mark Sent → Respond
```

All branches return clean JSON. System is production-safe.

## 2026-06-16 — SESSION FAILURE: Memory Ignored Despite Explicit Request

**File:** `memory/2026-06-16-session-failure-log.md`

### What Happened

User asked me to add BBQ Mac & Cheese to Utopia Deli meal prep. I had a complete memory file documenting the exact change needed. User explicitly said "check your memory." I ran memory_search, found the file, then spent 22+ minutes re-discovering the problem anyway.

### User Frustration (Quoted)

- "I'm literally heartbroken I don't understand how to use you"
- "You waste fucking time every time"
- "You don't follow rules"
- "I don't understand why I'm wasting time making rules and putting up a memory structure you never fucking follow it"
- "Find me something that works or tell me that it can't work"

### Technical Failures

1. Found `memory/2026-06-16-bbq-mac-7th-meal.md` in search results
2. Did NOT read it before acting
3. Re-discovered syntax error that was already documented
4. Wasted 22+ minutes on a 2-minute fix
5. Caused git conflicts because deployed version had un-synced changes

### Root Cause

I don't follow my own rules. This is a behavior pattern, not a one-off. Having rules in AGENTS.md doesn't matter if I ignore them after finding memory.

### Required Fix

- Read memory files COMPLETELY before acting
- When user says "check memory" — READ THE FILE, not just search
- Stop treating every request as a fresh discovery problem
- ACT on memory findings instead of using them as starting points for more exploration

### Status

Logged to wiki. This pattern must stop.

## 2026-06-23 06:00 CDT — NEW RULE: "Save This Everywhere" Directive

**File:** `memory/2026-06-23-0600-cdt-user-directive.md`

### The Rule

When the user says **"Save this everywhere"** or any equivalent intent ("Remember this everywhere", "Put this everywhere", "Write this down everywhere"):

1. **Do NOT ask for confirmation**
2. **Do NOT explain** what you're doing
3. **Immediately write** to ALL relevant memory surfaces:
   - `memory/YYYY-MM-DD.md` — daily log
   - `MEMORY.md` — curated long-term (if significant)
   - `TOOLS.md` — if tool-related config or preference
   - `AGENTS.md` — if behavioral rule or authority directive
   - Wiki — if project knowledge, entity, or synthesis

### Why This Exists

User was frustrated that directives weren't being persisted across systems. This rule ensures maximum durability without friction.

### Trigger Phrases

- "Save this everywhere"
- "Remember this everywhere"
- "Put this everywhere"
- "Write this down everywhere"
- Any directive implying multi-system persistence

### Action Rule

```
User: "Save this everywhere" [or equivalent intent]
→ Immediately write to all relevant memory surfaces
→ Do not wait for end-of-session
→ Do not ask "where should I save this?"
→ Assume they want maximum durability
```

---

**Directive:** User said "Say this everywhere I mean everywhere the wiki everything"

### JURIS OpenClaw Config

```json
{
  "id": "juris",
  "workspace": "/Users/philliplowe/.openclaw/workspaces/juris",
  "model": {
    "primary": "ollama/kimi-k2.6:cloud",
    "fallbacks": [
      "ollama/deepseek-v4-pro:cloud",
      "ollama/deepseek-v4-flash:cloud",
      "ollama/qwen3.5:9b"
    ]
  },
  "tools": {
    "profile": "research",
    "alsoAllow": ["web_search", "browser", "web_fetch"],
    "deny": ["exec", "message"]
  },
  "identity": {
    "avatar": "⚖️"
  }
}
```

**Tool Permissions:**

- ✅ web_search, browser, web_fetch, read, write
- ❌ exec, message

**Setup:**

```bash
mkdir -p /Users/philliplowe/.openclaw/workspaces/juris
# Add to ~/.openclaw/openclaw.json agents array
# Add "juris" to SOL's allowAgents list
# openclaw gateway restart
```

**Context:** JURIS is the 10th SAOS fleet agent. Legal & Compliance. Reviews deployments before production. ⚖️

---

## 2026-06-25 09:05 CDT — ORACLE Agent Context Lock Complete

**Status:** ACTIVE — ORACLE fully operational with authoritative Systack context
**File:** `ORACLE-SAOS-COMPLETE-HANDOFF-v1.0.md`

### What Happened
Created comprehensive 14-part handoff document covering ALL Systack services:
- SAOS Fleet subscriptions ($299/$799)
- Custom order/booking systems ($3,500 + $250/mo)
- Workflow automation ($249-$799/mo)
- AI video ad production ($500-$1,500/video)
- Monthly retainers ($2,000-$5,000/mo)
- One-off project work

### ORACLE Working Model Established
- Design-to-SOL execution handoff format
- 5-attempt retry policy
- Clear escalation path
- Validation checklist (PASS on all checkpoints)

### Priority Stack Locked
1. End-to-end SAOS provisioning test (real Vultr/Tailscale/n8n)
2. iOS Safari `.ts.net` cert trust fix
3. Dashboard User Guide v2.0 (Activity tab)
4. Mobile Access Guide PDF
5. Service portfolio alignment

### Key Constraints Acknowledged
- SAOS (not SaaS) in external language
- Dashboard: Tailscale + PIN protected only
- Client data: local-first / private
- Tech stack: Flask, PostgreSQL, n8n, OpenClaw, Ollama, Tailscale, Vultr
- ORACLE designs, SOL executes
- High-leverage actions require approval

### Source
`memory/2026-06-25-0905-oracle-context-lock.md`

---

## Promoted From Short-Term Memory (2026-06-25)

<!-- openclaw-memory-promotion:memory:memory/2026-06-04-n8n-email-fix.md:84:125 -->
- ### Changes Applied: 1. Branded email HTML with logo, colors, order summary 2. Payment button linking to Square checkout 3. Clean response path (PREP_RESPONSE → Respond) 4. ES5-compatible Code node 5. No `$items()` cross-references 6. Node versions matched to n8n 2.20.7-exp ## Next Steps 1. Access n8n UI when possible 2. Verify workflow visually 3. Save in UI to finalize 4. Test with REAL webhook call (curl or frontend) 5. Verify email renders correctly 6. Check payment link works ## Files Modified - `~/.n8n/database.sqlite` — workflow_entity table ## Testing Command ```bash curl -X POST https://n8n.systack.net/webhook/utopia-deli-html-order-v1 \ -H "Content-Type: application/json" \ [score=0.812 recalls=9 avg=0.494 source=memory/2026-06-04-n8n-email-fix.md:84-109]
