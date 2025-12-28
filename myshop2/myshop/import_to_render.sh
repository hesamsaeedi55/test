#!/bin/bash
# Script to import local SQLite data to Render PostgreSQL

set -e  # Exit on error

cd "$(dirname "$0")"

echo "🔄 Starting import process..."

# Step 1: Create dump from local SQLite
echo ""
echo "📦 Step 1: Creating dump from local SQLite database..."
unset DATABASE_URL  # Use local SQLite
python3 manage.py dumpdata \
  --exclude auth.permission \
  --exclude contenttypes \
  --exclude sessions \
  --exclude admin.logentry \
  --natural-primary --natural-foreign \
  > db_dump.json

if [ ! -f "db_dump.json" ]; then
    echo "❌ Failed to create db_dump.json"
    exit 1
fi

echo "✅ Dump created: db_dump.json ($(du -h db_dump.json | cut -f1))"

# Step 2: Point to Render Postgres
echo ""
echo "📡 Step 2: Connecting to Render PostgreSQL..."
export DATABASE_URL="postgresql://test:z8ocUc8F8eQxmOGSWG4XxsGSKJ5SAK0q@dpg-d50jummr433s73dbn8p0-a.oregon-postgres.render.com:5432/test_q2q6?sslmode=require"

# Step 3: Fake SQLite-only migrations
echo ""
echo "🔧 Step 3: Handling SQLite-only migrations..."
python3 manage.py migrate accounts 0008 --fake 2>/dev/null || echo "   (0008 already handled)"
python3 manage.py migrate accounts 0009 --fake 2>/dev/null || echo "   (0009 already handled)"

# Step 4: Run all migrations
echo ""
echo "📋 Step 4: Running migrations..."
python3 manage.py migrate --noinput

# Step 5: Load data
echo ""
echo "📥 Step 5: Loading data into Render PostgreSQL..."
python3 manage.py loaddata db_dump.json

echo ""
echo "✅ Import complete!"
echo ""
echo "Next steps:"
echo "1. Make sure DATABASE_URL is set in Render Web Service Environment"
echo "2. Redeploy your Render service"
echo "3. Visit https://test-0yq3.onrender.com"

