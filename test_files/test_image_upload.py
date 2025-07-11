#!/usr/bin/env python3
"""
Test script to verify image upload and processing
"""
import requests
import os

API_URL = 'http://localhost:8000/api/core/ai/image-search/'
# Use absolute path for the new test image
IMAGE_PATH = r'C:\Users\AMD\restyle_project\test_files\example2.jpg'
AUTH_URL = 'http://localhost:8000/api/token/'

# Use environment variables or defaults for test credentials
username = os.environ.get('DJANGO_TEST_USER', 'testuser')
password = os.environ.get('DJANGO_TEST_PASS', 'elliott123')

def get_jwt_token():
    auth_data = {
        'username': username,
        'password': password
    }
    try:
        response = requests.post(AUTH_URL, json=auth_data, timeout=10)
        if response.status_code == 200:
            token = response.json().get('access')
            if token:
                print('✅ Authenticated, got JWT token')
                return token
            else:
                print('❌ No access token in response')
        else:
            print(f'❌ Authentication failed: {response.status_code}')
            print('Response:', response.text)
    except Exception as e:
        print(f'❌ Error during authentication: {e}')
    return None

def main():
    token = get_jwt_token()
    if not token:
        print('❌ Could not get JWT token, aborting image upload test.')
        return
    headers = {
        'Authorization': f'Bearer {token}',
    }
    files = {
        'image': open(IMAGE_PATH, 'rb'),
    }
    response = requests.post(API_URL, headers=headers, files=files)
    print('Status code:', response.status_code)
    try:
        print('Response:', response.json())
    except Exception:
        print('Raw response:', response.text)

if __name__ == '__main__':
    main() 