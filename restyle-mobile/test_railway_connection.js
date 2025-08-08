#!/usr/bin/env node
/**
 * Test script to verify mobile app connection to Railway backend
 */
const axios = require('axios');
const logger = require('./shared/logger');

const RAILWAY_URL = 'https://restyleproject-production.up.railway.app';

async function testRailwayConnection() {
  logger.info('🔍 Testing Mobile App Connection to Railway Backend');
  logger.info('=' .repeat(60));
  logger.info(`Railway URL: ${RAILWAY_URL}`);
  logger.info('');

  const endpoints = [
    { path: '/', name: 'Root Endpoint' },
    { path: '/health', name: 'Health Check' },
    { path: '/api/core/health/', name: 'Core Health Check' },
    { path: '/api/token/', name: 'Token Endpoint' },
  ];

  for (const endpoint of endpoints) {
    try {
      logger.info(`Testing ${endpoint.name}...`);
      const response = await axios.get(`${RAILWAY_URL}${endpoint.path}`, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      logger.info(`✅ ${endpoint.name}: ${response.status}`);
      if (response.data) {
        logger.info(`   Response: ${JSON.stringify(response.data, null, 2).substring(0, 200)}...`);
      }
    } catch (error) {
      logger.error(`❌ ${endpoint.name}: ${error.response?.status || error.code}`);
      if (error.response?.data) {
        logger.error(`   Error: ${JSON.stringify(error.response.data, null, 2)}`);
      } else {
        logger.error(`   Error: ${error.message}`);
      }
    }
    logger.info('');
  }

  // Test authentication endpoints
  logger.info('Testing Authentication Endpoints...');
  try {
    // Test token endpoint (should return 400 for missing credentials, not 404)
    const tokenResponse = await axios.post(`${RAILWAY_URL}/api/token/`, {}, {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      }
    });
    logger.info(`✅ Token endpoint: ${tokenResponse.status}`);
  } catch (error) {
    if (error.response?.status === 400) {
      logger.info('✅ Token endpoint: 400 (expected - missing credentials)');
    } else {
      logger.error(`❌ Token endpoint: ${error.response?.status || error.code}`);
    }
  }

  logger.info('');
  logger.info('🎉 Railway Backend Connection Test Complete!');
  logger.info('Your mobile app should now be able to connect to the Railway backend.');
}

testRailwayConnection().catch(logger.error);