#!/usr/bin/env python3
"""
Test script for eBay Browse API (RESTful)
"""

import requests
import json

# Your OAuth2 token (provided by user)
OAUTH_TOKEN = "v^1.1#i^1#I^3#r^0#p^3#f^0#t^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"

# Endpoint for Browse API
BROWSE_API_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"

# Search parameters
params = {
    "q": "Levi jeans",
    "category_ids": "11450",
    "limit": 5
}

headers = {
    "Authorization": f"Bearer {OAUTH_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def main():
    print("🧪 Testing eBay Browse API (RESTful)...")
    print(f"Endpoint: {BROWSE_API_URL}")
    print(f"Params: {params}")
    try:
        response = requests.get(BROWSE_API_URL, headers=headers, params=params, timeout=15)
        print(f"\nStatus Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {data.get('total', 0)} items.")
            print(json.dumps(data, indent=2)[:2000])
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main() 