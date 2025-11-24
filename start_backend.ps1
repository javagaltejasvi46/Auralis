# AURALIS Backend Startup Script (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AURALIS Backend Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to backend directory
Set-Location backend

Write-Host "[1/3] Running auto-configuration..." -ForegroundColor Yellow
python auto_config.py
Write-Host ""

Write-Host "[2/3] Starting main API server (port 8002)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python main.py" -WindowStyle Normal
Start-Sleep -Seconds 3

Write-Host "[3/3] Starting transcription server (port 8003)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python transcription_server.py" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ All backend services started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "API Server: http://localhost:8002" -ForegroundColor White
Write-Host "Transcription: ws://localhost:8003" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit this window..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
