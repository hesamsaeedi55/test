#!/usr/bin/env python
"""
Export data from local SQLite database and prepare for PostgreSQL import
Run this locally to export your data, then import it to Render database
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'myshop2', 'myshop'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings

def export_data():
    """Export all data from local SQLite database"""
    print("🔄 Exporting data from local SQLite database...")
    
    # Change to Django project directory
    os.chdir(os.path.join(os.path.dirname(__file__), 'myshop2', 'myshop'))
    
    # Export all data
    output_file = 'database_export.json'
    
    try:
        print("📦 Exporting all apps data...")
        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--indent', '2',
            '--output', output_file,
            exclude=['contenttypes', 'auth.Permission', 'sessions.Session']
        )
        
        print(f"✅ Data exported to: {output_file}")
        print(f"📊 File size: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
        print("\n📤 Next steps:")
        print("1. Upload this file to Render (or copy the content)")
        print("2. In Render Shell, run:")
        print(f"   python manage.py loaddata {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    export_data()

