## 2026-06-04 - SQLite Lock Contention
/ **Incident:** Background delivery worker and FastAPI endpoints experienced concurrency issues and lock timeouts due to default SQLite journaling mode.
/ **Learning:** SQLite defaults to a rollback journal which locks the entire database for writes, causing contention when a background process (like `worker.py`) constantly polls or updates the queue while web endpoints try to create new claims/products.
/ **Prevention:** Enabled SQLite Write-Ahead Logging (WAL) mode via SQLAlchemy engine connect events using `PRAGMA journal_mode=WAL` and `PRAGMA synchronous=NORMAL` to allow concurrent readers and writers.
## 2024-05-23 - Add /health endpoint
**Incident:** The API was running in production without any health checks. This meant orchestration systems (like K8s or Docker Healthchecks) or reverse proxies (like Caddy/NGINX) couldn't tell if the application was actually capable of serving traffic or just hung. Furthermore, the background worker operates silently; if it dies, the only symptom is user complaints about missing emails.
**Learning:** A standard `/health` endpoint shouldn't just return 200 OK. It needs to actively probe critical dependencies like the database (`SELECT 1`) and verify background worker progress (checking for stale items in the queue) to provide a true picture of system health.
**Prevention:** Always implement a `/health` endpoint that checks DB connectivity and asynchronous worker status before deploying to production.
