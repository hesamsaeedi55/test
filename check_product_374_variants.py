#!/usr/bin/env python
"""
Check variants for product 374 to diagnose the cart issue
"""
import os
import sys
import django

# Setup Django
sys.path.append('/Users/hesamoddinsaeedi/Desktop/best/register rate works/myshop2/myshop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
django.setup()

from shop.models import Product, ProductVariant

product_id = 374

try:
    product = Product.objects.get(id=product_id)
    print(f"✅ Product {product_id}: {product.name}")
    print(f"   Active: {product.is_active}")
    print(f"   Has variants: {product.has_variants() if hasattr(product, 'has_variants') else 'N/A'}")
    print()
    
    variants = ProductVariant.objects.filter(product_id=product_id).order_by('id')
    print(f"📦 Found {variants.count()} variants:")
    print()
    
    for variant in variants:
        print(f"   Variant ID: {variant.id}")
        print(f"   SKU: {variant.sku}")
        print(f"   Attributes: {variant.attributes}")
        print(f"   Price: {variant.price_toman} تومان")
        print(f"   Stock: {variant.stock_quantity}")
        print(f"   Active: {variant.is_active}")
        print(f"   Default: {variant.is_default}")
        print(f"   Distinctive: {variant.isDistinctive}")
        print()
    
    # Check for potential issues
    print("🔍 Checking for issues:")
    
    # Check for duplicate attributes
    attributes_seen = {}
    for variant in variants:
        attrs_str = str(sorted(variant.attributes.items()))
        if attrs_str in attributes_seen:
            print(f"   ⚠️  DUPLICATE ATTRIBUTES FOUND:")
            print(f"      Variant {variant.id} has same attributes as Variant {attributes_seen[attrs_str]}")
            print(f"      Attributes: {variant.attributes}")
        else:
            attributes_seen[attrs_str] = variant.id
    
    if not attributes_seen or len(attributes_seen) == variants.count():
        print("   ✅ All variants have unique attributes")
    
except Product.DoesNotExist:
    print(f"❌ Product {product_id} not found")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

