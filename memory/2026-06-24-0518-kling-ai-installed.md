# Session — 2026-06-24 05:18 CDT

## Kling AI Skill — Installed and Authorized

### What Was Done
1. Cloned klingai-tech/skills to `~/.openclaw/skills/kling-ai/`
2. Installed global CLI: `npm i -g @klingai/cli-global`
3. Completed OAuth login via `kling login`
4. Verified with `kling who_am_i` — authenticated and ready

### Installation Details
- **Region:** Global (kling.ai)
- **CLI Version:** kling-cli 0.1.1
- **Binary Path:** `/Users/philliplowe/.local/bin/kling`
- **Credentials:** `~/.kling/.credentials`
- **User ID:** 40702873

### Available Capabilities
- Text → Image (v3.0 Omni 4K, v3.0 2K, v2.1 2K, o1 2K)
- Image → Image (same models)
- Text → Video (v3.0 Omni 4K 3-15s, v3.0 4K, v3.0 Turbo, v2.6, v2.5, o1)
- Image → Video (same video models)
- File Upload for reference images
- Task polling via `query_tasks`

### Key Constraints (User Should Know)
- Generated URLs expire in **24 hours** — download promptly
- Tasks **cannot be canceled** once submitted
- Only **Personal workspace** credits (no Team support yet)
- **Bonus credits don't work** via CLI — only paid credits
- Rate limit: **5 QPS**
- Non-subscribers: 1 concurrent video task at a time

### Next Steps
- Skill is ready for use in future sessions
- No action needed until user requests image/video generation

---
**Session ended by user request.**
