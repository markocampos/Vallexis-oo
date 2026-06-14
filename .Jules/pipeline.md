## 2026-06-04 - SQLite Lock Contention
/ **Incident:** Background delivery worker and FastAPI endpoints experienced concurrency issues and lock timeouts due to default SQLite journaling mode.
/ **Learning:** SQLite defaults to a rollback journal which locks the entire database for writes, causing contention when a background process (like `worker.py`) constantly polls or updates the queue while web endpoints try to create new claims/products.
/ **Prevention:** Enabled SQLite Write-Ahead Logging (WAL) mode via SQLAlchemy engine connect events using `PRAGMA journal_mode=WAL` and `PRAGMA synchronous=NORMAL` to allow concurrent readers and writers.
## 2025-02-26 - Add /health endpoint
**Incident:** Lack of visibility into DB and worker status in production meant failures could go unnoticed.
**Learning:** Returning a 200 OK status code when the health check actually fails (e.g., due to an exception or DB error) defeats the purpose of the endpoint, as orchestrators rely on the HTTP status code.
**Prevention:** Always ensure health endpoints return a 5xx status code (e.g., 503) when internal dependencies or checks fail.
