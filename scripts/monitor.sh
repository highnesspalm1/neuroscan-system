#!/bin/bash

# NeuroScan System Monitor Script
# This script monitors the health and performance of NeuroScan services

set -e

# Configuration
COMPOSE_FILE="docker-compose.yml"
LOG_FILE="/var/log/neuroscan-monitor.log"
ALERT_EMAIL=""  # Set email for alerts
SLACK_WEBHOOK=""  # Set Slack webhook for alerts

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[MONITOR]${NC} $1"
    echo "$(date): [MONITOR] $1" >> "$LOG_FILE" 2>/dev/null || true
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "$(date): [WARNING] $1" >> "$LOG_FILE" 2>/dev/null || true
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "$(date): [ERROR] $1" >> "$LOG_FILE" 2>/dev/null || true
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Function to send alerts
send_alert() {
    local message="$1"
    local level="$2"
    
    # Email alert
    if [ -n "$ALERT_EMAIL" ] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "NeuroScan Alert - $level" "$ALERT_EMAIL"
    fi
    
    # Slack alert
    if [ -n "$SLACK_WEBHOOK" ] && command -v curl &> /dev/null; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"NeuroScan Alert [$level]: $message\"}" \
            "$SLACK_WEBHOOK" &>/dev/null || true
    fi
}

# Function to check service health
check_service_health() {
    local service_name="$1"
    local health_url="$2"
    local timeout="${3:-10}"
    
    if curl -f -s --max-time "$timeout" "$health_url" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check container status
check_container_status() {
    local container_name="$1"
    local status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null)
    
    if [ "$status" = "running" ]; then
        return 0
    else
        return 1
    fi
}

# Function to get container stats
get_container_stats() {
    local container_name="$1"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" "$container_name" 2>/dev/null
}

# Function to check disk space
check_disk_space() {
    local threshold=80
    local usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -gt "$threshold" ]; then
        print_error "Disk space usage is ${usage}% (threshold: ${threshold}%)"
        send_alert "Disk space usage is ${usage}%" "ERROR"
        return 1
    else
        print_status "Disk space usage: ${usage}%"
        return 0
    fi
}

# Function to check memory usage
check_memory_usage() {
    local threshold=80
    local usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    
    if [ "$usage" -gt "$threshold" ]; then
        print_warning "Memory usage is ${usage}% (threshold: ${threshold}%)"
        return 1
    else
        print_status "Memory usage: ${usage}%"
        return 0
    fi
}

# Function to check database connectivity
check_database() {
    local container_name="neuroscan-postgres"
    
    if check_container_status "$container_name"; then
        if docker exec "$container_name" pg_isready -U neuroscan -d neuroscan_db &>/dev/null; then
            print_status "Database is healthy"
            return 0
        else
            print_error "Database is not responding"
            send_alert "PostgreSQL database is not responding" "ERROR"
            return 1
        fi
    else
        print_error "Database container is not running"
        send_alert "PostgreSQL container is not running" "ERROR"
        return 1
    fi
}

# Function to check Redis connectivity
check_redis() {
    local container_name="neuroscan-redis"
    
    if check_container_status "$container_name"; then
        if docker exec "$container_name" redis-cli ping | grep -q "PONG"; then
            print_status "Redis is healthy"
            return 0
        else
            print_error "Redis is not responding"
            send_alert "Redis cache is not responding" "ERROR"
            return 1
        fi
    else
        print_error "Redis container is not running"
        send_alert "Redis container is not running" "ERROR"
        return 1
    fi
}

# Function to check API endpoints
check_api_endpoints() {
    local base_url="http://localhost:8000"
    local endpoints=(
        "/health"
        "/api/v1/status"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if check_service_health "API $endpoint" "${base_url}${endpoint}"; then
            print_status "API endpoint $endpoint is healthy"
        else
            print_error "API endpoint $endpoint is not responding"
            send_alert "API endpoint $endpoint is not responding" "ERROR"
        fi
    done
}

# Function to check log files for errors
check_logs() {
    local log_patterns=(
        "ERROR"
        "CRITICAL"
        "FATAL"
        "Exception"
    )
    
    for pattern in "${log_patterns[@]}"; do
        local count=$(docker-compose logs --since="1h" 2>/dev/null | grep -c "$pattern" || echo "0")
        if [ "$count" -gt 10 ]; then
            print_warning "Found $count occurrences of '$pattern' in logs (last hour)"
        fi
    done
}

# Function to perform security checks
check_security() {
    # Check for default passwords
    if grep -q "change_this" .env 2>/dev/null; then
        print_error "Default passwords detected in .env file"
        send_alert "Default passwords detected in configuration" "ERROR"
    fi
    
    # Check SSL certificate expiration
    if [ -f "nginx/ssl/nginx.crt" ]; then
        local expiry_date=$(openssl x509 -enddate -noout -in nginx/ssl/nginx.crt | cut -d= -f2)
        local expiry_epoch=$(date -d "$expiry_date" +%s 2>/dev/null || echo "0")
        local current_epoch=$(date +%s)
        local days_left=$(( (expiry_epoch - current_epoch) / 86400 ))
        
        if [ "$days_left" -lt 30 ]; then
            print_warning "SSL certificate expires in $days_left days"
            send_alert "SSL certificate expires in $days_left days" "WARNING"
        fi
    fi
}

# Main monitoring function
main() {
    print_info "Starting NeuroScan system monitoring..."
    print_info "Timestamp: $(date)"
    echo ""
    
    # System resource checks
    print_info "=== System Resources ==="
    check_disk_space
    check_memory_usage
    echo ""
    
    # Service health checks
    print_info "=== Service Health ==="
    
    # Check individual containers
    local services=("neuroscan-backend" "neuroscan-frontend" "neuroscan-postgres" "neuroscan-redis" "neuroscan-nginx")
    
    for service in "${services[@]}"; do
        if check_container_status "$service"; then
            print_status "Container $service is running"
        else
            print_error "Container $service is not running"
            send_alert "Container $service is not running" "ERROR"
        fi
    done
    echo ""
    
    # Database and Redis specific checks
    print_info "=== Database & Cache ==="
    check_database
    check_redis
    echo ""
    
    # API endpoint checks
    print_info "=== API Endpoints ==="
    check_api_endpoints
    echo ""
    
    # Security checks
    print_info "=== Security ==="
    check_security
    echo ""
    
    # Log analysis
    print_info "=== Log Analysis ==="
    check_logs
    echo ""
    
    # Container statistics
    print_info "=== Container Statistics ==="
    for service in "${services[@]}"; do
        if check_container_status "$service"; then
            get_container_stats "$service"
        fi
    done
    echo ""
    
    # Docker system information
    print_info "=== Docker System ==="
    docker system df
    echo ""
    
    print_info "Monitoring completed at $(date)"
}

# Handle command line arguments
case "${1:-monitor}" in
    "monitor"|"")
        main
        ;;
    "status")
        docker-compose ps
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "stats")
        docker stats
        ;;
    "cleanup")
        print_info "Cleaning up Docker system..."
        docker system prune -f
        ;;
    "help")
        echo "NeuroScan System Monitor"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  monitor    Run full system monitoring (default)"
        echo "  status     Show service status"
        echo "  logs       Show and follow logs"
        echo "  stats      Show container statistics"
        echo "  cleanup    Clean up Docker system"
        echo "  help       Show this help message"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac
