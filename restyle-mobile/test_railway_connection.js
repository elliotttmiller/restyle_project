#!/usr/bin/env node
/**
 * Test script to verify mobile app connection to Railway backend
 */
const axios = require('axios');

const RAILWAY_URL = 'https://restyleproject-production.up.railway.app';

async function testRailwayConnection() {
  console.log('🔍 Testing Mobile App Connection to Railway Backend');
  console.log('=' .repeat(60));
  console.log(`Railway URL: ${RAILWAY_URL}`);
  console.log();

  const endpoints = [
    { path: '/', name: 'Root Endpoint' },
    { path: '/health', name: 'Health Check' },
    { path: '/api/core/health/', name: 'Core Health Check' },
    { path: '/api/token/', name: 'Token Endpoint' },
  ];

  for (const endpoint of endpoints) {
    try {
      console.log(`Testing ${endpoint.name}...`);
      const response = await axios.get(`${RAILWAY_URL}${endpoint.path}`, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      console.log(`✅ ${endpoint.name}: ${response.status}`);
      if (response.data) {
        console.log(`   Response: ${JSON.stringify(response.data, null, 2).substring(0, 200)}...`);
      }
    } catch (error) {
      console.log(`❌ ${endpoint.name}: ${error.response?.status || error.code}`);
      if (error.response?.data) {
        console.log(`   Error: ${JSON.stringify(error.response.data, null, 2)}`);
      } else {
        console.log(`   Error: ${error.message}`);
      }
    }
    console.log();
  }

  // Test authentication endpoints
  console.log('Testing Authentication Endpoints...');
  try {
    // Test token endpoint (should return 400 for missing credentials, not 404)
    const tokenResponse = await axios.post(`${RAILWAY_URL}/api/token/`, {}, {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      }
    });
    console.log(`✅ Token endpoint: ${tokenResponse.status}`);
  } catch (error) {
    if (error.response?.status === 400) {
      console.log('✅ Token endpoint: 400 (expected - missing credentials)');
    } else {
      console.log(`❌ Token endpoint: ${error.response?.status || error.code}`);
    }
  }

  console.log();
  console.log('🎉 Railway Backend Connection Test Complete!');
  console.log('Your mobile app should now be able to connect to the Railway backend.');
}

testRailwayConnection().catch(console.error); 