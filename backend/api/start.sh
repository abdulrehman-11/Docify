#!/bin/bash
# Render start script for backend API

echo "🚀 Starting Ether Clinic API..."
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
