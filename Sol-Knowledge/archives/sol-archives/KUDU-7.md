# KUDU-7 — High-Leverage Operations Protocol

**Issued:** 2026-06-02 05:12 CDT  
**From:** User directive  
**Applies To:** All agents (SOL, CODY, PESSI, SAGE, and future agents)

---

## Core Principle

**Stop asking the user to do anything that is not high-leverage.** Treat everything as a learning experience. Save all learning experiences everywhere for all agents.

---

## What This Means

### Do NOT Ask The User To:
- Test something that I can test myself (browser automation, curl, local server)
- Verify a deployment that I can verify (check the live site, run the code)
- Confirm a fix that I can confirm (read the deployed file, test the flow)
- Provide information I can find (check git history, read files, search web)
- Make a decision when I have enough context to decide

### DO Take As Learning Experience:
- Every bug fix → document the root cause, the fix, and the verification
- Every deployment → document the process, the pitfalls, and the success path
- Every failed attempt → document what went wrong and how to avoid it next time
- Every new tool or API → document usage patterns and gotchas

---

## Saving Learning Experiences

### Where To Save:
1. **MEMORY.md** — Long-term, curated wisdom (main session only)
2. **memory/YYYY-MM-DD.md** — Raw daily logs
3. **AGENTS.md** — Agent behavior conventions and red lines
4. **SOUL.md** — Personality and approach (if it changes how we operate)
5. **TOOLS.md** — Environment-specific notes, workarounds, local setup details
6. **Skill files** — If a skill needs updating based on the experience
7. **Project docs** — README, ARCHITECTURE, DEPLOYMENT_GUIDE, etc.

### What To Save:
- **Root cause** — What actually caused the problem (not just symptoms)
- **Fix applied** — Exact code or config change
- **Verification method** — How we confirmed it worked
- **Pitfalls encountered** — What went wrong during the fix process
- **Process gaps** — Where the workflow broke down
- **Tool limitations** — What the tools couldn't do and workarounds

---

## This Session's Learning Experience

### The Bug: Sides Not Adding to Cart

**Symptom:** User could add sandwiches/specialties but no sides would add to cart.

**Root Cause:** The `addToCart(id)` function in `order.html` (inline JavaScript) used global state variables:
- `selectedModifiers` — populated only when clicking an item card
- `itemQty` — changed globally, not per-item

When clicking "Add to Order" directly (without clicking item card first), `selectedModifiers` contained stale data from previous selections. For items with `modifiers: {}` (empty), the code still tried to use stale modifiers, causing silent failures or wrong data.

**Deployed Site vs Local Code:** The deployed site at `order.theutopiadeli.com` serves `index.html` from `Phillip-Lowe/utopia-deli-order` GitHub Pages. The local `utopia-deli-revamp/` directory was never pushed to the remote repo. CODY fixed the local file but the deployed site remained broken.

**Fix Applied:**
```javascript
// OLD (broken — uses global state)
function addToCart(id) {
  const mods = Object.values(selectedModifiers);  // stale!
  const totalPrice = unitPrice * itemQty;           // stale!
  // ...
}

// NEW (fixed — reads from DOM per-item)
function addToCart(id) {
  const qtyInput = document.getElementById(`qty-${id}`);
  const qty = qtyInput ? parseInt(qtyInput.value, 10) || 1 : 1;
  
  const modsContainer = document.getElementById(`mods-${id}`);
  const activeModBtns = modsContainer?.querySelectorAll('.mod-btn.active') || [];
  
  const mods = [];
  activeModBtns.forEach(btn => {
    const group = btn.dataset.group;
    const code = btn.dataset.code;
    if (item.modifiers?.[group]) {
      const opt = item.modifiers[group].find(o => o.code === code);
      if (opt) mods.push(opt);
    }
  });
  // ...
}
```

**Pitfalls During Fix:**
1. Initially thought it was a DOM ID collision or category-specific bug — wasted time on wrong hypotheses
2. CODY fixed local `order-form.js` but deployed site uses inline script in `index.html` — fix didn't reach users
3. Git repo had no remote configured — had to add `origin` manually
4. GitHub Push Protection blocked push due to secret scanning in unrelated files (old commits with API keys in `memory/` and `SOL n8n templates/`)
5. Had to `git reset --hard origin/main` and apply fix cleanly to avoid pushing secrets

**Verification Method:**
- Browser automation to inspect live site DOM (`browser` tool with `act` + `evaluate`)
- Confirmed modifier buttons had `modBtnActiveCount: 0` globally
- Confirmed `addToCart` used old code on deployed site
- Pushed fix to GitHub Pages
- Verified push succeeded

**Process Gaps Identified:**
- No deployment pipeline — manual git push to GitHub Pages
- Local `utopia-deli-revamp/` is not the deployed directory — `index.html` at repo root is
- No staging environment to test before production
- Git history contains secrets in unrelated files — blocks all future pushes
- **Cloudflare tunnel unreliable** — home machine tunnel goes down frequently (sleep, network changes, crashes)

---

## Cloudflare Tunnel Reliability (05:55 CDT, 2026-06-02)

**Problem:** Tunnel `n8n.theutopiadeli.com` → `cfargotunnel.com` keeps going down after working initially.

