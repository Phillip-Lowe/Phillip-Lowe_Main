# Voicebox MCP Server — Research

**Date:** 2026-06-24 10:36 CDT
**Trigger:** Green directive "save this everywhere"

## MCP Config

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

## Status

- Voicebox MCP server not responding on port 17493 yet
- Likely needs Voicebox app to fully initialize or enable MCP in settings

## Why This Matters

Voicebox MCP could provide an easier path than building custom OpenClaw provider:
- Already has 7 TTS engines
- Zero-shot voice cloning via MCP
- Desktop app handles heavy lifting
- Could integrate with OpenClaw's existing MCP framework

## Integration Path

1. Add Voicebox to OpenClaw mcp.servers config
2. SOL agent can call Voicebox tools (clone voice, list voices, generate TTS)
3. Use Voicebox as the TTS engine instead of Coqui/Kokoro
4. Keep our SOL Voice Agent as fallback or for specific integrations

## Comparison

| Approach | Effort | Quality | Integration |
|----------|--------|---------|-------------|
| Custom OpenClaw provider | High (fork core) | Best | Native Talk mode |
| Voicebox MCP | Low (config only) | Excellent | Via MCP tools |
| Current stt-tts | Working | Generic | Talk mode broken |

## Saved Per RULE 8

User said "save this everywhere" — persisted to:
- `memory/2026-06-24-1036-voicebox-mcp-research.md`
- `VOICEBOX_MCP_SETUP.md`
- AGENTS.md TODO (realtime voice entry updated)

## Green's Note

"Maybe we can come up with some voices there or something" — exploring Voicebox as voice source for SOL.
