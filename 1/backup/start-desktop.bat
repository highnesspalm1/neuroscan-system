@echo off
REM NeuroScan Desktop-App Starter
REM Windows Batch-Skript zum Starten der Desktop-App

echo =====================================
echo     NeuroScan Desktop-App Starter   
echo =====================================
echo.

REM Zum DesktopApp-Verzeichnis wechseln
cd /d "%~dp0\DesktopApp"

if not exist "%CD%" (
    echo Fehler: DesktopApp-Verzeichnis nicht gefunden!
    pause
    exit /b 1
)

REM Das Desktop-Start-Skript ausführen
call start-desktop.bat
