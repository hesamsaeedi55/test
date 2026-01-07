#!/usr/bin/env python3
"""
Fix variants that have price_toman = 0 by setting them to their product's base price
"""
import os
import sys
import django

# Setup Django
sys.path.append('/Users/hesamoddinsaeedi/Desktop/best/register rate works/myshop2/myshop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
django.setup()

from shop.models import ProductVariant, Product
from decimal import Decimal

print("🔍 Finding variants with price_toman = 0...")

# Find all variants with 0 price
zero_price_variants = ProductVariant.objects.filter(price_toman=0, is_active=True).select_related('product')

print(f"Found {zero_price_variants.count()} variants with 0 price")
print()

if zero_price_variants.count() == 0:
    print("✅ No variants found with 0 price. All good!")
    sys.exit(0)

updated_count = 0
skipped_count = 0

for variant in zero_price_variants:
    product = variant.product
    product_price = product.price_toman
    
    print(f"Variant ID {variant.id}: {variant.sku}")
    print(f"  Product: {product.name} (ID: {product.id})")
    print(f"  Product price: {product_price} تومان")
    print(f"  Current variant price: {variant.price_toman} تومان")
    print(f"  Attributes: {variant.attributes}")
    
    if product_price and product_price > 0:
        variant.price_toman = product_price
        variant.save()
        print(f"  ✅ Updated to {product_price} تومان")
        updated_count += 1
    else:
        print(f"  ⚠️  Skipped (product price is also 0 or invalid)")
        skipped_count += 1
    
    print()

print("="*50)
print(f"✅ Updated {updated_count} variants")
print(f"⚠️  Skipped {skipped_count} variants (product price also 0)")
print()

# Show product 374 specifically
print("="*50)
print("Checking product 374 specifically:")
print("="*50)
product_374_variants = ProductVariant.objects.filter(product_id=374).order_by('id')
product_374 = Product.objects.get(id=374)

print(f"Product 374: {product_374.name}")
print(f"Base price: {product_374.price_toman} تومان")
print()

for v in product_374_variants:
    print(f"Variant {v.id}: {v.sku}")
    print(f"  Price: {v.price_toman} تومان")
    print(f"  Attributes: {v.attributes}")
    print()

