## 2024-05-18 - PayMongo Webhooks and Subscription Gating
**Experiment:** Integrate PayMongo webhooks for subscription management and gate product creation behind active subscriptions.
**Result:** Successfully added `subscription.activated` and `invoice.payment_failed` webhook handlers with HMAC SHA-256 signature verification. Product creation is now restricted to sellers with active subscriptions.
**Action:** Always ensure secure signature verification for webhooks to prevent spoofing and properly downgrade accounts upon payment failure.
