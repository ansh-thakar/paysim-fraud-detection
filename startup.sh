#!/bin/bash

# Start FastAPI backend on port 8000 in background
uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# Wait briefly for FastAPI to initialize
sleep 2

# Start Streamlit frontend on port 7860 in foreground
streamlit run frontend/app.py \
    --server.port=7860 \
    --server.address=0.0.0.0 \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
