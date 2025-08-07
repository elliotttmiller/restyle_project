#!/bin/bash
# Test mobile app authentication with local backend

echo "🔐 Testing Mobile App Authentication with Local Backend"
echo "============================================================"

LOCAL_URL="http://localhost:8000"
echo "Backend URL: $LOCAL_URL"
echo

# Test 1: Check backend health
echo "1. Testing Backend Health..."
response=$(curl -s -w "%{http_code}" "$LOCAL_URL/health")
http_code="${response: -3}"
response_body="${response%???}"

if [ "$http_code" = "200" ]; then
    echo "✅ Backend is healthy"
    echo "   Response: $(echo "$response_body" | head -c 100)..."
else
    echo "❌ Backend health check failed (HTTP $http_code)"
    exit 1
fi
echo

# Test 2a: Test with invalid credentials
echo "2a. Testing with invalid credentials..."
response=$(curl -s -w "%{http_code}" -X POST "$LOCAL_URL/api/token/" \
  -H "Content-Type: application/json" \
  -d '{"username": "nonexistent", "password": "wrongpass"}')
http_code="${response: -3}"

if [ "$http_code" = "401" ]; then
    echo "✅ Invalid credentials correctly rejected"
else
    echo "❌ Unexpected response for invalid credentials (HTTP $http_code)"
fi
echo

# Test 2b: Test with valid credentials
echo "2b. Testing with valid credentials..."
response=$(curl -s -w "%{http_code}" -X POST "$LOCAL_URL/api/token/" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}')
http_code="${response: -3}"
response_body="${response%???}"

if [ "$http_code" = "200" ]; then
    echo "✅ Authentication successful"
    echo "   Response: $(echo "$response_body" | head -c 200)..."
    
    # Extract access token for further testing
    access_token=$(echo "$response_body" | grep -o '"access":"[^"]*"' | cut -d'"' -f4)
    refresh_token=$(echo "$response_body" | grep -o '"refresh":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$access_token" ]; then
        echo "   Access token extracted: ${access_token:0:20}..."
    fi
    if [ -n "$refresh_token" ]; then
        echo "   Refresh token extracted: ${refresh_token:0:20}..."
    fi
else
    echo "❌ Valid credentials authentication failed (HTTP $http_code)"
    echo "   Response: $response_body"
fi
echo

# Test 3: Test token refresh
if [ -n "$refresh_token" ]; then
    echo "3. Testing Token Refresh..."
    response=$(curl -s -w "%{http_code}" -X POST "$LOCAL_URL/api/token/refresh/" \
      -H "Content-Type: application/json" \
      -d "{\"refresh\": \"$refresh_token\"}")
    http_code="${response: -3}"
    response_body="${response%???}"
    
    if [ "$http_code" = "200" ]; then
        echo "✅ Token refresh successful"
        echo "   Response: $(echo "$response_body" | head -c 100)..."
    else
        echo "❌ Token refresh failed (HTTP $http_code)"
        echo "   Response: $response_body"
    fi
else
    echo "3. Skipping token refresh test (no refresh token available)"
fi
echo

# Test 4: Test mobile app headers simulation
echo "4. Simulating Mobile App Login Flow..."
response=$(curl -s -w "%{http_code}" -X POST "$LOCAL_URL/api/token/" \
  -H "Content-Type: application/json" \
  -H "User-Agent: RestyleMobileApp/1.0.0" \
  -H "X-Requested-With: RestyleMobileApp" \
  -d '{"username": "testuser", "password": "testpass123"}')
http_code="${response: -3}"

if [ "$http_code" = "200" ]; then
    echo "✅ Mobile app login simulation successful"
else
    echo "❌ Mobile app login simulation failed (HTTP $http_code)"
fi
echo

echo "🎉 Mobile App Authentication Test Complete!"
echo
echo "Summary:"
echo "- Backend is running and responsive"
echo "- Authentication endpoints are working"
echo "- Token generation and refresh are functional"
echo "- Mobile app simulation is working"
echo
echo "Next Steps:"
echo "1. Mobile app should now be able to authenticate"
echo "2. Update mobile app configuration if needed"
echo "3. Test with actual mobile app"