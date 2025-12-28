#!/usr/bin/env python
"""
Import database data from JSON export
Run this in Render Shell after the export file is available
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
django.setup()

from django.core.management import call_command

def import_data():
    """Import data from database_export.json"""
    export_file = '../../database_export.json'
    
    if not os.path.exists(export_file):
        print(f"❌ File not found: {export_file}")
        print("Make sure database_export.json is in the repository root")
        return
    
    print("🔄 Importing data from database_export.json...")
    print("⚠️  This will add data to your database")
    print("⚠️  Make sure migrations are up to date first!")
    
    try:
        # Run migrations first
        print("\n📦 Running migrations...")
        call_command('migrate', verbosity=1)
        
        # Import data
        print("\n📥 Importing data...")
        call_command('loaddata', export_file, verbosity=2)
        
        print("\n✅ Data import completed!")
        print("📊 Check your API to verify data is restored")
        
    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import_data()

