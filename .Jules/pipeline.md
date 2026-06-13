## 2026-06-04 - SQLite Lock Contention
/ **Incident:** Background delivery worker and FastAPI endpoints experienced concurrency issues and lock timeouts due to default SQLite journaling mode.
/ **Learning:** SQLite defaults to a rollback journal which locks the entire database for writes, causing contention when a background process (like `worker.py`) constantly polls or updates the queue while web endpoints try to create new claims/products.
/ **Prevention:** Enabled SQLite Write-Ahead Logging (WAL) mode via SQLAlchemy engine connect events using `PRAGMA journal_mode=WAL` and `PRAGMA synchronous=NORMAL` to allow concurrent readers and writers.

## 2026-06-13 - Missing End-to-End Health Checks
/ **Incident:** Production environment lacked visibility into database connectivity and background worker health, making silent failures (e.g., stalled delivery queues) invisible to orchestration or monitoring systems.
/ **Learning:** Without a dedicated health endpoint, infrastructure cannot automatically detect or mitigate service degradation beyond basic HTTP ping.
/ **Prevention:** Added a `/health` endpoint in `main.py` that explicitly queries the database (`SELECT 1`) and checks the `DeliveryQueue` for stalled jobs (pending > 10 minutes), enabling automated recovery and alerting.
