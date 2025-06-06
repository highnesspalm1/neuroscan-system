# NeuroScan Deployment Guide

## Overview

This guide covers the deployment of NeuroScan in various environments from development to production. The system supports multiple deployment strategies including Docker, Kubernetes, and traditional server deployments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Traditional Server Deployment](#traditional-server-deployment)
6. [Database Setup](#database-setup)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Monitoring Setup](#monitoring-setup)
9. [Backup and Recovery](#backup-and-recovery)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB SSD
- OS: Ubuntu 20.04+, CentOS 8+, or Windows Server 2019+

**Recommended for Production:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 50GB+ SSD
- OS: Ubuntu 22.04 LTS

### Software Dependencies

- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL 12+
- Redis 6+
- Nginx 1.20+
- Python 3.8+
- Node.js 16+

## Environment Configuration

### Development Environment

```bash
# Clone repository
git clone https://github.com/neurocompany/neuroscan.git
cd neuroscan

# Setup environment
cp .env.example .env.development
```

**Environment Variables (.env.development):**
```env
# Application
APP_ENV=development
DEBUG=true
SECRET_KEY=dev_secret_key_change_in_production

# Database
DATABASE_URL=postgresql://neuroscan:password@localhost:5432/neuroscan_dev
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=dev_jwt_secret
ENCRYPTION_KEY=dev_encryption_key_32_characters
API_KEY_SECRET=dev_api_key_secret

# External Services
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=60

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### Staging Environment

**Environment Variables (.env.staging):**
```env
# Application
APP_ENV=staging
DEBUG=false
SECRET_KEY=staging_secret_key_use_random_generator

# Database
DATABASE_URL=postgresql://neuroscan:secure_password@staging-db:5432/neuroscan_staging
REDIS_URL=redis://staging-redis:6379/0

# Security
JWT_SECRET_KEY=staging_jwt_secret_use_random_generator
ENCRYPTION_KEY=staging_encryption_key_32_chars
API_KEY_SECRET=staging_api_key_secret

# External Services
SMTP_HOST=smtp.staging.com
SMTP_PORT=587
SMTP_USERNAME=neuroscan@staging.com
SMTP_PASSWORD=staging_smtp_password

# Rate Limiting
RATE_LIMIT_REQUESTS=500
RATE_LIMIT_WINDOW=60

# CORS
ALLOWED_ORIGINS=["https://staging.neuroscan.com"]
```

### Production Environment

**Environment Variables (.env.production):**
```env
# Application
APP_ENV=production
DEBUG=false
SECRET_KEY=production_secret_key_use_strong_random

# Database
DATABASE_URL=postgresql://neuroscan:very_secure_password@prod-db:5432/neuroscan_prod
REDIS_URL=redis://prod-redis:6379/0

# Security
JWT_SECRET_KEY=production_jwt_secret_use_strong_random
ENCRYPTION_KEY=production_encryption_key_32_chars
API_KEY_SECRET=production_api_key_secret

# External Services
SMTP_HOST=smtp.neurocompany.com
SMTP_PORT=587
SMTP_USERNAME=neuroscan@neurocompany.com
SMTP_PASSWORD=production_smtp_password

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# CORS
ALLOWED_ORIGINS=["https://neuroscan.com", "https://verify.neuroscan.com"]

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
PROMETHEUS_ENABLED=true

# SSL
SSL_CERT_PATH=/etc/ssl/certs/neuroscan.crt
SSL_KEY_PATH=/etc/ssl/private/neuroscan.key
```

## Docker Deployment

### Single Container Development

```bash
# Build and run backend
cd BackendAPI
docker build -t neuroscan-api .
docker run -d \
  --name neuroscan-api \
  -p 8000:8000 \
  --env-file .env.development \
  neuroscan-api

# Build and run frontend
cd ../WebFrontend
docker build -t neuroscan-web .
docker run -d \
  --name neuroscan-web \
  -p 3000:3000 \
  neuroscan-web
```

### Docker Compose Development

```bash
# Start all services
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Compose Production

```bash
# Production deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale API instances
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale api=3

# Update services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://get.helm.sh/helm-v3.12.0-linux-amd64.tar.gz | tar xz
sudo mv linux-amd64/helm /usr/local/bin/
```

### Namespace Setup

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: neuroscan
  labels:
    name: neuroscan
    environment: production
```

### ConfigMap and Secrets

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: neuroscan-config
  namespace: neuroscan
data:
  APP_ENV: "production"
  DEBUG: "false"
  RATE_LIMIT_REQUESTS: "100"
  RATE_LIMIT_WINDOW: "60"
  PROMETHEUS_ENABLED: "true"
```

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: neuroscan-secrets
  namespace: neuroscan
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret>
  DATABASE_URL: <base64-encoded-db-url>
  JWT_SECRET_KEY: <base64-encoded-jwt-secret>
  ENCRYPTION_KEY: <base64-encoded-encryption-key>
```

### Database Deployment

```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: neuroscan
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: neuroscan_prod
        - name: POSTGRES_USER
          value: neuroscan
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: neuroscan-secrets
              key: POSTGRES_PASSWORD
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

### API Deployment

```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: neuroscan-api
  namespace: neuroscan
spec:
  replicas: 3
  selector:
    matchLabels:
      app: neuroscan-api
  template:
    metadata:
      labels:
        app: neuroscan-api
    spec:
      containers:
      - name: api
        image: neuroscan/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: APP_ENV
          valueFrom:
            configMapKeyRef:
              name: neuroscan-config
              key: APP_ENV
        envFrom:
        - secretRef:
            name: neuroscan-secrets
        - configMapRef:
            name: neuroscan-config
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Service and Ingress

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: neuroscan-api-service
  namespace: neuroscan
spec:
  selector:
    app: neuroscan-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: neuroscan-ingress
  namespace: neuroscan
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - api.neuroscan.com
    secretName: neuroscan-tls
  rules:
  - host: api.neuroscan.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: neuroscan-api-service
            port:
              number: 80
```

### Deployment Commands

```bash
# Apply configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Deploy database
kubectl apply -f k8s/postgres.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n neuroscan --timeout=300s

# Deploy API
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Check deployment status
kubectl get pods -n neuroscan
kubectl get services -n neuroscan
kubectl get ingress -n neuroscan
```

## Traditional Server Deployment

### Ubuntu Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.8 python3.8-venv python3-pip postgresql postgresql-contrib redis-server nginx supervisor git

# Create application user
sudo useradd -m -s /bin/bash neuroscan
sudo usermod -aG sudo neuroscan

# Switch to application user
sudo su - neuroscan

# Clone and setup application
git clone https://github.com/neurocompany/neuroscan.git
cd neuroscan

# Setup Python environment
python3.8 -m venv venv
source venv/bin/activate
pip install -r BackendAPI/requirements.txt

# Setup database
sudo -u postgres createuser neuroscan
sudo -u postgres createdb neuroscan_prod -O neuroscan
sudo -u postgres psql -c "ALTER USER neuroscan PASSWORD 'secure_password';"
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/neuroscan
server {
    listen 80;
    server_name api.neuroscan.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.neuroscan.com;

    ssl_certificate /etc/ssl/certs/neuroscan.crt;
    ssl_certificate_key /etc/ssl/private/neuroscan.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/neuroscan/neuroscan/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Supervisor Configuration

```ini
# /etc/supervisor/conf.d/neuroscan.conf
[program:neuroscan-api]
command=/home/neuroscan/neuroscan/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/home/neuroscan/neuroscan/BackendAPI
user=neuroscan
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/neuroscan/api.log
environment=PATH="/home/neuroscan/neuroscan/venv/bin"

[program:neuroscan-worker]
command=/home/neuroscan/neuroscan/venv/bin/celery -A app.worker worker --loglevel=info
directory=/home/neuroscan/neuroscan/BackendAPI
user=neuroscan
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/neuroscan/worker.log
environment=PATH="/home/neuroscan/neuroscan/venv/bin"
```

### Service Management

```bash
# Enable and start services
sudo systemctl enable nginx postgresql redis-server supervisor
sudo systemctl start nginx postgresql redis-server supervisor

# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/neuroscan /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Start Supervisor programs
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start neuroscan-api
sudo supervisorctl start neuroscan-worker
```

## Database Setup

### PostgreSQL Configuration

```sql
-- Create database and user
CREATE USER neuroscan WITH PASSWORD 'secure_password';
CREATE DATABASE neuroscan_prod OWNER neuroscan;
GRANT ALL PRIVILEGES ON DATABASE neuroscan_prod TO neuroscan;

-- Configure PostgreSQL for production
-- /etc/postgresql/14/main/postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### Database Migrations

```bash
# Run initial migrations
cd /home/neuroscan/neuroscan/BackendAPI
source ../venv/bin/activate
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

### Database Backup Setup

```bash
# Create backup script
cat > /home/neuroscan/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/neuroscan/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="neuroscan_backup_$DATE.sql"

mkdir -p $BACKUP_DIR
pg_dump -h localhost -U neuroscan neuroscan_prod > $BACKUP_DIR/$FILENAME
gzip $BACKUP_DIR/$FILENAME

# Keep only last 7 days of backups
find $BACKUP_DIR -name "neuroscan_backup_*.sql.gz" -mtime +7 -delete

echo "Database backup completed: $FILENAME.gz"
EOF

chmod +x /home/neuroscan/backup_db.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /home/neuroscan/backup_db.sh
```

## SSL/TLS Configuration

### Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.neuroscan.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Custom SSL Certificate

```bash
# Generate private key
sudo openssl genrsa -out /etc/ssl/private/neuroscan.key 2048

# Generate certificate signing request
sudo openssl req -new -key /etc/ssl/private/neuroscan.key -out /tmp/neuroscan.csr

# Install provided certificate
sudo cp neuroscan.crt /etc/ssl/certs/
sudo chmod 644 /etc/ssl/certs/neuroscan.crt
sudo chmod 600 /etc/ssl/private/neuroscan.key
```

## Monitoring Setup

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'neuroscan-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "NeuroScan Monitoring",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, neuroscan_request_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph", 
        "targets": [
          {
            "expr": "rate(neuroscan_requests_total[5m])"
          }
        ]
      }
    ]
  }
}
```

## Backup and Recovery

### Automated Backup Script

```bash
#!/bin/bash
# /home/neuroscan/scripts/backup.sh

