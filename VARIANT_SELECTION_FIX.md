# Variant Selection Fix

## Problem
When adding products with variants to cart, the wrong variant was being added. For example:
- Product 374 (جکت پاییزی)
- Selecting: **Black (مشکی), Size M** 
- Result: **Black (مشکی), Size L** was added instead ❌

## Root Cause
The client app's variant selection logic was sending the wrong `variant_id` to the backend. The backend itself was working correctly.

## Solution
Created a new API endpoint that finds the correct variant_id based on attributes.

### New API Endpoint

**Endpoint:** `POST /shop/api/customer/find-variant/`

**Request Body:**
```json
{
  "product_id": 374,
  "attributes": {
    "color": "مشکی",
    "size": "M"
  }
}
```

**Success Response (200):**
```json
{
  "variant_id": 196,
  "sku": "جکت-341",
  "price_toman": 500000.0,
  "stock_quantity": 10,
  "attributes": {
    "color": "مشکی",
    "size": "M"
  },
  "is_active": true,
  "is_default": false
}
```

**Error Response (404):**
```json
{
  "error": "No variant found matching the requested attributes",
  "requested_attributes": {
    "color": "مشکی",
    "size": "XS"
  },
  "available_variants": [
    {
      "id": 153,
      "sku": "DAS-481",
      "attributes": {"color": "مشکی", "size": "L"},
      "price_toman": 500000.0,
      "stock_quantity": 8
    },
    {
      "id": 196,
      "sku": "جکت-341",
      "attributes": {"color": "مشکی", "size": "M"},
      "price_toman": 500000.0,
      "stock_quantity": 10
    }
  ]
}
```

## How to Use in Client App

### Step 1: Get Available Variants
```swift
// GET /shop/api/products/374/variants/
// Returns list of all variants with their attributes
```

### Step 2: User Selects Attributes
```swift
let selectedColor = "مشکی"
let selectedSize = "M"
```

### Step 3: Find Correct Variant ID
```swift
// POST /shop/api/customer/find-variant/
let request = [
    "product_id": 374,
    "attributes": [
        "color": selectedColor,
        "size": selectedSize
    ]
]

// Returns: {"variant_id": 196, ...}
let variantId = response["variant_id"] // 196
```

### Step 4: Add to Cart with Correct Variant
```swift
// POST /shop/api/customer/cart/
let cartRequest = [
    "product_id": 374,
    "variant_id": variantId,  // 196 (correct!)
    "quantity": 1
]
```

## Testing the Fix

### Test Case: Product 374 Variants
```bash
# Test finding Black, M variant
curl -X POST https://test-0yq3.onrender.com/shop/api/customer/find-variant/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 374,
    "attributes": {"color": "مشکی", "size": "M"}
  }'

# Expected: variant_id = 196 ✅
```

```bash
# Test finding Black, L variant  
curl -X POST https://test-0yq3.onrender.com/shop/api/customer/find-variant/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 374,
    "attributes": {"color": "مشکی", "size": "L"}
  }'

# Expected: variant_id = 153 ✅
```

```bash
# Test with invalid size
curl -X POST https://test-0yq3.onrender.com/shop/api/customer/find-variant/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 374,
    "attributes": {"color": "مشکی", "size": "XS"}
  }'

# Expected: 404 error with available variants list ✅
```

## Benefits

1. ✅ **Accurate Variant Selection** - No more wrong variants being added
2. ✅ **Clear Error Messages** - Shows available variants if selection invalid
3. ✅ **Client-Agnostic** - Works with any client (iOS, Android, Web)
4. ✅ **Debugging** - Server logs show exact variant matching process
5. ✅ **Flexible** - Works with any number of attributes (color, size, material, etc.)

## Debug Logs

The endpoint includes detailed logging:
```
🔍 Finding variant for product 374 with attributes: {'color': 'مشکی', 'size': 'M'}
   Found 4 active variants
   Checking variant 153: {'size': 'L', 'color': 'مشکی'}
   Checking variant 194: {'size': 'XXL', 'color': 'مشکی'}
   Checking variant 195: {'size': 'M', 'color': 'خاکستری'}
   Checking variant 196: {'size': 'M', 'color': 'مشکی'}
   ✅ MATCH FOUND: Variant 196
```

## Migration Guide for Existing Code

**Old approach (broken):**
```swift
// ❌ Client tries to match variants locally - prone to errors
let variants = getVariants(productId: 374)
let variant = variants.first { 
    $0.attributes["size"] == "M" // Might pick wrong one!
}
addToCart(productId: 374, variantId: variant.id)
```

**New approach (correct):**
```swift
// ✅ Server finds the exact match
let response = findVariant(
    productId: 374,
    attributes: ["color": "مشکی", "size": "M"]
)
addToCart(productId: 374, variantId: response.variant_id)
```

## Status
- ✅ API Endpoint Created
- ✅ URL Route Added
- ✅ Debug Logging Implemented
- ✅ Deployed to Production
- ⏳ Client App Update Required (use new endpoint)

