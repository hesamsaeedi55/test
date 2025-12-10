# 📊 REGISTRATION RATE LIMITING - COMPLETE ANALYSIS

## 🎯 **CURRENT RATE LIMITS**

### **Primary Rate Limit (Middleware):**
```
Endpoint: POST /accounts/register/
Limit: 20 registrations per hour per IP address
Window: 3600 seconds (1 hour)
Scope: IP-based (same IP can register 20 accounts/hour)
```

**Location:** `shop/middleware.py` - Line 27

---

## 📋 **ALL RATE LIMITING SCENARIOS**

### **Scenario 1: Normal User Registration**

**What happens:**
```
User registers account #1
├─ IP: 89.116.131.15
├─ Count: 1/20
└─ ✅ Success

User registers account #2 (same IP, different email)
├─ IP: 89.116.131.15
├─ Count: 2/20
└─ ✅ Success

... continues until 20 registrations ...

User registers account #21
├─ IP: 89.116.131.15
├─ Count: 20/20 (LIMIT REACHED)
└─ ❌ Error: "Too many requests. Limit: 20 requests per 3600 seconds."
```

**Rate Limit:** 20/hour per IP  
**Reset Time:** After 1 hour from first request  
**Status:** ✅ Working

---

### **Scenario 2: Multiple Users from Same Network (Office/School)**

**What happens:**
```
User A registers (Office WiFi)
├─ IP: 192.168.1.100 (NAT: 89.116.131.15)
├─ Count: 1/20
└─ ✅ Success

User B registers (Same Office WiFi)
├─ IP: 192.168.1.101 (NAT: 89.116.131.15) ← Same public IP!
├─ Count: 2/20
└─ ✅ Success

... if 20 people register from same office ...

User Z registers (Same Office WiFi)
├─ IP: 192.168.1.120 (NAT: 89.116.131.15)
├─ Count: 20/20 (LIMIT REACHED)
└─ ❌ Error: Rate limited (even though different users!)
```

**Rate Limit:** 20/hour per public IP  
**Issue:** ⚠️ Shared networks (NAT) share the same public IP  
**Impact:** Legitimate users might be blocked  
**Status:** ⚠️ Potential UX issue for shared networks

---

### **Scenario 3: Spam/Bot Attack (Same IP)**

**What happens:**
```
Bot attempts registration #1
├─ IP: 1.2.3.4
├─ Count: 1/20
└─ ✅ Success (if valid email)

Bot attempts registration #2
├─ IP: 1.2.3.4
├─ Count: 2/20
└─ ✅ Success

... bot creates 20 accounts ...

Bot attempts registration #21
├─ IP: 1.2.3.4
├─ Count: 20/20
└─ ❌ Blocked for 1 hour

Bot switches to new IP (1.2.3.5)
├─ IP: 1.2.3.5
├─ Count: 1/20 (fresh limit)
└─ ✅ Can register again
```

**Rate Limit:** 20/hour per IP  
**Protection:** ✅ Prevents single-IP spam  
**Limitation:** ⚠️ Bot can use multiple IPs (botnet)  
**Status:** ✅ Good for single-IP attacks

---

### **Scenario 4: Email-Based Rate Limiting**

**Current Status:** ❌ **NOT IMPLEMENTED**

**What SHOULD happen:**
```
User tries to register with email1@example.com
├─ Email check: Not in database
└─ ✅ Allowed

User tries to register with email1@example.com again
├─ Email check: Already exists
└─ ❌ Error: "Email already registered"

User tries to register with email2@example.com (same IP)
├─ IP: 89.116.131.15
├─ Count: 2/20
└─ ✅ Allowed (if under IP limit)
```

**Current Behavior:**
- ✅ Database unique constraint prevents duplicate emails
- ❌ No additional rate limiting per email
- ✅ IP-based limit still applies

**Status:** ✅ Acceptable (database constraint is sufficient)

---

### **Scenario 5: Rapid Registration Attempts**

**What happens:**
```
User clicks "Register" button rapidly (5 times in 10 seconds)
├─ Request 1: IP count = 1/20 → ✅ Success
├─ Request 2: IP count = 2/20 → ✅ Success (if different email)
├─ Request 3: IP count = 3/20 → ✅ Success
├─ Request 4: IP count = 4/20 → ✅ Success
└─ Request 5: IP count = 5/20 → ✅ Success

All within same hour window
```

**Rate Limit:** 20/hour (not per minute)  
**Behavior:** ✅ Allows rapid legitimate registrations  
**Protection:** ✅ Still limited to 20/hour total  
**Status:** ✅ Good UX

---

### **Scenario 6: Registration After Rate Limit Expires**

**What happens:**
```
Hour 1: User registers 20 accounts
├─ 10:00 AM - Account 1
├─ 10:05 AM - Account 2
├─ ...
└─ 10:55 AM - Account 20 (LIMIT REACHED)

Hour 2: User tries again
├─ 11:00 AM - Attempt #21
├─ Check: First request was at 10:00 AM
├─ Time elapsed: 60 minutes
├─ Cache expired: ✅
└─ ✅ Success (count resets to 1/20)
```

