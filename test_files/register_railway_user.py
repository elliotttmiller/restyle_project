#!/usr/bin/env python3
"""
Register a user on the Railway backend
"""
import requests

RAILWAY_URL = 'https://restyleproject-production.up.railway.app'
REGISTER_ENDPOINT = '/api/users/register/'

USERNAME = 'admin'
PASSWORD = 'test123'
EMAIL = 'admin@example.com'

def register_user():
    print('👤 Registering user on Railway Backend')
    print('=' * 50)
    print(f'Endpoint: {RAILWAY_URL}{REGISTER_ENDPOINT}')
    print(f'Username: {USERNAME}')
    print()

    try:
        response = requests.post(
            f'{RAILWAY_URL}{REGISTER_ENDPOINT}',
            json={
                'username': USERNAME,
                'password': PASSWORD,
                'email': EMAIL
            },
            timeout=10
        )
        print(f'Status Code: {response.status_code}')
        if response.status_code in (200, 201):
            print('✅ Registration successful!')
            print(f'Response: {response.json()}')
            return True
        else:
            print('❌ Registration failed!')
            print(f'Response: {response.text}')
            return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == '__main__':
    register_user() 