# PowerShell-Skript zum Starten der NeuroScan Desktop-App

# Zum Verzeichnis des Skripts wechseln
Set-Location $PSScriptRoot

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "    NeuroScan Desktop-App Starter    " -ForegroundColor Cyan  
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Prüfen ob Python installiert ist
try {
    $pythonVersion = python --version
    Write-Host "Python Version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Fehler: Python ist nicht installiert." -ForegroundColor Red
    Write-Host "Bitte installiere Python von https://python.org/" -ForegroundColor Yellow
    Read-Host "Drücke Enter zum Beenden"
    exit 1
}

# Prüfen ob pip installiert ist
try {
    $pipVersion = pip --version
    Write-Host "pip Version: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "Fehler: pip ist nicht installiert." -ForegroundColor Red
    Read-Host "Drücke Enter zum Beenden"
    exit 1
}

# Prüfen ob Virtual Environment existiert
if (!(Test-Path "venv")) {
    Write-Host "Virtual Environment nicht gefunden. Erstelle neues venv..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Fehler beim Erstellen des Virtual Environments!" -ForegroundColor Red
        Read-Host "Drücke Enter zum Beenden"
        exit 1
    }
}

# Virtual Environment aktivieren
Write-Host "Aktiviere Virtual Environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Abhängigkeiten installieren/aktualisieren
Write-Host "Installiere/Aktualisiere Abhängigkeiten..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Fehler beim Installieren der Abhängigkeiten!" -ForegroundColor Red
    Read-Host "Drücke Enter zum Beenden"
    exit 1
}

Write-Host ""
Write-Host "Starte NeuroScan Desktop-App..." -ForegroundColor Cyan
Write-Host ""

# Desktop-App starten
python main.py
