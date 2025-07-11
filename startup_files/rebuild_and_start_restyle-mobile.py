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

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MOBILE_DIR = os.path.join(PROJECT_ROOT, 'restyle-mobile')
NODE_MODULES = os.path.join(MOBILE_DIR, 'node_modules')
API_CONFIG_FILE = os.path.join(MOBILE_DIR, 'shared', 'api.js')

print('--- Rebuilding and Starting restyle-mobile app with automatic IP detection and Docker containers ---')

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

def start_docker_services():
    """Start all Docker services using docker-compose"""
    print('Starting Docker services...')
    
    # Check if Docker is available
    try:
        result = subprocess.run(['docker', '--version'], shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print('Docker not found. Skipping container startup.')
            return False
    except:
        print('Docker not found. Skipping container startup.')
        return False
    
    # Check if docker-compose is available
    try:
        result = subprocess.run(['docker-compose', '--version'], shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print('docker-compose not found. Skipping container startup.')
            return False
    except:
        print('docker-compose not found. Skipping container startup.')
        return False
    
    # Start all services using docker-compose
    print('Starting all Docker services (PostgreSQL, Redis, Django, Celery)...')
    start_result = subprocess.run([
        'docker-compose', 'up', '-d'
    ], shell=True, capture_output=True, text=True)
    
    if start_result.returncode == 0:
        print('All Docker services started successfully.')
        print('Services running:')
        print('- PostgreSQL database')
        print('- Redis cache')
        print('- Django backend (port 8000)')
        print('- Celery worker')
        print('- Celery beat scheduler')
        print('- Celery monitor/Flower (port 5555)')
        return True
    else:
        print(f'Failed to start Docker services: {start_result.stderr}')
        return False

def stop_docker_services():
    """Stop all Docker services"""
    print('Stopping Docker services...')
    subprocess.run(['docker-compose', 'down'], shell=True)
    print('Docker services stopped.')

def detect_package_manager():
    """Detect which package manager to use (npm or yarn)"""
    # Check if yarn is available and preferred
    try:
        yarn_result = subprocess.run(['yarn', '--version'], shell=True, capture_output=True, text=True)
        if yarn_result.returncode == 0:
            # Check if yarn.lock exists
            yarn_lock_path = os.path.join(MOBILE_DIR, 'yarn.lock')
            if os.path.exists(yarn_lock_path):
                print('Detected yarn.lock - using yarn package manager')
                return 'yarn'
    except:
        pass
    
    # Default to npm
    print('Using npm package manager')
    return 'npm'

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
    package_manager = detect_package_manager()
    
    if package_manager == 'yarn':
        result = subprocess.run(['yarn', 'install'], cwd=MOBILE_DIR, shell=True)
    else:
        result = subprocess.run(['npm', 'install'], cwd=MOBILE_DIR, shell=True)
    
    if result.returncode != 0:
        print(f'{package_manager} install failed. Exiting.')
        sys.exit(1)
    
    # Check if expo is installed
    try:
        result = subprocess.run(['npx', 'expo', '--version'], cwd=MOBILE_DIR, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print('Expo not found. Installing expo...')
            if package_manager == 'yarn':
                subprocess.run(['yarn', 'add', 'expo'], cwd=MOBILE_DIR, shell=True, check=True)
            else:
                subprocess.run(['npm', 'install', 'expo'], cwd=MOBILE_DIR, shell=True, check=True)
            print('Expo installed successfully.')
        else:
            print('Expo is already installed.')
    except subprocess.CalledProcessError as e:
        print(f'Failed to install expo: {e}')
        sys.exit(1)

def start_expo():
    """Start Expo development server"""
    print('Starting Expo development server with cache clear...')
    subprocess.run(['npx', 'expo', 'start', '--clear'], cwd=MOBILE_DIR, shell=True)

if __name__ == '__main__':
    # Detect and configure IP address
    print("Detecting current IP address...")
    current_ip = get_local_ip()

    # --- NEW: Update backend settings.py with current IP ---
    SETTINGS_PATH = os.path.join(PROJECT_ROOT, 'backend', 'backend', 'settings.py')
    if current_ip:
        print(f"Detected IP address: {current_ip}")
        # Read settings.py
        with open(SETTINGS_PATH, 'r') as f:
            settings_content = f.read()
        changed = False
        # Update ALLOWED_HOSTS
        allowed_hosts_pattern = r"ALLOWED_HOSTS\s*=\s*\[(.*?)\]"
        match = re.search(allowed_hosts_pattern, settings_content, re.DOTALL)
        if match:
            allowed_hosts_str = match.group(1)
            if f"'{current_ip}'" not in allowed_hosts_str:
                # Insert before last ]
                new_hosts = allowed_hosts_str.strip() + f", '{current_ip}'"
                settings_content = re.sub(allowed_hosts_pattern,
                    f"ALLOWED_HOSTS = [{new_hosts}]", settings_content, flags=re.DOTALL)
                changed = True
        # Update CORS_ALLOWED_ORIGINS
        cors_pattern = r"CORS_ALLOWED_ORIGINS\s*=\s*\[(.*?)\]"
        match = re.search(cors_pattern, settings_content, re.DOTALL)
        cors_url = f'"http://{current_ip}:8000"'
        if match:
            cors_str = match.group(1)
            if cors_url not in cors_str:
                new_cors = cors_str.strip() + f", {cors_url}"
                settings_content = re.sub(cors_pattern,
                    f"CORS_ALLOWED_ORIGINS = [{new_cors}]", settings_content, flags=re.DOTALL)
                changed = True
        if changed:
            with open(SETTINGS_PATH, 'w') as f:
                f.write(settings_content)
            print(f"Updated backend/settings.py with IP: {current_ip}")
        else:
            print(f"backend/settings.py already contains IP: {current_ip}")
    else:
        print("Warning: Could not detect IP address. Using existing configuration.")
    # --- END NEW ---
    if current_ip:
        if update_api_config(current_ip):
            print("API configuration updated successfully!")
        else:
            print("Warning: Failed to update API configuration")
    else:
        print("Warning: Could not detect IP address. Using existing configuration.")
    
    # Start Docker services
    docker_started = start_docker_services()
    
    if docker_started:
        print("Waiting for Docker services to be ready...")
        time.sleep(15)  # Give services more time to start up for rebuild
    
    # Clean and install dependencies
    clean_mobile()
    install_dependencies()
    
    try:
        start_expo()
    finally:
        print('Shutting down services...')
        
        # Stop Docker services
        if docker_started:
            stop_docker_services() 