#!/bin/bash
# Usage: bash curl_analyze_and_price.sh <image_path>
# Example: bash curl_analyze_and_price.sh ../test_files/example2.jpg

IMAGE_PATH=${1:-../test_files/example2.jpg}
API_URL="https://restyleproject-production.up.railway.app/api/core/analyze-and-price/"

curl -v -k -X POST "$API_URL" \
  -F "image=@$IMAGE_PATH" \
  -H "Accept: application/json"
