@echo off
echo ========================================
echo Therapy Model Fine-Tuning
echo ========================================
echo.

cd backend
python quick_finetune.py

echo.
echo Press any key to exit...
pause >nul