**Root Causes Learned:**
1. **Computer goes to sleep** — Home machine sleeps, tunnel disconnects
2. **Network change** — WiFi drops, IP changes, tunnel loses connection
3. **Cloudflared crashes** — Daemon stops and doesn't auto-restart
4. **No systemd service** — If not installed as a service, it won't survive reboots/crashes
5. **Reinstalling n8n** — If n8n was reinstalled, the tunnel config might have been lost or the service disabled

**Fix Applied:**
- Restarted tunnel at 05:55 CDT
- But user notes "it keeps going down"

**Permanent Solutions:**
- Install cloudflared as systemd service with auto-restart
- Or use a VPS instead of home machine
- Or use a more reliable tunnel provider

**What Reinstalling n8n Does NOT Do:**
- Reinstalling n8n does NOT affect the tunnel directly
- But if reinstalling meant reconfiguring the machine, the tunnel service might have been disabled
- The tunnel UUID (`fc0bcffc-e6da-45db-a3ee-598bd847e9e5`) is persistent
- But the tunnel process must be running

---

## Cloudflare Tunnel Reliability — Updated (05:55-07:15 CDT, 2026-06-02)

**Problem:** Tunnel `n8n.systack.net` → `cfargotunnel.com` kept going down.

**Root Causes Learned:**
1. **Computer goes to sleep** — Home machine sleeps, tunnel disconnects
2. **Network change** — WiFi drops, IP changes, tunnel loses connection
3. **Cloudflared crashes** — Daemon stops and doesn't auto-restart
4. **No systemd service** — If not installed as a service, it won't survive reboots/crashes
5. **Reinstalling n8n** — If n8n was reinstalled, the tunnel config might have been lost or the service disabled
6. **DNS misconfiguration** — Manual CNAME to `cfargotunnel.com` subdomain returns broken IPv6 only. Must use `cloudflared tunnel route dns` to create proper proxied A records
7. **LaunchDaemon misconfiguration** — Original plist didn't specify which tunnel to run (missing UUID and config path)

**Fix Applied:**
- Fixed LaunchDaemon to specify tunnel UUID and config path
- Deleted broken CNAME, used `cloudflared tunnel route dns` to create proper DNS
- Set up auto-restart monitor (`restart-tunnel.sh` + LaunchAgent)
- Set `N8N_SECURE_COOKIE=false` in n8n start script

**Permanent Solutions:**
- Install cloudflared as systemd service with auto-restart (DONE)
- Or use a VPS instead of home machine
- Or use a more reliable tunnel provider

**What Reinstalling n8n Does NOT Do:**
- Reinstalling n8n does NOT affect the tunnel directly
- But if reinstalling meant reconfiguring the machine, the tunnel service might have been disabled
- The tunnel UUID (`fc0bcffc-e6da-45db-a3ee-598bd847e9e5`) is persistent
- But the tunnel process must be running

**DNS Fix Process:**
- `cfargotunnel.com` subdomains only return IPv6 and are unreliable
- Must use `cloudflared tunnel route dns <tunnel-name> <hostname>` to create proper A records
- The CNAME approach (manually pointing to UUID.cfargotunnel.com) is deprecated/broken

**User Decision:** Accept the loop for now (free/local), set up monitoring to minimize downtime

---

## Agent Conventions Updated

### From AGENTS.md (already exists):
> **Be resourceful before asking.** Try to figure it out. Read the file. Check the context. Search for it. _Then_ ask if you're stuck. The goal is to come back with answers, not questions.

### KUDU-7 Addition:
> **Never ask the user to verify what you can verify yourself.** If a fix is deployed, check the live site. If code is changed, read the file. If a build succeeded, check the output. Treat every obstacle as a learning experience to document, not a question to ask.

---

## Files Updated With This Learning
- `memory/2026-06-02.md` — Daily log
- `MEMORY.md` — Curated wisdom (long-term)
- `AGENTS.md` — Behavior conventions
- `KUDU-7.md` — This file (reference for all agents)

---

## Session 2 — 16:10 CDT: The Complete Fix Log

### Bugs Fixed Today
1. **Cart add bug** — stale global state + missing `MENU.sides` in `findItem`
2. **Checkout hang** — wrong endpoint (`theutopiadeli.com` vs `systack.net`), broken DNS, no timeout
3. **n8n validation errors** — wrong field names, tax rounding, price in cents vs dollars
4. **JavaScript parse error** — duplicate `const frontend_total_cents` broke entire site
5. **City/county fields** — removed from checkout form

### Key Learning: Price Format Matters
The n8n `Generate Order ID` node builds Square API body:
```javascript
line_items: items.map(item => ({
  name: item.name,
  quantity: String(item.qty),
  base_price_money: {
    amount: Math.round(item.price * 100),  // ← price MUST be in DOLLARS
    currency: "USD"
  }
}))
```
So `item.price` MUST be `13.00` (dollars), NOT `1300` (cents).

### Key Learning: DNS for Cloudflare Tunnels
- `cfargotunnel.com` subdomains only return IPv6 and are unreliable
- Must use `cloudflared tunnel route dns <tunnel-name> <hostname>` to create proper A records
- The CNAME approach (manually pointing to UUID.cfargotunnel.com) is deprecated/broken

### Key Learning: Deployed Site ≠ Local Code
- GitHub Pages serves `index.html` at repo root
- Local `utopia-deli-revamp/` files are NOT deployed
- Always verify live site after push, not just local files

---

## Related
- [AGENTS.md](/reference/AGENTS.default)
- [MEMORY.md](/memory/MEMORY.md)
- [SOUL.md](/SOUL.md)
