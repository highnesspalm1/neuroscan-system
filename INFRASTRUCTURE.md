# NeuroScan Hosting Infrastructure

## 📋 Overview

This directory contains the complete Docker-based hosting infrastructure for the NeuroScan system, including:

- **Multi-container orchestration** with Docker Compose
- **Production-ready configurations** for all services
- **Automated deployment scripts** for different environments
- **Monitoring and maintenance tools**
- **Backup and recovery solutions**
- **Security hardening configurations**

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │────│  Vue.js Frontend │────│  FastAPI Backend│
│   (Port 80/443) │    │   (Port 3000)    │    │   (Port 8000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐    ┌─────────────────┐
                    │  PostgreSQL DB  │────│  Redis Cache    │
                    │   (Port 5432)   │    │   (Port 6379)   │
                    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker 20.0+
- Docker Compose 2.0+
- 4GB+ RAM
- 20GB+ disk space

### 1. Clone and Setup
```bash
git clone <repository-url>
cd NeuroScan
cp .env.example .env
# Edit .env with your configuration
```

### 2. Deploy
```bash
# Linux/macOS
chmod +x deploy.sh
./deploy.sh

# Windows
deploy.bat
```

### 3. Access
- **Web Interface**: http://localhost
- **API Docs**: http://localhost/api/docs
- **Admin Panel**: http://localhost/admin

## 📁 File Structure

```
NeuroScan/
├── docker-compose.yml              # Main compose file
├── docker-compose.prod.yml         # Production configuration
├── docker-compose.override.yml     # Development overrides
├── .env.example                    # Environment template
├── deploy.sh / deploy.bat          # Deployment scripts
├── DEPLOYMENT.md                   # Detailed deployment guide
├── crontab.txt                     # Automated tasks
│
├── BackendAPI/
│   ├── Dockerfile                  # Backend container config
│   └── requirements.txt            # Python dependencies
│
├── WebFrontend/
│   ├── Dockerfile                  # Frontend container config
│   └── nginx.conf                  # Nginx configuration
│
├── nginx/
│   ├── nginx.conf                  # Main proxy configuration
│   └── ssl/                        # SSL certificates
│
├── database/
│   └── init.sql                    # Database initialization
│
└── scripts/
    ├── backup.sh                   # Database backup
    ├── restore.sh                  # Database restoration
    ├── monitor.sh                  # System monitoring
    └── dashboard.sh                # Status dashboard
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# Database
POSTGRES_PASSWORD=secure_password
JWT_SECRET_KEY=your_jwt_secret

# API
CORS_ORIGINS=https://yourdomain.com
VITE_API_URL=https://api.yourdomain.com

# Security
REDIS_PASSWORD=redis_password
```

### SSL Configuration
```bash
# Generate certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/nginx.key \
    -out nginx/ssl/nginx.crt
```

## 🔍 Monitoring

### System Dashboard
```bash
./scripts/dashboard.sh
```

### Health Monitoring
```bash
./scripts/monitor.sh
```

### View Logs
```bash
docker-compose logs -f
```

### Service Status
```bash
docker-compose ps
```

## 💾 Backup & Recovery

### Automated Backups
```bash
# Setup daily backups
crontab < crontab.txt
```

### Manual Backup
```bash
./scripts/backup.sh
```

### Restore Database
```bash
./scripts/restore.sh [backup_file]
```

## 🏭 Production Deployment

### 1. Use Production Compose
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Security Hardening
- Change default passwords
- Configure SSL certificates
- Set up firewall rules
- Enable monitoring alerts

### 3. Performance Tuning
- Configure resource limits
- Optimize database settings
- Set up caching strategies
- Enable compression

## 📊 Available Services

| Service | Port | Description |
|---------|------|-------------|
| Nginx | 80, 443 | Reverse proxy & load balancer |
| Frontend | 3000 | Vue.js web application |
| Backend | 8000 | FastAPI REST API |
| PostgreSQL | 5432 | Primary database |
| Redis | 6379 | Cache & session store |

## 🔒 Security Features

- **SSL/TLS encryption** for all communications
- **Rate limiting** to prevent abuse
- **Input validation** and sanitization
- **JWT token authentication**
- **Database connection encryption**
- **Container isolation**
- **Security headers** (HSTS, CSP, etc.)

## 📈 Monitoring & Alerting

### Health Checks
- Container health monitoring
- Database connectivity
- API endpoint verification
- SSL certificate expiration
- Disk space monitoring

### Automated Alerts
- Email notifications
- Slack integration
- Log analysis
- Performance metrics

## 🛠️ Maintenance Tasks

### Daily
- Health check monitoring
- Log analysis
- Backup verification

### Weekly
- System resource review
- Security updates
- Performance analysis

### Monthly
- Database optimization
- Certificate renewal
- Capacity planning

## 🚨 Troubleshooting

### Common Issues

**Port Conflicts**
```bash
sudo netstat -tulpn | grep :8000
sudo systemctl stop conflicting-service
```

**Database Connection**
```bash
docker-compose logs postgres
docker-compose restart postgres
```

**Memory Issues**
```bash
docker system prune -f
docker-compose down && docker-compose up -d
```

### Performance Optimization

**Database**
- Increase shared_buffers
- Configure connection pooling
- Add database indexes

**Redis**
- Configure memory limits
- Enable persistence
- Monitor cache hit rates

**Nginx**
- Enable gzip compression
- Configure cache headers
- Tune worker processes

## 📞 Support

### Log Locations
- Application logs: `docker-compose logs [service]`
- System logs: `/var/log/neuroscan-*.log`
- Access logs: `nginx/logs/`

### Debug Commands
```bash
# Container inspection
docker inspect [container_name]

# Resource usage
docker stats

# Network inspection
docker network ls
docker network inspect neuroscan_neuroscan-network
```

### Recovery Procedures
1. **Service restart**: `docker-compose restart [service]`
2. **Full rebuild**: `docker-compose down && docker-compose up -d --build`
3. **Database recovery**: `./scripts/restore.sh latest`
4. **Emergency shutdown**: `docker-compose down`

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [PostgreSQL Configuration](https://www.postgresql.org/docs/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [Redis Configuration](https://redis.io/documentation)

---

**NeuroScan Infrastructure v1.0**  
© 2025 NeuroCompany. All rights reserved.
