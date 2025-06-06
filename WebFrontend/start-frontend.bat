@echo off
REM Windows Batch-Skript zum Starten des Web-Frontends
cd /d "%~dp0"
echo Starte NeuroScan Web-Frontend...
echo.
npm run dev
pause
