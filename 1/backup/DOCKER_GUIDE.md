# NeuroScan Docker Setup & Management Guide

## Overview

NeuroScan uses Docker and Docker Compose to provide a consistent development and production environment. This guide covers everything you need to know about working with Docker in the NeuroScan project.

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose (included with Docker Desktop)
- Git
- PowerShell (Windows) or Bash (Linux/Mac)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd NeuroScan
```

### 2. Environment Configuration

Copy the environment template and configure it:

```bash
# Windows PowerShell
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit the `.env` file with your configuration.

### 3. Start Development Environment

```bash
# Using PowerShell script (Windows)
.\docker.ps1 setup

# Using batch file (Windows)
docker.bat setup

# Using Make (Linux/Mac)
make setup

# Using Docker Compose directly
docker-compose up -d
```

## Docker Architecture

### Services

The NeuroScan application consists of several Docker services:

1. **backend** - FastAPI application server
2. **frontend** - Vue.js web application
3. **postgres** - PostgreSQL database
4. **redis** - Redis cache and session store
5. **nginx** - Reverse proxy and load balancer

### Networks

All services communicate through the `neuroscan-network` bridge network.

### Volumes

- `postgres_data` - Database persistent storage
- `redis_data` - Redis persistent storage
- `backend_uploads` - File uploads storage
- `backend_logs` - Application logs

## Environment Configurations

### Development Environment

```bash
# Start with hot reload enabled
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Or use the development script
.\docker.ps1 dev-up
```

Development features:
- Hot reload for backend and frontend
- Debug mode enabled
- Development tools (PgAdmin, Redis Commander, MailHog)
- Volume mounts for live code editing

### Production Environment

```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Or use the production script
.\docker.ps1 prod-up
```

Production features:
- Optimized builds
- Resource limits
- Health checks
- Backup services
- SSL/TLS support

## Management Commands

### Windows PowerShell Script

```powershell
# Basic commands
.\docker.ps1 build          # Build all images
.\docker.ps1 up             # Start services
.\docker.ps1 down           # Stop services
.\docker.ps1 restart        # Restart services
.\docker.ps1 logs           # View logs
.\docker.ps1 ps             # List containers

# Development commands
.\docker.ps1 shell-backend  # Open backend shell
.\docker.ps1 shell-db       # Open database shell
.\docker.ps1 test           # Run tests

# Maintenance commands
.\docker.ps1 backup         # Create database backup
.\docker.ps1 clean          # Clean up containers/volumes
.\docker.ps1 health         # Check system health
```

### Windows Batch Script

```batch
docker.bat build
docker.bat up
docker.bat down
docker.bat logs
docker.bat health
```

### Make Commands (Linux/Mac)

```bash
make build
make up
make down
make logs
make test
make backup
make clean
```

## Development Workflow

### 1. Starting Development

```bash
# First time setup
.\docker.ps1 setup

# Daily development
.\docker.ps1 up
```

### 2. Making Changes

- Backend changes: Edit files in `BackendAPI/` - auto-reload enabled
- Frontend changes: Edit files in `WebFrontend/` - auto-reload enabled
- Database changes: Use migrations in `database/`

### 3. Running Tests

```bash
# Run all tests
.\docker.ps1 test

# Run specific test suites
docker-compose exec backend pytest tests/unit/
docker-compose exec backend pytest tests/integration/
```

### 4. Database Operations

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Access database
.\docker.ps1 shell-db
```

### 5. Viewing Logs

```bash
# All services
.\docker.ps1 logs

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Development Tools

### Database Administration (PgAdmin)

Access at: http://localhost:5050
- Email: admin@neuroscan.dev
- Password: admin123

### Redis Administration (Redis Commander)

Access at: http://localhost:8081
- Username: admin
- Password: admin123

### Email Testing (MailHog)

Access at: http://localhost:8025
SMTP: localhost:1025

## Production Deployment

### 1. Environment Setup

```bash
# Copy production environment
cp .env.example .env.prod

# Edit production values
nano .env.prod
```

### 2. SSL/TLS Configuration

```bash
# Generate SSL certificates
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/nginx.key \
  -out nginx/ssl/nginx.crt
```

### 3. Start Production

```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 4. Backup Setup

```bash
# Manual backup
.\docker.ps1 backup

# Setup automated backups (cron)
crontab -e
# Add: 0 2 * * * /path/to/scripts/backup.sh
```

## Monitoring & Maintenance

### Health Checks

```bash
# System health
.\docker.ps1 health

# Detailed health check
./scripts/health-check.sh
```

### Resource Monitoring

```bash
# Container stats
docker stats

# System resources
docker system df
```

### Log Management

```bash
# View logs
docker-compose logs -f --tail=100

# Clear logs
docker-compose down
docker system prune -f
```

## Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check port usage
   netstat -an | findstr :8000
   
   # Change ports in docker-compose.override.yml
   ```

2. **Database connection issues**
   ```bash
   # Check database status
   docker-compose exec postgres pg_isready
   
   # Reset database
   docker-compose down -v
   docker-compose up -d
   ```

3. **Build failures**
   ```bash
   # Clean rebuild
   docker-compose build --no-cache
   docker system prune -f
   ```

4. **Permission issues (Linux)**
   ```bash
   # Fix volume permissions
   sudo chown -R $USER:$USER ./uploads
   sudo chown -R $USER:$USER ./logs
   ```

### Log Analysis

```bash
# Backend errors
docker-compose logs backend | grep ERROR

# Database logs
docker-compose logs postgres

# Nginx access logs
docker-compose exec nginx tail -f /var/log/nginx/access.log
```

## Performance Optimization

### Resource Limits

Edit `docker-compose.prod.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

### Caching

- Redis caching enabled by default
- Nginx static file caching
- Browser caching headers

### Database Optimization

```sql
-- Check database performance
SELECT * FROM pg_stat_activity;

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM users;
```

## Security Considerations

### Environment Variables

- Never commit `.env` files
- Use strong passwords in production
- Rotate secrets regularly

### Network Security

- Use internal networks for service communication
- Limit exposed ports
- Enable SSL/TLS in production

### Container Security

- Regular image updates
- Security scanning
- Non-root users in containers

## Backup & Recovery

### Automated Backups

```bash
# Setup backup cron job
0 2 * * * /path/to/NeuroScan/scripts/backup.sh
```

### Manual Backup

```bash
# Create backup
.\docker.ps1 backup

# List backups
ls -la backups/
```

### Restore Process

```bash
# Restore from backup
.\docker.ps1 restore backup_filename.sql.gz
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: NeuroScan CI/CD

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          docker-compose up -d
          docker-compose exec -T backend pytest
```

## Support

For issues with Docker setup:

1. Check the troubleshooting section
2. Review logs: `.\docker.ps1 logs`
3. Check health status: `.\docker.ps1 health`
4. Create an issue in the repository

## Useful Commands Reference

```bash
# Quick commands
.\docker.ps1 up              # Start everything
.\docker.ps1 down            # Stop everything
.\docker.ps1 restart         # Restart all services
.\docker.ps1 logs            # View all logs
.\docker.ps1 ps              # List containers
.\docker.ps1 health          # Health check

# Development
.\docker.ps1 shell-backend   # Backend shell
.\docker.ps1 shell-db        # Database shell
.\docker.ps1 test            # Run tests

# Maintenance
.\docker.ps1 backup          # Database backup
.\docker.ps1 clean           # Clean up
.\docker.ps1 build           # Rebuild images
```
