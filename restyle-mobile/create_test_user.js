#!/usr/bin/env node
/**
 * Create a test user for mobile app testing
 */
const axios = require('axios');

const RAILWAY_URL = 'https://restyleproject-production.up.railway.app';

async function createTestUser() {
  console.log('👤 Creating Test User for Mobile App');
  console.log('=' .repeat(40));
  
  const testUser = {
    username: 'mobiletest',
    email: 'mobiletest@example.com',
    password: 'mobilepass123',
    first_name: 'Mobile',
    last_name: 'Test'
  };

  try {
    console.log('Creating user:', testUser.username);
    
    const response = await axios.post(`${RAILWAY_URL}/api/users/register/`, testUser, {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      }
    });

    console.log('✅ User created successfully!');
    console.log('📱 Use these credentials in your mobile app:');
    console.log(`   Username: ${testUser.username}`);
    console.log(`   Password: ${testUser.password}`);
    console.log();
    
    // Test login with the new user
    console.log('🔐 Testing login with new user...');
    const loginResponse = await axios.post(`${RAILWAY_URL}/api/token/`, {
      username: testUser.username,
      password: testUser.password
    }, {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      }
    });

    console.log('✅ Login test successful!');
    console.log(`   Access Token: ${loginResponse.data.access.substring(0, 20)}...`);
    console.log(`   Refresh Token: ${loginResponse.data.refresh.substring(0, 20)}...`);
    
  } catch (error) {
    if (error.response?.status === 400 && error.response.data?.username) {
      console.log('⚠️ User already exists, testing login...');
      
      const loginResponse = await axios.post(`${RAILWAY_URL}/api/token/`, {
        username: testUser.username,
        password: testUser.password
      }, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        }
      });

      console.log('✅ Login successful with existing user!');
      console.log('📱 Use these credentials in your mobile app:');
      console.log(`   Username: ${testUser.username}`);
      console.log(`   Password: ${testUser.password}`);
    } else {
      console.error('❌ Error creating user:', error.response?.data || error.message);
    }
  }
}

createTestUser().catch(console.error); 