# Utopia Deli Confirmation Email — Pitfalls & Fixes

**Document:** Critical issues found by ORACLE and their solutions  
**Date:** 2026-06-12  
**Status:** All fixed and deployed

---

## ⚠️ PITFALL 1: Merge Node Deadlock

### Problem
Used `mergeByIndex` node expecting both inputs simultaneously.

```
Frontend Webhook ───┐
                    ├─→ Merge (mergeByIndex) → STALLS ❌
Square Webhook ─────┘
```

**Result:** Only one trigger fires → workflow never completes.

### ORACLE Fix
**REMOVE Merge node.** Use direct parallel routing:

```
Frontend Webhook → Normalize Frontend ───┐
                                         ├─→ Route Trigger → Continue
Square Webhook → Normalize Square ───────┘
```

**Why this works:** Both triggers independently flow into same downstream node. No waiting.

---

## ⚠️ PITFALL 2: SQLite Returns Array, Not Object

### Problem
SQLite node returns array of rows:
```json
[{"order_id": "...", "email_sent": 0}]
```

But downstream nodes expect object:
```json
{"order_id": "...", "email_sent": 0}
```

**Result:** `IF` nodes break, `email_sent` check fails.

### ORACLE Fix
**Add "Extract DB Row" Code node after SQLite lookup:**

```javascript
const rows = $json;

if (!rows || rows.length === 0) {
  return [{ json: { error: "NOT_FOUND" } }];
}

return [{ json: rows[0] }];  // Extract first row
```

**Why this works:** Normalizes array → object before IF nodes.

---

## ⚠️ PITFALL 3: email_sent Check Was Wrong

### Problem
Original IF condition:
```javascript
// WRONG — compares string "true" to string "true"
$json.email_sent !== "true"
```

But SQLite returns INTEGER `0` or `1`, not string `"true"`.

**Result:** Emails resent incorrectly (deduplication fails).

### ORACLE Fix
**Use Number() comparison:**

```javascript
Number($json.email_sent || 0) !== 1
```

| email_sent Value | Result |
|-----------------|--------|
| 0 (default) | ✅ Send email |
| 1 (already sent) | ✅ Skip (deduplicated) |
| null/undefined | ✅ Send email (Number(null) = 0) |

**Why this works:** Forces integer comparison, handles all SQLite return types.

---

## ⚠️ PITFALL 4: Missing Order Handling

### Problem
If DB returns no rows, workflow continued with undefined fields.

**Result:** Cascading errors downstream (email to undefined, etc.)

### ORACLE Fix
**Add "Order Exists?" IF node before email check:**

```javascript
// Condition: check if error === "NOT_FOUND"
$json.error === "NOT_FOUND"
```

**TRUE branch:** → Not Found Response → Respond  
**FALSE branch:** → Continue to Email Not Sent check

**Why this works:** Explicitly handles missing orders with clean JSON response.

---

## ⚠️ PITFALL 5: Frontend vs Square Payload Mismatch

### Problem
Frontend sends simple payload:
```json
{"order_id": "UDO-xxx", "source": "pickup-order"}
```

But workflow expects Square format:
```json
{"type": "payment.updated", "data": {"object": {"payment": {...}}}}
```

**Result:** 404 or "Missing order_id" errors.

### ORACLE Fix
**Frontend sends Square-compatible payload:**

```javascript
var payload = {
  type: "payment.updated",
  data: {
    object: {
      payment: {
        id: "frontend_" + orderId,
        status: "COMPLETED",
        reference_id: orderId
      }
    }
  }
};
```

**Why this works:** Single webhook handler processes both Square and frontend triggers.

---

## ⚠️ PITFALL 6: Missing Email Guard

### Problem
If customer_email is null/empty, email node tries to send anyway.

**Result:** SMTP error or email to empty address.

### ORACLE Fix
**Add "Email Exists?" IF node before sending:**

```javascript
// Condition: email is not empty
$json.email !== "" && $json.email !== null && $json.email !== undefined
```

**TRUE branch:** → Send Email → Mark Sent → Respond  
**FALSE branch:** → No Email Response → Respond

**Why this works:** Prevents sending to invalid/empty addresses.

---

## ⚠️ PITFALL 7: Escaped Characters in JSON

### Problem
When copying workflow JSON to chat, special characters get escaped:
```javascript
// WRONG (chat artifact)
&amp;&amp;
<table>
=&gt;
```

**Result:** Syntax errors if pasted directly into n8n.

### ORACLE Fix
**Verify in n8n UI that actual nodes show:**
```javascript
// CORRECT (in n8n)
&&
<table>
=>
```

**Why this works:** JSON escapes are decoded on import. Visual verification confirms.

---

## ⚠️ PITFALL 8: DB Path Access

### Problem
SQLite database path may not be accessible from n8n runtime.

**Path:** `/Users/philliplowe/.openclaw/workspaces/sol/utopia-deli-revamp/orders.db`

### ORACLE Fix
**Verified:**
- File exists ✅
- Readable/writable ✅
- 26 rows ✅

**Fallback if path fails:** Update SQLite node credential to correct path.

---

## 📋 Complete Fixed Flow

```
Webhook (Square or Frontend)
→ Normalize (parses payment.updated + COMPLETED)
→ Should Process? (IF $json.process === true)
  YES:
    → Prep DB Lookup
    → Lookup Order in DB (SQLite)
    → Extract DB Row (array → object)
    → Order Exists? (IF error !== "NOT_FOUND")
      YES:
        → Email Not Sent? (IF Number(email_sent) !== 1)
          YES:
            → Build Order Data (parse cart_json)
            → Build Cart HTML (table)
            → Build Branded Email (Utopia template)
            → Email Exists? (IF email !== "")
              YES:
                → Send Email (Gmail SMTP)
                → Mark Email Sent (UPDATE email_sent = 1)
                → Build Success Response
                → Respond ✅
              NO:
                → No Email Response → Respond ⚠️
          NO:
            → Already Sent Response → Respond ✅
      NO:
        → Not Found Response → Respond ❌
  NO:
    → Skipped Response → Respond ℹ️
```

---

## ✅ Validation Checklist

Before deploying, verify:

- [ ] Webhook path is active (not 404)
- [ ] SQLite DB path is accessible
- [ ] `email_sent` column exists (INTEGER DEFAULT 0)
- [ ] `email_sent_at` column exists
- [ ] `reference_id` column exists
- [ ] Test order exists with email_sent = 0
- [ ] SMTP credential is configured
- [ ] Response node returns valid JSON

---

## 📚 Source

- ORACLE handout: `memory/2026-06-12-oracle-confirmation-email-handout.md`
- Test results: `memory/2026-06-12-utopia-deli-test-results-final.md`
- Full docs: `docs/utopia-deli-confirmation-email-v3.md`

---

**All pitfalls fixed.** System is production-safe.
