# ORACLE Design: Bidirectional Invoice System

**Date:** 2026-06-07
**Source:** ORACLE (M365 Copilot consultation)
**Status:** Design complete, implementation pending

## Goal

Convert any invoice into a single canonical object that dynamically behaves as:
- **RECEIVABLE** (customer owes you — money coming IN)
- **PAYABLE** (you owe vendor — money going OUT)

## Core Concept

Every invoice becomes a **Ledger-Ready Financial Object (LRFO)** with a required field:

```plaintext
direction: INBOUND | OUTBOUND
```

## Canonical Invoice Parcel Schema

```json
{
  "invoice_id": "string",
  "invoice_number": "string",
  "invoice_date": "YYYY-MM-DD",
  "due_date": "YYYY-MM-DD",
  "direction": "INBOUND | OUTBOUND",
  "entity_issuer": {
    "name": "string",
    "address": "string",
    "email": "string",
    "tax_id": "string"
  },
  "entity_receiver": {
    "name": "string",
    "address": "string",
    "email": "string"
  },
  "line_items": [
    {
      "description": "string",
      "quantity": "number",
      "unit_price": "number",
      "total": "number"
    }
  ],
  "financials": {
    "subtotal": "number",
    "tax": "number",
    "discount": "number",
    "total": "number",
    "currency": "USD"
  },
  "payment": {
    "status": "PAID | UNPAID | PARTIAL",
    "method": "string",
    "terms": "string"
  },
  "metadata": {
    "source_type": "OCR | PDF | EMAIL | API",
    "confidence_score": "0-1",
    "raw_text": "string"
  }
}
```

## Direction Resolution Engine

SOL must determine: Is this invoice money coming in, or going out?

### Rule Engine

```plaintext
IF business_name == entity_issuer.name
  → direction = INBOUND (Receivable)
IF business_name == entity_receiver.name
  → direction = OUTBOUND (Payable)
ELSE
  → direction = UNKNOWN (flag for review)
```

### Examples

| Scenario | FROM | TO | Direction |
|----------|------|-----|-----------|
| You sent invoice to customer | Your Company | Client | INBOUND (AR) |
| Vendor invoiced you | Vendor | Your Company | OUTBOUND (AP) |

## Dual Ledger Transformation

### Receivable Mode (INBOUND)
```json
{
  "type": "AR",
  "customer": "entity_receiver.name",
  "amount_due": 5078.72,
  "status": "UNPAID",
  "due_date": "2026-06-20",
  "journal_entry": {
    "debit": "Accounts Receivable",
    "credit": "Revenue"
  }
}
```

### Payable Mode (OUTBOUND)
```json
{
  "type": "AP",
  "vendor": "entity_issuer.name",
  "amount_due": 2587.70,
  "status": "UNPAID",
  "due_date": "2026-06-30",
  "journal_entry": {
    "debit": "Expense / COGS",
    "credit": "Accounts Payable"
  }
}
```

## SOL Execution Pipeline

1. **Extract Invoice** → OCR / parser → Raw structured data
2. **Normalize Schema** → Map extracted fields → canonical schema
3. **Inject Business Identity** → `SET business_name = "Green Systems LLC"`
4. **Direction Resolver** (Code Node) → Compare issuer/receiver to business name
5. **Ledger Mapper** (Switch Node) → AR mapping vs AP mapping
6. **Store** → Google Sheets / SQL (separate AR and AP tables)
7. **Validation** (VALI/PESSI) → Check totals, direction, currency, required fields

## Retry Policy (5 Attempts)

1. Re-run extraction with adjusted OCR threshold
2. Re-map missing fields
3. Fallback heuristics (email domain match)
4. Manual flag if confidence < 0.7
5. Escalate to review queue

## Escalation Path

```plaintext
UNKNOWN direction
Missing totals
Conflicting issuer/receiver
→ Route to REVIEW QUEUE
```

## Design Invariants

- No direction = **FAIL**
- Totals must reconcile
- Schema must always be complete
- No silent assumptions
- Confidence < threshold → flag

## System Advantage

- ✅ One pipeline for **all invoices**
- ✅ Automatic AR/AP classification
- ✅ Ledger-ready data
- ✅ Scalable accounting integration
- ✅ Works across industries + messy inputs
