## 2024-06-11 - PayMongo Webhooks
**Experiment:** Add PayMongo webhooks for subscription gating.
**Result:** Successfully added PayMongo webhooks with HMAC signature verification, checking subscription status to gate the products creation endpoint.
**Action:** Always verify PayMongo webhook signatures to ensure security and prevent unauthorized access.

## 2024-06-12 - Handle PayMongo invoice.payment_failed
**Experiment:** Handling failed invoice payments from PayMongo by using the `invoice.payment_failed` webhook event.
**Result:** Successfully downgrades seller subscription to `inactive` and sends them an email notification via Resend, encouraging them to resolve the payment.
**Action:** A failed payment is a conversation, not a cancellation. Continue to monitor recovery rates from these automated email nudges.
