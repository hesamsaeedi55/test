#!/usr/bin/env bash
# Build script for Render

set -o errexit

echo "================================"
echo "STARTING BUILD PROCESS"
echo "================================"

# We're already in myshop2/myshop/ due to rootDir in render.yaml
echo "Current directory: $(pwd)"
echo "Files here: $(ls -la)"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo ""
echo "🔄 Running migrations..."
python manage.py migrate --no-input

# Collect static files
echo ""
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

echo ""
echo "================================"
echo "✅ BUILD COMPLETE"
echo "================================"
