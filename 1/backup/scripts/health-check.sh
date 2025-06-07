#!/bin/bash
# NeuroScan Docker Health Check Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to check if a service is healthy
check_service_health() {
    local service_name="$1"
    local health_url="$2"
    local expected_status="$3"
    
    echo -n "Checking $service_name... "
    
    if curl -f -s "$health_url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ Unhealthy${NC}"
        return 1
    fi
}

# Function to check container status
check_container_status() {
    local container_name="$1"
    
    echo -n "Checking container $container_name... "
    
    if docker ps --filter "name=$container_name" --filter "status=running" | grep -q "$container_name"; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not running${NC}"
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    echo -n "Checking database connectivity... "
    
    if docker-compose exec -T postgres pg_isready -U neuroscan -d neuroscan_db > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Connected${NC}"
        return 0
    else
        echo -e "${RED}✗ Connection failed${NC}"
        return 1
    fi
}

# Function to check Redis connectivity
check_redis() {
    echo -n "Checking Redis connectivity... "
    
    if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
        echo -e "${GREEN}✓ Connected${NC}"
        return 0
    else
        echo -e "${RED}✗ Connection failed${NC}"
        return 1
    fi
}

# Main health check
echo -e "${BLUE}NeuroScan System Health Check${NC}"
echo "================================"

# Check Docker daemon
echo -n "Checking Docker daemon... "
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Docker daemon not running${NC}"
    exit 1
fi

# Check containers
echo ""
echo "Container Status:"
check_container_status "neuroscan-backend"
check_container_status "neuroscan-frontend" 
check_container_status "neuroscan-postgres"
check_container_status "neuroscan-redis"
check_container_status "neuroscan-nginx"

# Check services
echo ""
echo "Service Health:"
check_service_health "Backend API" "http://localhost:8000/health" "200"
check_service_health "Frontend" "http://localhost:3000" "200"
check_service_health "Nginx" "http://localhost/health" "200"

# Check database and cache
echo ""
echo "Database & Cache:"
check_database
check_redis

# Overall system status
echo ""
echo "System Resources:"
echo -n "CPU Usage: "
cpu_usage=$(docker stats --no-stream --format "table {{.CPUPerc}}" | grep -v CPU | head -1)
echo -e "${YELLOW}$cpu_usage${NC}"

echo -n "Memory Usage: "
memory_usage=$(docker stats --no-stream --format "table {{.MemUsage}}" | grep -v MEM | head -1)
echo -e "${YELLOW}$memory_usage${NC}"

echo -n "Disk Usage: "
disk_usage=$(df -h / | awk 'NR==2{print $5}')
echo -e "${YELLOW}$disk_usage${NC}"

echo ""
echo -e "${GREEN}Health check completed!${NC}"
