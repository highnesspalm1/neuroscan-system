# NeuroScan Native Startup Script (Without Docker) - FIXED VERSION
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
    Write-Status "Checking dependencies..." "INFO"
    
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
    
    # Check SQLite database
    $dbPath = "f:\NeuroCompany\NeuroScan\neuroscan.db"
    if (Test-Path $dbPath) {
        Write-Status "SQLite database found: $dbPath" "SUCCESS"
    } else {
        Write-Status "SQLite database not found, will be created" "WARNING"
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
        "cd '$frontendPath'; Write-Host 'NeuroScan Frontend Starting...' -ForegroundColor Green; npm run dev -- --host 0.0.0.0"
    )
    
    Start-Process powershell -ArgumentList $frontendArgs
    Write-Status "Frontend started in new window" "SUCCESS"
    return $true
}

function Wait-ForServices {
    Write-Status "Waiting for services to start..." "INFO"
    
    $maxAttempts = 10
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        $attempt++
        Start-Sleep 2
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Status "Backend API is responding" "SUCCESS"
                break
            }
        } catch {
            Write-Status "Attempt $attempt/$maxAttempts - Backend not ready yet..." "INFO"
        }
        
        if ($attempt -eq $maxAttempts) {
            Write-Status "Backend API did not start within expected time" "WARNING"
        }
    }
}

function Open-Browser {
    $response = Read-Host "Do you want to open the browser? (Y/n)"
    if ($response -eq "" -or $response -eq "Y" -or $response -eq "y") {
        Start-Process "http://localhost:3000"
        Start-Process "http://localhost:8000/docs"
        Write-Status "Browser opened with NeuroScan URLs" "SUCCESS"
    }
}

# Main execution
Clear-Host
Write-Host "NeuroScan Native Startup" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Status "Starting NeuroScan without Docker..." "INFO"

# Check dependencies unless skipped
if (-not $SkipDependencyCheck) {
    $dependenciesOk = Test-Dependencies
    if (-not $dependenciesOk) {
        Write-Status "Dependency check failed. Please install missing components." "ERROR"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Start backend
$backendStarted = Start-Backend
if (-not $backendStarted) {
    Write-Status "Failed to start backend. Exiting." "ERROR"
    Read-Host "Press Enter to exit"
    exit 1
}

# Wait a moment for backend to initialize
Start-Sleep 3

# Start frontend
$frontendStarted = Start-Frontend
if (-not $frontendStarted) {
    Write-Status "Failed to start frontend. Backend is still running." "WARNING"
} else {
    # Wait for services to be ready
    Wait-ForServices
    
    Write-Status "NeuroScan started successfully in native mode!" "SUCCESS"
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Yellow
    Write-Host "  Frontend:    http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: Two new PowerShell windows were opened for Backend and Frontend" -ForegroundColor Yellow
    Write-Host "Close those windows to stop the services" -ForegroundColor Yellow
    
    Open-Browser
    
    Write-Status "Startup complete!" "SUCCESS"
}

Write-Host "Press Enter to exit this window:" -ForegroundColor Gray
Read-Host
