# Session Log — 2026-06-22

## Lesson: Wait for Cloud-Init Before Assuming Failure

**Context:** Testing SAOS VPS provisioning pipeline. Created test VPS, SSH kept refusing connection.

**What Happened:**
1. Created test VPS (`saos-test002`) using provision script
2. Tried to SSH immediately — got "Connection refused"
3. Tried password login — got "Permission denied"
4. **Assumed failure** and spent 10+ minutes debugging auth issues
5. Eventually got in via pexpect and discovered cloud-init was still running
6. **Root cause:** Not failure — cloud-init was downloading Ollama model (~4.7GB)
7. Once I checked `cloud-init status` and `/var/log/saas-provision.log`, everything was actually working fine
8. Tailscale joined successfully: `100.95.242.89` — `saos-test002.tail573d57.ts.net`

**The Lesson:**
- **"Connection refused" on a fresh VPS ≠ failure**
- **"Permission denied" during cloud-init ≠ auth problem**
- Cloud-init can take 5-15 minutes (especially with large downloads)
- **Always check `cloud-init status` and `/var/log/cloud-init-output.log` before diagnosing**
- The provisioning log showed exactly what was happening — I just didn't look there first

**Prevention:**
After creating any VPS, always run in this order:
1. `cloud-init status` — Is it done?
2. `cat /var/log/saas-provision.log` — What step is it on?
3. Only THEN diagnose SSH/auth issues if those look wrong

**Related:** The `--wait` flag on `provision_vps.py` should check cloud-init status, not just Vultr instance status. Consider adding a cloud-init wait loop.

---
**Saved by user request:** "Save this in your memory this treaty has a learning lesson"
**Date:** 2026-06-22 06:39 CDT
