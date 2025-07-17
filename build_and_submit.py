import os
import subprocess
import requests
import time
import json
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env
env_path = find_dotenv()
if env_path:
    print(f"Loading environment variables from {env_path}")
    load_dotenv(env_path)
else:
    print("No .env file found. Using system environment variables.")

# Helper to get env vars with error if missing
def get_env_var(key):
    value = os.environ.get(key)
    if not value:
        print(f"❌ Missing required environment variable: {key}")
        exit(1)
    return value

EXPO_TOKEN = get_env_var("EXPO_TOKEN")
APPLE_ID = get_env_var("APPLE_ID")
APPLE_APP_SPECIFIC_PASSWORD = get_env_var("APPLE_APP_SPECIFIC_PASSWORD")

# Allow EAS_PATH to be set in .env, fallback to default
EAS_PATH = os.environ.get("EAS_PATH", r"C:\Users\AMD\AppData\Roaming\npm\eas.cmd")

# 1. Start EAS build for iOS production
print("\n=== Starting EAS Build (iOS, production) ===")
build_cmd = [
    EAS_PATH, "build", "-p", "ios", "--profile", "production", "--non-interactive", "--json"
]
build_proc = subprocess.run(build_cmd, capture_output=True, text=True, env={**os.environ, "EXPO_TOKEN": EXPO_TOKEN})
if build_proc.returncode != 0:
    print("EAS build failed!")
    print("STDOUT:\n", build_proc.stdout)
    print("STDERR:\n", build_proc.stderr)
    exit(1)
try:
    build_info = json.loads(build_proc.stdout)
    if isinstance(build_info, list):
        build_data = build_info[0]
    else:
        build_data = build_info
    build_id = build_data["id"].strip('{}')
except Exception as e:
    print("Failed to parse EAS build output:", e)
    print(build_proc.stdout)
    exit(1)

# 2. Poll for build status
print(f"\n=== Polling for build completion (build id: {build_id}) ===")
build_status_url = f"https://api.expo.dev/v2/builds/{build_id}"
headers = {"Authorization": f"Bearer {EXPO_TOKEN}"}
while True:
    resp = requests.get(build_status_url, headers=headers)
    if resp.status_code != 200 or not resp.text.strip():
        print(f"Failed to get build status (HTTP {resp.status_code}): {resp.text}")
        time.sleep(10)
        continue
    try:
        status_data = resp.json()
    except Exception as e:
        print(f"Failed to parse build status JSON: {e}")
        print("Response text:", resp.text)
        time.sleep(10)
        continue
    if isinstance(status_data, list):
        status_data = status_data[0]
    status = status_data.get("status")
    print(f"Build status: {status}")
    if status == "finished" or status == "FINISHED":
        download_url = status_data["artifacts"]["buildUrl"]
        print(f"Build finished! Download URL: {download_url}")
        break
    elif status in ["errored", "canceled", "ERRORED", "CANCELED"]:
        print("Build failed or was canceled.")
        exit(1)
    time.sleep(30)

# 3. Download the .ipa file
print("\n=== Downloading .ipa file ===")
ipa_response = requests.get(download_url)
ipa_path = "app.ipa"
with open(ipa_path, "wb") as f:
    f.write(ipa_response.content)
print(f"Downloaded .ipa to {ipa_path}")

# 4. Submit to App Store Connect using EAS Submit
print("\n=== Submitting to App Store Connect ===")
submit_cmd = [
    EAS_PATH, "submit", "-p", "ios", "--latest", "--non-interactive"
]
submit_env = {
    **os.environ,
    "EXPO_TOKEN": EXPO_TOKEN,
    "APPLE_ID": APPLE_ID,
    "APPLE_APP_SPECIFIC_PASSWORD": APPLE_APP_SPECIFIC_PASSWORD
}
submit_proc = subprocess.run(submit_cmd, env=submit_env)
if submit_proc.returncode == 0:
    print("\n✅ Build submitted to App Store Connect!")
else:
    print("\n❌ EAS submit failed.") 