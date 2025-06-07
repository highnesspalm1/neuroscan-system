# NeuroScan Native Startup Script (Without Docker)
# This script starts NeuroScan components natively on Windows

param(
    [switch]$SkipDependencyCheck,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"

function Write-Status {
    param([string]$Message, [string]$Status = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    switch ($Status) {
        "SUCCESS" { 
            Write-Host "[$timestamp] ✓ $Message" -ForegroundColor Green 
        }
        "ERROR" { 
            Write-Host "[$timestamp] ✗ $Message" -ForegroundColor Red 
        }
        "WARNING" { 
            Write-Host "[$timestamp] ⚠ $Message" -ForegroundColor Yellow 
        }
        default { 
            Write-Host "[$timestamp] ℹ $Message" -ForegroundColor Cyan 
        }
    }
}

function Test-Dependencies {
    Write-Status "Checking dependencies..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3") {
            Write-Status "Python found: $pythonVersion" "SUCCESS"
        } else {
            Write-Status "Python 3 not found" "ERROR"
            return $false
        }
    } catch {
        Write-Status "Python not found in PATH" "ERROR"
        return $false
    }
    
    # Check Node.js
    try {
        $nodeVersion = node --version 2>&1
        if ($nodeVersion -match "v\d+") {
            Write-Status "Node.js found: $nodeVersion" "SUCCESS"
        } else {
            Write-Status "Node.js not found" "ERROR"
            return $false
        }
    } catch {
        Write-Status "Node.js not found in PATH" "ERROR"
        return $false
    }
    
    return $true
}

function Start-Backend {
    Write-Status "Starting Backend API..." "INFO"
    
    # Check if backend directory exists
    $backendPath = "f:\NeuroCompany\NeuroScan\BackendAPI"
    if (-not (Test-Path $backendPath)) {
        Write-Status "Backend directory not found: $backendPath" "ERROR"
        return $false
    }
    
    # Install Python dependencies if needed
    if (Test-Path "$backendPath\requirements.txt") {
        Write-Status "Installing Python dependencies..." "INFO"
        Set-Location $backendPath
        pip install -r requirements.txt --quiet
    }
    
    # Start backend in new window
    $backendArgs = @(
        "-NoExit",
        "-Command", 
        "cd '$backendPath'; Write-Host 'NeuroScan Backend API Starting...' -ForegroundColor Green; python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    )
    
    Start-Process powershell -ArgumentList $backendArgs
    Write-Status "Backend API started in new window" "SUCCESS"
    return $true
}

function Start-Frontend {
    Write-Status "Starting Frontend..." "INFO"
    
    # Check if frontend directory exists
    $frontendPath = "f:\NeuroCompany\NeuroScan\WebFrontend"
    if (-not (Test-Path $frontendPath)) {
        Write-Status "Frontend directory not found: $frontendPath" "ERROR"
        return $false
    }
    
    # Install Node.js dependencies if needed
    if (Test-Path "$frontendPath\package.json") {
        Write-Status "Installing Node.js dependencies..." "INFO"
        Set-Location $frontendPath
        npm install --silent
    }
    
    # Start frontend in new window
    $frontendArgs = @(
        "-NoExit",
        "-Command", 
        "cd '$frontendPath'; Write-Host 'NeuroScan Frontend Starting...' -ForegroundColor Green; npm run dev"
    )
    
    Start-Process powershell -ArgumentList $frontendArgs
    Write-Status "Frontend started in new window" "SUCCESS"
    return $true
}

function Start-Database {
    Write-Status "Checking for local database..." "INFO"
    
    $dbPath = "f:\NeuroCompany\NeuroScan\neuroscan.db"
    if (Test-Path $dbPath) {
        Write-Status "SQLite database found: $dbPath" "SUCCESS"
        return $true
    } else {
        Write-Status "Creating SQLite database..." "INFO"
        # The backend will create the database automatically
        return $true
    }
}

# Main execution
Write-Host "NeuroScan Native Startup" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host "Starting NeuroScan without Docker..." -ForegroundColor Yellow
Write-Host ""

# Check dependencies
if (-not $SkipDependencyCheck) {
    if (-not (Test-Dependencies)) {
        Write-Status "Dependency check failed. Install Python 3 and Node.js first." "ERROR"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Start database
Start-Database

# Start backend
if (-not (Start-Backend)) {
    Write-Status "Failed to start backend" "ERROR"
    Read-Host "Press Enter to exit"
    exit 1
}

# Wait for backend to initialize
Write-Status "Waiting for backend to initialize..." "INFO"
Start-Sleep 5

# Start frontend
if (-not (Start-Frontend)) {
    Write-Status "Failed to start frontend" "ERROR"
    Read-Host "Press Enter to exit"
    exit 1
}

# Wait for frontend to initialize
Write-Status "Waiting for frontend to initialize..." "INFO"
Start-Sleep 5

# Show status
Write-Host ""
Write-Status "NeuroScan started successfully in native mode!" "SUCCESS"
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Green
Write-Host "  Frontend:    http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: Two new PowerShell windows were opened for Backend and Frontend" -ForegroundColor Yellow
Write-Host "Close those windows to stop the services" -ForegroundColor Yellow

# Open browser
$openBrowser = Read-Host "Do you want to open the browser? (Y/n)"
if ($openBrowser -ne 'n' -and $openBrowser -ne 'N') {
    Start-Process "http://localhost:3000"
}

Write-Host ""
Write-Status "Startup complete!" "SUCCESS"
Read-Host "Press Enter to exit this window"
