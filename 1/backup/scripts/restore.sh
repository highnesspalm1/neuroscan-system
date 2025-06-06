#!/bin/bash

# NeuroScan Database Restore Script
# This script restores the PostgreSQL database from encrypted backups

set -e

# Configuration
BACKUP_DIR="/backups"
POSTGRES_HOST="postgres"
POSTGRES_PORT="5432"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[RESTORE]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [backup_file]"
    echo ""
    echo "If no backup file is specified, the script will show available backups"
    echo ""
    echo "Examples:"
    echo "  $0                                    # List available backups"
    echo "  $0 neuroscan_backup_20250101_120000.sql.gpg  # Restore specific backup"
    echo "  $0 latest                            # Restore latest backup"
}

# Check if required environment variables are set
if [ -z "$POSTGRES_DB" ] || [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ]; then
    print_error "Required environment variables are not set"
    exit 1
fi

# List available backups if no file specified
if [ $# -eq 0 ]; then
    print_status "Available backups in $BACKUP_DIR:"
    if ls -lht "$BACKUP_DIR"/neuroscan_backup_*.sql* 2>/dev/null; then
        echo ""
        echo "To restore a backup, run: $0 <backup_filename>"
        echo "To restore the latest backup, run: $0 latest"
    else
        print_warning "No backups found in $BACKUP_DIR"
    fi
    exit 0
fi

BACKUP_FILE="$1"

# Handle 'latest' option
if [ "$BACKUP_FILE" = "latest" ]; then
    BACKUP_FILE=$(ls -t "$BACKUP_DIR"/neuroscan_backup_*.sql* 2>/dev/null | head -n1)
    if [ -z "$BACKUP_FILE" ]; then
        print_error "No backups found"
        exit 1
    fi
    BACKUP_FILE=$(basename "$BACKUP_FILE")
    print_status "Using latest backup: $BACKUP_FILE"
fi

# Full path to backup file
FULL_BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILE"

# Check if backup file exists
if [ ! -f "$FULL_BACKUP_PATH" ]; then
    print_error "Backup file not found: $FULL_BACKUP_PATH"
    exit 1
fi

# Verify checksum if available
CHECKSUM_FILE="${FULL_BACKUP_PATH}.sha256"
if [ -f "$CHECKSUM_FILE" ]; then
    print_status "Verifying backup integrity..."
    cd "$BACKUP_DIR"
    if sha256sum -c "$CHECKSUM_FILE"; then
        print_status "Backup integrity verified"
    else
        print_error "Backup integrity check failed!"
        exit 1
    fi
else
    print_warning "No checksum file found, skipping integrity check"
fi

# Determine if file is encrypted
RESTORE_FILE="$FULL_BACKUP_PATH"
TEMP_FILE=""

if [[ "$BACKUP_FILE" == *.gpg ]]; then
    print_status "Decrypting backup file..."
    TEMP_FILE="/tmp/$(basename "${BACKUP_FILE%.gpg}")"
    
    if echo "neuroscan_backup_password" | gpg --batch --yes --passphrase-fd 0 \
        --decrypt "$FULL_BACKUP_PATH" > "$TEMP_FILE"; then
        print_status "Backup decrypted successfully"
        RESTORE_FILE="$TEMP_FILE"
    else
        print_error "Failed to decrypt backup file"
        exit 1
    fi
fi

# Confirmation prompt
print_warning "This will replace the current database: $POSTGRES_DB"
read -p "Are you sure you want to continue? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    print_status "Restore cancelled"
    [ -n "$TEMP_FILE" ] && rm -f "$TEMP_FILE"
    exit 0
fi

# Set password for PostgreSQL commands
export PGPASSWORD="$POSTGRES_PASSWORD"

# Check database connection
print_status "Testing database connection..."
if ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB"; then
    print_error "Cannot connect to database"
    exit 1
fi

# Create a backup of current database before restore
print_status "Creating safety backup of current database..."
SAFETY_BACKUP="/tmp/safety_backup_$(date +%Y%m%d_%H%M%S).sql"
pg_dump -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    --format=custom --file="$SAFETY_BACKUP"
print_status "Safety backup created: $SAFETY_BACKUP"

# Terminate active connections to the database
print_status "Terminating active connections to database..."
psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "postgres" -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$POSTGRES_DB' AND pid <> pg_backend_pid();"

# Drop and recreate database
print_status "Recreating database..."
psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "postgres" -c \
    "DROP DATABASE IF EXISTS $POSTGRES_DB;"
psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "postgres" -c \
    "CREATE DATABASE $POSTGRES_DB;"

# Restore database
print_status "Restoring database from backup..."
if pg_restore -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    --verbose --clean --no-owner --no-privileges "$RESTORE_FILE"; then
    
    print_status "Database restored successfully!"
    
    # Verify restore
    print_status "Verifying restored database..."
    TABLE_COUNT=$(psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
        -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
    print_status "Restored $TABLE_COUNT tables"
    
    # Remove safety backup if restore was successful
    rm -f "$SAFETY_BACKUP"
    
else
    print_error "Database restore failed!"
    
    # Restore from safety backup
    print_status "Restoring from safety backup..."
    psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "postgres" -c \
        "DROP DATABASE IF EXISTS $POSTGRES_DB;"
    psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "postgres" -c \
        "CREATE DATABASE $POSTGRES_DB;"
    pg_restore -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
        "$SAFETY_BACKUP"
    
    print_status "Original database restored from safety backup"
    rm -f "$SAFETY_BACKUP"
    exit 1
fi

# Clean up temporary files
[ -n "$TEMP_FILE" ] && rm -f "$TEMP_FILE"

# Clean up environment
unset PGPASSWORD

print_status "Restore completed successfully at $(date)"
