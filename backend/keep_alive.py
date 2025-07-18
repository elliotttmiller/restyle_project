#!/usr/bin/env python3
"""
Simple keep-alive script to test if Railway keeps the container running
"""
import time
import os

def main():
    print("=== Keep Alive Test ===")
    print(f"Container started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Environment variables:")
    print(f"  PORT: {os.environ.get('PORT', 'Not set')}")
    print(f"  RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'Not set')}")
    print(f"  RAILWAY_SERVICE_NAME: {os.environ.get('RAILWAY_SERVICE_NAME', 'Not set')}")
    
    # Keep the container alive for testing
    try:
        while True:
            print(f"Container still running at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(30)  # Log every 30 seconds
    except KeyboardInterrupt:
        print("Container stopped by user")
    except Exception as e:
        print(f"Container stopped due to error: {e}")

if __name__ == '__main__':
    main() 