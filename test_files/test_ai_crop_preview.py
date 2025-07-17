import requests
import base64

url = 'http://localhost:8000/api/core/ai/crop-preview/'
image_path = 'test_files/example.JPG'

with open(image_path, 'rb') as f:
    files = {'image': f}
    response = requests.post(url, files=files)

print('Status code:', response.status_code)
try:
    data = response.json()
    print('Keys in response:', list(data.keys()))
    if 'cropped_image_base64' in data:
        print('Cropped image base64 present.')
        # Save cropped image for inspection
        with open('test_files/cropped_preview.jpg', 'wb') as out:
            out.write(base64.b64decode(data['cropped_image_base64']))
        print('Cropped image saved to test_files/cropped_preview.jpg')
    if 'crop_info' in data:
        print('Crop info:', data['crop_info'])
    if 'original_image_base64' in data:
        print('Original image base64 present.')
except Exception as e:
    print('Error parsing response:', e)
    print('Raw response:', response.text) 