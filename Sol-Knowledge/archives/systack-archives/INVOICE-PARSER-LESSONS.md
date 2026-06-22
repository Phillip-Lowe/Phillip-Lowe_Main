# Invoice Parser — Lessons From Making It Bulletproof (2026-06-07)

## Result: 7/7 Test Formats Now Passing

---

## Lesson 1: Format Detection Order Matters — Most Specific First

**Problem:** The `FROM:/BILL TO:` check was too greedy. It caught EVERY invoice with both fields,
including contractor invoices and table-format invoices.

**Fix pattern:**
```python
# ❌ Wrong: greedy pattern first
if 'FROM:' in text and 'BILL TO:' in text:
    return parse_from_bill_format()  # catches everything!

# ✅ Right: specific patterns before general ones
if has_work_completed or has_dotted_items:
    return parse_contractor_format()  # specific first
if has_from_bill and has_items_section:
    return parse_from_bill_format()   # then general
# Fall through to standard parser
```

**Rule:** Always check for the MOST distinctive pattern first. "work completed" with dotted items
is more specific than "FROM:/BILL TO:".

---

## Lesson 2: Vendor On Next Line (Multi-line Fields)

**Problem:** `From:\nABC Restaurant Supply Co.` — vendor on next line, not same line.

**Fix:** When vendor prefix matches but value is empty after colon, scan next 1-5 lines
for a valid company name (not address, not phone, not skip words).

```python
if any(line.startswith(p) for p in VENDOR_PREFIXES):
    val = line.split(":", 1)[1].strip()
    if val:
        result["vendor"] = val  # same-line vendor
    else:
        # Multi-line: "From:\nCompany Name"
        for j in range(i+1, min(i+5, len(lines))):
            if is_company_name(lines[j]):
                result["vendor"] = lines[j]
                break
```

---

## Lesson 3: Double Price Lines (Unit + Total on Same Line)

**Problem:** `FLR-001 Flour 2 $24.99 $49.98` — unit price AND total on same line.
The parser must extract the LAST price (total) and the item code/name.

**Fix:** Use `rsplit('$', 1)` to always get the rightmost price, which is the total.
`clean_item_name` handles stripping the unit price that remains in the left side.

```python
# Line: "FLR-001 Flour 2 $24.99 $49.98"
parts = line.rsplit('$', 1)   # ["FLR-001 Flour 2 $24.99 ", "49.98"]
item_name = clean_item_name(parts[0])  # "FLR-001 Flour 2"
total = float(parts[1])        # 49.98
```

---

## Lesson 4: Non-Decimal Values (Contractor Style)

**Problem:** `sub total 765` — no decimal, no `$` sign. Old regex `\d+\.\d{2}` required
exactly two decimal places.

**Fix:** Make decimal part optional in regex: `(\d+,?\.?\d{0,2})` — handles both
`$194.66` and `765` and `826.20`.

---

## Lesson 5: Tax Lines With Percentages

**Problem:** `tax 8% = 61.20` — the `%` sign and `=` confused the old regex which
picked up `8.00` from `8%` instead of `61.20`.

**Fix:** Split on `=` or `:` first, extract from the right side (the dollar amount),
not the left (the percentage).

```python
if 'tax' in line and '=' in line:
    # "tax 8% = 61.20" → split on "=" → "61.20"
    right_side = line.split('=')[-1]
    match = re.search(r'(\d+,?\.?\d{0,2})', right_side)
    tax = float(match.group(1))
```

---

## Lesson 6: Dotted Item Lines

**Problem:** `- rewired kitchen panel ............ $450` — items separated from
prices by variable-length dots.

**Fix:** Use `rsplit('$', 1)` (splits on dollar sign) plus strip dots from item name.
```python
item_name = parts[0].replace('-', '').replace('.', '').strip()
```

---

## Lesson 7: Contractors Have Unique Signatures

The messy contractor format is identifiable by:
- `work completed:` section header (or `services:`)
- Dotted lines between items and prices
- Lowercase, no punctuation, OCR noise
- "sub total" with space (not "Subtotal:")
- "total due" with space

Detection: `has_work_completed OR has_dotted_items`

---

## Lesson 8: Always Test the API, Not Just the Module

**Problem:** Python module tests passed but API returned different results.

**Causes:**
1. Python cached old `.pyc` files
2. The API wraps results in normalized format, hiding raw fields
3. Frontend expects flat fields (`vendor`, `items`, `success`) at top level

**Fix routine after every parser change:**
```bash
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
kill API && restart API
test ALL examples via curl
```

---

## Lesson 9: Normalized vs Raw Response Shape

The API must serve BOTH:
- Raw fields at top level (`vendor`, `items`, `success`, `total`) — for frontend
- Normalized fields (`direction`, `ledger_entry`, `entity_issuer`) — for system

**Pattern:** Merge raw + normalized instead of wrapping.
```python
result = dict(raw_result)  # Start with raw fields
result['direction'] = normalized.get('direction')  # Add normalized
result['ledger_entry'] = normalized.get('ledger_entry')
```

---

## Current Format Coverage (7/7)

| Format | Detection | Status |
|--------|-----------|--------|
| FROM:/BILL TO: + ITEMS: (NovaTech style) | has_from_bill + numbered items | ✅ |
| Table (Item Description Qty Unit Price Amount) | has_table_header | ✅ |
| Contractor (work completed + dots) | has_work_completed OR dotted_items | ✅ |
| International (Supplier: + TAX INVOICE) | SUPPLIER: + VAT | ✅ |
| POS Receipt (ITEMS + --- borders) | ITEMS in borders | ✅ |
| Professional Services (• bullets) | • + Date Issued: | ✅ |
| Subscription (Billing Period:) | Billing Period: | ✅ |
