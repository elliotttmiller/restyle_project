# Test script for credential validation
from backend.core.credential_manager import credential_manager

if __name__ == "__main__":
    status = credential_manager.get_status()
    print("Credential Manager Status:")
    for key, value in status.items():
        print(f"  {key}: {value}") 