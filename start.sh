#!/bin/bash
echo "🚀 Starting Eliza on Render..."
gunicorn eliza_api:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
