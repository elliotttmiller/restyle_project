#!/usr/bin/env python3
"""
Secure Credential Setup Script
This script helps you set up credentials without committing them to git.
"""

import os
import shutil
from pathlib import Path

def setup_credentials():
    """Set up credentials securely"""
    print("🔐 SECURE CREDENTIAL SETUP")
    print("=" * 50)
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file from template...")
        if Path("env.template").exists():
            shutil.copy("env.template", ".env")
            print("✅ .env file created from template")
            print("📋 Please edit .env with your real credentials")
        else:
            print("❌ env.template not found")
            return False
    
    # Check if local_settings.py exists
    local_settings = Path("backend/backend/local_settings.py")
    if not local_settings.exists():
        print("📝 Creating local_settings.py from template...")
        template = Path("backend/backend/local_settings_template.py")
        if template.exists():
            shutil.copy(template, local_settings)
            print("✅ local_settings.py created from template")
            print("📋 Please edit backend/backend/local_settings.py with your real credentials")
        else:
            print("❌ local_settings_template.py not found")
            return False
    
    print("\n✅ CREDENTIAL SETUP COMPLETE")
    print("📋 Next steps:")
    print("   1. Edit .env with your real credentials")
    print("   2. Edit backend/backend/local_settings.py with your real credentials")
    print("   3. Place your credential files in the project root:")
    print("      - Google Cloud JSON file")
    print("      - AWS credentials CSV file")
    print("   4. Update the paths in your config files")
    print("\n🔒 Your credentials are now protected by .gitignore")
    print("🚀 You can now commit and push safely!")
    
    return True

def check_gitignore():
    """Check if .gitignore is properly configured"""
    gitignore = Path(".gitignore")
    if not gitignore.exists():
        print("❌ .gitignore not found")
        return False
    
    with open(gitignore, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    
    required_patterns = [
        '.env', '*.json', '*.csv', '__pycache__/', '*credentials*', '*secret*', 'backend/backend/local_settings.py'
    ]
    missing = []
    
    for pattern in required_patterns:
        if pattern not in lines:
            missing.append(pattern)
    
    if missing:
        print(f"⚠️  Missing patterns in .gitignore: {missing}")
        return False
    
    print("✅ .gitignore is properly configured")
    return True

if __name__ == "__main__":
    print("🔍 Checking gitignore configuration...")
    if check_gitignore():
        setup_credentials()
    else:
        print("❌ Please fix .gitignore before setting up credentials") 