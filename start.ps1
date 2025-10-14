# Expense Tracker Startup Script
Write-Host "🚀 Starting Expense Tracker Web Application..." -ForegroundColor Green
Write-Host ""
Write-Host "📍 The application will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "👤 NEW: User authentication is now required!" -ForegroundColor Magenta
Write-Host "🆕 New users: Register a new account" -ForegroundColor Green
Write-Host "🔐 Demo account: demo / demo123" -ForegroundColor Yellow
Write-Host "⏹️  Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Get the directory where this script is located
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptPath

# Start the Flask application
python app.py