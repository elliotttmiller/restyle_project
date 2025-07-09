import os
import sys
import subprocess
import shutil
import socket
import re
import time
import psutil
import psutil
import psutil

PROJECT_ROOT = os.path.dirname(__file__)
MOBILE_DIR = os.path.join(PROJECT_ROOT, 'restyle-mobile')
NODE_MODULES = os.path.join(MOBILE_DIR, 'node_modules')
API_CONFIG_FILE = os.path.join(MOBILE_DIR, 'shared', 'api.js')

print('--- Rebuilding and Starting restyle-mobile app with automatic IP detection ---')

def kill_expo_processes():
    """Kill any running Expo/React Native processes that might lock files"""
    print('Checking for running Expo/React Native processes...')
    
    processes_to_kill = [
        'expo',
        'node',
        'metro',
        'react-native',
        'npx',
        'npm'
    ]
    
    killed_count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            proc_name = proc.info['name'].lower()
            cmdline = ' '.join(proc.info['cmdline'] or []).lower()
            
            # Check if this is an Expo/React Native related process
            should_kill = False
            for target in processes_to_kill:
                if target in proc_name or target in cmdline:
                    # Additional check to avoid killing our own script
                    if 'rebuild_and_start_restyle-mobile.py' not in cmdline and 'start_restyle-mobile.py' not in cmdline:
                        should_kill = True
                        break
            
            if should_kill:
                print(f'Killing process: {proc.info["name"]} (PID: {proc.info["pid"]})')
                proc.terminate()
                killed_count += 1
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if killed_count > 0:
        print(f'Killed {killed_count} processes. Waiting 3 seconds for cleanup...')
        time.sleep(3)
    else:
        print('No running Expo/React Native processes found.')

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

def safe_remove_path(path, max_retries=3):
    """Safely remove a file or directory with retry logic"""
    for attempt in range(max_retries):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f'Removed directory: {path}')
            elif os.path.isfile(path):
                os.remove(path)
                print(f'Removed file: {path}')
            return True
        except PermissionError as e:
            if attempt < max_retries - 1:
                print(f'Permission denied, retrying in 2 seconds... (attempt {attempt + 1}/{max_retries})')
                time.sleep(2)
            else:
                print(f'Failed to remove {path} after {max_retries} attempts: {e}')
                return False
        except Exception as e:
            print(f'Error removing {path}: {e}')
            return False

def kill_expo_processes():
    """Kill any running Expo/React Native processes that might lock files"""
    print('Checking for running Expo/React Native processes...')
    
    processes_to_kill = [
        'expo',
        'node',
        'metro',
        'react-native',
        'npx',
        'npm'
    ]
    
    killed_count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            proc_name = proc.info['name'].lower()
            cmdline = ' '.join(proc.info['cmdline'] or []).lower()
            
            # Check if this is an Expo/React Native related process
            should_kill = False
            for target in processes_to_kill:
                if target in proc_name or target in cmdline:
                    # Additional check to avoid killing our own script
                    if 'rebuild_and_start_restyle-mobile.py' not in cmdline and 'start_restyle-mobile.py' not in cmdline:
                        should_kill = True
                        break
            
            if should_kill:
                print(f'Killing process: {proc.info["name"]} (PID: {proc.info["pid"]})')
                proc.terminate()
                killed_count += 1
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if killed_count > 0:
        print(f'Killed {killed_count} processes. Waiting 3 seconds for cleanup...')
        time.sleep(3)
    else:
        print('No running Expo/React Native processes found.')

def clean_mobile():
    print('Cleaning node_modules and lockfiles...')
    files_to_remove = ['node_modules', 'yarn.lock', 'package-lock.json']
    
    for fname in files_to_remove:
        path = os.path.join(MOBILE_DIR, fname)
        if os.path.exists(path):
            safe_remove_path(path)
        else:
            print(f'{fname} not found, skipping...')

def install_dependencies():
    print('Installing dependencies...')
    result = subprocess.run(['npm', 'install'], cwd=MOBILE_DIR, shell=True)
    if result.returncode != 0:
        print('npm install failed. Exiting.')
        sys.exit(1)
    
    # Check if expo is installed
    try:
        result = subprocess.run(['npx', 'expo', '--version'], cwd=MOBILE_DIR, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print('Expo not found. Installing expo...')
            subprocess.run(['npm', 'install', 'expo'], cwd=MOBILE_DIR, shell=True, check=True)
            print('Expo installed successfully.')
        else:
            print('Expo is already installed.')
    except subprocess.CalledProcessError as e:
        print(f'Failed to install expo: {e}')
        sys.exit(1)

def start_backend():
    print('Starting Django backend server...')
    backend_manage_py = os.path.join(PROJECT_ROOT, 'backend', 'manage.py')
    backend_process = subprocess.Popen([
        sys.executable, backend_manage_py, 'runserver', '0.0.0.0:8000'
    ], cwd=PROJECT_ROOT)
    return backend_process

def start_expo():
    print('Starting Expo development server with cache clear...')
    subprocess.run(['npx', 'expo', 'start', '--clear'], cwd=MOBILE_DIR, shell=True)

if __name__ == '__main__':
    # Kill any running Expo/React Native processes first
    # Temporarily disabled to fix startup issues
    # kill_expo_processes()
    
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
    
    clean_mobile()
    install_dependencies()
    backend_process = start_backend()
    try:
        start_expo()
    finally:
        print('Shutting down backend server...')
        backend_process.terminate() 