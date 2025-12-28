# How to Load Data into SQLite Database

## Problem
When trying to load data from `database_export.json` into SQLite, you get errors like:
- `UNIQUE constraint failed: shop_categoryattribute.category_id, shop_categoryattribute.key`
- `NOT NULL constraint failed: accounts_address.customer_id`
- `FOREIGN KEY constraint failed`

## Solution

### Step 1: Fix Signals to Skip During loaddata

Edit `myshop2/myshop/shop/signals.py` and add `if kwargs.get("raw"): return` at the start of all signal handlers:

```python
@receiver(post_save, sender=Category)
def inherit_parent_attributes_for_new_category(sender, instance: Category, created, **kwargs):
    # When loading fixtures (loaddata) Django calls save(..., raw=True).
    # In that case we must not run any business logic or hit related fields.
    if kwargs.get("raw"):
        return
    
    # ... rest of signal code ...

@receiver(post_save, sender=CategoryAttribute)
def propagate_category_attribute_to_children(sender, instance: CategoryAttribute, created, **kwargs):
    # Skip during fixtures (loaddata)
    if kwargs.get("raw"):
        return
    
    # ... rest of signal code ...

@receiver(post_save, sender=AttributeValue)
def propagate_attribute_value_to_children(sender, instance: AttributeValue, created, **kwargs):
    # Skip during fixtures (loaddata)
    if kwargs.get("raw"):
        return
    
    # ... rest of signal code ...
```

**Why:** During `loaddata`, Django calls `save(..., raw=True)`. Your signals try to access related objects that don't exist yet, causing errors. The `raw` check skips signals during fixture loading.

---

### Step 2: Clean Export File and Load Data

Create a script to:
1. Remove duplicates (especially `CategoryAttribute`)
2. Remove problematic models (addresses, suppliers, wishlist, cart)
3. Fix foreign key references (set `supplier_id` to NULL)
4. Disable foreign key checks during load

**Script:**

```python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
import django
django.setup()

import json
from django.core.management import call_command
from django.db import connection

# Load export file
with open('../../database_export.json') as f:
    data = json.load(f)

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
print(f"✅ {len(unique)} objects ready to load")

# Save cleaned data
with open('temp_shop.json', 'w') as f:
    json.dump(unique, f)

# Disable foreign key checks (SQLite only)
with connection.cursor() as cursor:
    cursor.execute("PRAGMA foreign_keys = OFF")

try:
    # Load data
    call_command('loaddata', 'temp_shop.json', verbosity=1)
finally:
    # Re-enable foreign key checks
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = ON")

# Verify
from shop.models import Category, Product, ProductImage
c = Category.objects.count()
p = Product.objects.count()
pi = ProductImage.objects.count()
print(f"\n✅ Categories: {c}, Products: {p}, Images: {pi}")
```

---

### Step 3: Run the Script

```bash
cd "/Users/hesamoddinsaeedi/Desktop/best/register rate works/myshop2/myshop"
unset DATABASE_URL  # Use SQLite
python3 manage.py migrate --noinput
python3 <script_above>
```

---

### Step 4: Commit to Git

```bash
git add -f db.sqlite3
git commit -m "SQLite database with data loaded"
git push origin main
```

---

## Key Points

1. **Signals must check `raw`** - Prevents signals from running during `loaddata`
2. **Remove duplicates** - Especially `CategoryAttribute` by `(category, key)`
3. **Skip problematic models** - Addresses, suppliers, wishlist, cart have foreign key issues
4. **Fix foreign keys** - Set `supplier_id` to NULL for products
5. **Disable FK checks** - Use `PRAGMA foreign_keys = OFF` during load (SQLite only)
6. **Load essential models only** - Categories, products, images, attributes

---

## What Gets Loaded

✅ Categories (18)  
✅ Products (141)  
✅ Product Images (250)  
✅ Attributes  
✅ Category Attributes  
✅ Attribute Values  

❌ Addresses (foreign key issues)  
❌ Suppliers (not needed for shop)  
❌ Wishlist (foreign key issues)  
❌ Cart items (foreign key issues)  

---

## For Render Deployment

1. **Remove `DATABASE_URL`** from Render Environment (so it uses SQLite)
2. **Commit `db.sqlite3`** to git (already done)
3. **Redeploy** - Render will use the SQLite file with all your data

---

## Quick Reference

**Fix signals:**
```python
if kwargs.get("raw"):
    return
```

**Disable FK checks (SQLite):**
```python
cursor.execute("PRAGMA foreign_keys = OFF")
# ... load data ...
cursor.execute("PRAGMA foreign_keys = ON")
```

**Deduplicate CategoryAttribute:**
```python
unique_key = (category_id, key_value)
if unique_key not in seen:
    seen[unique_key] = True
    unique.append(obj)
```

