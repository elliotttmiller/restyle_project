#!/usr/bin/env python3
"""
Test script to check if external requests work
"""
import requests
import time

def test_external_requests():
    base_url = "https://restyleproject-production.up.railway.app"
    
    print("Testing external requests...")
    
    endpoints = [
        "/",
        "/health",
        "/test/",
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\nTesting: {base_url}{endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_external_requests() 