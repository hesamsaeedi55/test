#!/usr/bin/env python
"""Load export in strict dependency order"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
django.setup()

from django.core.management import call_command

# Load export
with open('../../database_export.json') as f:
    data = json.load(f)

print(f"📖 Loaded {len(data)} objects")

# Remove duplicates first
seen = set()
unique_data = []
for obj in data:
    model = obj['model']
    fields = obj['fields']
    
    if model == 'shop.categoryattribute':
        key = ('categoryattribute', fields.get('category'), fields.get('key'))
    else:
        key = (model, obj.get('pk'))
    
    if key in seen:
        continue
    seen.add(key)
    unique_data.append(obj)

print(f"   After dedup: {len(unique_data)} objects")

# Group by model
by_model = {}
for obj in unique_data:
    model = obj['model']
    if model not in by_model:
        by_model[model] = []
    by_model[model].append(obj)

# Load in strict order
load_order = [
    'sites.site',
    'contenttypes.contenttype',
    'auth.permission', 
    'accounts.customer',  # MUST be before addresses
    'accounts.address',  # After customers
    'shop.category',  # Before products
    'shop.attribute',
    'shop.attributevalue',
    'shop.categoryattribute',  # After categories
    'shop.product',  # After categories
    'shop.productimage',  # After products
    'shop.productattribute',  # After products
]

total_loaded = 0
for model in load_order:
    if model not in by_model:
        continue
    
    model_data = by_model[model]
    temp_file = f'temp_{model.replace(".", "_")}.json'
    
    with open(temp_file, 'w') as f:
        json.dump(model_data, f)
    
    try:
        call_command('loaddata', temp_file, verbosity=1)
        total_loaded += len(model_data)
        print(f"✅ {model}: {len(model_data)} loaded")
    except Exception as e:
        print(f"❌ {model}: Failed - {str(e)[:150]}")
    
    os.remove(temp_file)

# Load remaining
remaining = {k: v for k, v in by_model.items() if k not in load_order}
for model, model_data in remaining.items():
    temp_file = f'temp_{model.replace(".", "_")}.json'
    with open(temp_file, 'w') as f:
        json.dump(model_data, f)
    try:
        call_command('loaddata', temp_file, verbosity=0, ignorenonexistent=True)
        total_loaded += len(model_data)
    except:
        pass
    os.remove(temp_file)

print(f"\n✅ Total loaded: {total_loaded} objects")

