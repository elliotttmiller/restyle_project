#!/usr/bin/env node
/**
 * Test authentication with Railway backend
 */
const axios = require('axios');
const logger = require('./shared/logger');

const RAILWAY_URL = 'https://restyleproject-production.up.railway.app';

async function testAuthentication() {
  logger.info('🔐 Testing Authentication with Railway Backend');
  logger.info('=' .repeat(50));
  logger.info(`Railway URL: ${RAILWAY_URL}`);
  logger.info('');

  // Test 1: Register a test user
  logger.info('1. Testing User Registration...');
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

    logger.info('✅ Registration successful');
    logger.info(`   User ID: ${registerResponse.data.user?.id}`);
    
    // Test 2: Login with the registered user
    logger.info('\n2. Testing User Login...');
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

    logger.info('✅ Login successful');
    logger.info(`   Access Token: ${loginResponse.data.access?.substring(0, 20)}...`);
    logger.info(`   Refresh Token: ${loginResponse.data.refresh?.substring(0, 20)}...`);

    // Test 3: Test authenticated endpoint
    logger.info('\n3. Testing Authenticated Endpoint...');
    const authResponse = await axios.get(`${RAILWAY_URL}/api/core/health-check/`, {
      timeout: 10000,
      headers: {
        'Authorization': `Bearer ${loginResponse.data.access}`,
        'Content-Type': 'application/json',
      }
    });

    logger.info('✅ Authenticated endpoint successful');
    logger.info(`   Response: ${JSON.stringify(authResponse.data, null, 2)}`);

  } catch (error) {
    logger.error(`❌ Authentication test failed: ${error.response?.status || error.code}`);
    if (error.response?.data) {
      logger.error(`   Error: ${JSON.stringify(error.response.data, null, 2)}`);
    } else {
      logger.error(`   Error: ${error.message}`);
    }
  }

  logger.info('\n🎉 Authentication Test Complete!');
  logger.info('Your mobile app should now be able to authenticate with the Railway backend.');
}

testAuthentication().catch(logger.error);