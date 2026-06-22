# Systack — Invoice Parser
## Vendor Format Guide

**Document ID:** `SY-IP-VENDOR-001`  
**Version:** 1.0  
**Status:** Internal — Systack Only  
**Source System:** Systack Invoice Parser API (Live since 2026-06-08)  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## Brand Reference

| Role | Color | Hex |
|------|-------|-----|
| Headers, CTAs | Navy | `#001a2d` |
| Navy Light | Navy Light | `#002845` |
| Secondary accents | Teal | `#007da9` |
| Primary buttons, links | Cyan | `#00a1db` |
| Gradients | Cyan Bright | `#00c5e0` |
| Backgrounds | Gray 50 | `#f8fafc` |
| Cards | Gray 100 | `#f1f5f9` |
| Borders | Gray 200 | `#e2e8f0` |
| Muted text | Gray 400 | `#94a3b8` |
| Body text | Gray 600 | `#475569` |
| Headings | Gray 800 | `#1e293b` |
| Success | Green | `#22c55e` |
| Error | Red | `#ef4444` |
| Accent highlights | Purple | `#8b5cf6` |

---

## 1. Overview

The Invoice Parser uses format-specific handlers to extract structured data from known vendor invoice layouts. When a vendor format is not recognized, the system falls back to OCR.

This guide explains how to add support for new vendor formats.

---

## 2. How Format Detection Works

```
PDF received
  → Extract text content
    → Match against known vendor signatures
      → Found? → Use format-specific handler
      → Not found? → Use OCR fallback
```

**Vendor signatures** are unique text patterns that identify a vendor:

- Company name in header
- Specific formatting patterns
- Unique field labels (e.g., "AT&T Account Number")
- Logo text recognition

---

## 3. Currently Supported Vendors

| Vendor | Handler | Signature Pattern |
|--------|---------|-------------------|
| AT&T | `att_handler` | "AT&T" + account number format |
| Verizon | `verizon_handler` | "Verizon" + billing period |
| Utility (generic) | `utility_handler` | "Service Address" + meter number |
| Wholesale (generic) | `wholesale_handler` | "PO Number" + quantity columns |
| Service (generic) | `generic_handler` | "Invoice Date" + "Service Description" |

---

## 4. Adding a New Vendor Format

### Step 1 — Collect Sample Invoices

Gather 3–5 sample PDF invoices from the vendor. Variety helps:

- Different billing periods
- Different amounts
- Different line item counts

---

### Step 2 — Identify Extraction Fields

Map the vendor's invoice layout to our standard fields:

| Our Field | Vendor's Label | Location on Page |
|-----------|---------------|------------------|
| `vendor` | Company name | Top header |
| `invoice_number` | "Invoice #", "Bill #", "Reference" | Top right or below header |
| `date` | "Invoice Date", "Bill Date" | Near invoice number |
| `line_items[].name` | Item description column | Table body |
| `line_items[].qty` | "Qty", "Units" | Table column |
| `line_items[].price` | "Rate", "Unit Price" | Table column |
| `line_items[].total` | "Amount", "Charge" | Table column |
| `subtotal` | "Subtotal", "Net Amount" | Below table |
| `tax` | "Tax", "GST", "VAT" | Below subtotal |
| `total` | "Total", "Amount Due", "Balance" | Bottom of invoice |

---

### Step 3 — Write the Handler

Create a new handler in the parser codebase:

```python
# handlers/vendor_name_handler.py

def extract(pdf_text: str) -> dict:
    """
    Extract invoice data from Vendor Name PDF format.
    
    Args:
        pdf_text: Raw text extracted from PDF
        
    Returns:
        Dict with standard invoice fields
    """
    
    result = {
        "vendor": "Vendor Name",
        "invoice_number": None,
        "date": None,
        "line_items": [],
        "subtotal": None,
        "tax": None,
        "total": None,
    }
    
    # 1. Extract invoice number
    # Look for pattern: "Invoice #: XXXXX"
    import re
    inv_match = re.search(r'Invoice\s*#:\s*(\S+)', pdf_text)
    if inv_match:
        result["invoice_number"] = inv_match.group(1)
    
    # 2. Extract date
    date_match = re.search(r'Date:\s*(\d{1,2}/\d{1,2}/\d{4})', pdf_text)
    if date_match:
        result["date"] = date_match.group(1)
    
    # 3. Extract line items from table
    # ... vendor-specific table parsing logic ...
    
    # 4. Extract totals
    total_match = re.search(r'Total\s*\$?([\d,]+\.\d{2})', pdf_text)
    if total_match:
        result["total"] = float(total_match.group(1).replace(',', ''))
    
    return result
```

---

### Step 4 — Register the Handler

Add to the handler registry:

```python
# handlers/registry.py

HANDLERS = {
    "att": att_handler.extract,
    "verizon": verizon_handler.extract,
    "vendor_name": vendor_name_handler.extract,  # NEW
}
```

Add signature detection:

```python
# handlers/detector.py

SIGNATURES = {
    "AT&T": "att",
    "Verizon": "verizon",
    "Vendor Name": "vendor_name",  # NEW
}
```

---

### Step 5 — Test

```bash
# Test with sample invoice
curl -X POST https://invoices.systack.net/extract \
  -F "file=@sample_vendor_invoice.pdf"

# Verify response
{
  "vendor": "Vendor Name",
  "invoice_number": "12345",
  ...
}
```

---

### Step 6 — Document

Add to this guide:

- Vendor name and handler file
- Signature pattern used
- Any special extraction logic
- Known limitations

---

## 5. Handler Design Guidelines

### Do

- Use regex patterns that are specific enough to avoid false matches
- Handle variations in formatting (spacing, punctuation)
- Return `None` for fields that can't be confidently extracted
- Test with multiple sample invoices
- Handle multi-page invoices (check all pages)

### Don't

- Hardcode dollar amounts or dates
- Assume table column positions (use labels, not positions)
- Crash on unexpected formats (return partial data gracefully)
- Use filename for vendor detection (use content)

---

## 6. OCR Fallback

When no format handler matches:

1. PDF is rendered to image
2. Tesseract OCR extracts all visible text
3. Generic patterns are applied:
   - Largest dollar amount → likely total
   - Date-like patterns → likely invoice date
   - Number with 4+ digits → likely invoice number
   - Company name at top → likely vendor

**OCR limitations:**

- Handwriting not recognized
- Complex table layouts may scramble
- Confidence varies by PDF quality

---

## 7. Testing New Formats

### Test Script

```bash
#!/bin/bash
# test_vendor_format.sh

VENDOR_DIR="./test_invoices/vendor_name"

for pdf in "$VENDOR_DIR"/*.pdf; do
  echo "Testing: $pdf"
  curl -s -X POST https://invoices.systack.net/extract \
    -F "file=@$pdf" | python3 -m json.tool
  echo "---"
done
```

### Validation Checklist

- [ ] Vendor name correctly identified
- [ ] Invoice number extracted
- [ ] Date parsed correctly
- [ ] All line items captured
- [ ] Quantities match invoice
- [ ] Prices match invoice
- [ ] Subtotal calculated correctly
- [ ] Tax extracted (if present)
- [ ] Total matches invoice
- [ ] Works across 3+ sample invoices

---

## 8. Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-08 | Initial 9 handlers deployed |
| 1.0 | 2026-06-16 | Documented (this file) |

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
