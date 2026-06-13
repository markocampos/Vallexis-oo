## 2024-06-11 - PayMongo Webhooks
**Experiment:** Add PayMongo webhooks for subscription gating.
**Result:** Successfully added PayMongo webhooks with HMAC signature verification, checking subscription status to gate the products creation endpoint.
**Action:** Always verify PayMongo webhook signatures to ensure security and prevent unauthorized access.

## 2024-05-18 - Checkout Link Generation API
**Experiment:** Added an endpoint to generate PayMongo checkout links on-the-fly for products.
**Result:** Successfully integrates the PayMongo link API using `httpx` and generates URLs for the frontend without storing checkout details in the database.
**Action:** Use this to convert buyers smoothly instead of hardcoded payment links. Ensure we use the proper base64-encoded secret key format (`sk_test_xxx:`) in authorization headers.
