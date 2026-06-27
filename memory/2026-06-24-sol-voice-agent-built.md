# SOL Voice Agent — Build Session

**Date:** 2026-06-24 09:00 CDT
**Session:** SOL
**Trigger:** ORACLE recommended Coqui/Qwen3-TTS stack for local ElevenLabs alternative

## What Was Built

Complete local voice agent skill at `~/.openclaw/skills/sol-voice-agent/`:

### Files Created
1. `server.py` — WebSocket + FastAPI HTTP server (VAD → STT → LLM → TTS pipeline)
2. `models.py` — Model download + warmup manager
3. `tts_engine.py` — Unified TTS with 3 backends (Coqui → Kokoro → Placeholder)
4. `voice_clone.py` — Voice cloning via XTTS v2 / OpenVoice
5. `requirements.txt` — Dependencies
6. `plugin.json` — OpenClaw skill manifest
7. `README.md` — Full documentation
8. `STATUS.md` — Build status + blockers

### Pipeline Status
- VAD (Silero): ✅ Ready
- STT (Whisper): ✅ Ready
- LLM (Qwen3): ✅ Ready
- TTS: ⚠️ Placeholder only (real TTS blocked)

## ⚠️ Blocker: Python Version — RESOLVED

**Python 3.11.15 installed via Homebrew** at `/opt/homebrew/opt/python@3.11/`.
Coqui TTS installed and working.

## ⚠️ Remaining: XTTS v2 License

Voice cloning requires accepting Coqui CPML license interactively:
```bash
python3.11 -c "from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/xtts_v2')"
# Type 'y' to accept
```

## TTS Verified

- Engine: Coqui TTS (Tacotron2 + HiFi-GAN)
- Speed: 9x faster than real-time (RTF 0.11)
- Quality: Good — LJSpeech-trained voice
- Memory: ~400MB model

## Next Steps

1. Accept XTTS license (interactive — Green must do this)
2. Clone a voice with XTTS v2
3. Wire OpenClaw Talk to WebSocket
4. Build n8n integration for voice alerts

## Memory Budget

- Whisper STT: ~1.5GB
- Qwen3 LLM: ~4.5GB
- Coqui TTS: ~400MB
- Overhead: ~2GB
- **Total: ~8.4GB** (comfortable on 16GB Mac Air M4)

## Reference

- ORACLE response: Coqui/Qwen3-TTS stack recommended for scalable voice agent
- Previous work: `~/.openclaw/skills/local-voice-streaming/` (Kokoro-based skeleton, Jun 5-6)
- Full status: `~/.openclaw/skills/sol-voice-agent/STATUS.md`
