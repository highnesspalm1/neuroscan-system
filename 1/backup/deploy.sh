#!/bin/bash

# NeuroScan Deployment Script
# This script builds and deploys the NeuroScan system using Docker

set -e

echo "🚀 Starting NeuroScan Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p nginx/ssl
mkdir -p database/backups
mkdir -p logs

# Generate SSL certificates (self-signed for development)
if [ ! -f "nginx/ssl/nginx.crt" ]; then
    print_status "Generating self-signed SSL certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/nginx.key \
        -out nginx/ssl/nginx.crt \
        -subj "/C=US/ST=State/L=City/O=NeuroCompany/CN=localhost"
fi

# Environment setup
print_status "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# NeuroScan Environment Configuration
COMPOSE_PROJECT_NAME=neuroscan

# Database Configuration
POSTGRES_DB=neuroscan_db
POSTGRES_USER=neuroscan
POSTGRES_PASSWORD=neuroscan_password_$(openssl rand -hex 16)

# Backend Configuration
JWT_SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:3000,https://localhost

# Frontend Configuration
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=production

# Redis Configuration
REDIS_PASSWORD=$(openssl rand -hex 16)
EOF
    print_status "Environment file created with secure random passwords"
else
    print_warning "Environment file already exists. Using existing configuration."
fi

# Function to check service health
check_service_health() {
    local service_name=$1
    local health_url=$2
    local max_attempts=30
    local attempt=1

    print_status "Checking health of $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$health_url" > /dev/null 2>&1; then
            print_status "$service_name is healthy!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name failed to become healthy"
    return 1
}

# Build and start services
print_status "Building Docker images..."
docker-compose build --no-cache

print_status "Starting services..."
docker-compose up -d

# Wait for services to be ready
sleep 10

# Check service health
print_status "Performing health checks..."
check_service_health "Database" "http://localhost:5432" || true
check_service_health "Redis" "http://localhost:6379" || true
check_service_health "Backend API" "http://localhost:8000/health"
check_service_health "Frontend" "http://localhost:3000"
check_service_health "Nginx" "http://localhost/health"

# Display service status
print_status "Service Status:"
docker-compose ps

# Display access information
echo ""
print_status "🎉 NeuroScan deployment completed successfully!"
echo ""
echo "Access your NeuroScan system:"
echo "  • Web Interface: http://localhost"
echo "  • API Documentation: http://localhost/api/docs"
echo "  • Admin Panel: http://localhost/admin"
echo ""
echo "Service URLs:"
echo "  • Frontend: http://localhost:3000"
echo "  • Backend API: http://localhost:8000"
echo "  • Database: localhost:5432"
echo "  • Redis: localhost:6379"
echo ""
print_warning "Note: This is a development setup with self-signed certificates."
print_warning "For production, replace with proper SSL certificates."
echo ""

# Show logs option
read -p "Would you like to view the logs? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose logs -f
fi
