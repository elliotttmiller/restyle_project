#!/usr/bin/env node
/**
 * Test authentication with Railway backend
 */
const axios = require('axios');

const RAILWAY_URL = 'https://restyleproject-production.up.railway.app';

async function testAuthentication() {
  console.log('🔐 Testing Authentication with Railway Backend');
  console.log('=' .repeat(50));
  console.log(`Railway URL: ${RAILWAY_URL}`);
  console.log();

  // Test 1: Register a test user
  console.log('1. Testing User Registration...');
  try {
    const registerData = {
      username: 'testuser_' + Date.now(),
      email: `test${Date.now()}@example.com`,
      password: 'testpass123',
      first_name: 'Test',
      last_name: 'User'
    };

    const registerResponse = await axios.post(`${RAILWAY_URL}/api/users/register/`, registerData, {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      }
    });

    console.log('✅ Registration successful');
    console.log(`   User ID: ${registerResponse.data.user?.id}`);
    
    // Test 2: Login with the registered user
    console.log('\n2. Testing User Login...');
    const loginData = {
      username: registerData.username,
      password: registerData.password
    };

    const loginResponse = await axios.post(`${RAILWAY_URL}/api/token/`, loginData, {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      }
    });

    console.log('✅ Login successful');
    console.log(`   Access Token: ${loginResponse.data.access?.substring(0, 20)}...`);
    console.log(`   Refresh Token: ${loginResponse.data.refresh?.substring(0, 20)}...`);

    // Test 3: Test authenticated endpoint
    console.log('\n3. Testing Authenticated Endpoint...');
    const authResponse = await axios.get(`${RAILWAY_URL}/api/core/health-check/`, {
      timeout: 10000,
      headers: {
        'Authorization': `Bearer ${loginResponse.data.access}`,
        'Content-Type': 'application/json',
      }
    });

    console.log('✅ Authenticated endpoint successful');
    console.log(`   Response: ${JSON.stringify(authResponse.data, null, 2)}`);

  } catch (error) {
    console.log(`❌ Authentication test failed: ${error.response?.status || error.code}`);
    if (error.response?.data) {
      console.log(`   Error: ${JSON.stringify(error.response.data, null, 2)}`);
    } else {
      console.log(`   Error: ${error.message}`);
    }
  }

  console.log('\n🎉 Authentication Test Complete!');
  console.log('Your mobile app should now be able to authenticate with the Railway backend.');
}

testAuthentication().catch(console.error); 