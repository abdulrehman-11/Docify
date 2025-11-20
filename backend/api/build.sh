#!/bin/bash
# Render build script for backend API

echo "🔧 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build complete!"
