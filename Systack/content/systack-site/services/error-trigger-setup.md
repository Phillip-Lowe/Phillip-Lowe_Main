# n8n Error Trigger — Safety Net Setup

**Created:** 2026-05-16
**Priority:** CRITICAL — P0

## What This Does

Every n8n workflow should have an Error Trigger attached. When any node fails during execution, instead of the error vanishing silently into n8n's internal log, it gets routed to a notification channel where a human (or SOL) can see the actual error message — not an AI's hallucinated interpretation of it.

## Current State (2026-05-16)

16 active workflows in n8n. **Zero have Error Triggers configured.** Any failure in production is invisible.

---

## Setup: Add Error Trigger to Every Production Workflow

### Step 1: Create the Error Notification Workflow

In n8n, create ONE dedicated workflow called **"Error Catcher — Master"** with:
- **Error Trigger** node (catches errors from all workflows)
- **Send notification** node (Telegram/Slack/Email) with `{{ $json }}` payload
- Optional: **Write to log file** node for audit trail

### Step 2: For Each Existing Workflow

1. Open the workflow in n8n UI
2. Click **"Settings"** tab → **"Error Workflow"**
3. Select **"Error Catcher — Master"** from the dropdown
4. Save

### Alternative: In-Workflow Error Trigger

If you prefer per-workflow error handling, add an **Error Trigger** node directly to each workflow and chain it to a notification node.

### What the Error Payload Contains

The error payload automatically includes:
- `name` — Node that failed
- `message` — Actual error message
- `time` — When it occurred
- `workflow name` — Which workflow broke
- `execution id` — For debugging

This is the **real, raw error** — not an AI's guess. This is what the research document insisted on.

---

## Minimum Viable Setup

For a quick fix: pick the 5 most critical production workflows and add them to the Error Catcher. These are:

1. **Utopia Deli — Full Checkout** (revenue-critical)
2. **Utopia Deli — HTML Webhook Checkout v2** (currently broken — will fire immediately)
3. **Utopia Deli — HTML Checkout v3** (active alternative)
4. **Systack Lead Scraper — SQLite CRM** (lead gen pipeline)
5. **Green Systems — Outreach Sequencer** (client outreach)

---

## Testing

1. Intentionally break a node (wrong variable reference)
2. Run the workflow
3. Verify the error notification arrives
4. Check that the error message is the actual n8n error, not a rewritten version

---

## ⚠️ Critical Note

**Do NOT route errors through OpenClaw/SOL for interpretation.** The whole point is to bypass the AI's tendency to hallucinate error causes. Route errors directly to the human (Telegram/Slack/Email) with the raw n8n error payload.
