#!/usr/bin/env python
"""
Load data from database_export.json into SQLite database
Run: python3 load_data_to_sqlite.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
django.setup()

import json
from django.core.management import call_command
from django.db import connection

def load_data_to_sqlite():
    """Load and clean data from export file into SQLite"""
    
    # Load export file
    export_file = '../../database_export.json'
    if not os.path.exists(export_file):
        print(f"❌ Export file not found: {export_file}")
        return
    
    print("📖 Loading export file...")
    with open(export_file) as f:
        data = json.load(f)
    
    print(f"   Total objects: {len(data)}")
    
    # Essential shop models only
    essential = [
        'sites.site',
        'contenttypes.contenttype',
        'auth.permission',
        'accounts.customer',
        'shop.categorygender',
        'shop.categorygroup',
        'shop.category',
        'shop.attribute',
        'shop.categoryattribute',
        'shop.attributevalue',
        'shop.product',
        'shop.productimage',
    ]
    
    # Separate CategoryAttribute for deduplication
    ca_entries = [o for o in data if o['model'] == 'shop.categoryattribute']
    other_essential = [o for o in data if o['model'] in essential and o['model'] != 'shop.categoryattribute']
    
    print(f"   CategoryAttribute entries: {len(ca_entries)}")
    print(f"   Other essential entries: {len(other_essential)}")
    
    # Deduplicate CategoryAttribute by (category, key)
    ca_seen = {}
    unique_ca = []
    for obj in ca_entries:
        cat = obj['fields'].get('category')
        key = obj['fields'].get('key')
        # Handle natural keys (lists)
        if isinstance(cat, list):
            cat = cat[0] if cat else None
        unique_key = (str(cat) if cat else None, str(key) if key else None)
        if unique_key not in ca_seen:
            ca_seen[unique_key] = True
            unique_ca.append(obj)
    
    print(f"   Unique CategoryAttribute: {len(unique_ca)} (removed {len(ca_entries) - len(unique_ca)} duplicates)")
    
    # Process other models - remove supplier_id from products
    seen = {}
    unique_other = []
    for obj in other_essential:
        # Remove supplier_id from products (suppliers not loaded)
        if obj['model'] == 'shop.product' and 'supplier' in obj['fields']:
            obj['fields']['supplier'] = None
        key = (obj['model'], obj.get('pk'))
        if key not in seen:
            seen[key] = True
            unique_other.append(obj)
    
    # Combine
    unique = unique_other + unique_ca
    print(f"✅ Cleaned: {len(unique)} objects ready to load")
    
    # Save cleaned data
    temp_file = 'temp_shop_clean.json'
    with open(temp_file, 'w') as f:
        json.dump(unique, f, indent=2)
    
    # Disable foreign key checks (SQLite only)
    print("\n📥 Loading data into SQLite...")
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = OFF")
    
    try:
        # Load data
        call_command('loaddata', temp_file, verbosity=1)
        print("✅ Data loaded successfully!")
    finally:
        # Re-enable foreign key checks
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = ON")
        
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    # Verify
    from shop.models import Category, Product, ProductImage
    c = Category.objects.count()
    p = Product.objects.count()
    pi = ProductImage.objects.count()
    print(f"\n✅ Final counts:")
    print(f"   Categories: {c}")
    print(f"   Products: {p}")
    print(f"   Product Images: {pi}")

if __name__ == '__main__':
    load_data_to_sqlite()

