#!/usr/bin/env node
/**
 * Debug script to test mobile app connection issues
 */
const axios = require('axios');

const RAILWAY_URL = 'https://restyleproject-production.up.railway.app';

async function debugMobileConnection() {
  console.log('🔍 Debugging Mobile App Connection Issues');
  console.log('=' .repeat(50));
  console.log(`Testing URL: ${RAILWAY_URL}`);
  console.log();

  // Test 1: Basic connectivity
  console.log('1. Testing basic connectivity...');
  try {
    const response = await axios.get(RAILWAY_URL, {
      timeout: 10000,
      headers: {
        'User-Agent': 'RestyleMobile/1.0',
        'Accept': 'application/json',
      }
    });
    console.log(`✅ Basic connectivity: ${response.status}`);
    console.log(`   Response: ${JSON.stringify(response.data, null, 2)}`);
  } catch (error) {
    console.log(`❌ Basic connectivity failed: ${error.message}`);
    if (error.response) {
      console.log(`   Status: ${error.response.status}`);
      console.log(`   Data: ${JSON.stringify(error.response.data, null, 2)}`);
    }
  }

  console.log();

  // Test 2: Health endpoint
  console.log('2. Testing health endpoint...');
  try {
    const response = await axios.get(`${RAILWAY_URL}/health`, {
      timeout: 10000,
      headers: {
        'User-Agent': 'RestyleMobile/1.0',
        'Accept': 'application/json',
      }
    });
    console.log(`✅ Health endpoint: ${response.status}`);
    console.log(`   Response: ${JSON.stringify(response.data, null, 2)}`);
  } catch (error) {
    console.log(`❌ Health endpoint failed: ${error.message}`);
    if (error.response) {
      console.log(`   Status: ${error.response.status}`);
      console.log(`   Data: ${JSON.stringify(error.response.data, null, 2)}`);
    }
  }

  console.log();

  // Test 3: Token endpoint with POST
  console.log('3. Testing token endpoint (POST)...');
  try {
    const response = await axios.post(`${RAILWAY_URL}/api/token/`, {
      username: 'testuser',
      password: 'testpass'
    }, {
      timeout: 10000,
      headers: {
        'User-Agent': 'RestyleMobile/1.0',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    });
    console.log(`✅ Token endpoint: ${response.status}`);
    console.log(`   Response: ${JSON.stringify(response.data, null, 2)}`);
  } catch (error) {
    console.log(`❌ Token endpoint failed: ${error.message}`);
    if (error.response) {
      console.log(`   Status: ${error.response.status}`);
      console.log(`   Data: ${JSON.stringify(error.response.data, null, 2)}`);
    }
  }

  console.log();

  // Test 4: Network simulation (mobile-like)
  console.log('4. Testing with mobile-like headers...');
  try {
    const response = await axios.get(`${RAILWAY_URL}/health`, {
      timeout: 15000,
      headers: {
        'User-Agent': 'RestyleMobile/1.0 (React Native)',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
      }
    });
    console.log(`✅ Mobile-like request: ${response.status}`);
  } catch (error) {
    console.log(`❌ Mobile-like request failed: ${error.message}`);
  }

  console.log();
  console.log('🎯 Debug Summary:');
  console.log('- If all tests pass, the issue is in the mobile app code');
  console.log('- If tests fail, the issue is with Railway or network');
  console.log('- Check the specific error messages above');
}

debugMobileConnection().catch(console.error); 