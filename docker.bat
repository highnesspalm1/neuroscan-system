@echo off
setlocal EnableDelayedExpansion

REM NeuroScan Docker Management Script for Windows
REM This script provides easy Docker management commands

if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="build" goto :build
if "%1"=="up" goto :up
if "%1"=="down" goto :down
if "%1"=="restart" goto :restart
if "%1"=="logs" goto :logs
if "%1"=="ps" goto :ps
if "%1"=="prod-up" goto :prod-up
if "%1"=="prod-down" goto :prod-down
if "%1"=="backup" goto :backup
if "%1"=="restore" goto :restore
if "%1"=="clean" goto :clean
if "%1"=="test" goto :test
if "%1"=="health" goto :health
if "%1"=="setup" goto :setup

goto :unknown

:help
echo.
echo NeuroScan Docker Management Commands:
echo.
echo Development Commands:
echo   docker.bat build       - Build all Docker images
echo   docker.bat up          - Start all services in development mode
echo   docker.bat down        - Stop all services
echo   docker.bat restart     - Restart all services
echo   docker.bat logs        - Show logs from all services
echo   docker.bat ps          - Show running containers
echo.
echo Production Commands:
echo   docker.bat prod-up     - Start all services in production mode
echo   docker.bat prod-down   - Stop production services
echo.
echo Database Commands:
echo   docker.bat backup      - Create database backup
echo   docker.bat restore     - Restore database from backup
echo.
echo Maintenance Commands:
echo   docker.bat clean       - Remove all containers and volumes
echo   docker.bat test        - Run all tests
echo   docker.bat health      - Check service health
echo   docker.bat setup       - Complete setup for new developers
echo.
goto :end

:build
echo Building Docker images...
docker-compose -f docker-compose.yml build --no-cache
if !errorlevel! equ 0 (
    echo Successfully built all images!
) else (
    echo Failed to build images!
    exit /b 1
)
goto :end

:up
echo Starting all services in development mode...
docker-compose -f docker-compose.yml up -d
if !errorlevel! equ 0 (
    echo.
    echo Services started successfully!
    echo.
    echo Access the application at:
    echo   Frontend: http://localhost:3000
    echo   Backend API: http://localhost:8000
    echo   Backend Docs: http://localhost:8000/docs
    echo.
) else (
    echo Failed to start services!
    exit /b 1
)
goto :end

:down
echo Stopping all services...
docker-compose -f docker-compose.yml down
if !errorlevel! equ 0 (
    echo Services stopped successfully!
) else (
    echo Failed to stop services!
    exit /b 1
)
goto :end

:restart
echo Restarting all services...
docker-compose -f docker-compose.yml restart
if !errorlevel! equ 0 (
    echo Services restarted successfully!
) else (
    echo Failed to restart services!
    exit /b 1
)
goto :end

:logs
echo Showing logs from all services...
docker-compose -f docker-compose.yml logs -f
goto :end

:ps
echo Running containers:
docker-compose -f docker-compose.yml ps
goto :end

:prod-up
echo Starting all services in production mode...
docker-compose -f docker-compose.prod.yml up -d
if !errorlevel! equ 0 (
    echo.
    echo Production services started successfully!
    echo Access the application at: http://localhost
    echo.
) else (
    echo Failed to start production services!
    exit /b 1
)
goto :end

:prod-down
echo Stopping production services...
docker-compose -f docker-compose.prod.yml down
if !errorlevel! equ 0 (
    echo Production services stopped successfully!
) else (
    echo Failed to stop production services!
    exit /b 1
)
goto :end

:backup
echo Creating database backup...
docker-compose -f docker-compose.yml exec postgres /backup.sh
if !errorlevel! equ 0 (
    echo Backup created successfully!
) else (
    echo Failed to create backup!
    exit /b 1
)
goto :end

:restore
if "%2"=="" (
    echo Error: Backup file name is required
    echo Usage: docker.bat restore ^<backup_filename.sql.gz^>
    exit /b 1
)
echo Restoring database from backup: %2
docker-compose -f docker-compose.yml exec postgres /restore.sh %2
if !errorlevel! equ 0 (
    echo Database restored successfully!
) else (
    echo Failed to restore database!
    exit /b 1
)
goto :end

:clean
echo Removing all containers, networks, and volumes...
docker-compose -f docker-compose.yml down -v --remove-orphans
docker-compose -f docker-compose.prod.yml down -v --remove-orphans
docker system prune -f
echo All containers, networks, and volumes removed successfully!
goto :end

:test
echo Running all tests...
docker-compose -f docker-compose.yml exec backend python -m pytest tests/ -v
if !errorlevel! equ 0 (
    echo All tests completed successfully!
) else (
    echo Some tests failed!
    exit /b 1
)
goto :end

:health
echo Checking service health...
docker-compose -f docker-compose.yml ps
echo.
echo Checking backend health...
curl -f http://localhost:8000/health >nul 2>&1
if !errorlevel! equ 0 (
    echo Backend is healthy
) else (
    echo Backend not responding
)
echo.
echo Checking frontend health...
curl -f http://localhost:3000 >nul 2>&1
if !errorlevel! equ 0 (
    echo Frontend is healthy
) else (
    echo Frontend not responding
)
goto :end

:setup
echo Setting up NeuroScan development environment...
if not exist ".env" (
    copy ".env.example" ".env"
    echo Created .env file from template. Please edit it with your configuration.
    echo.
)
call :build
if !errorlevel! neq 0 exit /b 1
call :up
if !errorlevel! neq 0 exit /b 1
echo.
echo Running database migrations...
docker-compose -f docker-compose.yml exec backend alembic upgrade head
echo.
echo Setup complete! Access the application at http://localhost:3000
goto :end

:unknown
echo Unknown command: %1
echo.
goto :help

:end
echo.
pause
