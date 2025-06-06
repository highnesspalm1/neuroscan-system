#!/bin/bash

# NeuroScan System Dashboard
# This script provides a comprehensive overview of the system status

clear

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Function to draw a separator
draw_separator() {
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════════════════${NC}"
}

# Function to get service status
get_service_status() {
    local container_name="$1"
    local status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null)
    
    case "$status" in
        "running")
            echo -e "${GREEN}●${NC} Running"
            ;;
        "exited")
            echo -e "${RED}●${NC} Exited"
            ;;
        "restarting")
            echo -e "${YELLOW}●${NC} Restarting"
            ;;
        "paused")
            echo -e "${YELLOW}●${NC} Paused"
            ;;
        *)
            echo -e "${RED}●${NC} Not Found"
            ;;
    esac
}

# Function to get uptime
get_uptime() {
    local container_name="$1"
    local started=$(docker inspect --format='{{.State.StartedAt}}' "$container_name" 2>/dev/null)
    if [ -n "$started" ]; then
        local started_epoch=$(date -d "$started" +%s 2>/dev/null || echo "0")
        local current_epoch=$(date +%s)
        local uptime_seconds=$((current_epoch - started_epoch))
        
        if [ "$uptime_seconds" -gt 86400 ]; then
            echo "$((uptime_seconds / 86400))d $((uptime_seconds % 86400 / 3600))h"
        elif [ "$uptime_seconds" -gt 3600 ]; then
            echo "$((uptime_seconds / 3600))h $((uptime_seconds % 3600 / 60))m"
        else
            echo "$((uptime_seconds / 60))m"
        fi
    else
        echo "N/A"
    fi
}

# Function to check URL health
check_url_health() {
    local url="$1"
    if curl -f -s --max-time 5 "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Healthy"
    else
        echo -e "${RED}✗${NC} Down"
    fi
}

# Header
echo -e "${WHITE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           NeuroScan System Dashboard                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${CYAN}Last Updated: $(date)${NC}"
echo ""

# System Information
draw_separator
echo -e "${WHITE}📊 SYSTEM INFORMATION${NC}"
draw_separator

echo -e "${BLUE}Hostname:${NC} $(hostname)"
echo -e "${BLUE}OS:${NC} $(uname -o) $(uname -r)"
echo -e "${BLUE}Architecture:${NC} $(uname -m)"
echo -e "${BLUE}Load Average:${NC} $(uptime | awk -F'load average:' '{ print $2 }')"
echo -e "${BLUE}Disk Usage:${NC} $(df -h / | awk 'NR==2 {print $5 " of " $2 " used"}')"
echo -e "${BLUE}Memory Usage:${NC} $(free -h | awk 'NR==2{printf "%s of %s used (%.1f%%)", $3, $2, $3*100/$2}')"
echo ""

# Service Status
draw_separator
echo -e "${WHITE}🐳 CONTAINER STATUS${NC}"
draw_separator

printf "%-25s %-15s %-15s %-10s\n" "Service" "Status" "Uptime" "Health"
echo "────────────────────────────────────────────────────────────────────────"

# Backend API
printf "%-25s %-15s %-15s %-10s\n" \
    "Backend API" \
    "$(get_service_status neuroscan-backend)" \
    "$(get_uptime neuroscan-backend)" \
    "$(check_url_health http://localhost:8000/health)"

# Frontend
printf "%-25s %-15s %-15s %-10s\n" \
    "Frontend" \
    "$(get_service_status neuroscan-frontend)" \
    "$(get_uptime neuroscan-frontend)" \
    "$(check_url_health http://localhost:3000)"

# Database
printf "%-25s %-15s %-15s %-10s\n" \
    "PostgreSQL" \
    "$(get_service_status neuroscan-postgres)" \
    "$(get_uptime neuroscan-postgres)" \
    "$(docker exec neuroscan-postgres pg_isready -U neuroscan -d neuroscan_db &>/dev/null && echo -e "${GREEN}✓${NC} Connected" || echo -e "${RED}✗${NC} Error")"

# Redis
printf "%-25s %-15s %-15s %-10s\n" \
    "Redis Cache" \
    "$(get_service_status neuroscan-redis)" \
    "$(get_uptime neuroscan-redis)" \
    "$(docker exec neuroscan-redis redis-cli ping 2>/dev/null | grep -q "PONG" && echo -e "${GREEN}✓${NC} Connected" || echo -e "${RED}✗${NC} Error")"

# Nginx
printf "%-25s %-15s %-15s %-10s\n" \
    "Nginx Proxy" \
    "$(get_service_status neuroscan-nginx)" \
    "$(get_uptime neuroscan-nginx)" \
    "$(check_url_health http://localhost/health)"

echo ""

# Resource Usage
draw_separator
echo -e "${WHITE}📈 RESOURCE USAGE${NC}"
draw_separator

echo "Container Resource Statistics:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}" 2>/dev/null | head -6
echo ""

# Network Information
draw_separator
echo -e "${WHITE}🌐 NETWORK ACCESS${NC}"
draw_separator

echo -e "${BLUE}Web Interface:${NC} http://localhost"
echo -e "${BLUE}API Documentation:${NC} http://localhost/api/docs"
echo -e "${BLUE}Admin Panel:${NC} http://localhost/admin"
echo -e "${BLUE}Health Check:${NC} http://localhost/health"
echo ""

