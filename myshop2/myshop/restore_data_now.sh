#!/bin/bash
# Script to restore database data
# This can be run in Render Shell or locally

cd "$(dirname "$0")"

echo "🔄 Restoring database data..."

# First, create a superuser if needed
echo "📝 Creating superuser..."
python manage.py shell << EOF
from accounts.models import Customer
if not Customer.objects.filter(is_superuser=True).exists():
    Customer.objects.create_superuser(
        email='admin@example.com',
        password='admin123',
        username='admin'
    )
    print("✅ Superuser created: admin@example.com / admin123")
else:
    print("✅ Superuser already exists")
EOF

# Then import the data
echo ""
echo "📥 Importing data from database_export.json..."

if [ -f "database_export.json" ]; then
    python manage.py loaddata database_export.json
    echo "✅ Data imported successfully!"
elif [ -f "../database_export.json" ]; then
    python manage.py loaddata ../database_export.json
    echo "✅ Data imported successfully!"
else
    echo "❌ database_export.json not found!"
    echo "   Checked: ./database_export.json and ../database_export.json"
    exit 1
fi

echo ""
echo "🎉 Done! You can now log in and access the admin panel."

