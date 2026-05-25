# White-Label Deployment Checklist

Use this checklist when deploying the order page for a **new client**.

---

## Pre-Deployment

- [ ] Fork or clone `utopia-deli-order` repo
- [ ] Create new repo under client name or your org
- [ ] Update `config.js` with client's brand details
- [ ] Replace `images/logo.png` with client's logo
- [ ] Replace product photos in `images/` with client's photos
- [ ] Update `menu-data.js` with client's menu, prices, modifiers
- [ ] Update `CNAME` file with client's custom domain
- [ ] Update DNS CNAME record at client's registrar

## GitHub Pages Setup

- [ ] Enable GitHub Pages in repo settings (Source: `main`, Folder: `/`)
- [ ] Verify `https://your-username.github.io/repo-name/` loads
- [ ] Add custom domain in Pages settings (or let CNAME file handle it)
- [ ] Wait for HTTPS certificate to provision (checkmark in Pages settings)
- [ ] Verify `https://order.clientdomain.com` loads

## Backend Wiring

- [ ] Set up n8n webhook or checkout server
- [ ] Configure SMTP for order confirmation emails
- [ ] Test order submission from frontend to backend
- [ ] Verify Square payment link generation
- [ ] Test complete flow: order → email → payment → confirmation

## Post-Deployment

- [ ] Test on iPhone (primary customer device)
- [ ] Test on Android
- [ ] Test cart functionality end-to-end
- [ ] Verify hours gate (closed/open messaging)
- [ ] Check that all images load correctly
- [ ] Confirm HTTPS lock icon in browser

---

## Client Handoff

- [ ] Provide client with admin dashboard URL (if applicable)
- [ ] Show client how to update menu in spreadsheet → sync to `menu-data.js`
- [ ] Document how to change hours in `config.js`
- [ ] Give client a one-page "how to view orders" guide

---

## Maintenance

- [ ] Schedule monthly menu price reviews
- [ ] Monitor GitHub Pages uptime (automatic, but verify)
- [ ] Check backend logs for failed orders
- [ ] Update product photos seasonally if needed
