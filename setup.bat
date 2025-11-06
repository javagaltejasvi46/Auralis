@echo off
echo Setting up Audio Recording App...
echo.

echo [1/4] Setting up Python Backend...
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo.
echo [2/4] Setting up React Native Frontend...
cd frontend
call npm install
cd ..

echo.
echo [3/4] Creating database tables...
cd backend
python -c "from models import create_tables; create_tables(); print('Database tables created successfully')"
cd ..

echo.
echo [4/4] Setup complete!
echo.
echo To start development:
echo 1. Run start-dev.bat
echo 2. Install Expo Go on your phone
echo 3. Scan the QR code to test the app
echo.
echo Backend will be available at: http://localhost:8000
echo API docs will be available at: http://localhost:8000/docs
echo.
pause