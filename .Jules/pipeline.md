## 2026-06-04 - SQLite Lock Contention
/ **Incident:** Background delivery worker and FastAPI endpoints experienced concurrency issues and lock timeouts due to default SQLite journaling mode.
/ **Learning:** SQLite defaults to a rollback journal which locks the entire database for writes, causing contention when a background process (like `worker.py`) constantly polls or updates the queue while web endpoints try to create new claims/products.
/ **Prevention:** Enabled SQLite Write-Ahead Logging (WAL) mode via SQLAlchemy engine connect events using `PRAGMA journal_mode=WAL` and `PRAGMA synchronous=NORMAL` to allow concurrent readers and writers.

## 2026-06-09 - Missing /health endpoint
/ **Incident:** Unsupervised background worker failing silently or getting stuck, with no programmatic way to verify app/DB health or queue processing status.
/ **Learning:** Without a dedicated health check that verifies critical infrastructure (DB connectivity) and worker progress (stale tasks in queue), silent failures lead to missed SLAs and undetected downtime.
/ **Prevention:** Implemented a `/health` endpoint that runs a `SELECT 1` query against the database and checks `DeliveryQueue` for pending tasks older than 10 minutes, returning 503 if unhealthy.
