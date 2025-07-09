import os
import sys
import subprocess
import threading
import socket
import re
import psutil
import time

PROJECT_ROOT = os.path.dirname(__file__)
MOBILE_DIR = os.path.join(PROJECT_ROOT, 'restyle-mobile')
NODE_MODULES = os.path.join(MOBILE_DIR, 'node_modules')
API_CONFIG_FILE = os.path.join(MOBILE_DIR, 'shared', 'api.js')

print('--- Starting restyle-mobile app with automatic IP detection ---')

def get_local_ip():
    """Get the current local IP address"""
    try:
        # Create a socket to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Error getting IP address: {e}")
        return None

def update_api_config(ip_address):
    """Update the API configuration file with the current IP address"""
    if not ip_address:
        print("Warning: Could not detect IP address. Using default configuration.")
        return False
    
    try:
        # Read the current API config file
        with open(API_CONFIG_FILE, 'r') as f:
            content = f.read()
        
        # Check if the IP address is already correct
        if f'http://{ip_address}:8000/api' in content:
            print(f"API configuration already correct for IP: {ip_address}")
            return True
        
        # Update the IP address in the configuration
        # Replace any existing IP address pattern
        updated_content = re.sub(
            r'http://\d+\.\d+\.\d+\.\d+:8000/api',
            f'http://{ip_address}:8000/api',
            content
        )
        
        # If no IP was found, add the API_BASE_URL line
        if 'API_BASE_URL' not in updated_content:
            # Find the axios.create line and add API_BASE_URL before it
            updated_content = updated_content.replace(
                'const api = axios.create({',
                f'const API_BASE_URL = "http://{ip_address}:8000/api";\n\nconst api = axios.create({{'
            )
        
        # Write the updated configuration
        with open(API_CONFIG_FILE, 'w') as f:
            f.write(updated_content)
        
        print(f"Updated API configuration to use IP: {ip_address}")
        return True
        
    except Exception as e:
        print(f"Error updating API configuration: {e}")
        return False

# Step 1: Start backend server from project root
def start_backend():
    print('Starting Django backend server...')
    backend_manage_py = os.path.join(PROJECT_ROOT, 'backend', 'manage.py')
    backend_process = subprocess.Popen([
        sys.executable, backend_manage_py, 'runserver', '0.0.0.0:8000'
    ], cwd=PROJECT_ROOT)
    return backend_process

# Step 2: Change directory
def cd_mobile():
    os.chdir(MOBILE_DIR)
    print(f'Changed directory to {MOBILE_DIR}')

# Step 3: Install dependencies if needed
def ensure_dependencies():
    if not os.path.exists(NODE_MODULES):
        print('node_modules not found. Installing dependencies...')
        result = subprocess.run(['npm', 'install'], shell=True)
        if result.returncode != 0:
            print('npm install failed. Exiting.')
            sys.exit(1)
    else:
        print('Dependencies already installed.')
    
    # Check if expo is installed
    try:
        result = subprocess.run(['npx', 'expo', '--version'], shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print('Expo not found. Installing expo...')
            subprocess.run(['npm', 'install', 'expo'], shell=True, check=True)
            print('Expo installed successfully.')
        else:
            print('Expo is already installed.')
    except subprocess.CalledProcessError as e:
        print(f'Failed to install expo: {e}')
        sys.exit(1)

# Step 4: Start Expo server
def start_expo():
    print('Starting Expo development server...')
    subprocess.run(['npx', 'expo', 'start'], shell=True)

if __name__ == '__main__':
    # Detect and configure IP address
    print("Detecting current IP address...")
    current_ip = get_local_ip()
    
    if current_ip:
        print(f"Detected IP address: {current_ip}")
        if update_api_config(current_ip):
            print("API configuration updated successfully!")
        else:
            print("Warning: Failed to update API configuration")
    else:
        print("Warning: Could not detect IP address. Using existing configuration.")
    
    backend_process = start_backend()
    try:
        cd_mobile()
        ensure_dependencies()
        start_expo()
    finally:
        print('Shutting down backend server...')
        backend_process.terminate() 