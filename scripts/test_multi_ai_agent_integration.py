import requests
import time

# Path to your example image
IMAGE_PATH = './test_files/example2.jpg'  # Change if you want to use a different image

# Read Railway public domain from .env
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
RAILWAY_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN')
API_URL = f'https://{RAILWAY_DOMAIN}/api/core/ai/advanced-search/'

def main():
    with open(IMAGE_PATH, 'rb') as img_file:
        image_bytes = img_file.read()

    files = {'image': ('example2.jpg', image_bytes, 'image/jpeg')}
    data = {
        'intelligent_crop': True,
        'use_advanced_ai': True
    }

    start_time = time.time()
    response = requests.post(API_URL, files=files, data=data)
    elapsed = time.time() - start_time

    print(f'Response time: {elapsed:.2f} seconds')
    if response.status_code == 200:
        print('AI Agent Response:')
        print(response.json())
    else:
        print(f'Error: {response.status_code}')
        print(response.text)

if __name__ == '__main__':
    main()
