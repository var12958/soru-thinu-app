<#
run-app.ps1

Starts the backend (uvicorn), serves the frontend with live-server,
and opens the browser to the login page.

Usage: In PowerShell (may need admin for execution policy):
  powershell -ExecutionPolicy Bypass -File run-app.ps1
#>

$ErrorActionPreference = 'Stop'

try {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
    Set-Location $ScriptDir

    Write-Output "Starting backend (uvicorn)..."
    $python = "C:/Users/Varun/python.exe"
    if (-not (Test-Path $python)) {
        Write-Warning "Python executable not found at $python. Using 'python' from PATH."
        $python = "python"
    }

    $uvicornArgs = "-m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080"
    $backendProc = Start-Process -FilePath $python -ArgumentList $uvicornArgs -WorkingDirectory $ScriptDir -WindowStyle "Normal" -PassThru

    Start-Sleep -Seconds 2

    Write-Output "Starting frontend (live-server)..."
    $liveExe = "live-server"
    # If live-server not on PATH, try npx
    $liveArgs = "--port=3000 --entry-file=login.html ."
    try {
        Start-Process -FilePath $liveExe -ArgumentList $liveArgs -WorkingDirectory $ScriptDir -WindowStyle "Normal" -PassThru | Out-Null
    } catch {
        Write-Warning "'live-server' not found on PATH; falling back to 'npx live-server'."
        Start-Process -FilePath "npx" -ArgumentList "live-server --port=3000 --entry-file=login.html ." -WorkingDirectory $ScriptDir -WindowStyle "Normal" -PassThru | Out-Null
    }

    Start-Sleep -Seconds 1
    $url = "http://127.0.0.1:3000/login.html"
    Write-Output "Opening browser to $url"
    Start-Process $url

    Write-Output "App started. Backend PID: $($backendProc.Id). Frontend serving on port 3000."
    Write-Output "Close the terminal windows to stop the servers, or terminate the processes manually."

} catch {
    Write-Error "Failed to start app: $_"
    exit 1
}
