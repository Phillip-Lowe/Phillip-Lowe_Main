# Bidirectional Invoice Training Dataset

**Date:** 2026-06-07
**Source:** ORACLE (M365 Copilot)
**Purpose:** AR/AP classification training + pipeline validation

## Business Identity Pool

```javascript
const businessNames = [
  "Green Systems LLC",
  "MOD 1 Apparel", 
  "The Utopia Deli"
];
```

---

## Accounts Receivable (INBOUND — You Sent Invoice)

### AR-1: B2B Invoice — Clean

```
INVOICE

Invoice #: GS-1001
Date: 06/01/2026
Due: 06/15/2026

FROM:
Green Systems LLC
Little Rock, AR

BILL TO:
Delta Retail Group
Memphis, TN

--------------------------------

Custom POS System Build
Qty: 1
Unit Price: $4,500.00

--------------------------------
Subtotal: $4,500.00
Tax (8.5%): $382.50
TOTAL: $4,882.50
```

**Direction:** INBOUND (Green Systems LLC = issuer)
**Ledger:** AR → Debit: Accounts Receivable, Credit: Revenue

---

### AR-2: Wholesale / Product Invoice

```
Invoice #: MOD-884
Seller: MOD 1 Apparel
Buyer: Urban Streetwear Co.

Items:
50 Hoodies @ $28.00 = $1,400.00
30 Joggers @ $22.00 = $660.00

Subtotal: $2,060.00
Shipping: $120.00
TOTAL: $2,180.00
Terms: Net 30
```

**Direction:** INBOUND (MOD 1 Apparel = issuer)
**Ledger:** AR → Debit: Accounts Receivable, Credit: Revenue

---

### AR-3: Subscription Billing — Unpaid

```
NovaCloud Systems

Invoice ID: SUB-77821
Customer: BrightScale Inc.

Enterprise Plan: $499
API Usage: $120

Total Due: $619.00
Status: UNPAID
Due Date: 06/10/2026
```

