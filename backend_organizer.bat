@echo off
echo.
echo =================================================
echo ==     Backend Directory Organizer Script      ==
echo =================================================
echo.
echo This script uses 'git' to move and remove files from the 'backend'
echo directory, staging the changes for your review before committing.
echo.

REM Set the project root directory
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo --- (1/3) Consolidating test files from 'backend/' to 'test_files/'...
git mv backend/test_ai_integration.py test_files/
git mv backend/test_ebay_integration.py test_files/
git mv backend/test_ebay_search_simple.py test_files/
git mv backend/test_external.py test_files/
git mv backend/test_multi_expert_ai_system.py test_files/
git mv backend/test_railway_endpoints.py test_files/
echo    Test files moved.

echo.
echo --- (2/3) Moving documentation to 'readme_files/'...
git mv backend/fix_aws_permissions.md readme_files/
echo    Documentation moved.

echo.
echo --- (3/3) Removing redundant and temporary files from 'backend/'...
git rm -f backend/simple_start.py
git rm -f backend/start.py
git rm -f backend/railway_start.sh
git rm -f backend/celerybeat-schedule
git rm -f backend/debug.log
git rm -f backend/debug_tail.log
git rm -f backend/ebay_refresh_token.txt
echo    Redundant files removed.

echo.
echo =================================================
echo ==      Backend Organization Complete!         ==
echo =================================================
echo.
echo Please run 'git status' to review the changes.
echo.
pause
