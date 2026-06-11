## 2024-06-11 - PayMongo Webhooks
**Experiment:** Add PayMongo webhooks for subscription gating.
**Result:** Successfully added PayMongo webhooks with HMAC signature verification, checking subscription status to gate the products creation endpoint.
**Action:** Always verify PayMongo webhook signatures to ensure security and prevent unauthorized access.
