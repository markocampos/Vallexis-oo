## 2024-05-15 - PayMongo Webhooks Critical Fix
**Experiment:** Add PayMongo webhook validation per the guidelines: fail on unconfigured secret, check both `te` (test) and `li` (live) signatures via HMAC SHA256.
**Result:** Webhook signatures are correctly verified without failing on unconfigured secrets silently or restricting to only `te` signatures. It's now less than 50 lines.
**Action:** Always verify HMAC signatures for webhooks, check for `li` in live mode, and fail 500 securely if the secret is unconfigured.
