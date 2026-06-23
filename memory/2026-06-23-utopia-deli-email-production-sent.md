# Session — 2026-06-23 ~10:30 CDT
## Utopia Deli Email Campaign — PRODUCTION DEPLOYMENT

### What Happened
- Successfully sent test email earlier (10:28 CDT)
- **Sent full campaign to actual recipients** (10:30 CDT)
- **Issue encountered:** "Sent too many" error toward the end
- **Fix:** Changed n8n node delay/wait from 10 seconds → 20 seconds between sends
- Campaign completed successfully after fix

### Production Lesson
**SMTP rate limiting is real.** Even with modest list sizes (300+ contacts), Gmail/SMTP will throttle if emails send too fast.
- **Old setting:** 10 second delay between emails
- **New setting:** 20 second delay between emails
- **Result:** No more "sent too many" errors

### What Still Works
- Email content renders correctly
- All links trackable with UTM parameters
- Unsubscribe footer present
- Contact list pulling from Postgres correctly

### Files
- `email-campaign/utopia-deli-5day-campaign.js` — Live code in n8n

---
**Status:** PRODUCTION LIVE — Campaign sent successfully
**Tested:** Yes — full recipient list
**Note:** Monitor next send for any additional throttling
