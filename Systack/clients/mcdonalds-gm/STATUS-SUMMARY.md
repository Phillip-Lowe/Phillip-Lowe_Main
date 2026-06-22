# Percy Deployment — Status Summary

**Date:** 2026-06-05  
**Client:** Jacqueline, McDonald's General Manager  
**Status:** ⚠️ FUNCTIONAL BUT LIMITED (pending 8GB upgrade)

---

## What Works ✅

- **VPS deployed:** Vultr 4GB, Chicago (66.42.121.145)
- **Tailscale:** Connected (percy-mcdonalds.taildd162e.ts.net)
- **Devices:** iPhone 15 Plus ✅, Windows laptop ✅
- **OpenClaw Gateway:** Running, accessible via HTTPS
- **Ollama:** Installed with qwen2.5:3b model
- **Percy responds:** But with 2-minute+ delays due to RAM pressure

---

## What's Blocked ❌

**Root cause: 4GB RAM is insufficient for OpenClaw + model + identity files**

- Model with context loads → uses 3.1GB RAM
- System has 3.6GB total → only 500MB left for OS/gateway
- Result: Model swaps to disk, responds in 2+ minutes or times out
- Context overflow errors when identity files are too large

**Solution: Upgrade to 8GB VPS ($40/mo)**
- 7B model with 32K context fits comfortably
- Full identity files (SOUL.md, AGENTS.md, USER.md, etc.)
- Responds in 5-10 seconds
- No timeouts, no compaction errors

---

## For Jacqueline (Simple Explanation)

**Percy is installed and working.** You can chat with him from your phone or laptop.

**Right now he's a bit slow** (takes 1-2 minutes to respond) because the server needs more memory.

**Tomorrow:** Phillip will upgrade the server from 4GB to 8GB memory ($20 more per month). Then Percy will respond in seconds, just like a normal chat.

**Your cost:** $40/month for the server (was $20, now $40 with upgrade)
**Systack setup:** FREE (in exchange for testimonial)

---

## Access Instructions for Jacqueline

**From your phone or laptop:**
1. Make sure **Tailscale** app shows "Connected"
2. Open browser (Chrome, Safari, Edge)
3. Go to: **https://percy-mcdonalds.taildd162e.ts.net/**
4. No password needed — just click "Connect"
5. Type messages and wait for response

**If it doesn't load:**
- Check Tailscale is connected
- Try refreshing the page (pull down on phone, F5 on laptop)
- Try the direct IP: **https://100.98.244.115/**

---

## Next Steps (Tomorrow)

1. **Jacqueline checks email** for Vultr verification
2. **Phillip logs into Vultr console**
3. **Upgrade VPS from 4GB → 8GB** ($20 → $40/mo)
4. **Switch to qwen2.5:7b model** with 32K context
5. **Restore full identity files** (SOUL.md, AGENTS.md, etc.)
6. **Test response time** (target: 5-10 seconds)
7. **Train Jacqueline** on Percy's capabilities (Tier 0)

---

## Lessons Learned (For Future Clients)

| Lesson | Application |
|--------|-------------|
| 4GB VPS = demo only | Minimum 8GB for production |
| Model context determines RAM | 7B/32K needs 8GB, 3B/4K fits 4GB |
| Identity files add to system prompt | 1000 words = ~750 tokens |
| Context overflow = silent failure | Model doesn't respond, just spins |
| Tailscale Serve + HTTPS required | HTTP workarounds fail |
| Phone works before laptop | Always test phone first |
| Windows S mode blocks installs | Check before deploying |
| `/new` clears old session | Use when model config changes |
| Document working config exactly | Future clients need copy-paste setup |

---

## File References

- `DEPLOYMENT-PLAYBOOK.md` — Full troubleshooting guide
- `MODEL-CONTEXT-SIZING-GUIDE.md` — RAM/context math
- `FINAL-WORKING-CONFIG.md` — Exact config JSON
- `PERCY-DEPLOYMENT-PLAN.md` — Original deployment steps
- `memory/2026-06-04-percy-deployment.md` — Raw day 1 log

---

## Billing

| Item | Current | After Upgrade |
|------|---------|---------------|
| Vultr VPS | 4GB @ $20/mo | **8GB @ $40/mo** |
| Tailscale | Free | Free |
| OpenClaw | Free | Free |
| Ollama | Free | Free |
| Systack setup | Free (beta) | Free (beta) |
| **Total** | **$20/mo** | **$40/mo** |

---

## Contact

**For issues:** Phillip Lowe (Systack)
**For server:** Vultr console → https://console.vultr.com/
**For Tailscale:** https://login.tailscale.com/admin

---

*Deployment by Sol on behalf of Systack*
*2026-06-05*
