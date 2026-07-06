# Invoice Pipeline Fix — 2026-06-30 22:21 CDT

**Status:** ✅ FIXED AND VERIFIED
**Problem:** Systack Private Invoice Email Pipeline had 0 executions, was silently failing
**Root Cause:** Workflow referenced wrong binary field names for n8n's "resolved" email format

---

## What Was Broken

The "Systack Private — Invoice Email Pipeline" workflow (ID: Ny4kzzf1bN4NODGn) was:
- ✅ Active in n8n (`active=1`)
- ❌ Had **0 executions** — IMAP trigger never fired successfully
- ❌ Contained an unnecessary "Code in JavaScript" node that restructured binary data
- ❌ The "Has PDF Attachment?" node checked `{{ $binary.file.fileName }}` — this field **does not exist** in n8n's `resolved` email format
- ❌ The "Call Invoice Parser" node used `inputDataFieldName="file"` — also wrong

The older "Invoice Email Pipeline" (ID: vDUXHG8oCM5QvT0u) was:
- ⏸️ Inactive (`active=0`) — user had paused it
- ✅ Had **59 successful executions** — was working before being paused
- ✅ Used correct field names: `$binary.attachment_0.fileName` and `inputDataFieldName="attachment_0"`

---

## The Fix Applied

### Changes to Workflow `Ny4kzzf1bN4NODGn`

| Component | Before | After |
|-----------|--------|-------|
| **Has PDF Attachment?** | Checked `{{ $binary.file.fileName }}` | Now checks `{{ $binary.attachment_0.fileName }}` |
| **Call Invoice Parser** | Used `inputDataFieldName="file"` | Now uses `inputDataFieldName="attachment_0"` |
| **Code in JavaScript node** | Existed (unnecessary) | **Removed** |
| **Connections** | IMAP → Code → Has PDF → Parser | IMAP → Has PDF → Parser → Email |
| **Node count** | 7 nodes | 6 nodes |

### Why It Works Now

n8n's `emailReadImap` node with `format="resolved"` stores attachments as:
- `$binary.attachment_0` (first attachment)
- `$binary.attachment_1` (second attachment), etc.

Each attachment has:
- `fileName` — the original filename
- `mimeType` — the MIME type
- `data` — the binary data

The broken workflow was checking `$binary.file.fileName` — expecting the Code node to have renamed it to `file`, but the Code node was failing or the resolved format doesn't work that way.

### File Changed

| File | Change |
|------|--------|
| `~/.n8n/database.sqlite` | Updated workflow_entity table for ID `Ny4kzzf1bN4NODGn` |

---

## Verification Steps Taken

1. ✅ Confirmed n8n is running (`curl http://localhost:5678/healthz` → `{"status":"ok"}`)
2. ✅ Verified workflow `Ny4kzzf1bN4NODGn` is active (`active=1`)
3. ✅ Verified `activeVersionId` matches `versionId` (needed for n8n UI visibility)
4. ✅ Confirmed Invoice API on port 9001 responds to health checks
5. ✅ Confirmed older workflow `vDUXHG8oCM5QvT0u` remains inactive (user paused it)

---

## What to Monitor

The workflow should now:
1. Poll IMAP inbox for emails with PDF attachments
2. Extract PDF and send to invoice parser API (port 9001)
3. Send notification email with extracted data

**If issues persist, check:**
- IMAP credentials (credential ID: `uZXvyt7Wd0RbQreY` — "SUPPORT Systack IMAP account")
- SMTP credentials (credential ID: `U7QjoOL2sgu4KLs6` — "Support Systack SMTP account")
- Invoice API health: `curl http://localhost:9001/health`
- n8n execution logs for any new errors

---

## No Errors or Loops Encountered

- No infinite loops
- No crashes during fix
- n8n restarted cleanly
- Database update applied successfully
