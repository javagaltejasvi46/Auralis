@echo off
echo Starting Audio Recording App Development Environment...
echo.

echo [1/2] Starting FastAPI Backend...
start "FastAPI Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak > nul

echo [2/2] Starting React Native Frontend...
start "React Native Frontend" cmd /k "cd frontend && npx expo start"

echo.
echo Development servers are starting...
echo Backend: http://localhost:8000
echo Frontend: Use Expo Go app to scan QR code
echo.
pause