**Direction:** INBOUND (NovaCloud = issuer, but wait — this needs review)
**Note:** If NovaCloud is NOT in businessNames, this would be OUTBOUND (we're the customer)
**Correction:** If customer is BrightScale and we're Green Systems, this is OUTBOUND for us

---

## Accounts Payable (OUTBOUND — You Received Invoice)

### AP-1: Vendor Supply Invoice

```
Invoice No: SUP-3321

FROM:
Arkansas Food Supply Co.

TO:
The Utopia Deli

Ingredients Bulk Order:
Produce: $320.00
Dry Goods: $180.00

Subtotal: $500.00
Tax: $45.00
TOTAL: $545.00
```

**Direction:** OUTBOUND (The Utopia Deli = receiver)
**Ledger:** AP → Debit: COGS, Credit: Accounts Payable

---

### AP-2: SaaS Paid Invoice

```
Stripe Billing

Invoice #: STR-99281
Customer: Green Systems LLC

Processing Fees: $82.55
Platform Fee: $15.00

TOTAL: $97.55
Status: PAID
```

**Direction:** OUTBOUND (Green Systems LLC = receiver)
**Ledger:** AP → Debit: Expense, Credit: Accounts Payable
**Status:** PAID (already paid, no action needed)

---

### AP-3: Contractor

```
Invoice 8891

Mike Repairs
to Green Systems LLC

Labor: $300
Parts: $120

Total = 420.00
Due in 7 days
```

**Direction:** OUTBOUND (Green Systems LLC = receiver)
**Ledger:** AP → Debit: Expense, Credit: Accounts Payable

---

## Ground Truth Labels

### AR-1 Labeled

```json
{
  "invoice_id": "GS-1001",
  "direction": "INBOUND",
  "entity_issuer": {"name": "Green Systems LLC"},
  "entity_receiver": {"name": "Delta Retail Group"},
  "financials": {
    "subtotal": 4500.00,
    "tax": 382.50,
    "total": 4882.50,
    "currency": "USD"
  },
  "payment": {
    "status": "UNPAID",
    "due_date": "2026-06-15"
  },
  "classification": {
    "type": "AR",
    "account": "Revenue"
  }
}
```

### AP-1 Labeled

```json
{
  "invoice_id": "SUP-3321",
  "direction": "OUTBOUND",
  "entity_issuer": {"name": "Arkansas Food Supply Co."},
  "entity_receiver": {"name": "The Utopia Deli"},
  "financials": {
    "subtotal": 500.00,
    "tax": 45.00,
    "total": 545.00
  },
  "payment": {
    "status": "UNPAID"
  },
  "classification": {
    "type": "AP",
    "account": "COGS"
  }
}
```

---

## Database Schema

### Tables

```sql
-- Raw extracted invoices
CREATE TABLE invoices_raw (
  id INTEGER PRIMARY KEY,
  raw_text TEXT,
  extracted_at TIMESTAMP,
  source TEXT
);

-- Normalized invoices
CREATE TABLE invoices_normalized (
  id INTEGER PRIMARY KEY,
  invoice_id TEXT,
  direction TEXT, -- INBOUND | OUTBOUND | UNKNOWN
  invoice_number TEXT,
  invoice_date TEXT,
  due_date TEXT,
  entity_issuer_name TEXT,
  entity_receiver_name TEXT,
  subtotal REAL,
  tax REAL,
  discount REAL,
  total REAL,
  currency TEXT DEFAULT 'USD',
  payment_status TEXT,
  payment_method TEXT,
  payment_terms TEXT,
  confidence_score REAL,
  raw_text_id INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts Receivable
CREATE TABLE accounts_receivable (
  id INTEGER PRIMARY KEY,
  invoice_id TEXT,
  customer_name TEXT,
  amount_due REAL,
  amount_paid REAL DEFAULT 0,
  status TEXT, -- UNPAID | PARTIAL | PAID | OVERDUE
  due_date TEXT,
  ledger_debit TEXT,
  ledger_credit TEXT,
  journal_entry TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts Payable
CREATE TABLE accounts_payable (
  id INTEGER PRIMARY KEY,
  invoice_id TEXT,
  vendor_name TEXT,
  amount_due REAL,
  amount_paid REAL DEFAULT 0,
  status TEXT, -- UNPAID | PARTIAL | PAID | OVERDUE
  due_date TEXT,
  ledger_debit TEXT,
  ledger_credit TEXT,
  journal_entry TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Review Queue (direction UNKNOWN or validation failed)
CREATE TABLE review_queue (
  id INTEGER PRIMARY KEY,
  invoice_id TEXT,
  reason TEXT,
  raw_data TEXT,
  assigned_to TEXT,
  status TEXT DEFAULT 'PENDING',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## SOL Execution Pipeline

```
INPUT (Email/API/Upload)
  → EXTRACT (OCR/parser)
  → NORMALIZE (map to schema)
  → RESOLVE DIRECTION (compare to business names)
  → MAP LEDGER (AR vs AP)
  → VALIDATE (rules check)
  → ROUTE (AR table | AP table | Review Queue)
```

### Validation Rules

```plaintext
✔ total exists and > 0
✔ direction != UNKNOWN
✔ issuer + receiver exist
✔ subtotal + tax ≈ total (±1% tolerance)
✔ confidence_score >= 0.5
```

### Routing Logic

```javascript
if (direction === "INBOUND") {
  store_in(accounts_receivable);
} else if (direction === "OUTBOUND") {
  store_in(accounts_payable);
} else {
  store_in(review_queue);
  alert("Invoice requires manual review");
}
```

---

## Files

- `invoice_parser_production.py` — OCR + text extraction
- `invoice_normalizer.py` — schema normalization + direction resolution
- `invoice_db.py` — database layer
- `invoice_api.py` — HTTP API endpoint

## Next Steps

1. Create the AR/AP/review_queue tables in SQLite
2. Update n8n email workflow to use normalizer
3. Build validation layer
4. Add review queue dashboard
