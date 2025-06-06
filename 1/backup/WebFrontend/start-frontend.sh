#!/bin/bash
# Bash-Skript zum Starten des Web-Frontends (macOS/Linux)

# Zum Verzeichnis des Skripts wechseln
cd "$(dirname "$0")"

echo "Starte NeuroScan Web-Frontend..."
echo

# Prüfen ob Node.js installiert ist
if ! command -v node &> /dev/null; then
    echo "Fehler: Node.js ist nicht installiert."
    echo "Bitte installiere Node.js von https://nodejs.org/"
    exit 1
fi

# Prüfen ob npm installiert ist
if ! command -v npm &> /dev/null; then
    echo "Fehler: npm ist nicht installiert."
    exit 1
fi

# Prüfen ob node_modules existiert
if [ ! -d "node_modules" ]; then
    echo "node_modules nicht gefunden. Installiere Abhängigkeiten..."
    npm install
fi

# Development Server starten
npm run dev