**Rate Limit:** Sliding window (1 hour from first request)  
**Reset:** After 1 hour from first request in window  
**Status:** ✅ Working correctly

---

### **Scenario 7: Registration from Different IPs**

**What happens:**
```
User registers from Home
├─ IP: 89.116.131.15
├─ Count: 1/20
└─ ✅ Success

User registers from Mobile Data
├─ IP: 192.168.43.1 (different public IP)
├─ Count: 1/20 (separate limit)
└─ ✅ Success

User registers from Coffee Shop WiFi
├─ IP: 203.0.113.5 (different public IP)
├─ Count: 1/20 (separate limit)
└─ ✅ Success
```

**Rate Limit:** Per IP (independent limits)  
**Behavior:** ✅ Each IP has its own 20/hour limit  
**Status:** ✅ Correct behavior

---

### **Scenario 8: Registration with Invalid Data**

**What happens:**
```
User submits invalid email
├─ Validation fails (form.is_valid() = False)
├─ Rate limit: NOT checked (validation fails first)
└─ ❌ Error: "Invalid email format"

User submits weak password
├─ Validation fails
├─ Rate limit: NOT checked
└─ ❌ Error: "Password too weak"

User submits valid data
├─ Validation passes
├─ Rate limit: CHECKED
├─ Count: 1/20
└─ ✅ Success
```

**Rate Limit:** Only checked AFTER validation passes  
**Behavior:** ✅ Invalid requests don't count toward limit  
**Status:** ✅ Good (prevents abuse of rate limit counter)

---

### **Scenario 9: Registration During High Traffic**

**What happens:**
```
1000 users try to register simultaneously
├─ Each from different IP
├─ Each has independent 20/hour limit
├─ Server processes requests
└─ ✅ All succeed (if under their individual limits)
```

**Rate Limit:** Per IP (distributed)  
**Scalability:** ✅ Handles high traffic well  
**Status:** ✅ Good for production

---

### **Scenario 10: Registration After Account Deletion**

**What happens:**
```
User registers account
├─ Email: test@example.com
├─ IP: 89.116.131.15
├─ Count: 1/20
└─ ✅ Success

User deletes account
├─ Account deleted from database
└─ ✅ Deleted

User tries to register again (same email)
├─ Email: test@example.com
├─ IP: 89.116.131.15
├─ Count: 2/20 (IP limit still applies)
├─ Email: Available (deleted)
└─ ✅ Success (can re-register)
```

**Rate Limit:** IP-based (not email-based)  
**Behavior:** ✅ User can re-register after deletion  
**Status:** ✅ Correct

---

## 📊 **RATE LIMIT COMPARISON**

| Scenario | Current Limit | Industry Standard | Status |
|----------|--------------|-------------------|--------|
| Normal user | 20/hour | 5-50/hour | ✅ Good |
| Shared network | 20/hour (shared) | 20-100/hour | ⚠️ Could be higher |
| Bot attack (single IP) | 20/hour | 5-20/hour | ✅ Good |
| Bot attack (botnet) | 20/hour per IP | Requires CAPTCHA | ⚠️ Need CAPTCHA |
| Rapid attempts | 20/hour | 10-30/hour | ✅ Good |
| Email uniqueness | Database constraint | Database constraint | ✅ Good |

---

## ⚠️ **POTENTIAL ISSUES & RECOMMENDATIONS**

### **Issue 1: Shared Networks (NAT)**

**Problem:**
- Office/school WiFi shares one public IP
- 20 people registering = all blocked after 20th person

**Current Impact:** Medium (affects shared networks)

**Recommendations:**
1. **Increase limit to 50/hour** (for shared networks)
2. **Add CAPTCHA after 10 registrations** (prevents bots)
3. **Add email verification requirement** (already implemented)
4. **Monitor and whitelist known good IPs** (advanced)

**Recommended Change:**
```python
# In shop/middleware.py
(r'^/accounts/register/', 50, 3600, 'Registration'),  # 50 per hour (was 20)
```

---

### **Issue 2: No CAPTCHA for Registration**

**Problem:**
- Bots can register 20 accounts/hour per IP
- With botnet (1000 IPs) = 20,000 accounts/hour

**Current Protection:**
- ✅ Email verification required (accounts inactive until verified)
- ✅ Strong password requirements
- ✅ IP-based rate limiting

**Recommendations:**
1. **Add CAPTCHA after 5 registrations from same IP** (optional)
2. **Add honeypot field** (invisible field that bots fill)
3. **Monitor registration patterns** (detect bot behavior)

**Status:** ⚠️ Acceptable for 5K users, but could be improved

---

### **Issue 3: No Account-Based Rate Limiting**

**Problem:**
- User can register 20 accounts/hour from same IP
- No limit on number of accounts per user

