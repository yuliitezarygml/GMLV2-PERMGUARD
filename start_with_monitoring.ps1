# SwaWeb Server with PermGuard Monitoring Launcher
# PowerShell версия

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "       SWAWEB SERVER WITH PERMGUARD MONITORING" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# Проверить наличие Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python not found in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Проверить наличие файлов
$requiredFiles = @("app.py", "permguard_monitor.py", "permguard_auth.py")

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ Found: $file" -ForegroundColor Green
    } else {
        Write-Host "❌ ERROR: $file not found" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "🚀 Starting Flask server..." -ForegroundColor Yellow

# Запустить Flask сервер в новом окне PowerShell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python app.py; Write-Host 'Flask server stopped. Press any key to close...' -ForegroundColor Red; Read-Host"

# Пауза для запуска сервера
Start-Sleep -Seconds 3

Write-Host "📊 Starting PermGuard monitor..." -ForegroundColor Yellow

# Запустить монитор PermGuard в новом окне PowerShell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python permguard_monitor.py"

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "🎉 Both windows started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Window 1: Flask Server (http://localhost:5000)" -ForegroundColor White
Write-Host "📊 Window 2: PermGuard Real-time Monitor" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Open http://localhost:5000/admin/traffic to see traffic monitoring" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to close this launcher..." -ForegroundColor Gray
Write-Host "===============================================" -ForegroundColor Cyan

Read-Host