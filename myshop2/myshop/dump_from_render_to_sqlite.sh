#!/bin/bash
# Dump from Render PostgreSQL to local SQLite

cd "$(dirname "$0")"

echo "📥 Dumping from Render PostgreSQL..."

# Point to Render Postgres
export DATABASE_URL="postgresql://test:z8ocUc8F8eQxmOGSWG4XxsGSKJ5SAK0q@dpg-d50jummr433s73dbn8p0-a.oregon-postgres.render.com:5432/test_q2q6?sslmode=require"

# Dump to JSON
python3 manage.py dumpdata \
  --exclude auth.permission \
  --exclude contenttypes \
  --exclude sessions \
  --exclude admin.logentry \
  --natural-primary --natural-foreign \
  > render_dump.json

echo "✅ Dump created: render_dump.json"

# Switch to SQLite
unset DATABASE_URL

# Recreate SQLite
rm -f db.sqlite3
python3 manage.py migrate --noinput

# Load into SQLite
python3 manage.py loaddata render_dump.json

echo "✅ Data loaded into SQLite!"
python3 manage.py shell -c "from shop.models import Category, Product; print(f'Categories: {Category.objects.count()}, Products: {Product.objects.count()}')"

