import os
import sys
import subprocess
import json
import shutil
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MOBILE_DIR = PROJECT_ROOT / 'restyle-mobile'
PACKAGE_JSON = MOBILE_DIR / 'package.json'

LATEST_EXPO_SDK = None
LATEST_REACT = None
LATEST_REACT_NATIVE = None

# Utility functions

def run(cmd, cwd=None, check=True):
    print(f"\n>>> Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        sys.exit(1)
    return result

def fetch_latest_versions():
    """Fetch latest Expo SDK, React, and React Native versions from npm registry."""
    import requests
    global LATEST_EXPO_SDK, LATEST_REACT, LATEST_REACT_NATIVE
    print("Fetching latest Expo SDK version...")
    expo_resp = requests.get('https://registry.npmjs.org/expo')
    expo_data = expo_resp.json()
    LATEST_EXPO_SDK = expo_data['dist-tags']['latest']
    print(f"Latest Expo SDK: {LATEST_EXPO_SDK}")
    # Fetch Expo SDK compatibility table
    compat_resp = requests.get('https://raw.githubusercontent.com/expo/expo/main/packages/expo/sdk/version-mapping.json')
    if compat_resp.status_code == 200:
        compat = compat_resp.json()
        if LATEST_EXPO_SDK in compat:
            LATEST_REACT = compat[LATEST_EXPO_SDK]['react']
            LATEST_REACT_NATIVE = compat[LATEST_EXPO_SDK]['react-native']
            print(f"Expo SDK {LATEST_EXPO_SDK} requires:")
            print(f"  react: {LATEST_REACT}")
            print(f"  react-native: {LATEST_REACT_NATIVE}")
        else:
            print("Could not find compatibility info for latest SDK. Using npm registry...")
            react_resp = requests.get('https://registry.npmjs.org/react')
            rn_resp = requests.get('https://registry.npmjs.org/react-native')
            LATEST_REACT = react_resp.json()['dist-tags']['latest']
            LATEST_REACT_NATIVE = rn_resp.json()['dist-tags']['latest']
    else:
        print("Could not fetch Expo compatibility table. Using npm registry...")
        react_resp = requests.get('https://registry.npmjs.org/react')
        rn_resp = requests.get('https://registry.npmjs.org/react-native')
        LATEST_REACT = react_resp.json()['dist-tags']['latest']
        LATEST_REACT_NATIVE = rn_resp.json()['dist-tags']['latest']
    print(f"Using react: {LATEST_REACT}, react-native: {LATEST_REACT_NATIVE}")

def update_package_json():
    print(f"Updating {PACKAGE_JSON} with latest Expo/React/React Native versions...")
    with open(PACKAGE_JSON, 'r') as f:
        pkg = json.load(f)
    pkg['dependencies']['expo'] = LATEST_EXPO_SDK
    pkg['dependencies']['react'] = LATEST_REACT
    pkg['dependencies']['react-native'] = LATEST_REACT_NATIVE
    with open(PACKAGE_JSON, 'w') as f:
        json.dump(pkg, f, indent=2)
    print("package.json updated.")

def clean_project():
    print("Cleaning node_modules, .expo, and lock files...")
    for folder in ['node_modules', '.expo']:
        path = MOBILE_DIR / folder
        if path.exists():
            shutil.rmtree(path)
            print(f"Deleted {path}")
    for lockfile in ['package-lock.json', 'yarn.lock']:
        path = MOBILE_DIR / lockfile
        if path.exists():
            path.unlink()
            print(f"Deleted {path}")

def main():
    print("\n=== Automated Expo/React Native Upgrade & Sync ===\n")
    os.chdir(MOBILE_DIR)
    fetch_latest_versions()
    update_package_json()
    clean_project()
    print("\nInstalling/updating dependencies with npx expo install...")
    run('npx expo install')
    print("\nRunning npx expo doctor to check for issues...")
    doctor = run('npx expo doctor', check=False)
    if 'should be updated' in doctor.stdout or 'outdated dependencies' in doctor.stdout or doctor.returncode != 0:
        print("\nDetected issues. Attempting to auto-fix with another npx expo install...")
        run('npx expo install')
    print("\nStarting Expo with cache clear...")
    run('npx expo start -c', check=False)
    print("\n=== Upgrade & Sync Complete ===")
    print("If you see any errors above, please review them and let the AI assistant know!")

if __name__ == '__main__':
    main() 