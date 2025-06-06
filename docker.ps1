# NeuroScan Docker Management PowerShell Script
# Windows-compatible version of Makefile

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    [string]$BackupFile
)

$ComposeFile = "docker-compose.yml"
$ComposeProdFile = "docker-compose.prod.yml"
$ProjectName = "neuroscan"

function Show-Help {
    Write-Host "NeuroScan Docker Management Commands:" -ForegroundColor Green
    Write-Host ""
    Write-Host "Development Commands:" -ForegroundColor Yellow
    Write-Host "  .\docker.ps1 build       - Build all Docker images"
    Write-Host "  .\docker.ps1 up          - Start all services in development mode"
    Write-Host "  .\docker.ps1 down        - Stop all services"
    Write-Host "  .\docker.ps1 restart     - Restart all services"
    Write-Host "  .\docker.ps1 logs        - Show logs from all services"
    Write-Host "  .\docker.ps1 ps          - Show running containers"
    Write-Host ""
    Write-Host "Production Commands:" -ForegroundColor Yellow
    Write-Host "  .\docker.ps1 prod-up     - Start all services in production mode"
    Write-Host "  .\docker.ps1 prod-down   - Stop production services"
    Write-Host "  .\docker.ps1 prod-logs   - Show production logs"
    Write-Host ""
    Write-Host "Database Commands:" -ForegroundColor Yellow
    Write-Host "  .\docker.ps1 backup      - Create database backup"
    Write-Host "  .\docker.ps1 restore -BackupFile <file> - Restore database from backup"
    Write-Host "  .\docker.ps1 db-migrate  - Run database migrations"
    Write-Host ""
    Write-Host "Maintenance Commands:" -ForegroundColor Yellow
    Write-Host "  .\docker.ps1 clean       - Remove all containers and volumes"
    Write-Host "  .\docker.ps1 test        - Run all tests"
    Write-Host "  .\docker.ps1 health      - Check service health"
    Write-Host ""
    Write-Host "Development Helpers:" -ForegroundColor Yellow
    Write-Host "  .\docker.ps1 shell-backend  - Open shell in backend container"
    Write-Host "  .\docker.ps1 shell-frontend - Open shell in frontend container"
    Write-Host "  .\docker.ps1 shell-db       - Open PostgreSQL shell"
    Write-Host "  .\docker.ps1 setup          - Complete setup for new developers"
}

function Build-Images {
    Write-Host "Building Docker images..." -ForegroundColor Green
    docker-compose -f $ComposeFile build --no-cache
}

function Start-Services {
    Write-Host "Starting all services in development mode..." -ForegroundColor Green
    docker-compose -f $ComposeFile up -d
    Write-Host ""
    Write-Host "Services started. Access the application at:" -ForegroundColor Green
    Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "  Backend API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  Backend Docs: http://localhost:8000/docs" -ForegroundColor Cyan
}

function Stop-Services {
    Write-Host "Stopping all services..." -ForegroundColor Green
    docker-compose -f $ComposeFile down
}

function Restart-Services {
    Write-Host "Restarting all services..." -ForegroundColor Green
    docker-compose -f $ComposeFile restart
}

function Show-Logs {
    Write-Host "Showing logs from all services..." -ForegroundColor Green
    docker-compose -f $ComposeFile logs -f
}

function Show-Containers {
    Write-Host "Running containers:" -ForegroundColor Green
    docker-compose -f $ComposeFile ps
}

function Start-Production {
    Write-Host "Starting all services in production mode..." -ForegroundColor Green
    docker-compose -f $ComposeProdFile up -d
    Write-Host ""
    Write-Host "Production services started." -ForegroundColor Green
    Write-Host "Access the application at: http://localhost" -ForegroundColor Cyan
}

function Stop-Production {
    Write-Host "Stopping production services..." -ForegroundColor Green
    docker-compose -f $ComposeProdFile down
}

function Show-ProductionLogs {
    Write-Host "Showing production logs..." -ForegroundColor Green
    docker-compose -f $ComposeProdFile logs -f
}

function Create-Backup {
    Write-Host "Creating database backup..." -ForegroundColor Green
    docker-compose -f $ComposeFile exec postgres /backup.sh
}

function Restore-Backup {
    if (-not $BackupFile) {
        Write-Host "Error: BackupFile parameter is required" -ForegroundColor Red
        Write-Host "Usage: .\docker.ps1 restore -BackupFile backup_filename.sql.gz" -ForegroundColor Yellow
        return
    }
    Write-Host "Restoring database from backup: $BackupFile" -ForegroundColor Green
    docker-compose -f $ComposeFile exec postgres /restore.sh $BackupFile
}

function Run-Migrations {
    Write-Host "Running database migrations..." -ForegroundColor Green
    docker-compose -f $ComposeFile exec backend alembic upgrade head
}

function Clean-Everything {
    Write-Host "Removing all containers, networks, and volumes..." -ForegroundColor Green
    docker-compose -f $ComposeFile down -v --remove-orphans
    docker-compose -f $ComposeProdFile down -v --remove-orphans
    docker system prune -f
    Write-Host "All containers, networks, and volumes removed." -ForegroundColor Green
}

function Run-Tests {
    Write-Host "Running all tests..." -ForegroundColor Green
    docker-compose -f $ComposeFile exec backend python -m pytest tests/ -v
    Write-Host "All tests completed." -ForegroundColor Green
}

function Check-Health {
    Write-Host "Checking service health..." -ForegroundColor Green
    docker-compose -f $ComposeFile ps
    Write-Host ""
    
    Write-Host "Backend health:" -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "Backend is healthy" -ForegroundColor Green
        }
    } catch {
        Write-Host "Backend not responding" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Frontend health:" -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "Frontend is healthy" -ForegroundColor Green
        }
    } catch {
        Write-Host "Frontend not responding" -ForegroundColor Red
    }
}

function Open-BackendShell {
    Write-Host "Opening shell in backend container..." -ForegroundColor Green
    docker-compose -f $ComposeFile exec backend /bin/bash
}

function Open-FrontendShell {
    Write-Host "Opening shell in frontend container..." -ForegroundColor Green
    docker-compose -f $ComposeFile exec frontend /bin/sh
}

function Open-DatabaseShell {
    Write-Host "Opening PostgreSQL shell..." -ForegroundColor Green
    docker-compose -f $ComposeFile exec postgres psql -U neuroscan -d neuroscan_db
}

function Setup-Development {
    Write-Host "Setting up NeuroScan development environment..." -ForegroundColor Green
    
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
        Write-Host "Created .env file from template. Please edit it with your configuration." -ForegroundColor Yellow
    }
    
    Build-Images
    Start-Services
    Run-Migrations
    
    Write-Host ""
    Write-Host "Setup complete! Access the application at http://localhost:3000" -ForegroundColor Green
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "build" { Build-Images }
    "up" { Start-Services }
    "down" { Stop-Services }
    "restart" { Restart-Services }
    "logs" { Show-Logs }
    "ps" { Show-Containers }
    "prod-up" { Start-Production }
    "prod-down" { Stop-Production }
    "prod-logs" { Show-ProductionLogs }
    "backup" { Create-Backup }
    "restore" { Restore-Backup }
    "db-migrate" { Run-Migrations }
    "clean" { Clean-Everything }
    "test" { Run-Tests }
    "health" { Check-Health }
    "shell-backend" { Open-BackendShell }
    "shell-frontend" { Open-FrontendShell }
    "shell-db" { Open-DatabaseShell }
    "setup" { Setup-Development }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
    }
}
