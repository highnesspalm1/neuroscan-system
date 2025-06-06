# NeuroScan Desktop-App Starter
# PowerShell-Skript zum Starten der Desktop-App

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "    NeuroScan Desktop-App Starter   " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Zum DesktopApp-Verzeichnis wechseln
$desktopAppPath = Join-Path $PSScriptRoot "DesktopApp"

if (!(Test-Path $desktopAppPath)) {
    Write-Host "Fehler: DesktopApp-Verzeichnis nicht gefunden!" -ForegroundColor Red
    Read-Host "Drücke Enter zum Beenden"
    exit 1
}

Set-Location $desktopAppPath

# Das Desktop-Start-Skript ausführen
& ".\start-desktop.ps1"
