@echo off
echo.
echo =================================================
echo ==      Restyle Project Organizer Script       ==
echo =================================================
echo.
echo This script uses 'git' to move and remove files,
echo staging the changes for your review before committing.
echo.

REM Set the project root directory
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo --- (1/5) Creating 'scripts' directory...
if not exist "scripts" (
    mkdir "scripts"
    echo    'scripts' directory created.
) else (
    echo    'scripts' directory already exists.
)

echo.
echo --- (2/5) Moving utility scripts into 'scripts/'...
git mv build_and_submit.py scripts/
git mv setup_credentials.py scripts/
git mv ngrok.exe scripts/
echo    Utility scripts moved.

echo.
echo --- (3/5) Moving mobile config files into 'restyle-mobile/'...
git mv app.json restyle-mobile/
git mv babel.config.js restyle-mobile/
git mv eas.json restyle-mobile/
git mv metro.config.js restyle-mobile/
git mv tsconfig.json restyle-mobile/
echo    Mobile config files moved.

echo.
echo --- (4/5) Consolidating test files...
git mv test_railway_startup.py test_files/
echo    Test file moved.

echo.
echo --- (5/5) Removing redundant and temporary files from root...
git rm -f __init__.py
git rm -f all_python_files.txt
git rm -f bfg-1.14.0.jar
git rm -f bfg-secrets.txt
git rm -f codespell_report.txt
git rm -f db.sqlite3
git rm -f debug.log
git rm -f shutdown.log
git rm -f requirements.txt
git rm -f restyle-ai-driven.txt
git rm -r -f curl
echo    Redundant files removed.

echo.
echo =================================================
echo ==         Organization Complete!              ==
echo =================================================
echo.
echo Please run 'git status' to review the changes.
echo All moved and deleted files are staged for your next commit.
echo.
pause