echo "Service Endpoints:"
printf "%-20s %-30s %-15s\n" "Service" "URL" "Status"
echo "──────────────────────────────────────────────────────────────"
printf "%-20s %-30s %-15s\n" "Frontend" "http://localhost:3000" "$(check_url_health http://localhost:3000)"
printf "%-20s %-30s %-15s\n" "Backend API" "http://localhost:8000" "$(check_url_health http://localhost:8000/health)"
printf "%-20s %-30s %-15s\n" "Database" "localhost:5432" "$(nc -z localhost 5432 && echo -e "${GREEN}✓${NC} Open" || echo -e "${RED}✗${NC} Closed")"
printf "%-20s %-30s %-15s\n" "Redis" "localhost:6379" "$(nc -z localhost 6379 && echo -e "${GREEN}✓${NC} Open" || echo -e "${RED}✗${NC} Closed")"
echo ""

# Database Statistics
if docker exec neuroscan-postgres pg_isready -U neuroscan -d neuroscan_db &>/dev/null; then
    draw_separator
    echo -e "${WHITE}🗄️  DATABASE STATISTICS${NC}"
    draw_separator
    
    # Get database stats
    DB_SIZE=$(docker exec neuroscan-postgres psql -U neuroscan -d neuroscan_db -t -c "SELECT pg_size_pretty(pg_database_size('neuroscan_db'));" 2>/dev/null | xargs)
    TABLES_COUNT=$(docker exec neuroscan-postgres psql -U neuroscan -d neuroscan_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null | xargs)
    PRODUCTS_COUNT=$(docker exec neuroscan-postgres psql -U neuroscan -d neuroscan_db -t -c "SELECT COUNT(*) FROM products;" 2>/dev/null | xargs)
    USERS_COUNT=$(docker exec neuroscan-postgres psql -U neuroscan -d neuroscan_db -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | xargs)
    
    echo -e "${BLUE}Database Size:${NC} $DB_SIZE"
    echo -e "${BLUE}Tables Count:${NC} $TABLES_COUNT"
    echo -e "${BLUE}Products Count:${NC} $PRODUCTS_COUNT"
    echo -e "${BLUE}Users Count:${NC} $USERS_COUNT"
    echo ""
fi

# Recent Activity
draw_separator
echo -e "${WHITE}📝 RECENT ACTIVITY${NC}"
draw_separator

echo "Recent Container Events (last 10):"
docker events --since="24h" --until="0s" --format "{{.Time}} {{.Actor.Attributes.name}} {{.Action}}" 2>/dev/null | tail -5 2>/dev/null || echo "No recent events"
echo ""

# Backup Information
draw_separator
echo -e "${WHITE}💾 BACKUP STATUS${NC}"
draw_separator

if [ -d "/backups" ] || [ -d "database/backups" ]; then
    BACKUP_DIR="/backups"
    [ -d "database/backups" ] && BACKUP_DIR="database/backups"
    
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/neuroscan_backup_* 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        BACKUP_DATE=$(stat -c %y "$LATEST_BACKUP" 2>/dev/null | cut -d' ' -f1)
        BACKUP_SIZE=$(du -h "$LATEST_BACKUP" 2>/dev/null | cut -f1)
        echo -e "${BLUE}Latest Backup:${NC} $(basename "$LATEST_BACKUP")"
        echo -e "${BLUE}Backup Date:${NC} $BACKUP_DATE"
        echo -e "${BLUE}Backup Size:${NC} $BACKUP_SIZE"
        
        BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/neuroscan_backup_* 2>/dev/null | wc -l)
        echo -e "${BLUE}Total Backups:${NC} $BACKUP_COUNT"
    else
        echo -e "${YELLOW}No backups found${NC}"
    fi
else
    echo -e "${YELLOW}Backup directory not found${NC}"
fi
echo ""

# Security Status
draw_separator
echo -e "${WHITE}🔒 SECURITY STATUS${NC}"
draw_separator

# Check SSL certificate
if [ -f "nginx/ssl/nginx.crt" ]; then
    CERT_EXPIRY=$(openssl x509 -enddate -noout -in nginx/ssl/nginx.crt 2>/dev/null | cut -d= -f2)
    if [ -n "$CERT_EXPIRY" ]; then
        EXPIRY_EPOCH=$(date -d "$CERT_EXPIRY" +%s 2>/dev/null || echo "0")
        CURRENT_EPOCH=$(date +%s)
        DAYS_LEFT=$(( (EXPIRY_EPOCH - CURRENT_EPOCH) / 86400 ))
        
        if [ "$DAYS_LEFT" -gt 30 ]; then
            echo -e "${BLUE}SSL Certificate:${NC} ${GREEN}✓${NC} Valid ($DAYS_LEFT days left)"
        elif [ "$DAYS_LEFT" -gt 0 ]; then
            echo -e "${BLUE}SSL Certificate:${NC} ${YELLOW}⚠${NC} Expires in $DAYS_LEFT days"
        else
            echo -e "${BLUE}SSL Certificate:${NC} ${RED}✗${NC} Expired"
        fi
    fi
else
    echo -e "${BLUE}SSL Certificate:${NC} ${YELLOW}⚠${NC} Not found"
fi

# Check for default passwords
if grep -q "change_this" .env 2>/dev/null; then
    echo -e "${BLUE}Password Security:${NC} ${RED}✗${NC} Default passwords detected"
else
    echo -e "${BLUE}Password Security:${NC} ${GREEN}✓${NC} Custom passwords configured"
fi

echo ""

# Footer
draw_separator
echo -e "${CYAN}Use './scripts/monitor.sh help' for monitoring commands${NC}"
echo -e "${CYAN}Use 'docker-compose logs -f' to view live logs${NC}"
echo -e "${CYAN}Use 'docker-compose ps' for detailed container status${NC}"
draw_separator

echo ""
echo -e "${WHITE}Dashboard refresh: ./scripts/dashboard.sh${NC}"
