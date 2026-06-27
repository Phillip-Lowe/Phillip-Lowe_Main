# Voicebox MCP Integration — Research Notes

**Date:** 2026-06-24 10:36 CDT
**Source:** Green directive + Voicebox docs

## MCP Config (From Voicebox)

```json
{
  "mcpServers": {
    "voicebox": {
      "url": "http://127.0.0.1:17493/mcp",
      "headers": {
        "X-Voicebox-Client-Id": "claude-code"
      }
    }
  }
}
```

## What This Means

Voicebox exposes an **MCP (Model Context Protocol)** server on port 17493. MCP is the same protocol OpenClaw uses for n8n integration. This lets Claude Code, Cursor, and other MCP-aware agents:

- Discover Voicebox tools (voice cloning, TTS, dictation)
- Call Voicebox functions programmatically
- Use Voicebox voices in agent workflows

## Possible Integration

### For OpenClaw
Add Voicebox MCP server to `~/.openclaw/openclaw.json`:

```json
"mcp": {
  "servers": {
    "voicebox": {
      "url": "http://127.0.0.1:17493/mcp",
      "headers": {
        "X-Voicebox-Client-Id": "openclaw"
      },
      "transport": "streamable-http"
    }
  }
}
```

Then OpenClaw agents could:
- List available voices in Voicebox
- Clone new voices on demand
- Generate TTS audio through Voicebox
- Dictate text anywhere

### For SOL Agent
SOL could expose a tool that:
1. Sends audio to Voicebox MCP → clones voice
2. Receives voice ID back
3. Uses that voice for Talk mode or notifications

## Why This Matters

Instead of building a custom OpenClaw realtime provider (hard), we could:
1. Use Voicebox MCP for voice cloning/management
2. Have Voicebox handle the TTS engine
3. Keep OpenClaw Talk mode using whatever provider works

Voicebox already has:
- 7 TTS engines (Qwen3-TTS, LuxTTS, Chatterbox, Kokoro, HumeAI TADA)
- Zero-shot voice cloning
- 23 languages
- Desktop app + MCP server
- WebSocket for streaming

## Next Steps

1. Verify Voicebox MCP is running (check port 17493)
2. List available tools via MCP
3. Test voice cloning through MCP
4. Integrate with OpenClaw mcp.servers config
5. Explore if Voicebox can replace our custom SOL Voice Agent for production use

## Files
- `~/.openclaw/skills/sol-voice-agent/` — Our custom stack
- `/Applications/Voicebox.app` — Voicebox desktop app

---

*Saved per "save this everywhere" directive*
