#!/usr/bin/env python3
"""
Test login to Railway backend
"""
import requests

RAILWAY_URL = 'https://restyleproject-production.up.railway.app'
LOGIN_ENDPOINT = '/api/token/'

# Use the credentials of the newly registered user
TEST_USERNAME = 'admin'
TEST_PASSWORD = 'test123'

def test_railway_login():
    print('🔐 Testing Railway Backend Login')
    print('=' * 50)
    print(f'Endpoint: {RAILWAY_URL}{LOGIN_ENDPOINT}')
    print(f'Username: {TEST_USERNAME}')
    print()

    try:
        response = requests.post(
            f'{RAILWAY_URL}{LOGIN_ENDPOINT}',
            json={
                'username': TEST_USERNAME,
                'password': TEST_PASSWORD
            },
            timeout=10
        )
        print(f'Status Code: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print('✅ Login successful!')
            print(f"Access Token: {data.get('access', '')[:32]}...")
            print(f"Refresh Token: {data.get('refresh', '')[:32]}...")
            return True
        else:
            print('❌ Login failed!')
            print(f'Response: {response.text}')
            return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == '__main__':
    test_railway_login() 