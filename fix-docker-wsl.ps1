# NeuroScan Docker WSL2 Fix Script
# This script helps resolve Docker Desktop WSL2 engine issues

Write-Host "NeuroScan Docker WSL2 Troubleshooting Script" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

function Test-AdminRights {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Write-Status {
    param([string]$Message, [string]$Status = "INFO")
    switch ($Status) {
        "SUCCESS" { Write-Host "✓ $Message" -ForegroundColor Green }
        "ERROR"   { Write-Host "✗ $Message" -ForegroundColor Red }
        "WARNING" { Write-Host "⚠ $Message" -ForegroundColor Yellow }
        default   { Write-Host "ℹ $Message" -ForegroundColor Cyan }
    }
}

# Check if running as administrator
if (-not (Test-AdminRights)) {
    Write-Status "This script needs to be run as Administrator" "ERROR"
    Write-Host "Please right-click PowerShell and 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Status "Running as Administrator" "SUCCESS"

# Step 1: Stop Docker Desktop
Write-Host "`nStep 1: Stopping Docker Desktop..." -ForegroundColor Yellow
try {
    Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
    Write-Status "Docker Desktop stopped" "SUCCESS"
} catch {
    Write-Status "Docker Desktop was not running" "INFO"
}

# Step 2: Check and restart WSL
Write-Host "`nStep 2: Restarting WSL..." -ForegroundColor Yellow
try {
    wsl --shutdown
    Start-Sleep 5
    Write-Status "WSL shutdown completed" "SUCCESS"
} catch {
    Write-Status "Error shutting down WSL: $($_.Exception.Message)" "ERROR"
}

# Step 3: Check WSL distributions
Write-Host "`nStep 3: Checking WSL distributions..." -ForegroundColor Yellow
try {
    $wslList = wsl -l -v
    Write-Host $wslList
    Write-Status "WSL distributions listed" "SUCCESS"
} catch {
    Write-Status "Error listing WSL distributions" "ERROR"
}

# Step 4: Reset Docker Desktop data (if needed)
Write-Host "`nStep 4: Docker Desktop Reset Options..." -ForegroundColor Yellow
$resetChoice = Read-Host "Do you want to reset Docker Desktop data? This will remove all containers/images. (y/N)"

if ($resetChoice -eq 'y' -or $resetChoice -eq 'Y') {
    Write-Status "Resetting Docker Desktop data..." "WARNING"
    
    # Remove Docker Desktop data
    $dockerDataPath = "$env:APPDATA\Docker"
    if (Test-Path $dockerDataPath) {
        Remove-Item $dockerDataPath -Recurse -Force -ErrorAction SilentlyContinue
        Write-Status "Docker Desktop data removed" "SUCCESS"
    }
    
    # Remove WSL Docker distributions
    try {
        wsl --unregister docker-desktop 2>$null
        wsl --unregister docker-desktop-data 2>$null
        Write-Status "Docker WSL distributions removed" "SUCCESS"
    } catch {
        Write-Status "Docker WSL distributions not found" "INFO"
    }
}

# Step 5: Enable required Windows features
Write-Host "`nStep 5: Checking Windows Features..." -ForegroundColor Yellow

$features = @(
    "Microsoft-Windows-Subsystem-Linux",
    "VirtualMachinePlatform"
)

foreach ($feature in $features) {
    $featureState = Get-WindowsOptionalFeature -Online -FeatureName $feature
    if ($featureState.State -eq "Enabled") {
        Write-Status "$feature is enabled" "SUCCESS"
    } else {
        Write-Status "Enabling $feature..." "WARNING"
        Enable-WindowsOptionalFeature -Online -FeatureName $feature -NoRestart
    }
}

# Step 6: Set WSL2 as default
Write-Host "`nStep 6: Setting WSL2 as default..." -ForegroundColor Yellow
try {
    wsl --set-default-version 2
    Write-Status "WSL2 set as default version" "SUCCESS"
} catch {
    Write-Status "Error setting WSL2 as default: $($_.Exception.Message)" "ERROR"
}

# Step 7: Alternative Docker installation check
Write-Host "`nStep 7: Alternative Solutions..." -ForegroundColor Yellow
Write-Host "If Docker Desktop continues to have issues, consider:" -ForegroundColor White
Write-Host "1. Use Docker without WSL2 (Hyper-V backend)" -ForegroundColor White
Write-Host "2. Use Podman Desktop as alternative" -ForegroundColor White
Write-Host "3. Run NeuroScan without Docker (native installation)" -ForegroundColor White

# Step 8: Create native start script
Write-Host "`nStep 8: Creating native startup option..." -ForegroundColor Yellow

$nativeScript = @"
# NeuroScan Native Start (Without Docker)
# This script starts NeuroScan components natively on Windows

Write-Host "Starting NeuroScan in Native Mode..." -ForegroundColor Green

# Start Backend API
Write-Host "Starting Backend API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'f:\NeuroCompany\NeuroScan\BackendAPI'; python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

# Wait a moment
Start-Sleep 3

# Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'f:\NeuroCompany\NeuroScan\WebFrontend'; npm run dev"

Write-Host "NeuroScan started in native mode!" -ForegroundColor Green
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
"@

$nativeScript | Out-File -FilePath "start-neuroscan-native.ps1" -Encoding UTF8
Write-Status "Native startup script created: start-neuroscan-native.ps1" "SUCCESS"

# Final recommendations
Write-Host "`nNext Steps:" -ForegroundColor Green
Write-Host "1. Restart your computer to apply Windows feature changes" -ForegroundColor White
Write-Host "2. Try starting Docker Desktop again" -ForegroundColor White
Write-Host "3. If Docker still fails, use: .\start-neuroscan-native.ps1" -ForegroundColor White
Write-Host "4. Check Windows Update for latest WSL2 kernel" -ForegroundColor White

$restartChoice = Read-Host "`nDo you want to restart now? (y/N)"
if ($restartChoice -eq 'y' -or $restartChoice -eq 'Y') {
    Write-Status "Restarting computer..." "WARNING"
    Restart-Computer -Force
} else {
    Write-Status "Please restart manually when convenient" "INFO"
}

Read-Host "`nPress Enter to exit"
