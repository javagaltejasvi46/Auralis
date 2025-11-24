@echo off
echo ========================================
echo Set Gemini API Key
echo ========================================
echo.
echo Please enter your Gemini API key:
echo (Get it from: https://makersuite.google.com/app/apikey)
echo.
set /p APIKEY="API Key: "

echo.
echo Setting environment variable...
setx GEMINI_API_KEY "%APIKEY%"

echo.
echo ========================================
echo ✅ API Key Set Successfully!
echo ========================================
echo.
echo The key will be available in new terminal windows.
echo.
echo Next steps:
echo 1. Close this window
echo 2. Open a new terminal
echo 3. Run: python backend/main.py
echo.
pause
