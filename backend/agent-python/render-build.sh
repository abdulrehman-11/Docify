#!/bin/bash
set -e

echo "🔧 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗄️ Running database migrations..."
alembic upgrade head

echo "✅ Build complete!"