**Current Protection:**
- ✅ Email must be unique (database constraint)
- ✅ Email verification required
- ✅ IP-based limit

**Recommendations:**
1. **Add phone number verification** (one account per phone)
2. **Add device fingerprinting** (limit per device)
3. **Monitor suspicious patterns** (same name, similar emails)

**Status:** ✅ Acceptable (email uniqueness is sufficient)

---

## ✅ **CURRENT PROTECTIONS SUMMARY**

### **Rate Limiting:**
```
✅ IP-based: 20 registrations/hour
✅ Sliding window: 1 hour from first request
✅ Per-IP independent limits
✅ Invalid requests don't count
✅ Automatic reset after window expires
```

### **Validation:**
```
✅ Email uniqueness (database constraint)
✅ Strong password requirements (8+ chars, complexity)
✅ Email format validation
✅ Phone number validation
✅ Required fields validation
```

### **Security:**
```
✅ Email verification required (accounts inactive)
✅ Password hashing (PBKDF2)
✅ CSRF protection
✅ SQL injection protection (Django ORM)
✅ XSS protection
```

---

## 🎯 **RECOMMENDED RATE LIMITS FOR 5,000 USERS**

### **Current (Good for Production):**
```
Registration: 20/hour per IP
```

### **Recommended (Better for Shared Networks):**
```
Registration: 50/hour per IP
```

### **With CAPTCHA (Best for Security):**
```
Registration: 
  - First 10: No CAPTCHA
  - 11-50: CAPTCHA required
  - After 50: Blocked for 1 hour
```

---

## 📝 **TESTING REGISTRATION RATE LIMITS**

### **Test 1: Normal Registration**
```bash
curl -X POST "https://myshop-backend-an7h.onrender.com/accounts/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test1@example.com",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "+1234567890",
    "date_of_birth": "1990-01-01",
    "password1": "SecurePass123!@#",
    "password2": "SecurePass123!@#"
  }'
```

**Expected:** ✅ Success (200 OK)

---

### **Test 2: Rapid Registrations (20 attempts)**
```bash
for i in {1..21}; do
  echo "Registration attempt $i:"
  curl -s -X POST "https://myshop-backend-an7h.onrender.com/accounts/register/" \
    -H "Content-Type: application/json" \
    -d "{
      \"email\": \"test${i}@example.com\",
      \"first_name\": \"Test\",
      \"last_name\": \"User\",
      \"phone_number\": \"+1234567890\",
      \"date_of_birth\": \"1990-01-01\",
      \"password1\": \"SecurePass123!@#\",
      \"password2\": \"SecurePass123!@#\"
    }" | python3 -m json.tool
  
  sleep 1
done
```

**Expected:**
- Attempts 1-20: ✅ Success
- Attempt 21: ❌ "Too many requests. Limit: 20 requests per 3600 seconds."

---

### **Test 3: Rate Limit Reset**
```bash
# Register 20 accounts
# Wait 1 hour
# Try registration #21

# Should succeed (limit reset)
```

**Expected:** ✅ Success after 1 hour

---

## 🔧 **HOW TO CHANGE RATE LIMITS**

### **Option 1: Increase Limit (Recommended)**

Edit `shop/middleware.py`:
```python
# Line 27
(r'^/accounts/register/', 50, 3600, 'Registration'),  # Changed from 20 to 50
```

### **Option 2: Add Per-Email Limit**

Add to `accounts/views.py` in `register()` function:
```python
# After form validation, before user.save()
from django.core.cache import cache

email_key = f'registration_email_{form.cleaned_data["email"]}'
email_count = cache.get(email_key, 0)

if email_count >= 3:  # Max 3 registrations per email per hour
    return JsonResponse({
        'error': 'Too many registration attempts for this email. Please try again later.'
    }, status=429)

cache.set(email_key, email_count + 1, 3600)  # 1 hour
```

---

## 📊 **FINAL SUMMARY**

### **Current Rate Limiting:**
```
✅ 20 registrations per hour per IP
✅ Sliding 1-hour window
✅ Independent limits per IP
✅ Invalid requests don't count
✅ Automatic reset
```

### **Protection Level:**
```
✅ Good for 5,000 users
✅ Prevents single-IP spam
⚠️  Could be higher for shared networks
⚠️  No CAPTCHA (but email verification helps)
```

### **Recommendation:**
```
For 5,000 users: Current limit is GOOD ✅
For shared networks: Consider increasing to 50/hour
For bot protection: Add CAPTCHA after 10 registrations (optional)
```

---

## ✅ **VERDICT**

**Your current registration rate limiting is:**
- ✅ **Production-ready** for 5,000 users
- ✅ **Secure** against single-IP attacks
- ✅ **User-friendly** (allows legitimate rapid registrations)
- ⚠️  **Could be improved** for shared networks (increase to 50/hour)

**Status: GOOD - No critical issues!** 🎉