BACKUP_DIR="/home/neuroscan/backups"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/neuroscan/neuroscan"

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# Database backup
pg_dump -h localhost -U neuroscan neuroscan_prod | gzip > $BACKUP_DIR/$DATE/database.sql.gz

# Application files backup
tar -czf $BACKUP_DIR/$DATE/application.tar.gz -C $APP_DIR .

# Configuration backup
cp /etc/nginx/sites-available/neuroscan $BACKUP_DIR/$DATE/
cp /etc/supervisor/conf.d/neuroscan.conf $BACKUP_DIR/$DATE/

# Upload to cloud storage (optional)
# aws s3 sync $BACKUP_DIR/$DATE s3://neuroscan-backups/$DATE/

echo "Backup completed: $DATE"
```

### Recovery Procedures

```bash
# Database recovery
gunzip -c database.sql.gz | psql -h localhost -U neuroscan neuroscan_prod

# Application recovery
tar -xzf application.tar.gz -C /home/neuroscan/neuroscan/

# Restart services
sudo supervisorctl restart neuroscan-api
sudo supervisorctl restart neuroscan-worker
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql
sudo -u postgres psql -c "\l"

# Check connection
psql -h localhost -U neuroscan neuroscan_prod
```

2. **Application Not Starting**
```bash
# Check logs
sudo tail -f /var/log/neuroscan/api.log
sudo supervisorctl status

