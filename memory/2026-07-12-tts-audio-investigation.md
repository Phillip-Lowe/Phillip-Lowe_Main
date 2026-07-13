# TTS Audio Issue — Investigation Complete

**Date:** 2026-07-12 23:06 CDT
**Status:** ⏸️ PAUSED — TTS server down, compute being wasted
**Decision:** Pause TTS until local server is fixed

---

## Problem Summary

Audio files ARE being generated (visible in `~/.openclaw/media/outbound/`) but **never delivered** to user. User burning compute but hearing nothing.

**Root Cause:** Local TTS server (MLX/Kokoro on port 8080) is **not running**.

## Configuration Found

```json
// messages.tts in ~/.openclaw/openclaw.json
{
  "auto": "always",
  "provider": "openai",
  "providers": {
    "openai": {
      "apiKey": "mlx-lo…eded",
      "baseUrl": "http://127.0.0.1:8080/v1",
      "model": "mlx-community/Kokoro-82M-bf16",
      "speakerVoice": "af_bella"
    }
  }
}
```

**Issue:** Config points to `http://127.0.0.1:8080/v1` but **port 8080 has nothing listening**.

## What Was Checked

| Check | Result |
|-------|--------|
| Audio files in media/outbound/ | ✅ Generating (timestamps show active generation) |
| Symlink workspace/media → media/outbound | ✅ Working (from 2026-07-11 fix) |
| Port 8080 listening | ❌ Nothing running |
| Local voice server processes | ❌ None found |
| `messages.tts.auto` | `"always"` — always generating |
| `messages.tts.provider` | `"openai"` pointing to local MLX server |

## Why Files Generate But No Audio Heard

1. OpenClaw sees `tts` tool is available
2. `messages.tts.auto = "always"` triggers generation on every reply
3. TTS tool tries to call `http://127.0.0.1:8080/v1` (Kokoro/MLX)
4. Server is down → call fails or falls back to some internal generation
5. MP3 files are created but **never attached/played** in the channel
6. Compute is burned, user hears nothing

## Solution Options

### Option A: Restart Local MLX/Kokoro Server (Preferred — matches existing config)
- Start the local TTS server on port 8080
- No config changes needed
- Preserves local/offline voice synthesis

**Unknown:** What command/script starts this server? Need to find startup method.

### Option B: Switch to Cloud Provider
- Change `messages.tts.provider` to OpenAI, ElevenLabs, etc.
- Requires API key
- Costs money per request

### Option C: Fully Disable TTS
- Set `messages.tts.auto = "off"` or `"never"`
- No audio generation at all
- Zero compute burn

---

## Decision

**PAUSE TTS until local server is fixed.**

Config is protected (can't patch via gateway). To formally disable:
- Edit `~/.openclaw/openclaw.json` directly: change `messages.tts.auto` from `"always"` to `"off"`
- OR restart gateway with updated config

**For now:** TTS is effectively paused because server is down. If server restarts unexpectedly, audio will resume.

---

## To-Do

1. ⏸️ **Find/start the local MLX/Kokoro TTS server** (port 8080)
   - Was it `python3 -m mlx_lm.server`? 
   - Was it a custom script?
   - Check `~/.openclaw/skills/local-voice-streaming/` for startup scripts
   - Check `~/.openclaw/skills/sol-voice-agent/` for startup scripts

2. ⏸️ **Test audio delivery** after server restart
   - Send test TTS message
   - Verify audio plays on mobile and desktop

3. ⏸️ **If local server can't be fixed, decide:**
   - Switch to cloud provider (costs money)
   - Permanently disable TTS (save compute)

---

## Files/References

- Config: `~/.openclaw/openclaw.json` → `messages.tts`
- Media output: `~/.openclaw/media/outbound/`
- Symlink: `~/.openclaw/workspaces/sol/media` → `~/.openclaw/media/outbound`
- Local voice skill: `~/.openclaw/skills/sol-voice-agent/`
- Earlier voice skill: `~/.openclaw/skills/local-voice-streaming/`

---

**Next Action Required:** User to decide if they want to fix local server or permanently disable TTS.
