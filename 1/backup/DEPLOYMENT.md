# NeuroScan Production Deployment Guide

## Prerequisites

### System Requirements
- **Operating System**: Linux Ubuntu 20.04+ / CentOS 8+ / Windows 10+ with WSL2
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: Minimum 20GB free space
- **CPU**: 2+ cores recommended
- **Network**: Stable internet connection for Docker image downloads

### Required Software
- **Docker**: Version 20.0+
- **Docker Compose**: Version 2.0+
- **Git**: For source code management
- **OpenSSL**: For SSL certificate generation

## Quick Start Deployment

### 1. Clone Repository
```bash
git clone https://github.com/neurocompany/neuroscan.git
cd neuroscan
```

### 2. Run Deployment Script

**Linux/macOS:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```cmd
deploy.bat
```

### 3. Access Your System
- **Web Interface**: http://localhost
- **API Documentation**: http://localhost/api/docs
- **Admin Panel**: http://localhost/admin

## Manual Deployment

### 1. Environment Configuration
```bash
# Copy and edit environment file
cp .env.example .env
nano .env
```

### 2. SSL Certificates (Production)
```bash
# Generate SSL certificates
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/nginx.key \
    -out nginx/ssl/nginx.crt
```

### 3. Build and Start Services
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

## Service Configuration

### Backend API (Port 8000)
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache**: Redis
- **Features**: PDF generation, QR codes, authentication

### Frontend (Port 3000)
- **Framework**: Vue.js 3
- **UI Library**: Element Plus
- **Features**: Admin dashboard, product management

### Database (Port 5432)
- **Engine**: PostgreSQL 15
- **Features**: UUID support, audit logging, triggers

### Cache (Port 6379)
- **Engine**: Redis 7
- **Usage**: Session storage, API caching

## Production Hardening

### 1. Security Configuration
```bash
# Generate secure passwords
JWT_SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)
```

### 2. SSL/TLS Setup
- Replace self-signed certificates with CA-signed certificates
- Update nginx configuration for HTTPS redirect
- Configure HSTS headers

### 3. Database Security
- Change default credentials
- Enable SSL connections
- Configure backup encryption

### 4. Network Security
- Configure firewall rules
- Use private networks for internal communication
- Enable fail2ban for intrusion prevention

## Monitoring and Maintenance

### Health Checks
```bash
# Check all services
docker-compose ps

# Check individual service health
curl http://localhost/health
curl http://localhost:8000/health
```

### Logs Management
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

### Backup Procedures
```bash
# Database backup
docker-compose exec postgres pg_dump -U neuroscan neuroscan_db > backup.sql

# Volume backup
docker run --rm -v neuroscan_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data
```

### Updates and Scaling
```bash
# Pull latest images
docker-compose pull

# Recreate services with new images
docker-compose up -d --force-recreate

# Scale backend service
docker-compose up -d --scale backend=3
```

## Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Check what's using the port
sudo netstat -tulpn | grep :8000

# Stop conflicting services
sudo systemctl stop apache2
sudo systemctl stop nginx
```

**Database Connection Issues:**
```bash
# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down
docker volume rm neuroscan_postgres_data
docker-compose up -d
```

**Permission Issues:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x deploy.sh
```

### Performance Optimization

**Database Performance:**
- Increase shared_buffers in PostgreSQL
- Configure connection pooling
- Optimize queries and add indexes

**Redis Performance:**
- Configure memory limits
- Enable persistence if needed
- Monitor memory usage

**Nginx Performance:**
- Enable gzip compression
- Configure caching headers
- Tune worker processes

## Environment Variables

### Required Variables
```env
# Database
POSTGRES_DB=neuroscan_db
POSTGRES_USER=neuroscan
POSTGRES_PASSWORD=secure_password

# Backend
JWT_SECRET_KEY=your_jwt_secret
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com

# Frontend
VITE_API_URL=https://api.yourdomain.com
```

### Optional Variables
```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# File Storage
MAX_UPLOAD_SIZE=50MB
UPLOAD_DIRECTORY=/app/uploads

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## API Documentation

After deployment, comprehensive API documentation is available at:
- **Swagger UI**: http://localhost/api/docs
- **ReDoc**: http://localhost/api/redoc

## Support and Maintenance

### Regular Maintenance Tasks
1. **Weekly**: Check logs for errors, verify backups
2. **Monthly**: Update Docker images, security patches
3. **Quarterly**: Review performance metrics, capacity planning

### Monitoring Recommendations
- Set up log aggregation (ELK stack)
- Configure alerting (Prometheus + Grafana)
- Monitor disk space and memory usage
- Track API response times and error rates

### Backup Strategy
- **Daily**: Automated database backups
- **Weekly**: Full system backup including volumes
- **Monthly**: Offsite backup verification
- **Quarterly**: Disaster recovery testing

For additional support, contact: support@neurocompany.com
