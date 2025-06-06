@echo off
REM NeuroScan Web-Frontend Starter
REM Windows Batch-Skript zum Starten des Web-Frontends

echo =====================================
echo     NeuroScan Web-Frontend Starter   
echo =====================================
echo.

REM Zum WebFrontend-Verzeichnis wechseln
cd /d "%~dp0\WebFrontend"

if not exist "%CD%" (
    echo Fehler: WebFrontend-Verzeichnis nicht gefunden!
    pause
    exit /b 1
)

REM Das Frontend-Start-Skript ausführen
call start-frontend.bat
