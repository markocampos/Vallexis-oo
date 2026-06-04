## 2026-06-04 - SQLite Lock Contention
/ **Incident:** Background delivery worker and FastAPI endpoints experienced concurrency issues and lock timeouts due to default SQLite journaling mode.
/ **Learning:** SQLite defaults to a rollback journal which locks the entire database for writes, causing contention when a background process (like `worker.py`) constantly polls or updates the queue while web endpoints try to create new claims/products.
/ **Prevention:** Enabled SQLite Write-Ahead Logging (WAL) mode via SQLAlchemy engine connect events using `PRAGMA journal_mode=WAL` and `PRAGMA synchronous=NORMAL` to allow concurrent readers and writers.
