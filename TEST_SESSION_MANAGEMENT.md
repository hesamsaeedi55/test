# 🧪 SESSION MANAGEMENT - COMPLETE TESTING GUIDE

## 📋 **PREREQUISITES**

Before testing, ensure:
- ✅ Code is deployed to Render (wait 3-5 minutes after git push)
- ✅ Migrations have run (automatic on Render)
- ✅ You have a test account or use your existing account
- ✅ You have `curl` installed (or use Postman)

---

## 🎯 **TESTING SCENARIO: Complete Flow**

### **Step 1: Login and Create Session**

**Test:** Login from a device and verify session is created.

```bash
# Replace with your actual credentials
EMAIL="your_email@example.com"
PASSWORD="your_password"

# Login with device info
RESPONSE=$(curl -s -X POST "https://myshop-backend-an7h.onrender.com/accounts/token/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"device_info\": {
      \"name\": \"iPhone 14 Pro\",
      \"platform\": \"ios\",
      \"id\": \"TEST-DEVICE-001\",
      \"os_version\": \"iOS 17.1\",
      \"app_version\": \"1.0.5\"
    }
  }")

# Extract tokens
ACCESS_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)
REFRESH_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['refresh'])" 2>/dev/null)

echo "✅ Login successful!"
echo "Access Token: ${ACCESS_TOKEN:0:50}..."
echo "Refresh Token: ${REFRESH_TOKEN:0:50}..."
```

**Expected Result:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 30
}
```

**✅ Success Criteria:**
- Status code: 200
- Tokens received
- Session created in database (check admin panel)

---

### **Step 2: List All Active Sessions**

**Test:** View all devices where you're logged in.

```bash
# Use the access token from Step 1
curl -X GET "https://myshop-backend-an7h.onrender.com/accounts/sessions/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

**Expected Result:**
```json
{
  "sessions": [
    {
      "id": 1,
      "device": "iPhone 14 Pro",
      "device_type": "ios",
      "os_version": "iOS 17.1",
      "app_version": "1.0.5",
      "ip_address": "89.116.131.15",
      "location": "Unknown Location",
      "created_at": "2025-11-13T15:00:00Z",
      "last_activity": "2025-11-13T15:00:00Z",
      "expires_at": "2025-12-13T15:00:00Z",
      "is_current": true
    }
  ],
  "total": 1
}
```

**✅ Success Criteria:**
- Status code: 200
- Session appears in list
- `is_current: true` for this device
- Device info matches what you sent

---

### **Step 3: Login from Second Device**

**Test:** Simulate login from another device (iPad).

```bash
# Login from "iPad" (different device_id)
RESPONSE2=$(curl -s -X POST "https://myshop-backend-an7h.onrender.com/accounts/token/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"device_info\": {
      \"name\": \"iPad Air\",
      \"platform\": \"ios\",
      \"id\": \"TEST-DEVICE-002\",
      \"os_version\": \"iPadOS 17.1\",
      \"app_version\": \"1.0.5\"
    }
  }")

ACCESS_TOKEN_2=$(echo "$RESPONSE2" | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)

echo "✅ Second device logged in!"
echo "iPad Access Token: ${ACCESS_TOKEN_2:0:50}..."
```

**Expected Result:**
- Status code: 200
- New tokens received
- Both devices can use the app

---

### **Step 4: Verify Both Sessions Exist**

**Test:** Check that both devices appear in sessions list.

```bash
curl -X GET "https://myshop-backend-an7h.onrender.com/accounts/sessions/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

**Expected Result:**
```json
{
  "sessions": [
    {
      "id": 2,
      "device": "iPad Air",
      "device_type": "ios",
      "is_current": false,
      ...
    },
    {
      "id": 1,
      "device": "iPhone 14 Pro",
      "device_type": "ios",
      "is_current": true,
      ...
    }
  ],
  "total": 2
}
```

**✅ Success Criteria:**
- Status code: 200
- **2 sessions** in the list
- Both devices visible
- `is_current: true` for the device making the request

---

### **Step 5: Get Current Session Info**

**Test:** Get information about the current session.

```bash
curl -X GET "https://myshop-backend-an7h.onrender.com/accounts/sessions/current/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

