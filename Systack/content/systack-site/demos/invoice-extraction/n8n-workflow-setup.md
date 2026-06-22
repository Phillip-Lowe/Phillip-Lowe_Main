# n8n Workflow Setup — Invoice Extraction Pipeline

## Overview

This guide configures an n8n workflow that:
1. Receives invoice text via a Webhook (POST)
2. Sends it to the local Ollama API for structured extraction
3. Returns clean JSON with the 5 extracted fields

## Prerequisites

- Ollama running at `http://localhost:11434`
- Model `qwen2.5-coder:7b` pulled locally
- n8n running (e.g., Docker Desktop on port 5678)

---

## Node 1: Webhook (Trigger)

**Node type:** Webhook  
**Method:** POST  
**Path:** `invoice-extract`  
**Response Mode:** Last Node

### Expected JSON Body (Webhook Input)

```json
{
  "invoice_text": "Paste raw invoice text here..."
}
```

**Headers to set in client:**
```
Content-Type: application/json
```

---

## Node 2: HTTP Request (Ollama Call)

**Node type:** HTTP Request  
**Method:** POST  
**URL:** `http://host.docker.internal:11434/api/generate`  
*(If n8n runs in Docker, use `host.docker.internal` to reach the host's Ollama. If n8n runs natively, use `http://localhost:11434/api/generate`.)*

### Authentication: None

### Body (JSON)

Use **Expression** mode for the `prompt` field so it references the webhook input.

```json
{
  "model": "qwen2.5-coder:7b",
  "prompt": "You are an invoice data extraction engine. Your job is to read raw invoice text and extract structured fields into a JSON object.\n\nINSTRUCTIONS:\n1. Read the invoice text below carefully.\n2. Extract exactly these five fields:\n   - total_amount: The final total amount owed (as a string, e.g., \"1247.50\")\n   - invoice_date: The date of the invoice (as a string in YYYY-MM-DD format if possible; otherwise preserve original format)\n   - vendor_name: The company or vendor name that issued the invoice (as a string)\n   - invoice_number: The invoice identifier/number (as a string)\n   - line_items: An array of objects, each with:\n     - description: Item description (string)\n     - quantity: Quantity (number or string)\n     - unit_price: Price per unit (string, e.g., \"25.00\")\n     - total: Total for this line (string, e.g., \"100.00\")\n3. If a field is missing or cannot be determined, use null for scalar fields and [] for line_items.\n4. Return ONLY valid JSON. No markdown, no code fences, no explanations, no extra text.\n5. The JSON must parse cleanly with JSON.parse() or json.loads().\n\nEXPECTED JSON SCHEMA:\n{\n  \"total_amount\": \"string or null\",\n  \"invoice_date\": \"string or null\",\n  \"vendor_name\": \"string or null\",\n  \"invoice_number\": \"string or null\",\n  \"line_items\": [\n    {\n      \"description\": \"string\",\n      \"quantity\": \"number or string\",\n      \"unit_price\": \"string\",\n      \"total\": \"string\"\n    }\n  ]\n}\n\nINVOICE TEXT TO EXTRACT:\n---\n{{ $json.invoice_text }}\n---\n\nRESPONSE (valid JSON only):",
  "stream": false,
  "options": {
    "temperature": 0,
    "num_predict": 2048
  }
}
```

> In n8n expression mode, replace `{{ $json.invoice_text }}` with the actual expression reference `{{ $json.invoice_text }}` (or `{{ $input.item.json.invoice_text }}` depending on n8n version).

---

## Node 3: Code Node (Parse & Clean Response)

**Node type:** Code  
**Mode:** Run Once for All Items

### JavaScript Code

```javascript
const rawResponse = $input.first().json.response;

// Strip markdown fences if present
let cleaned = rawResponse
  .replace(/^```json\s*/, '')
  .replace(/^```\s*/, '')
  .replace(/```\s*$/, '')
  .trim();

let parsed;
try {
  parsed = JSON.parse(cleaned);
} catch (e) {
  parsed = {
    error: "Failed to parse JSON",
    raw_response: rawResponse,
    parse_error: e.message
  };
}

return [{
  json: {
    success: !parsed.error,
    extracted: parsed
  }
}];
```

---

## Node 4: Respond to Webhook (Output)

**Node type:** Respond to Webhook  
**Status Code:** 200  
**Response Body:** Expression mode → `{{ JSON.stringify($json) }}`

Or set **Response Mode** on the Webhook node to "Last Node" and let the Code node's output flow through.

---

## Full Workflow JSON (Import into n8n)

You can also paste this into n8n's "Import from JSON":

```json
{
  "name": "Invoice Extraction Pipeline",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "invoice-extract",
        "responseMode": "responseNode",
        "options": {}
      },
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 300],
      "webhookId": "invoice-extract",
      "name": "Webhook"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://host.docker.internal:11434/api/generate",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "model",
              "value": "qwen2.5-coder:7b"
            },
            {
              "name": "prompt",
              "value": "=You are an invoice data extraction engine...\n---\n{{ $json.invoice_text }}\n---\nRESPONSE (valid JSON only):"
            },
            {
              "name": "stream",
              "value": "false"
            },
            {
              "name": "options",
              "value": "{\"temperature\": 0, \"num_predict\": 2048}"
            }
          ]
        },
        "options": {}
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [450, 300],
      "name": "Ollama Extraction"
    },
    {
      "parameters": {
        "jsCode": "const rawResponse = $input.first().json.response;\nlet cleaned = rawResponse.replace(/^```json\\s*/, '').replace(/^```\\s*/, '').replace(/```\\s*$/, '').trim();\nlet parsed;\ntry { parsed = JSON.parse(cleaned); } catch (e) { parsed = { error: 'Failed to parse JSON', raw_response: rawResponse, parse_error: e.message }; }\nreturn [{ json: { success: !parsed.error, extracted: parsed } }];"
      },
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [650, 300],
      "name": "Parse JSON"
    },
    {
      "parameters": {
        "options": {}
      },
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [850, 300],
      "name": "Respond"
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Ollama Extraction", "type": "main", "index": 0}]]
    },
    "Ollama Extraction": {
      "main": [[{"node": "Parse JSON", "type": "main", "index": 0}]]
    },
    "Parse JSON": {
      "main": [[{"node": "Respond", "type": "main", "index": 0}]]
    }
  }
}
```

> Note: The prompt in the JSON above is abbreviated. Use the full prompt from `prompt-template.txt` in production.

---

## Testing the Webhook

```bash
curl -X POST http://localhost:5678/webhook/invoice-extract \
  -H "Content-Type: application/json" \
  -d '{"invoice_text": "INVOICE\n\nAcme Corp\nInvoice #: 12345\nDate: Jan 15, 2024\n\nWidget A  2 @ $50 = $100\nTotal: $100"}'
```

---

## Error Handling Notes

- If Ollama returns markdown fences, the Parse JSON node strips them.
- If JSON is still unparseable, the node returns `success: false` with the raw response for debugging.
- Set `temperature: 0` for deterministic extraction.
- Increase `num_predict` if invoices are very long (default 2048 tokens).
