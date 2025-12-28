#!/usr/bin/env python
"""Load data from JSON export, skipping duplicates"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
django.setup()

from django.core.management import call_command
from django.core import serializers
import json

# Load the JSON file
with open('database_export.json', 'r') as f:
    data = json.load(f)

# Track what we've seen to avoid duplicates
seen = set()
unique_data = []

for obj in data:
    # Create a unique key for CategoryAttribute
    if obj['model'] == 'shop.categoryattribute':
        key = (obj['fields'].get('category'), obj['fields'].get('key'))
        if key in seen:
            continue
        seen.add(key)
    unique_data.append(obj)

# Write unique data to temp file
with open('database_export_unique.json', 'w') as f:
    json.dump(unique_data, f, indent=2)

# Load the unique data
call_command('loaddata', 'database_export_unique.json', verbosity=2)

print("✅ Data loaded successfully!")

