#!/bin/bash
# Usage: bash curl_ssl_debug.sh <endpoint>
# Example: bash curl_ssl_debug.sh /api/core/ai/crop-preview/

ENDPOINT=${1:-/api/core/ai/crop-preview/}
API_URL="https://restyleproject-production.up.railway.app$ENDPOINT"

curl -v -k "$API_URL"
