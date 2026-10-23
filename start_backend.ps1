# Starts the Cropwise backend regardless of where this script is invoked from.
$backendDir = Join-Path $PSScriptRoot 'backend'
Start-Process python -ArgumentList '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000' -WorkingDirectory $backendDir
Write-Host "Backend starting at http://localhost:8000 (from $backendDir)"
