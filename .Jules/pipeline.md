## 2026-06-04 - SQLite Lock Contention
/ **Incident:** Background delivery worker and FastAPI endpoints experienced concurrency issues and lock timeouts due to default SQLite journaling mode.
/ **Learning:** SQLite defaults to a rollback journal which locks the entire database for writes, causing contention when a background process (like `worker.py`) constantly polls or updates the queue while web endpoints try to create new claims/products.
/ **Prevention:** Enabled SQLite Write-Ahead Logging (WAL) mode via SQLAlchemy engine connect events using `PRAGMA journal_mode=WAL` and `PRAGMA synchronous=NORMAL` to allow concurrent readers and writers.
## 2023-10-25 - Silent Worker Failures & Missing Health Checks
/ **Incident:** Background delivery worker was failing silently without any monitoring or alerting, causing undetected delivery delays. There was no health check endpoint to monitor the overall application or database state.
/ **Learning:** Relying solely on the main application to handle background processing without separate observability leads to silent failures. We need a way to track the health of both the main application and its background workers.
/ **Prevention:** Added a `/health` endpoint to the FastAPI application that checks database connectivity and also checks for any stalled jobs in the delivery queue (older than 10 minutes) indicating a worker failure.
