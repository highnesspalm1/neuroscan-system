#!/bin/bash
# NeuroScan Web-Frontend Starter
# Bash-Skript zum Starten des Web-Frontends (macOS/Linux)

echo "====================================="
echo "    NeuroScan Web-Frontend Starter   "
echo "====================================="
echo

# Zum Verzeichnis des Skripts wechseln
cd "$(dirname "$0")"

# Zum WebFrontend-Verzeichnis wechseln
if [ ! -d "WebFrontend" ]; then
    echo "Fehler: WebFrontend-Verzeichnis nicht gefunden!"
    exit 1
fi

cd WebFrontend

# Das Frontend-Start-Skript ausführen
./start-frontend.sh
