#!/bin/bash
# Usage: bash curl_env_debug.sh
API_URL="https://restyleproject-production.up.railway.app/api/core/env-debug/"
curl -v -k "$API_URL"
