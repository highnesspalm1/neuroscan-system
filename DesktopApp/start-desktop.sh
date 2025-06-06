#!/bin/bash
# Bash-Skript zum Starten der NeuroScan Desktop-App (macOS/Linux)

# Zum Verzeichnis des Skripts wechseln
cd "$(dirname "$0")"

echo "====================================="
echo "    NeuroScan Desktop-App Starter    "
echo "====================================="
echo

# Prüfen ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "Fehler: Python3 ist nicht installiert."
    echo "Bitte installiere Python3 von https://python.org/"
    exit 1
fi

# Prüfen ob pip installiert ist
if ! command -v pip3 &> /dev/null; then
    echo "Fehler: pip3 ist nicht installiert."
    exit 1
fi

echo "Python Version: $(python3 --version)"
echo "pip Version: $(pip3 --version)"

# Prüfen ob Virtual Environment existiert
if [ ! -d "venv" ]; then
    echo "Virtual Environment nicht gefunden. Erstelle neues venv..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Fehler beim Erstellen des Virtual Environments!"
        exit 1
    fi
fi

# Virtual Environment aktivieren
echo "Aktiviere Virtual Environment..."
source venv/bin/activate

# Abhängigkeiten installieren/aktualisieren
echo "Installiere/Aktualisiere Abhängigkeiten..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Fehler beim Installieren der Abhängigkeiten!"
    exit 1
fi

echo
echo "Starte NeuroScan Desktop-App..."
echo

# Desktop-App starten
python main.py
