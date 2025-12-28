#!/usr/bin/env python
"""Fix duplicate entries in export and load data"""
import os
import sys
import django
import json
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
django.setup()

from django.core.management import call_command

# Load the JSON file
print("📖 Loading export file...")
with open('database_export.json', 'r') as f:
    data = json.load(f)

print(f"   Original objects: {len(data)}")

# Track duplicates by (model, unique_key)
seen = defaultdict(set)
unique_data = []
skipped = 0

for obj in data:
    model = obj['model']
    fields = obj['fields']
    pk = obj.get('pk')
    
    # Create unique key based on model type
    if model == 'shop.categoryattribute':
        key = (fields.get('category'), fields.get('key'))
    elif model == 'shop.productattribute':
        key = (fields.get('product'), fields.get('attribute'), fields.get('value'))
    else:
        # For other models, use pk as key
        key = pk
    
    # Check if we've seen this before
    if key in seen[model]:
        skipped += 1
        continue
    
    seen[model].add(key)
    unique_data.append(obj)

print(f"   Unique objects: {len(unique_data)}")
print(f"   Skipped duplicates: {skipped}")

# Write unique data
print("💾 Writing fixed export file...")
with open('database_export_fixed.json', 'w') as f:
    json.dump(unique_data, f, indent=2)

# Load the fixed data
print("📥 Loading data into database...")
call_command('loaddata', 'database_export_fixed.json', verbosity=1)

print("✅ Done!")

