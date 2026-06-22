# Systack — Invoice Parser
## API Documentation

**Document ID:** `SY-IP-API-001`  
**Version:** 1.0  
**Status:** Live  
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

## 1. Endpoint

```
POST https://invoices.systack.net/extract
```

**Method:** POST  
**Content-Type:** `multipart/form-data`  
**Authentication:** None (internal service)

---

## 2. Request

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File (PDF) | Yes | The invoice PDF to extract |

### Example (curl)

```bash
curl -X POST https://invoices.systack.net/extract \
  -F "file=@invoice.pdf"
```

### Example (Python)

```python
import requests

with open("invoice.pdf", "rb") as f:
    response = requests.post(
        "https://invoices.systack.net/extract",
        files={"file": f}
    )

data = response.json()
print(f"Vendor: {data['vendor']}")
print(f"Total: ${data['total']}")
```

---

## 3. Response

### Success (200)

```json
{
  "vendor": "AT&T",
  "invoice_number": "12345",
  "date": "2026-06-01",
  "line_items": [
    {
      "name": "Wireless Plan",
      "qty": 1,
      "price": 85.00,
      "total": 85.00
    },
    {
      "name": "Device Payment",
      "qty": 1,
      "price": 15.00,
      "total": 15.00
    }
  ],
  "subtotal": 100.00,
  "tax": 8.50,
  "total": 108.50,
  "email_subject": "Invoice Processed: AT&T — 12345",
  "email_html": "<table>...</table>"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `vendor` | string | Vendor/company name |
| `invoice_number` | string | Invoice identifier |
| `date` | string | Invoice date (YYYY-MM-DD) |
| `line_items` | array | Itemized list of charges |
| `line_items[].name` | string | Line item description |
| `line_items[].qty` | number | Quantity |
| `line_items[].price` | number | Unit price (dollars) |
| `line_items[].total` | number | Line total (dollars) |
| `subtotal` | number | Pre-tax total (dollars) |
| `tax` | number | Tax amount (dollars) |
| `total` | number | Final total (dollars) |
| `email_subject` | string | Suggested email subject |
| `email_html` | string | Pre-formatted HTML summary table |

---

### Partial Success (200 with OCR fallback)

When vendor format is not recognized, OCR extracts what it can:

```json
{
  "vendor": "Unknown Vendor",
  "invoice_number": "Detected: 12345",
  "date": "2026-06-01",
  "line_items": [
    {"name": "Item 1", "qty": 1, "price": null, "total": 85.00}
  ],
  "subtotal": null,
  "tax": null,
  "total": 108.50,
  "ocr_fallback": true
}
```

Fields may be `null` when OCR cannot confidently extract them.

---

### Error (400)

```json
{
  "error": "No file provided",
  "detail": "Request must include a PDF file in the 'file' field"
}
```

### Error (422)

```json
{
  "error": "Unreadable PDF",
  "detail": "File could not be parsed. Ensure it is a valid PDF."
}
```

### Error (500)

```json
{
  "error": "Extraction failed",
  "detail": "Internal processing error. Try again or contact support."
}
```

---

## 4. Supported Formats

### Format-Matched Vendors (9+)

| Vendor | Format Handler | Confidence |
|--------|---------------|------------|
| AT&T | `att_handler` | High |
| Verizon | `verizon_handler` | High |
| Utility providers | `utility_handler` | Medium-High |
| Wholesale suppliers | `wholesale_handler` | Medium |
| Generic service invoices | `generic_handler` | Medium |

### OCR Fallback

For unrecognized formats:

- Uses Tesseract OCR engine
- Extracts text from PDF images
- Attempts to identify: vendor name, numbers, dates, totals
- Marks response with `ocr_fallback: true`

---

## 5. Rate Limits

| Limit | Value |
|-------|-------|
| Max file size | 10 MB |
| Requests per minute | 30 |
| Concurrent requests | 5 |

---

## 6. Error Codes

| Status | Meaning | Action |
|--------|---------|--------|
| 200 | Success | Process response data |
| 200 + `ocr_fallback` | Partial (OCR) | Review data, may need manual check |
| 400 | Bad request | Check file parameter |
| 422 | Unreadable | Verify PDF is valid |
| 500 | Server error | Retry, escalate if persistent |

---

## 7. Demo

Interactive demo available at:
**https://systack.net/services/invoice-extractor.html**

Upload any PDF invoice to see extraction results in real time.

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
