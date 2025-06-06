@echo off
REM NeuroScan Windows Deployment Script
REM This script builds and deploys the NeuroScan system using Docker on Windows

echo 🚀 Starting NeuroScan Deployment on Windows...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not available. Please ensure Docker Desktop is properly installed.
    exit /b 1
)

echo [INFO] Creating necessary directories...
if not exist "nginx\ssl" mkdir "nginx\ssl"
if not exist "database\backups" mkdir "database\backups"
if not exist "logs" mkdir "logs"

REM Environment setup
echo [INFO] Setting up environment variables...
if not exist ".env" (
    echo # NeuroScan Environment Configuration > .env
    echo COMPOSE_PROJECT_NAME=neuroscan >> .env
    echo. >> .env
    echo # Database Configuration >> .env
    echo POSTGRES_DB=neuroscan_db >> .env
    echo POSTGRES_USER=neuroscan >> .env
    echo POSTGRES_PASSWORD=neuroscan_password_secure123 >> .env
    echo. >> .env
    echo # Backend Configuration >> .env
    echo JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production >> .env
    echo ENVIRONMENT=production >> .env
    echo CORS_ORIGINS=http://localhost:3000,https://localhost >> .env
    echo. >> .env
    echo # Frontend Configuration >> .env
    echo VITE_API_URL=http://localhost:8000 >> .env
    echo VITE_ENVIRONMENT=production >> .env
    echo. >> .env
    echo # Redis Configuration >> .env
    echo REDIS_PASSWORD=redis_secure_password_123 >> .env
    
    echo [INFO] Environment file created
) else (
    echo [WARNING] Environment file already exists. Using existing configuration.
)

echo [INFO] Building Docker images...
docker-compose build --no-cache

echo [INFO] Starting services...
docker-compose up -d

echo [INFO] Waiting for services to start...
timeout /t 15 /nobreak >nul

echo [INFO] Service Status:
docker-compose ps

echo.
echo 🎉 NeuroScan deployment completed successfully!
echo.
echo Access your NeuroScan system:
echo   • Web Interface: http://localhost
echo   • API Documentation: http://localhost/api/docs
echo   • Admin Panel: http://localhost/admin
echo.
echo Service URLs:
echo   • Frontend: http://localhost:3000
echo   • Backend API: http://localhost:8000
echo   • Database: localhost:5432
echo   • Redis: localhost:6379
echo.
echo [WARNING] Note: This is a development setup.
echo [WARNING] For production, configure proper SSL certificates and secure passwords.
echo.

set /p "viewlogs=Would you like to view the logs? (y/n): "
if /i "%viewlogs%"=="y" (
    docker-compose logs -f
)

pause
