#!/usr/bin/env python3
"""Test Ollama API responsiveness."""
import json
import urllib.request
import socket
import sys

def test_ollama(model, timeout=10):
    payload = json.dumps({
        "model": model,
        "prompt": "Say 'OK' and nothing else.",
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 10}
    }).encode()

    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    print(f"Testing {model} (timeout={timeout}s)...")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
            print(f"  ✅ Response: {data.get('response','(empty)')[:100]}")
            print(f"  Total duration: {data.get('total_duration',0)/1e9:.2f}s")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        print(f"  ❌ HTTP {e.code}: {body}")
        return False
    except socket.timeout:
        print(f"  ❌ Socket timeout after {timeout}s")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

if __name__ == "__main__":
    models = ["qwen2.5-coder:7b", "qwen3.5:9b", "deepseek-v4-flash:cloud"]
    for m in models:
        test_ollama(m)
        print()
