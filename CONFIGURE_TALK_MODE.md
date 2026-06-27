# Configure OpenClaw Talk Mode for Local Voice

## Current Status

- `talk.provider`: `elevenlabs` (paid cloud service)
- `messages.tts.provider`: `openai` pointing to local Kokoro on port 8080
- Your SOL Voice Agent server: running on port 8769

## Goal

Switch Talk mode from ElevenLabs to your local cloned voice.

## Manual Config Steps (Required)

The `talk.provider` field is protected and cannot be changed via API. You must edit the config file directly.

### Step 1: Stop OpenClaw

```bash
openclaw stop
```

### Step 2: Edit Config File

Open `/Users/philliplowe/.openclaw/openclaw.json` in a text editor.

Find this section (around line 634):

```json
"talk": {
  "provider": "elevenlabs"
}
```

Replace it with:

```json
"talk": {
  "provider": "openai",
  "realtime": {
    "mode": "stt-tts",
    "transport": "gateway-relay",
    "brain": "agent-consult"
  }
}
```

### Step 3: Update messages.tts to point to SOL Voice Agent

Find the `messages.tts` section (around line 578) and change from Kokoro port 8080 to SOL Voice Agent port 8769:

**Current:**
```json
"tts": {
  "auto": "always",
  "provider": "openai",
  "providers": {
    "openai": {
      "apiKey": "not-needed",
      "baseUrl": "http://127.0.0.1:8080/v1",
      "model": "mlx-community/Kokoro-82M-bf16",
      "speakerVoice": "af_bella"
    }
  }
}
```

**Change to:**
```json
"tts": {
  "auto": "always",
  "provider": "openai",
  "providers": {
    "openai": {
      "apiKey": "not-needed",
      "baseUrl": "http://127.0.0.1:8769",
      "model": "sol_voice",
      "speakerVoice": "sol_voice"
    }
  }
}
```

### Step 4: Save and Restart

```bash
openclaw start
```

### Step 5: Verify

Check that Talk mode now uses local voice:
```bash
curl -s http://localhost:18789/config | grep -A 5 '"talk"'
```

## Alternative: Keep Kokoro for TTS, Use SOL Voice Agent for Cloning

If you want to keep using Kokoro (port 8080) for regular TTS and only use the SOL Voice Agent for voice cloning/cloned voice output, you can:

1. Leave `messages.tts` pointing to port 8080
2. Only change `talk.provider` to point to a custom local provider

But the simplest setup is to point everything to your SOL Voice Agent on port 8769.

## What's Running Where

| Service | Port | Purpose |
|---------|------|---------|
| Kokoro TTS | 8080 | Lightweight TTS (used by messages) |
| SOL Voice Agent | 8769 | Full pipeline + your cloned voice |
| SOL Voice WebSocket | 8765 | Real-time audio streaming |
| OpenClaw Gateway | 18789 | Main OpenClaw API |

## Voicebox

Voicebox is installed at `/Applications/Voicebox.app` for manual voice work (cloning, dictation, effects).

---

**Note:** The gateway API protects `talk.provider` from programmatic changes. You must edit `openclaw.json` directly while OpenClaw is stopped.
