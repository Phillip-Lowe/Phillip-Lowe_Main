# pgAdmin 4 + Ollama Setup Guide

**Date:** 2026-06-08  
**pgAdmin Version:** 9.15  
**Ollama Status:** Running on localhost:11434

## Current Status

- ✅ pgAdmin 4 v9.15 installed and running
- ✅ Ollama running locally (http://localhost:11434)
- ✅ Available models: qwen2.5-coder:7b, qwen3.5:9b, llama3.2:3b, etc.
- ⏳ pgAdmin AI configuration needs manual setup via UI

## How to Configure Ollama in pgAdmin 4

### Step 1: Open pgAdmin Preferences

1. Open pgAdmin 4 (already running)
2. Click **File** → **Preferences**
   OR
3. Click the **gear/settings icon** in the toolbar

### Step 2: Navigate to AI Settings

1. In Preferences dialog, scroll down and click **"AI"** in the left panel
2. You should see LLM Provider settings

### Step 3: Select Ollama as Provider

1. **LLM Provider:** Select **"Ollama"** from dropdown
2. **API URL:** Enter: `http://localhost:11434`
3. **Model:** Enter: `qwen2.5-coder:7b` (or another model from list below)

### Step 4: Save

1. Click **"Save"** button
2. pgAdmin will validate the connection to Ollama

### Step 5: Test AI Features

Once configured, you can use:
- **Tools → AI Reports → Security** — Analyze database security
- **Tools → AI Reports → Performance** — Query optimization recommendations
- **Tools → AI Reports → Design** — Schema design review

## Available Ollama Models

| Model | Size | Best For |
|-------|------|----------|
| qwen2.5-coder:7b | 4.7GB | Coding/SQL generation |
| qwen3.5:9b | 6.6GB | General + coding |
| llama3.2:3b | 2.0GB | Lightweight tasks |
| llama3.1:8b | 4.9GB | General purpose |

Recommended for pgAdmin AI: **qwen2.5-coder:7b** (good balance of capability and speed)

## Troubleshooting

### "AI features are disabled in server configuration"
- The `LLM_ENABLED = True` is already set in pgAdmin config
- If you still see this, restart pgAdmin completely

### "Cannot connect to Ollama"
1. Verify Ollama is running: `curl http://localhost:11434/api/tags`
2. Check firewall settings
3. Try `127.0.0.1` instead of `localhost`

### "Model not found"
1. Pull the model first: `ollama pull qwen2.5-coder:7b`
2. Verify with: `ollama list`

## Verification Commands

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check specific model exists
ollama list | grep qwen2.5-coder

# Test model directly
ollama run qwen2.5-coder:7b "Generate a SQL query to list all tables"
```

## User Config Override Created

Created: `~/.pgadmin/config.py`
- Sets `DEFAULT_LLM_PROVIDER = 'ollama'`
- Sets `OLLAMA_API_URL = 'http://localhost:11434'`
- Sets `OLLAMA_API_MODEL = 'qwen2.5-coder:7b'`

**Note:** pgAdmin may not read this user config. The UI Preferences method is the reliable approach.

## Next Steps

1. Open pgAdmin Preferences
2. Configure Ollama as described above
3. Test with Tools → AI Reports → Security on your database
4. Save this configuration to memory for future sessions

---
**Created by:** Sol (Systack)
