#!/usr/bin/env python3
"""
Test Files Cleanup Script
Removes redundant, duplicate, and obsolete test files from test_files directory.
"""

import os
import shutil
from pathlib import Path

# Files to DELETE (redundant/duplicate/obsolete)
FILES_TO_DELETE = [
    # Token/Auth Duplicates
    "test_token_refresh_system.py",
    "test_token_refresh_integration.py", 
    "test_jwt_refresh_integration.py",
    "test_jwt_refresh_simple.py",
    "test_ebay_token.py",
    "test_new_token.py",
    
    # eBay API Duplicates
    "test_ebay_api.py",
    "test_ebay_browse_api.py", 
    "test_ebay_integration.py",
    "test_ebay_search.py",
    "test_ebay_setup_simple.py",
    "get_ebay_refresh_token.py",
    
    # Search/Endpoint Duplicates
    "test_search.py",
    "test_search_endpoint.py",
    "test_search_with_auth.py", 
    "test_authn_auth_search.py",
    "test_analysis_pagination.py",
    
    # AI Service Duplicates
    "test_ai_integration.py",
    "test_ai_endpoint.py",
    "test_ai_search_terms.py",
    "test_enhanced_ai.py",
    
    # Utility/Misc Files
    "register_railway_user.py",
    "test_verification.py",
    "test_rate_limits.py", 
    "test_management_command.py",
    "test_env_credentials.py",
    "test_ai_crop_preview.py",
    "test_gemini_diagnosis.py"
]

# Files to KEEP (essential/current)
FILES_TO_KEEP = [
    "test_mobile_ai_accuracy.py",      # Mobile app simulation test
    "test_multi_expert_ai.py",         # Multi-expert AI system test  
    "test_ai_services_fix.py",         # AI services verification
    "test_railway_login.py",           # Railway backend auth
    "test_image_upload.py",            # Image upload functionality
    "test_monitoring_system.py",       # Monitoring system test
    "test_ebay_configuration.py",      # Main eBay setup test
    "example2.jpg"                     # Test image file
]

def cleanup_test_files():
    """Remove redundant test files and keep only essential ones."""
    
    test_files_dir = Path("C:/Users/AMD/restyle_project/test_files")
    
    if not test_files_dir.exists():
        print(f"❌ Test files directory not found: {test_files_dir}")
        return
    
    print("🧹 CLEANING UP TEST FILES")
    print("=" * 50)
    print(f"Directory: {test_files_dir}")
    print()
    
    deleted_count = 0
    kept_count = 0
    errors = []
    
    # Get all files in directory
    all_files = [f.name for f in test_files_dir.iterdir() if f.is_file()]
    
    print("📋 ANALYSIS:")
    print(f"Total files found: {len(all_files)}")
    print(f"Files to delete: {len(FILES_TO_DELETE)}")
    print(f"Files to keep: {len(FILES_TO_KEEP)}")
    print()
    
    # Delete redundant files
    print("🗑️  DELETING REDUNDANT FILES:")
    for filename in FILES_TO_DELETE:
        file_path = test_files_dir / filename
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"✅ Deleted: {filename}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error deleting {filename}: {e}")
                errors.append(f"{filename}: {e}")
        else:
            print(f"⚠️  Not found: {filename}")
    
    print()
    print("✅ KEEPING ESSENTIAL FILES:")
    for filename in FILES_TO_KEEP:
        file_path = test_files_dir / filename
        if file_path.exists():
            print(f"✅ Kept: {filename}")
            kept_count += 1
        else:
            print(f"⚠️  Essential file missing: {filename}")
    
    # Check for any unexpected files
    remaining_files = [f.name for f in test_files_dir.iterdir() if f.is_file()]
    unexpected_files = set(remaining_files) - set(FILES_TO_KEEP)
    
    if unexpected_files:
        print()
        print("⚠️  UNEXPECTED FILES FOUND:")
        for filename in unexpected_files:
            print(f"   - {filename}")
    
    print()
    print("📊 CLEANUP SUMMARY:")
    print(f"✅ Files deleted: {deleted_count}")
    print(f"✅ Files kept: {kept_count}")
    print(f"❌ Errors: {len(errors)}")
    
    if errors:
        print()
        print("❌ ERRORS:")
        for error in errors:
            print(f"   - {error}")
    
    print()
    print("🎉 TEST FILES CLEANUP COMPLETE!")
    print()
    print("📁 REMAINING TEST STRUCTURE:")
    print("├── test_mobile_ai_accuracy.py     # Mobile app simulation")
    print("├── test_multi_expert_ai.py        # Multi-expert AI system")  
    print("├── test_ai_services_fix.py        # AI services verification")
    print("├── test_railway_login.py          # Railway backend auth")
    print("├── test_image_upload.py           # Image upload test")
    print("├── test_monitoring_system.py      # Monitoring system")
    print("├── test_ebay_configuration.py     # eBay setup & config")
    print("└── example2.jpg                   # Test image")

if __name__ == "__main__":
    cleanup_test_files()
