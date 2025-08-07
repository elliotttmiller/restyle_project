#!/usr/bin/env node
/**
 * Comprehensive test for mobile app authentication flow
 * This script tests the entire authentication workflow that the mobile app will use
 */

const axios = require('axios');

const LOCAL_URL = 'http://localhost:8000';

class MobileAppAuthTest {
  constructor() {
    this.accessToken = null;
    this.refreshToken = null;
    this.userInfo = null;
  }

  async testBackendHealth() {
    console.log('🏥 Testing Backend Health...');
    try {
      const response = await axios.get(`${LOCAL_URL}/health`, {
        timeout: 5000
      });
      
      if (response.status === 200 && response.data.status === 'healthy') {
        console.log('✅ Backend is healthy and ready');
        return true;
      } else {
        console.log('❌ Backend returned unexpected response');
        return false;
      }
    } catch (error) {
      console.log('❌ Backend health check failed:', error.message);
      return false;
    }
  }

  async testInvalidLogin() {
    console.log('\n🔒 Testing Invalid Login (Should Fail)...');
    try {
      await axios.post(`${LOCAL_URL}/api/token/`, {
        username: 'invaliduser',
        password: 'wrongpassword'
      }, {
        timeout: 5000,
        headers: { 'Content-Type': 'application/json' }
      });
      
      console.log('❌ Invalid login should have failed but succeeded');
      return false;
    } catch (error) {
      if (error.response?.status === 401) {
        console.log('✅ Invalid login correctly rejected');
        console.log(`   Message: ${error.response.data.detail}`);
        return true;
      } else {
        console.log('❌ Unexpected error during invalid login:', error.message);
        return false;
      }
    }
  }