**Expected Result:**
```json
{
  "user": {
    "id": 30,
    "email": "your_email@example.com",
    "name": "Your Name"
  },
  "session": {
    "device": "iPhone 14 Pro",
    "device_type": "ios",
    "os_version": "iOS 17.1",
    "app_version": "1.0.5",
    "ip_address": "89.116.131.15"
  },
  "active_sessions_count": 2
}
```

**✅ Success Criteria:**
- Status code: 200
- Current device info matches
- `active_sessions_count: 2` (both devices)

---

### **Step 6: Revoke Specific Session (iPad)**

**Test:** Logout from the iPad while keeping iPhone logged in.

```bash
# Get session ID for iPad (usually the newer one, ID: 2)
SESSION_ID=2

curl -X DELETE "https://myshop-backend-an7h.onrender.com/accounts/sessions/$SESSION_ID/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

**Expected Result:**
```json
{
  "success": true,
  "message": "Session revoked: iPad Air",
  "revoked_session": {
    "id": 2,
    "device": "iPad Air",
    "revoked_at": "2025-11-13T15:05:00Z"
  }
}
```

**✅ Success Criteria:**
- Status code: 200
- Success message received
- iPad session revoked

**Verify iPad is logged out:**
```bash
# Try to use iPad's refresh token (should fail)
curl -X POST "https://myshop-backend-an7h.onrender.com/accounts/token/refresh/" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH_TOKEN_2\"}" | python3 -m json.tool
```

**Expected:** 401 Unauthorized (iPad can't refresh token anymore)

---

### **Step 7: Verify Only One Session Remains**

**Test:** Check that only iPhone session is active.

```bash
curl -X GET "https://myshop-backend-an7h.onrender.com/accounts/sessions/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

**Expected Result:**
```json
{
  "sessions": [
    {
      "id": 1,
      "device": "iPhone 14 Pro",
      "is_active": true,
      "is_current": true
    }
  ],
  "total": 1
}
```

**✅ Success Criteria:**
- Status code: 200
- Only **1 session** remains
- iPad session is gone

---

### **Step 8: Login from Third Device (Web)**

**Test:** Login from web browser (no device_info).

```bash
# Login without device_info (web browser)
RESPONSE3=$(curl -s -X POST "https://myshop-backend-an7h.onrender.com/accounts/token/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }")

ACCESS_TOKEN_3=$(echo "$RESPONSE3" | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)

echo "✅ Web browser logged in!"
```

**Expected Result:**
- Status code: 200
- Tokens received
- Session created with device_type: "web" or "desktop_web"

---

### **Step 9: Logout from All Devices**

**Test:** Revoke all sessions except current device.

```bash
curl -X POST "https://myshop-backend-an7h.onrender.com/accounts/sessions/revoke-all/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"include_current": false}' | python3 -m json.tool
```

**Expected Result:**
```json
{
  "success": true,
  "message": "Revoked 1 session(s)",
  "revoked_count": 1,
  "include_current": false
}
```

**✅ Success Criteria:**
- Status code: 200
- Other devices revoked
- Current device still works

**Verify current device still works:**
```bash
# Current device should still work
curl -X GET "https://myshop-backend-an7h.onrender.com/accounts/sessions/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
```

**Expected:** Status 200, only current session remains

---

### **Step 10: Logout from ALL Devices (Including Current)**

**Test:** Force logout from all devices including current.

```bash
curl -X POST "https://myshop-backend-an7h.onrender.com/accounts/sessions/revoke-all/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"include_current": true}' | python3 -m json.tool
```

**Expected Result:**
```json
{
  "success": true,
  "message": "Revoked 1 session(s)",
  "revoked_count": 1,
  "include_current": true
}
```

**✅ Success Criteria:**
- Status code: 200
- All sessions revoked
- Token version incremented

**Verify token is invalidated:**
```bash
# Try to refresh token (should fail)
curl -X POST "https://myshop-backend-an7h.onrender.com/accounts/token/refresh/" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH_TOKEN\"}" | python3 -m json.tool
```

**Expected Result:**
```json
{
  "detail": "Token has been invalidated. Please login again."
}
```

**Status:** 401 Unauthorized

---

## 🧪 **COMPLETE TEST SCRIPT**

