import subprocess
import requests
import time
import os
import sys
import re

NGROK_PATH = os.path.join(os.getcwd(), "ngrok.exe")
PORT = 8000  # Change if needed
API_JS_PATH = os.path.join(os.getcwd(), "restyle-mobile", "shared", "api.js")
EXPO_START_SCRIPT = os.path.join(os.getcwd(), "restyle-mobile", "start-expo.bat")


def start_ngrok(port):
    try:
        requests.get("http://127.0.0.1:4040/api/tunnels")
        print("ngrok is already running.")
    except requests.ConnectionError:
        print(f"Starting ngrok on port {port}...")
        subprocess.Popen([NGROK_PATH, "http", str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        time.sleep(3)

def get_ngrok_url():
    for _ in range(10):
        try:
            tunnels = requests.get("http://127.0.0.1:4040/api/tunnels").json()["tunnels"]
            for tunnel in tunnels:
                if tunnel["proto"] == "https":
                    return tunnel["public_url"]
        except Exception:
            pass
        time.sleep(1)
    return None

def update_mobile_api_url(new_url):
    if not os.path.exists(API_JS_PATH):
        print(f"ERROR: {API_JS_PATH} not found.")
        return False
    with open(API_JS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    # Replace the API_BASE_URL line
    new_content, count = re.subn(
        r'export const API_BASE_URL = "https://.*?";',
        f'export const API_BASE_URL = "{new_url}";',
        content
    )
    if count == 0:
        print("ERROR: API_BASE_URL line not found in api.js.")
        return False
    with open(API_JS_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated API_BASE_URL in {API_JS_PATH} to {new_url}")
    return True

def start_expo():
    if os.path.exists(EXPO_START_SCRIPT):
        print("Starting Expo app...")
        subprocess.Popen([EXPO_START_SCRIPT], shell=True)
    else:
        print(f"Expo start script not found at {EXPO_START_SCRIPT}. Please start Expo manually.")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    start_ngrok(port)
    url = get_ngrok_url()
    if url:
        print(f"ngrok public URL: {url}")
        if update_mobile_api_url(url):
            start_expo()
        else:
            print("Failed to update mobile API URL. Expo not started.")
    else:
        print("Failed to get ngrok public URL. Expo not started.") 