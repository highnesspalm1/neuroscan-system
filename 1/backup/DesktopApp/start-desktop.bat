@echo off
REM Windows Batch-Skript zum Starten der NeuroScan Desktop-App

cd /d "%~dp0"

echo =====================================
echo     NeuroScan Desktop-App Starter   
echo =====================================
echo.

REM Prüfen ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo Fehler: Python ist nicht installiert.
    echo Bitte installiere Python von https://python.org/
    pause
    exit /b 1
)

REM Virtual Environment prüfen/erstellen
if not exist "venv" (
    echo Virtual Environment nicht gefunden. Erstelle neues venv...
    python -m venv venv
    if errorlevel 1 (
        echo Fehler beim Erstellen des Virtual Environments!
        pause
        exit /b 1
    )
)

REM Virtual Environment aktivieren
echo Aktiviere Virtual Environment...
call venv\Scripts\activate.bat

REM Abhängigkeiten installieren
echo Installiere/Aktualisiere Abhängigkeiten...
pip install -r requirements.txt

if errorlevel 1 (
    echo Fehler beim Installieren der Abhängigkeiten!
    pause
    exit /b 1
)

echo.
echo Starte NeuroScan Desktop-App...
echo.

REM Desktop-App starten
python main.py

pause