# Check Python environment
source /home/neuroscan/neuroscan/venv/bin/activate
python -c "import app; print('OK')"
```

3. **High Memory Usage**
```bash
# Monitor processes
htop
ps aux | grep neuroscan

# Check database queries
sudo -u postgres psql neuroscan_prod -c "SELECT query, state, query_start FROM pg_stat_activity WHERE state = 'active';"
```

4. **SSL Certificate Issues**
```bash
# Check certificate
openssl x509 -in /etc/ssl/certs/neuroscan.crt -text -noout

# Test SSL
openssl s_client -connect api.neuroscan.com:443
```

### Performance Optimization

1. **Database Optimization**
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM certificates WHERE serial_number = 'NS-2024-001';

-- Create indexes
CREATE INDEX idx_certificates_serial ON certificates(serial_number);
CREATE INDEX idx_certificates_customer ON certificates(customer_name);
```

2. **Application Optimization**
```bash
# Increase worker processes
# Edit /etc/supervisor/conf.d/neuroscan.conf
command=/home/neuroscan/neuroscan/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 8
```

3. **Nginx Optimization**
```nginx
# Add to nginx configuration
worker_processes auto;
worker_connections 1024;

gzip on;
gzip_types text/plain application/json application/javascript text/css;

client_max_body_size 10M;
```

### Log Analysis

```bash
# API logs
tail -f /var/log/neuroscan/api.log | grep ERROR

# Access logs
tail -f /var/log/nginx/access.log | grep "POST /verify"

# System logs
journalctl -u nginx -f
journalctl -u postgresql -f
```

---

This deployment guide provides comprehensive instructions for deploying NeuroScan in various environments. For specific issues or advanced configurations, consult the detailed documentation or contact support.
