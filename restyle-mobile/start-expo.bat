@echo off
cd /d "%~dp0"
set EXPO_PROJECT_ROOT=%CD%
echo Starting Expo from: %CD%
echo Project root: %EXPO_PROJECT_ROOT%
npx expo start --clear 