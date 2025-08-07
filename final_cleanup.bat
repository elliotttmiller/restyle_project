@echo off
echo.
echo =================================================
echo ==    Final Project Cleanup & Organization     ==
echo =================================================
echo.

REM Set the project root directory
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo --- Consolidating essential startup scripts into 'scripts/'...
if exist "startup_files\\setup_project.py" (
    move /y "startup_files\\setup_project.py" "scripts\\" > nul
    echo    Moved setup_project.py.
)
if exist "startup_files\\start_restyle.py" (
    move /y "startup_files\\start_restyle.py" "scripts\\" > nul
    echo    Moved start_restyle.py.
)

echo.
echo --- Removing redundant 'startup_files' directory...
if exist "startup_files" (
    rmdir /s /q "startup_files"
    echo    'startup_files' directory removed.
) else (
    echo    'startup_files' directory not found.
)

echo.
echo =================================================
echo ==         Final Cleanup Complete!           ==
echo =================================================
echo.
pause
