#!/bin/sh
# Start the background worker
python worker.py &
# Start the uvicorn app
uvicorn main:app --host 0.0.0.0 --port 8000