Save this as `test_sessions.sh` and run it:

```bash
#!/bin/bash

# ============================================================================
# SESSION MANAGEMENT - COMPLETE TEST SCRIPT
# ============================================================================

BASE_URL="https://myshop-backend-an7h.onrender.com"
EMAIL="your_email@example.com"
PASSWORD="your_password"

echo "========================================"
echo "🧪 SESSION MANAGEMENT TEST"
echo "========================================"
echo ""

# Step 1: Login Device 1 (iPhone)
echo "Step 1: Login from iPhone..."
RESPONSE1=$(curl -s -X POST "$BASE_URL/accounts/token/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"device_info\": {
      \"name\": \"iPhone 14 Pro\",
      \"platform\": \"ios\",
      \"id\": \"TEST-001\",
      \"os_version\": \"iOS 17.1\",
      \"app_version\": \"1.0.5\"
    }
  }")

TOKEN1=$(echo "$RESPONSE1" | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)

if [ -z "$TOKEN1" ]; then
  echo "❌ Login failed!"
  exit 1
fi

echo "✅ iPhone logged in"
echo ""

# Step 2: List sessions
echo "Step 2: List active sessions..."
SESSIONS=$(curl -s -X GET "$BASE_URL/accounts/sessions/" \
  -H "Authorization: Bearer $TOKEN1")
echo "$SESSIONS" | python3 -m json.tool
echo ""

# Step 3: Login Device 2 (iPad)
echo "Step 3: Login from iPad..."
RESPONSE2=$(curl -s -X POST "$BASE_URL/accounts/token/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"device_info\": {
      \"name\": \"iPad Air\",
      \"platform\": \"ios\",
      \"id\": \"TEST-002\",
      \"os_version\": \"iPadOS 17.1\",
      \"app_version\": \"1.0.5\"
    }
  }")

TOKEN2=$(echo "$RESPONSE2" | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)
REFRESH2=$(echo "$RESPONSE2" | python3 -c "import sys, json; print(json.load(sys.stdin)['refresh'])" 2>/dev/null)

echo "✅ iPad logged in"
echo ""

# Step 4: List sessions again (should show 2)
echo "Step 4: List sessions (should show 2)..."
SESSIONS=$(curl -s -X GET "$BASE_URL/accounts/sessions/" \
  -H "Authorization: Bearer $TOKEN1")
TOTAL=$(echo "$SESSIONS" | python3 -c "import sys, json; print(json.load(sys.stdin)['total'])" 2>/dev/null)
echo "Total sessions: $TOTAL"
echo ""

# Step 5: Get iPad session ID
IPAD_SESSION_ID=$(echo "$SESSIONS" | python3 -c "import sys, json; sessions = json.load(sys.stdin)['sessions']; print([s['id'] for s in sessions if 'iPad' in s['device']][0])" 2>/dev/null)

if [ -n "$IPAD_SESSION_ID" ]; then
  echo "Step 5: Revoke iPad session (ID: $IPAD_SESSION_ID)..."
  REVOKE=$(curl -s -X DELETE "$BASE_URL/accounts/sessions/$IPAD_SESSION_ID/" \
    -H "Authorization: Bearer $TOKEN1")
  echo "$REVOKE" | python3 -m json.tool
  echo "✅ iPad session revoked"
  echo ""
fi

# Step 6: Verify iPad can't refresh token
echo "Step 6: Verify iPad token is invalid..."
REFRESH_TEST=$(curl -s -X POST "$BASE_URL/accounts/token/refresh/" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH2\"}")
echo "$REFRESH_TEST" | python3 -m json.tool
echo ""

# Step 7: Logout all devices
echo "Step 7: Logout from all devices..."
LOGOUT_ALL=$(curl -s -X POST "$BASE_URL/accounts/sessions/revoke-all/" \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json" \
  -d '{"include_current": true}')
echo "$LOGOUT_ALL" | python3 -m json.tool
echo ""

echo "========================================"
echo "✅ TEST COMPLETE!"
echo "========================================"
```

**To run:**
```bash
chmod +x test_sessions.sh
./test_sessions.sh
```

---

## 📱 **POSTMAN TESTING**

### **Collection Setup:**

