# SAOS Dashboard Mobile Access Guide

**Document ID:** SYS-MOBILE-v1.0
**Version:** 1.0
**Status:** LIVE
**Prepared for:** SAOS Business & Enterprise Fleet Clients
**Prepared by:** Systack
**Builder:** SOL + ASSEMBLY
**Source System:** SAOS v2026.06
**Date:** June 25, 2026
**Support:** support@systack.net

---

## Mobile Dashboard Access Guide

**Access your SAOS dashboard from anywhere — iPhone, iPad, Android, any device with Tailscale.**

---

## 1. Requirements

- Tailscale installed and connected
- Modern mobile browser (Safari iOS 14+ or Chrome Android 90+)
- Your Client ID and PIN (provided by Systack)

---

## 2. iPhone / iPad Setup

### Step 1: Install Tailscale
1. Open App Store
2. Search "Tailscale"
3. Download and install
4. Open app and sign in with your Systack account

### Step 2: Connect to Your Network
1. In Tailscale app, toggle "Connect"
2. Wait for "Connected" status
3. Your device now has secure access to your SAOS server

### Step 3: Open Dashboard
1. Open Safari
2. Visit your dashboard URL (provided by Systack)
   - Example: `https://your-server.tail573d57.ts.net/dashboard/`
3. Enter your **Client ID** and **PIN**
4. Tap "Access Dashboard"

### Step 4: Add to Home Screen (Optional)
1. Tap Share button (square with arrow)
2. Scroll down and tap "Add to Home Screen"
3. Name it "SAOS Dashboard"
4. Now it works like an app — full screen, no browser chrome

---

## 3. Android Setup

### Step 1: Install Tailscale
1. Open Google Play Store
2. Search "Tailscale"
3. Download and install
4. Open app and sign in with your Systack account

### Step 2: Connect to Your Network
1. In Tailscale app, toggle "Connect"
2. Wait for "Connected" status
3. Your device now has secure access to your SAOS server

### Step 3: Open Dashboard
1. Open Chrome
2. Visit your dashboard URL (provided by Systack)
3. Enter your **Client ID** and **PIN**
4. Tap "Access Dashboard"

### Step 4: Add to Home Screen (Optional)
1. Tap menu (three dots)
2. Tap "Add to Home screen"
3. Name it "SAOS Dashboard"
4. Now it opens full screen, like a native app

---

## 4. Dashboard Navigation on Mobile

### Tab Bar (Top)
- Tap **☰** (hamburger menu) to open navigation tabs
- Tabs: 💬 Chat, 📊 Fleet Status, 📦 Services, ✅ Tasks, 📋 Activity, 📄 Docs

### Chat Sidebar
- Tap **☰** in chat header to open conversation list
- Tap "+ New Chat" to start a new conversation
- Tap any conversation to open it

### Input Area
- Type your message in the text box
- Tap **Send** button to send
- Messages appear in real-time (no refresh needed)

---

## 5. Troubleshooting

| Problem | Solution |
|---------|----------|
| "Can't reach server" | Check Tailscale is connected (toggle off/on) |
| "Invalid PIN" | Double-check your PIN. Contact support to reset if needed. |
| "Page not loading" | Ensure you're using `https://` not `http://` |
| "Layout looks broken" | Refresh page (pull down on Safari, tap refresh on Chrome) |
| "Buttons too small" | Pinch to zoom is disabled — use landscape mode for larger view |
| "Keyboard covers input" | Tap anywhere outside keyboard to dismiss, then tap input again |
| "Session expired" | Log in again. Sessions last 30 days of inactivity. |

---

## 6. Tips for Best Mobile Experience

- **Bookmark the dashboard** for one-tap access
- **Add to home screen** for full-screen app-like experience
- **Use landscape mode** for wider chat view
- **Keep Tailscale running** in background for instant access
- **Pull to refresh** if data seems stale
- **Tap and hold** on links to open in new tab

---

## 7. Security Notes

- **PIN never transmitted in plain text** — encrypted over HTTPS
- **Session tokens stored securely** in browser localStorage
- **Logout clears all sessions** — use if device is shared
- **No public access** — requires Tailscale connection
- **Auto-lock recommended** — set device passcode for extra security

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-25 | Initial release — iOS and Android setup, navigation guide, troubleshooting |

**Latest version:** https://systack.net/docs/client/SAOS-Dashboard-Mobile-Access-Guide-v1.0.pdf
