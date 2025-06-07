# NeuroScan Windows Service Installation
# Requires Administrator privileges

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Install", "Uninstall", "Start", "Stop", "Restart")]
    [string]$Action = "Install"
)

# Ensure running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script requires Administrator privileges. Restarting as Administrator..." -ForegroundColor Yellow
    Start-Process PowerShell -Verb RunAs "-File `"$PSCommandPath`" -Action $Action"
    exit
}

$ServiceName = "NeuroScanAPI"
$ServiceDisplayName = "NeuroScan Authentication API"
$ServiceDescription = "NeuroScan Premium Product Authentication Service"
$BackendPath = "f:\NeuroCompany\NeuroScan\BackendAPI"
$PythonExe = (Get-Command python).Source
$ServiceExe = "$PythonExe -m uvicorn main:app --host 0.0.0.0 --port 8000"

function Install-NeuroScanService {
    Write-Host "Installing NeuroScan as Windows Service..." -ForegroundColor Green
    
    # Create service wrapper script
    $WrapperScript = @"
import sys
import os
import subprocess
import time

# Change to backend directory
os.chdir("$($BackendPath.Replace('\', '\\'))")

# Start the FastAPI server
try:
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ])
except KeyboardInterrupt:
    print("Service stopping...")
except Exception as e:
    print(f"Service error: {e}")
    time.sleep(10)
"@
    
    $WrapperPath = "$BackendPath\service_wrapper.py"
    $WrapperScript | Out-File -FilePath $WrapperPath -Encoding UTF8
    
    # Install NSSM (Non-Sucking Service Manager) if not present
    $NSSMPath = "$env:ProgramFiles\nssm\nssm.exe"
    if (-not (Test-Path $NSSMPath)) {
        Write-Host "Installing NSSM..." -ForegroundColor Yellow
        $NSSMUrl = "https://nssm.cc/release/nssm-2.24.zip"
        $TempPath = "$env:TEMP\nssm.zip"
        Invoke-WebRequest -Uri $NSSMUrl -OutFile $TempPath
        Expand-Archive -Path $TempPath -DestinationPath "$env:ProgramFiles\nssm" -Force
        Move-Item "$env:ProgramFiles\nssm\nssm-2.24\win64\nssm.exe" "$env:ProgramFiles\nssm\nssm.exe" -Force
    }
    
    # Create service
    & $NSSMPath install $ServiceName $PythonExe "$WrapperPath"
    & $NSSMPath set $ServiceName DisplayName "$ServiceDisplayName"
    & $NSSMPath set $ServiceName Description "$ServiceDescription"
    & $NSSMPath set $ServiceName Start SERVICE_AUTO_START
    
    Write-Host "Service installed successfully!" -ForegroundColor Green
}

function Uninstall-NeuroScanService {
    Write-Host "Uninstalling NeuroScan Service..." -ForegroundColor Yellow
    
    $NSSMPath = "$env:ProgramFiles\nssm\nssm.exe"
    if (Test-Path $NSSMPath) {
        & $NSSMPath stop $ServiceName
        & $NSSMPath remove $ServiceName confirm
        Write-Host "Service uninstalled successfully!" -ForegroundColor Green
    }
}

function Start-NeuroScanService {
    Write-Host "Starting NeuroScan Service..." -ForegroundColor Green
    Start-Service -Name $ServiceName
    Write-Host "Service started!" -ForegroundColor Green
}

function Stop-NeuroScanService {
    Write-Host "Stopping NeuroScan Service..." -ForegroundColor Yellow
    Stop-Service -Name $ServiceName
    Write-Host "Service stopped!" -ForegroundColor Green
}

# Execute action
switch ($Action) {
    "Install" { Install-NeuroScanService }
    "Uninstall" { Uninstall-NeuroScanService }
    "Start" { Start-NeuroScanService }
    "Stop" { Stop-NeuroScanService }
    "Restart" { 
        Stop-NeuroScanService
        Start-Sleep 2
        Start-NeuroScanService
    }
}

Write-Host "Action '$Action' completed!" -ForegroundColor Cyan