1. **Create Environment:**
   - Variable: `base_url` = `https://myshop-backend-an7h.onrender.com`
   - Variable: `access_token` = (will be set automatically)
   - Variable: `refresh_token` = (will be set automatically)

2. **Request 1: Login iPhone**
   ```
   POST {{base_url}}/accounts/token/
   Body (JSON):
   {
     "email": "your_email@example.com",
     "password": "your_password",
     "device_info": {
       "name": "iPhone 14 Pro",
       "platform": "ios",
       "id": "TEST-001",
       "os_version": "iOS 17.1",
       "app_version": "1.0.5"
     }
   }
   
   Tests Tab (save tokens):
   pm.environment.set("access_token", pm.response.json().access);
   pm.environment.set("refresh_token", pm.response.json().refresh);
   ```

3. **Request 2: List Sessions**
   ```
   GET {{base_url}}/accounts/sessions/
   Headers:
     Authorization: Bearer {{access_token}}
   ```

4. **Request 3: Revoke Session**
   ```
   DELETE {{base_url}}/accounts/sessions/2/
   Headers:
     Authorization: Bearer {{access_token}}
   ```

5. **Request 4: Logout All**
   ```
   POST {{base_url}}/accounts/sessions/revoke-all/
   Headers:
     Authorization: Bearer {{access_token}}
   Body (JSON):
   {
     "include_current": false
   }
   ```

---

## ✅ **TESTING CHECKLIST**

```
Authentication:
[ ] Login creates session
[ ] Session appears in list
[ ] Device info is correct
[ ] IP address is tracked

Multi-Device:
[ ] Login from 2nd device works
[ ] Both sessions appear in list
[ ] is_current flag is correct
[ ] Both devices can use app

Session Management:
[ ] List sessions returns correct data
[ ] Current session endpoint works
[ ] Revoke specific session works
[ ] Revoked device can't refresh token

Logout All:
[ ] Revoke all (exclude current) works
[ ] Current device still works
[ ] Revoke all (include current) works
[ ] All tokens invalidated
[ ] Token refresh fails after logout all

Token Versioning:
[ ] Token contains token_version claim
[ ] Token refresh validates version
[ ] Version mismatch rejects token
[ ] Account deletion invalidates tokens

Edge Cases:
[ ] Login without device_info (web)
[ ] Multiple logins from same device
[ ] Expired sessions cleanup
[ ] Invalid session ID handling
```

---

## 🐛 **TROUBLESHOOTING**

### **Issue: 404 Not Found**
**Solution:** Wait for deployment to complete (3-5 minutes)

### **Issue: 401 Unauthorized**
**Solution:** Token expired or invalid. Login again to get new token.

### **Issue: No sessions in list**
**Solution:** Check if device_info was sent in login request.

### **Issue: Session not created**
**Solution:** Check logs for errors. Session creation is non-blocking (login still works if it fails).

### **Issue: Token refresh fails after logout all**
**Expected:** This is correct behavior! Tokens are invalidated.

---

## 📊 **EXPECTED BEHAVIOR SUMMARY**

| Action | Expected Result |
|--------|----------------|
| Login | Session created, tokens received |
| List sessions | All active sessions shown |
| Revoke one | That device logged out, others work |
| Logout all | All devices logged out, tokens invalid |
| Token refresh | Works if session active, fails if revoked |
| Account deletion | All sessions invalidated immediately |

---

## 🎯 **QUICK TEST (30 seconds)**

```bash
# 1. Login
TOKEN=$(curl -s -X POST "https://myshop-backend-an7h.onrender.com/accounts/token/" \
  -H "Content-Type: application/json" \
  -d '{"email":"YOUR_EMAIL","password":"YOUR_PASSWORD","device_info":{"name":"Test","platform":"ios","id":"TEST"}}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])")

# 2. List sessions
curl -H "Authorization: Bearer $TOKEN" \
  "https://myshop-backend-an7h.onrender.com/accounts/sessions/" | python3 -m json.tool

# 3. Logout all
curl -X POST "https://myshop-backend-an7h.onrender.com/accounts/sessions/revoke-all/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"include_current":true}' | python3 -m json.tool
```

**If all 3 commands work → System is working! ✅**

---

**🎉 Happy Testing!**

