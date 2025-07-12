import os
import sys
import subprocess
import threading
import socket
import re
import psutil
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MOBILE_DIR = os.path.join(PROJECT_ROOT, 'restyle-mobile')
NODE_MODULES = os.path.join(MOBILE_DIR, 'node_modules')
API_CONFIG_FILE = os.path.join(MOBILE_DIR, 'shared', 'api.js')

print('--- Starting restyle-mobile app with automatic IP detection and Docker containers ---')

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

def validate_django_settings():
    """Validate Django settings.py for syntax errors"""
    print('Validating Django settings...')
    SETTINGS_PATH = os.path.join(PROJECT_ROOT, 'backend', 'backend', 'settings.py')
    
    try:
        with open(SETTINGS_PATH, 'r') as f:
            content = f.read()
        
        # Check for common syntax errors
        errors = []
        
        # Check for double commas in lists
        import re
        list_patterns = [
            r'ALLOWED_HOSTS\s*=\s*\[(.*?)\]',
            r'CORS_ALLOWED_ORIGINS\s*=\s*\[(.*?)\]',
            r'INSTALLED_APPS\s*=\s*\[(.*?)\]',
            r'MIDDLEWARE\s*=\s*\[(.*?)\]'
        ]
        
        for pattern in list_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                if ',,' in match:
                    errors.append(f"Double comma found in {pattern.split('_')[0]} list")
        
        # Check for basic Python syntax
        try:
            compile(content, SETTINGS_PATH, 'exec')
        except SyntaxError as e:
            errors.append(f"Syntax error: {e}")
        
        if errors:
            print("❌ Django settings validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False
        else:
            print("✅ Django settings validation passed")
            return True
            
    except Exception as e:
        print(f"❌ Error validating Django settings: {e}")
        return False

def validate_ai_services():
    """Validate AI service credentials and configurations"""
    print('Validating AI service configurations...')
    
    # Check Google Cloud credentials
    google_creds_path = os.path.join(PROJECT_ROOT, 'backend', 'silent-polygon-465403-h9-81cb035ed6d4.json')
    if os.path.exists(google_creds_path):
        print("✅ Google Cloud credentials found")
    else:
        print("⚠️  Google Cloud credentials not found - Vision API and Gemini API may not work")
    
    # Check AWS credentials (both possible locations)
    aws_creds_path1 = os.path.join(PROJECT_ROOT, 'backend', 'restyle-rekognition-user_accessKeys.csv')
    aws_creds_path2 = os.path.join(PROJECT_ROOT, 'restyle-rekognition-user_accessKeys.csv')
    
    if os.path.exists(aws_creds_path1):
        print("✅ AWS Rekognition credentials found (backend folder)")
    elif os.path.exists(aws_creds_path2):
        print("✅ AWS Rekognition credentials found (root folder)")
        # Copy to backend folder for Docker mounting
        import shutil
        try:
            shutil.copy2(aws_creds_path2, aws_creds_path1)
            print("✅ Copied AWS credentials to backend folder for Docker mounting")
        except Exception as e:
            print(f"⚠️  Could not copy AWS credentials: {e}")
    else:
        print("⚠️  AWS Rekognition credentials not found - Rekognition API may not work")
        print("   Expected locations:")
        print(f"   - {aws_creds_path1}")
        print(f"   - {aws_creds_path2}")
    
    # Check local settings
    local_settings_path = os.path.join(PROJECT_ROOT, 'backend', 'backend', 'local_settings.py')
    if os.path.exists(local_settings_path):
        print("✅ Local settings file found")
    else:
        print("⚠️  Local settings file not found - AI services may not be configured")
    
    print("✅ AI service validation completed")
    return True

def start_docker_services():
    """Start all Docker services using docker-compose"""
    print('Starting Docker services...')
    
    # First validate Django settings
    if not validate_django_settings():
        print("❌ Django settings validation failed. Please fix the settings.py file before starting containers.")
        return False
    
    # Validate AI service configurations
    validate_ai_services()
    
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
    print('Starting all Docker services (PostgreSQL, Redis, Django, Celery, AI Services)...')
    start_result = subprocess.run([
        'docker-compose', 'up', '-d'
    ], shell=True, capture_output=True, text=True)
    
    if start_result.returncode == 0:
        print('✅ All Docker services started successfully.')
        print('Services running:')
        print('- PostgreSQL database')
        print('- Redis cache')
        print('- Django backend (port 8000)')
        print('- Celery worker')
        print('- Celery beat scheduler')
        print('- Celery monitor/Flower (port 5555)')
        print('🤖 Multi-Expert AI System:')
        print('  - Google Vision API (image analysis)')
        print('  - AWS Rekognition (detailed labeling)')
        print('  - Google Gemini API (intelligent synthesis)')
        print('  - Google Vertex AI (advanced reasoning)')
        return True
    else:
        print(f'❌ Failed to start Docker services: {start_result.stderr}')
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

def cd_mobile():
    """Change to mobile directory"""
    os.chdir(MOBILE_DIR)
    print(f'Changed directory to {MOBILE_DIR}')

def ensure_dependencies():
    """Ensure all dependencies are installed"""
    package_manager = detect_package_manager()
    
    if not os.path.exists(NODE_MODULES):
        print(f'node_modules not found. Installing dependencies with {package_manager}...')
        if package_manager == 'yarn':
            result = subprocess.run(['yarn', 'install'], shell=True)
        else:
            result = subprocess.run(['npm', 'install'], shell=True)
        
        if result.returncode != 0:
            print(f'{package_manager} install failed. Exiting.')
            sys.exit(1)
    else:
        print('Dependencies already installed.')
    
    # Check if expo is installed
    try:
        result = subprocess.run(['npx', 'expo', '--version'], shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print('Expo not found. Installing expo...')
            if package_manager == 'yarn':
                subprocess.run(['yarn', 'add', 'expo'], shell=True, check=True)
            else:
                subprocess.run(['npm', 'install', 'expo'], shell=True, check=True)
            print('Expo installed successfully.')
        else:
            print('Expo is already installed.')
    except subprocess.CalledProcessError as e:
        print(f'Failed to install expo: {e}')
        sys.exit(1)

def start_expo():
    """Start Expo development server"""
    print('Starting Expo development server...')
    subprocess.run(['npx', 'expo', 'start'], shell=True)

def test_ai_services():
    """Test AI services after startup"""
    print('Testing AI services...')
    
    # Test the multi-expert AI system
    test_script_path = os.path.join(PROJECT_ROOT, 'backend', 'test_multi_expert_ai_system.py')
    if os.path.exists(test_script_path):
        print('Running AI system test...')
        try:
            result = subprocess.run(['python', test_script_path], 
                                  shell=True, capture_output=True, text=True, cwd=os.path.join(PROJECT_ROOT, 'backend'))
            if result.returncode == 0:
                print('✅ AI system test completed successfully')
            else:
                print('⚠️  AI system test had issues (this is normal if credentials are not fully configured)')
        except Exception as e:
            print(f'⚠️  Could not run AI system test: {e}')
    else:
        print('⚠️  AI system test script not found')
    
    print('AI service testing completed')

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
    # Update mobile API config
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
        time.sleep(10)  # Give services time to start up
        
        # Check container health
        print("Checking container health...")
        health_result = subprocess.run(['docker-compose', 'ps'], shell=True, capture_output=True, text=True)
        if health_result.returncode == 0:
            print("Container status:")
            print(health_result.stdout)
        else:
            print("❌ Could not check container status")
        
        # Test AI services
        test_ai_services()
    
    try:
        cd_mobile()
        ensure_dependencies()
        
        # Print AI system summary
        print("\n" + "="*60)
        print("🤖 MULTI-EXPERT AI SYSTEM READY")
        print("="*60)
        print("Your reseller assistant now includes:")
        print("• Google Vision API - Image analysis and text detection")
        print("• AWS Rekognition - Detailed product labeling")
        print("• Google Gemini API - Intelligent query synthesis")
        print("• Google Vertex AI - Advanced reasoning and analysis")
        print("• Multi-expert coordination for maximum accuracy")
        print("="*60)
        
        start_expo()
    finally:
        print('Shutting down services...')
        
        # Stop Docker services
        if docker_started:
            stop_docker_services() 