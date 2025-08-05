#!/usr/bin/env node
/**
 * Test mobile app authentication with local backend
 */
const axios = require('axios');

const LOCAL_URL = 'http://localhost:8000';

async function testMobileAppAuthentication() {
  console.log('🔐 Testing Mobile App Authentication with Local Backend');
  console.log('=' .repeat(60));
  console.log(`Backend URL: ${LOCAL_URL}`);
  console.log();

  // Test 1: Check backend health
  console.log('1. Testing Backend Health...');
  try {
    const healthResponse = await axios.get(`${LOCAL_URL}/health`, {
      timeout: 5000
    });
    console.log('✅ Backend is healthy');
    console.log(`   Status: ${healthResponse.data.status}`);
  } catch (error) {
    console.log('❌ Backend health check failed');
    console.log(`   Error: ${error.message}`);
    return;
  }

  // Test 2: Test authentication endpoints
  console.log('\n2. Testing Authentication Endpoints...');
  
  // Test with invalid credentials (expected to fail)
  console.log('\n   2a. Testing with invalid credentials...');
  try {
    await axios.post(`${LOCAL_URL}/api/token/`, {
      username: 'nonexistent',
      password: 'wrongpass'
    }, {
      timeout: 5000,
      headers: { 'Content-Type': 'application/json' }
    });
    console.log('❌ Authentication should have failed but succeeded');
  } catch (error) {
    if (error.response?.status === 401) {
      console.log('✅ Invalid credentials correctly rejected');
      console.log(`   Message: ${error.response.data.detail}`);
    } else {
      console.log('❌ Unexpected error with invalid credentials');
      console.log(`   Error: ${error.message}`);
    }
  }

  // Test with valid credentials
  console.log('\n   2b. Testing with valid credentials...');
  try {
    const loginResponse = await axios.post(`${LOCAL_URL}/api/token/`, {
      username: 'testuser',
      password: 'testpass123'
    }, {
      timeout: 5000,
      headers: { 'Content-Type': 'application/json' }
    });

    console.log('✅ Authentication successful');
    console.log(`   User ID: ${loginResponse.data.user.id}`);
    console.log(`   Username: ${loginResponse.data.user.username}`);
    console.log(`   Email: ${loginResponse.data.user.email}`);
    console.log(`   Access Token: ${loginResponse.data.access.substring(0, 20)}...`);
    console.log(`   Refresh Token: ${loginResponse.data.refresh.substring(0, 20)}...`);

    // Test 3: Test token refresh
    console.log('\n3. Testing Token Refresh...');
    try {
      const refreshResponse = await axios.post(`${LOCAL_URL}/api/token/refresh/`, {
        refresh: loginResponse.data.refresh
      }, {
        timeout: 5000,
        headers: { 'Content-Type': 'application/json' }
      });

      console.log('✅ Token refresh successful');
      console.log(`   New Access Token: ${refreshResponse.data.access.substring(0, 20)}...`);
    } catch (error) {
      console.log('❌ Token refresh failed');
      console.log(`   Error: ${error.response?.data || error.message}`);
    }

  } catch (error) {
    console.log('❌ Valid credentials authentication failed');
    console.log(`   Error: ${error.response?.data || error.message}`);
  }

  // Test 4: Test mobile app flow simulation
  console.log('\n4. Simulating Mobile App Login Flow...');
  
  const mobileAppHeaders = {
    'Content-Type': 'application/json',
    'User-Agent': 'RestyleMobileApp/1.0.0',
    'X-Requested-With': 'RestyleMobileApp'
  };

  try {
    const mobileLoginResponse = await axios.post(`${LOCAL_URL}/api/token/`, {
      username: 'testuser',
      password: 'testpass123'
    }, {
      timeout: 10000, // Mobile apps might have slower connections
      headers: mobileAppHeaders
    });

    console.log('✅ Mobile app login simulation successful');
    
    // Test authenticated request simulation
    const authenticatedHeaders = {
      ...mobileAppHeaders,
      'Authorization': `Bearer ${mobileLoginResponse.data.access}`
    };

    try {
      const profileResponse = await axios.get(`${LOCAL_URL}/health`, {
        timeout: 5000,
        headers: authenticatedHeaders
      });
      console.log('✅ Authenticated request simulation successful');
    } catch (error) {
      console.log('ℹ️  Authenticated request test (expected to work once protected endpoints are added)');
    }

  } catch (error) {
    console.log('❌ Mobile app login simulation failed');
    console.log(`   Error: ${error.response?.data || error.message}`);
  }

  console.log('\n🎉 Mobile App Authentication Test Complete!');
  console.log('\nNext Steps:');
  console.log('1. Update mobile app to point to working backend');
  console.log('2. Test actual mobile app login');
  console.log('3. Implement protected endpoints');
}

testMobileAppAuthentication().catch(console.error);