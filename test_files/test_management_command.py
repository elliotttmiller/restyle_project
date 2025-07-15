#!/usr/bin/env python3
"""
Simple test for management command functionality
"""

import os
import sys
import subprocess

def test_management_command():
    """Test the management command"""
    print("🧪 Testing Management Command")
    print("=" * 40)
    
    try:
        # Change to backend directory
        backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
        os.chdir(backend_dir)
        
        # Run the management command
        result = subprocess.run([
            'python', 'manage.py', 'manage_ebay_tokens', 'status'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Management command executed successfully")
            print("Output:")
            print(result.stdout)
        else:
            print("❌ Management command failed")
            print("Error:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error testing management command: {e}")

if __name__ == "__main__":
    test_management_command() 