  async testValidLogin() {
    console.log('\n🔑 Testing Valid Login...');
    try {
      const response = await axios.post(`${LOCAL_URL}/api/token/`, {
        username: 'testuser',
        password: 'testpass123'
      }, {
        timeout: 10000, // Mobile apps might be slower
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'RestyleMobileApp/1.0.0'
        }
      });

      if (response.status === 200 && response.data.access) {
        this.accessToken = response.data.access;
        this.refreshToken = response.data.refresh;
        this.userInfo = response.data.user;

        console.log('✅ Valid login successful');
        console.log(`   User: ${this.userInfo.username} (${this.userInfo.email})`);
        console.log(`   Access Token: ${this.accessToken.substring(0, 20)}...`);
        console.log(`   Refresh Token: ${this.refreshToken.substring(0, 20)}...`);
        return true;
      } else {
        console.log('❌ Login response missing required fields');
        return false;
      }
    } catch (error) {
      console.log('❌ Valid login failed:', error.response?.data || error.message);
      return false;
    }
  }

  async testTokenRefresh() {
    console.log('\n🔄 Testing Token Refresh...');
    if (!this.refreshToken) {
      console.log('❌ No refresh token available for testing');
      return false;
    }

    try {
      const response = await axios.post(`${LOCAL_URL}/api/token/refresh/`, {
        refresh: this.refreshToken
      }, {
        timeout: 5000,
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'RestyleMobileApp/1.0.0'
        }
      });

      if (response.status === 200 && response.data.access) {
        const newAccessToken = response.data.access;
        console.log('✅ Token refresh successful');
        console.log(`   New Access Token: ${newAccessToken.substring(0, 20)}...`);
        
        // Update stored token
        this.accessToken = newAccessToken;
        return true;
      } else {
        console.log('❌ Token refresh response missing access token');
        return false;
      }
    } catch (error) {
      console.log('❌ Token refresh failed:', error.response?.data || error.message);
      return false;
    }
  }

  async testAuthenticatedRequest() {
    console.log('\n🛡️ Testing Authenticated Request...');
    if (!this.accessToken) {
      console.log('❌ No access token available for testing');
      return false;
    }

    try {
      // Test protected endpoint
      const response = await axios.get(`${LOCAL_URL}/api/protected/`, {
        timeout: 5000,
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json',
          'User-Agent': 'RestyleMobileApp/1.0.0'
        }
      });

      if (response.status === 200 && response.data.message === 'You are authenticated!') {
        console.log('✅ Protected endpoint access successful');
        console.log(`   Authenticated as: ${response.data.user.username}`);
        return true;
      } else {
        console.log('❌ Protected endpoint returned unexpected response');
        return false;
      }
    } catch (error) {
      console.log('❌ Protected endpoint request failed:', error.response?.data || error.message);
      return false;
    }
  }

  async testUserProfile() {
    console.log('\n👤 Testing User Profile Endpoint...');
    if (!this.accessToken) {
      console.log('❌ No access token available for testing');
      return false;
    }

    try {
      const response = await axios.get(`${LOCAL_URL}/api/profile/`, {
        timeout: 5000,
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json',
          'User-Agent': 'RestyleMobileApp/1.0.0'
        }
      });

      if (response.status === 200 && response.data.profile) {
        console.log('✅ User profile retrieved successfully');
        console.log(`   Profile: ${response.data.profile.username} (${response.data.profile.email})`);
        console.log(`   Account created: ${response.data.profile.date_joined}`);
        return true;
      } else {
        console.log('❌ User profile endpoint returned unexpected response');
        return false;
      }
    } catch (error) {
      console.log('❌ User profile request failed:', error.response?.data || error.message);
      return false;
    }
  }

  async testMobileAppWorkflow() {
    console.log('\n📱 Testing Complete Mobile App Workflow...');
    
    // Simulate the exact flow a mobile app would follow
    console.log('   1. App opens, checks for stored tokens...');
    let storedTokens = null; // In real app, this would come from AsyncStorage
    
    console.log('   2. No stored tokens found, showing login screen...');
    
    console.log('   3. User enters credentials and presses login...');
    const loginSuccess = await this.testValidLogin();
    if (!loginSuccess) return false;
    
    console.log('   4. Tokens received, storing in AsyncStorage...');
    storedTokens = {
      access: this.accessToken,
      refresh: this.refreshToken,
      user: this.userInfo
    };
    
    console.log('   5. Navigating to dashboard with authenticated user...');
    const authSuccess = await this.testAuthenticatedRequest();
    if (!authSuccess) return false;
    
    console.log('   6. Loading user profile...');
    const profileSuccess = await this.testUserProfile();
    if (!profileSuccess) return false;
    
    console.log('   7. Testing token refresh (background process)...');
    const refreshSuccess = await this.testTokenRefresh();
    if (!refreshSuccess) return false;
    
    console.log('✅ Complete mobile app workflow successful!');
    return true;
  }

  async runAllTests() {
    console.log('🚀 Starting Comprehensive Mobile App Authentication Tests');
    console.log('=' .repeat(70));
    console.log(`Backend URL: ${LOCAL_URL}`);
    console.log();

    const tests = [
      { name: 'Backend Health', fn: this.testBackendHealth },
      { name: 'Invalid Login', fn: this.testInvalidLogin },
      { name: 'Valid Login', fn: this.testValidLogin },
      { name: 'Token Refresh', fn: this.testTokenRefresh },
      { name: 'Authenticated Request', fn: this.testAuthenticatedRequest },
      { name: 'User Profile', fn: this.testUserProfile },
      { name: 'Mobile App Workflow', fn: this.testMobileAppWorkflow }
    ];

    let passed = 0;
    let failed = 0;

    for (const test of tests) {
      try {
        const success = await test.fn.call(this);
        if (success) {
          passed++;
        } else {
          failed++;
        }
      } catch (error) {
        console.log(`❌ ${test.name} threw an exception:`, error.message);
        failed++;
      }
    }

    console.log('\n' + '=' .repeat(70));
    console.log('📊 Test Summary:');
    console.log(`   ✅ Passed: ${passed}`);
    console.log(`   ❌ Failed: ${failed}`);
    console.log(`   📈 Success Rate: ${Math.round((passed / (passed + failed)) * 100)}%`);

    if (failed === 0) {
      console.log('\n🎉 All tests passed! Mobile app authentication should work perfectly.');
      console.log('\n📋 Next Steps:');
      console.log('   1. Update mobile app to point to the working backend');
      console.log('   2. Test with actual mobile app on device/simulator');
      console.log('   3. Monitor authentication logs for any issues');
    } else {
      console.log('\n⚠️  Some tests failed. Please review the errors above.');
    }

    return failed === 0;
  }
}

// Run the tests
const tester = new MobileAppAuthTest();
tester.runAllTests().catch(console.error);