import os
import sys
import subprocess

MOBILE_DIR = os.path.join(os.path.dirname(__file__), 'restyle-mobile')
NODE_MODULES = os.path.join(MOBILE_DIR, 'node_modules')

print('--- Starting restyle-mobile app ---')

# Step 1: Change directory
def cd_mobile():
    os.chdir(MOBILE_DIR)
    print(f'Changed directory to {MOBILE_DIR}')

# Step 2: Install dependencies if needed
def ensure_dependencies():
    if not os.path.exists(NODE_MODULES):
        print('node_modules not found. Installing dependencies...')
        result = subprocess.run(['npm', 'install'], shell=True)
        if result.returncode != 0:
            print('npm install failed. Exiting.')
            sys.exit(1)
    else:
        print('Dependencies already installed.')

# Step 3: Start Expo server
def start_expo():
    print('Starting Expo development server...')
    subprocess.run(['npx', 'expo', 'start'], shell=True)

if __name__ == '__main__':
    cd_mobile()
    ensure_dependencies()
    start_expo() 