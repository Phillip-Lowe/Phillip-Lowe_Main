#!/bin/bash
# Deploy Llama 3.2 3B on Mother's VPS
# Run this on the VPS as root

set -e

echo "=== Step 1: Pull Llama 3.2 3B (American model) ==="
ollama pull llama3.2:3b

echo ""
echo "=== Step 2: Verify model ==="
ollama list | grep llama3.2

echo ""
echo "=== Step 3: Test model ==="
curl -s http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "Hello, I am a personal assistant. What can you help with?",
  "stream": false
}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('Response:', d['response'][:100] if 'response' in d else 'Error: ' + str(d))"

echo ""
echo "=== Step 4: Update OpenClaw config ==="
cat > /tmp/new-model.json << 'EOF'
{
  "id": "llama3.2:3b",
  "name": "llama3.2:3b",
  "reasoning": false,
  "input": ["text"],
  "cost": {
    "input": 0,
    "output": 0,
    "cacheRead": 0,
    "cacheWrite": 0
  },
  "contextWindow": 32768,
  "maxTokens": 8192,
  "compat": {
    "supportsTools": true,
    "supportsUsageInStreaming": true
  },
  "params": {
    "num_ctx": 32768
  }
}
EOF

echo ""
echo "=== Step 5: Backup current config ==="
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak.$(date +%Y%m%d-%H%M%S)

echo ""
echo "=== Step 6: Update config (replace qwen2.5:3b with llama3.2:3b) ==="
# This uses Python to safely edit the JSON
python3 << 'PYEOF'
import json

with open('/root/.openclaw/openclaw.json', 'r') as f:
    config = json.load(f)

# Find and replace the model entry
for provider in config.get('models', {}).get('providers', {}).values():
    if 'models' in provider:
        for i, model in enumerate(provider['models']):
            if model.get('id') == 'qwen2.5:3b':
                provider['models'][i] = {
                    "id": "llama3.2:3b",
                    "name": "llama3.2:3b",
                    "reasoning": False,
                    "input": ["text"],
                    "cost": {
                        "input": 0,
                        "output": 0,
                        "cacheRead": 0,
                        "cacheWrite": 0
                    },
                    "contextWindow": 32768,
                    "maxTokens": 8192,
                    "compat": {
                        "supportsTools": True,
                        "supportsUsageInStreaming": True
                    },
                    "params": {
                        "num_ctx": 32768
                    }
                }
                print("Replaced qwen2.5:3b with llama3.2:3b")

# Update default model
if 'agents' in config and 'defaults' in config['agents']:
    old_model = config['agents']['defaults'].get('model', '')
    if 'qwen' in old_model:
        config['agents']['defaults']['model'] = 'ollama/llama3.2:3b'
        print(f"Updated default model from {old_model} to ollama/llama3.2:3b")

with open('/root/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Config updated successfully")
PYEOF

echo ""
echo "=== Step 7: Validate config ==="
openclaw config validate

echo ""
echo "=== Step 8: Restart gateway ==="
systemctl --user restart openclaw-gateway
sleep 3

echo ""
echo "=== Step 9: Verify gateway running ==="
systemctl --user status openclaw-gateway --no-pager

echo ""
echo "=== Step 10: Check RAM usage ==="
free -h

echo ""
echo "=== Step 11: Test with a message ==="
curl -s http://localhost:18789/api/chat -H "Content-Type: application/json" -d '{
  "message": "Hi Percy, can you help me schedule interviews?",
  "model": "ollama/llama3.2:3b"
}' 2>/dev/null | head -c 200 || echo "(Gateway test requires proper auth)"

echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo "Model: llama3.2:3b (American/Meta)"
echo "Size: 2.0GB"
echo "Context: 32K tokens"
echo ""
echo "Test from your phone/laptop:"
echo "1. Open https://percy-mcdonalds.taildd162e.ts.net"
echo "2. Send 'Hi Percy'"
echo "3. Should respond with American model"
