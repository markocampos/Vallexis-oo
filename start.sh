#!/bin/sh
# Start the background worker
python worker.py &

# Start the simple dashboard server on port 3000
python -m http.server 3000 --directory dashboard_ui &

# Start the docs UI server on port 4000
python -m http.server 4000 --directory docs_ui &

# Start the uvicorn app
uvicorn main:app --host 0.0.0.0 --port 8000
