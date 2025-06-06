# PowerShell-Skript zum Starten des Web-Frontends

# Zum Verzeichnis des Skripts wechseln
Set-Location $PSScriptRoot

Write-Host "Starte NeuroScan Web-Frontend..." -ForegroundColor Cyan
Write-Host ""

# Prüfen ob Node.js installiert ist
try {
    $nodeVersion = node --version
    Write-Host "Node.js Version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Fehler: Node.js ist nicht installiert." -ForegroundColor Red
    Write-Host "Bitte installiere Node.js von https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Drücke Enter zum Beenden"
    exit 1
}

# Prüfen ob npm installiert ist
try {
    $npmVersion = npm --version
    Write-Host "npm Version: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "Fehler: npm ist nicht installiert." -ForegroundColor Red
    Read-Host "Drücke Enter zum Beenden"
    exit 1
}

# Prüfen ob node_modules existiert
if (!(Test-Path "node_modules")) {
    Write-Host "node_modules nicht gefunden. Installiere Abhängigkeiten..." -ForegroundColor Yellow
    npm install
}

Write-Host ""
Write-Host "Starte Development Server..." -ForegroundColor Cyan

# Development Server starten
npm run dev
