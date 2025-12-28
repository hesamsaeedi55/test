#!/usr/bin/env python
"""Load export file, skipping errors"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
django.setup()

from django.core.management import call_command
from django.core import serializers
from django.db import transaction

# Load export file
with open('../../database_export.json') as f:
    data = json.load(f)

print(f"📖 Loaded {len(data)} objects from export")

# Group by model
by_model = {}
for obj in data:
    model = obj['model']
    if model not in by_model:
        by_model[model] = []
    by_model[model].append(obj)

# Load in dependency order - categories need to be loaded by parent first
# Sort categories by parent (None/null first, then by parent_id)
if 'shop.category' in by_model:
    categories = by_model['shop.category']
    # Separate root categories (no parent) from child categories
    root_cats = [c for c in categories if not c['fields'].get('parent')]
    child_cats = [c for c in categories if c['fields'].get('parent')]
    # Sort child categories by parent_id so parents load first
    child_cats.sort(key=lambda x: x['fields'].get('parent', 0))
    by_model['shop.category'] = root_cats + child_cats

# Load in dependency order
load_order = [
    'sites.site',
    'contenttypes.contenttype', 
    'auth.permission',
    'accounts.customer',
    'accounts.address',
    'shop.category',  # Will load root categories first, then children
    'shop.attribute',
    'shop.attributevalue',
    'shop.categoryattribute',  # After categories exist
    'shop.product',  # After categories exist
    'shop.productimage',  # After products exist
    'shop.productattribute',  # After products and attributes exist
]

loaded_count = 0
failed_count = 0

for model in load_order:
    if model not in by_model:
        continue
    
    model_data = by_model[model]
    print(f"📥 Loading {len(model_data)} {model} objects...")
    
    # Save to temp file
    temp_file = f'temp_{model.replace(".", "_")}.json'
    with open(temp_file, 'w') as f:
        json.dump(model_data, f)
    
    # Try to load
    try:
        call_command('loaddata', temp_file, verbosity=0)
        loaded_count += len(model_data)
        print(f"   ✅ Loaded {len(model_data)}")
    except Exception as e:
        failed_count += len(model_data)
        print(f"   ⚠️  Failed: {str(e)[:100]}")
    
    # Clean up
    os.remove(temp_file)

# Load remaining models
remaining = {k: v for k, v in by_model.items() if k not in load_order}
if remaining:
    print(f"\n📥 Loading {len(remaining)} remaining model types...")
    for model, model_data in remaining.items():
        temp_file = f'temp_{model.replace(".", "_")}.json'
        with open(temp_file, 'w') as f:
            json.dump(model_data, f)
        try:
            call_command('loaddata', temp_file, verbosity=0, ignorenonexistent=True)
            loaded_count += len(model_data)
        except:
            failed_count += len(model_data)
        os.remove(temp_file)

print(f"\n✅ Summary: Loaded {loaded_count}, Failed {failed_count}")

