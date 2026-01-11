<#
run-app.ps1

Starts the FoodSnap backend server with FastAPI/uvicorn.

Usage: In PowerShell:
  powershell -ExecutionPolicy Bypass -File run-app.ps1
#>

$ErrorActionPreference = 'Stop'

Write-Host "🍕 Starting FoodSnap Application..." -ForegroundColor Green

try {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
    Set-Location $ScriptDir

    # Check if backend directory exists
    if (-not (Test-Path "backend\main.py")) {
        Write-Host "❌ Error: backend\main.py not found!" -ForegroundColor Red
        Write-Host "Make sure you're running this from the soru-thinu-app directory" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Change to backend directory
    Set-Location backend
    Write-Host "📂 Changed to backend directory" -ForegroundColor Cyan

    # Find Python executable
    $python = "python"
    $pythonPath = "C:/Users/Varun/python.exe"
    if (Test-Path $pythonPath) {
        $python = $pythonPath
    }

    # Check dependencies
    Write-Host "📦 Checking dependencies..." -ForegroundColor Cyan
    $checkCmd = "& '$python' -c 'import fastapi, uvicorn' 2>$null"
    $result = Invoke-Expression $checkCmd
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Missing dependencies! Installing..." -ForegroundColor Red
        & $python -m pip install -r requirements.txt
    } else {
        Write-Host "✅ Dependencies OK" -ForegroundColor Green
    }

    # Start the server
    Write-Host "🚀 Starting FastAPI server..." -ForegroundColor Green
    Write-Host "📱 Frontend: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "📚 API Docs: http://localhost:8080/docs" -ForegroundColor Cyan
    Write-Host "💬 Chat Test: http://localhost:8080/api/chat/test" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⏹️  Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""

    & $python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload

} catch {
    Write-Host "❌ Error starting server: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
