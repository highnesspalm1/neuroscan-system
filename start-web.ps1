# NeuroScan Web-Frontend Starter
# PowerShell-Skript zum Starten des Web-Frontends

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "    NeuroScan Web-Frontend Starter   " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Zum WebFrontend-Verzeichnis wechseln
$webFrontendPath = Join-Path $PSScriptRoot "WebFrontend"

if (!(Test-Path $webFrontendPath)) {
    Write-Host "Fehler: WebFrontend-Verzeichnis nicht gefunden!" -ForegroundColor Red
    Read-Host "Drücke Enter zum Beenden"
    exit 1
}

Set-Location $webFrontendPath

# Das Frontend-Start-Skript ausführen
& ".\start-frontend.ps1"
