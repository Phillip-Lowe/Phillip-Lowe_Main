# Real-Time Voice Chat — TODO Added

**Date:** 2026-06-24 10:31 CDT
**User:** Green
**Action:** Added to AGENTS.md TODO list

## What Was Decided

Real-time voice chat with cloned voice is **not happening today**, but it's a **critical priority** for "very soon."

## Current Status

- ✅ Voicebox installed (manual voice work)
- ✅ SOL Voice Agent server running (port 8769, cloned voice ready)
- ✅ OpenClaw Talk mode configured with `stt-tts` + `gateway-relay` (works, but generic voice)
- ❌ Real-time Talk mode using cloned voice — **needs custom provider adapter**

## The Work Required

### Phase 1: Research (DONE — ORACLE completed this)
- ✅ Feasibility confirmed: OpenClaw can be extended
- ✅ Architecture defined: WebSocket bridge + provider adapter
- ✅ Event contract documented (session.create, audio.append, transcript.delta, response.audio.delta, etc.)

### Phase 2: Build (NEXT SESSION)

1. **Create Realtime Bridge** (`realtime_bridge.py`)
   - WebSocket server on new port (e.g., 8770)
   - Accepts OpenClaw realtime events
   - Forwards to SOL Voice Agent REST API (port 8769)
   - Streams TTS audio back as PCM16 chunks

2. **Modify OpenClaw Source** (when ready)
   - Add `"local"` to `talk.realtime.provider` enum
   - Add provider factory case for `"local"`
   - Point to `ws://localhost:8770/realtime`

3. **Test End-to-End**
   - Talk mode → WebSocket bridge → SOL Voice Agent → Cloned voice output

## Files
- Architecture analysis: `memory/2026-06-24-0942-talk-mode-local-voice.md`
- Config guide: `CONFIGURE_TALK_MODE.md`
- Skill root: `~/.openclaw/skills/sol-voice-agent/`

## Priority
🔴 CRITICAL — Next major build session

## Note
Green explicitly said: "not right now today but very soon" — respect this timeline.
