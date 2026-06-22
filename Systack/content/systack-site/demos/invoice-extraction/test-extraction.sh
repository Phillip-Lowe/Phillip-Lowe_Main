#!/usr/bin/env bash
set -euo pipefail

OLLAMA_URL="http://localhost:11434/api/generate"
MODEL="qwen2.5-coder:7b"
INVOICES_FILE="test-invoices.json"
PROMPT_TEMPLATE="prompt-template.txt"
RESULTS_FILE="results.json"

# Check Ollama is reachable
if ! curl -s "$OLLAMA_URL" > /dev/null 2>&1; then
  echo "ERROR: Cannot reach Ollama at $OLLAMA_URL"
  exit 1
fi

# Check model is available
if ! curl -s "http://localhost:11434/api/tags" | grep -q "$MODEL"; then
  echo "ERROR: Model $MODEL not found in Ollama. Available models:"
  curl -s "http://localhost:11434/api/tags" | grep '"name"'
  exit 1
fi

# Read prompt template
PROMPT_TEMPLATE_TEXT=$(cat "$PROMPT_TEMPLATE")

# Count invoices
INV_COUNT=$(jq '. | length' "$INVOICES_FILE")
echo "Testing $INV_COUNT invoices against model: $MODEL"
echo ""

# Initialize results array
RESULTS="[]"

for i in $(seq 0 $((INV_COUNT - 1))); do
  ID=$(jq -r ".[$i].id" "$INVOICES_FILE")
  NAME=$(jq -r ".[$i].name" "$INVOICES_FILE")
  TEXT=$(jq -r ".[$i].text" "$INVOICES_FILE")

  echo "--- [$ID] $NAME ---"

  # Substitute invoice text into prompt using jq gsub (handles newlines safely)
  PROMPT=$(jq -n --arg tmpl "$PROMPT_TEMPLATE_TEXT" --arg text "$TEXT" '$tmpl | gsub("{{invoice_text}}"; $text)')

  # Build JSON payload
  PAYLOAD=$(jq -n \
    --arg model "$MODEL" \
    --arg prompt "$PROMPT" \
    '{model: $model, prompt: $prompt, stream: false, options: {temperature: 0.0, num_predict: 2048}}')

  # Call Ollama
  RESPONSE=$(curl -s "$OLLAMA_URL" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

  # Extract the generated text
  GENERATED=$(echo "$RESPONSE" | jq -r '.response // empty')

  # Clean up: strip markdown fences if present (portable across GNU/BSD sed)
  CLEANED=$(printf '%s' "$GENERATED" | python3 -c '
import sys, re
text = sys.stdin.read()
# Remove ```json ... ``` blocks
text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
text = re.sub(r"```\s*$", "", text, flags=re.MULTILINE)
text = text.strip()
print(text)
')

  # Try to parse as JSON
  if printf '%s' "$CLEANED" | jq empty 2>/dev/null; then
    PARSED=$(printf '%s' "$CLEANED" | jq '.')
    VALID="true"
    echo "  VALID JSON"
  else
    PARSED="null"
    VALID="false"
    echo "  INVALID JSON - raw response saved"
  fi

  # Build result object
  RESULT=$(jq -n \
    --arg id "$ID" \
    --arg name "$NAME" \
    --arg model "$MODEL" \
    --argjson valid "$VALID" \
    --argjson extracted "$PARSED" \
    --arg raw "$GENERATED" \
    '{id: $id, name: $name, model: $model, valid_json: $valid, extracted: $extracted, raw_response: $raw}')

  RESULTS=$(echo "$RESULTS" | jq --argjson r "$RESULT" '. + [$r]')
  echo ""
done

# Write results
echo "$RESULTS" | jq '.' > "$RESULTS_FILE"
echo "Results written to $RESULTS_FILE"

# Summary
VALID_COUNT=$(echo "$RESULTS" | jq '[.[] | select(.valid_json == true)] | length')
echo ""
echo "=========================="
echo "SUMMARY: $VALID_COUNT / $INV_COUNT invoices produced valid JSON"
echo "=========================="

if [ "$VALID_COUNT" -eq "$INV_COUNT" ]; then
  echo "All extractions successful."
  exit 0
else
  echo "Some extractions failed. Check $RESULTS_FILE for details."
  exit 1
fi
