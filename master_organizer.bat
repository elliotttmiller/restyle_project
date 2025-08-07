@echo off
echo.
echo =================================================
echo ==      Master Project Organizer Script        ==
echo =================================================
echo.

REM Set the project root directory
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo --- (1/4) Moving utility scripts into 'scripts/'...
if not exist "scripts" mkdir "scripts"
move /y "build_and_submit.py" "scripts\" > nul
move /y "check_ai_services.py" "scripts\" > nul
move /y "cleanup_test_files.py" "scripts\" > nul
move /y "deploy_production.sh" "scripts\" > nul
move /y "setup_credentials.py" "scripts\" > nul
move /y "setup_ios_icons.py" "scripts\" > nul
move /y "simple_railway_test.py" "scripts\" > nul
move /y "verify_app_icon_setup.py" "scripts\" > nul
move /y "ngrok.exe" "scripts\" > nul
echo    Utility scripts moved.

echo.
echo --- (2/4) Moving test files into 'test_files/'...
if not exist "test_files" mkdir "test_files"
for %%f in (test_*.py test_*.js test_*.sh) do (
    if exist "%%f" (
        move /y "%%f" "test_files\" > nul
    )
)
echo    Test files moved.

echo.
echo --- (3/4) Moving mobile config files into 'restyle-mobile/'...
if not exist "restyle-mobile" mkdir "restyle-mobile"
move /y "app.json" "restyle-mobile\" > nul
move /y "babel.config.js" "restyle-mobile\" > nul
move /y "eas.json" "restyle-mobile\" > nul
move /y "metro.config.js" "restyle-mobile\" > nul
echo    Mobile config files moved.

echo.
echo --- (4/4) Deleting obsolete organizer scripts...
del /f /q "cleanup.bat" > nul
del /f /q "backend_organizer.bat" > nul
del /f /q "project_organizer.bat" > nul
del /f /q "final_cleanup.bat" > nul
del /f /q "master_organizer.bat" > nul
echo    Obsolete scripts removed.

echo.
echo =================================================
echo ==      Master Organization Complete!          ==
echo =================================================
echo.
pause
