#!/bin/bash

# NeuroScan Database Backup Script
# This script creates encrypted backups of the PostgreSQL database

set -e

# Configuration
BACKUP_DIR="/backups"
POSTGRES_HOST="postgres"
POSTGRES_PORT="5432"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="neuroscan_backup_${TIMESTAMP}.sql"
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"
RETENTION_DAYS=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[BACKUP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required environment variables are set
if [ -z "$POSTGRES_DB" ] || [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ]; then
    print_error "Required environment variables are not set"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

print_status "Starting backup of database: $POSTGRES_DB"

# Set password for pg_dump
export PGPASSWORD="$POSTGRES_PASSWORD"

# Create database backup
if pg_dump -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    --verbose \
    --clean \
    --no-owner \
    --no-privileges \
    --format=custom \
    --file="$BACKUP_DIR/$BACKUP_FILE"; then
    
    print_status "Database backup created: $BACKUP_FILE"
    
    # Get backup file size
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    print_status "Backup size: $BACKUP_SIZE"
    
    # Compress and encrypt backup (optional)
    if command -v gpg &> /dev/null; then
        print_status "Encrypting backup..."
        
        # Use symmetric encryption (password-based)
        if echo "neuroscan_backup_password" | gpg --batch --yes --passphrase-fd 0 \
            --cipher-algo AES256 --compress-algo 2 --symmetric \
            --output "$BACKUP_DIR/$ENCRYPTED_FILE" "$BACKUP_DIR/$BACKUP_FILE"; then
            
            print_status "Backup encrypted: $ENCRYPTED_FILE"
            
            # Remove unencrypted backup
            rm "$BACKUP_DIR/$BACKUP_FILE"
            FINAL_FILE="$ENCRYPTED_FILE"
        else
            print_warning "Encryption failed, keeping unencrypted backup"
            FINAL_FILE="$BACKUP_FILE"
        fi
    else
        print_warning "GPG not available, backup will not be encrypted"
        FINAL_FILE="$BACKUP_FILE"
    fi
    
    # Create checksums
    cd "$BACKUP_DIR"
    sha256sum "$FINAL_FILE" > "${FINAL_FILE}.sha256"
    print_status "Checksum created: ${FINAL_FILE}.sha256"
    
    # Clean up old backups
    print_status "Cleaning up backups older than $RETENTION_DAYS days..."
    find "$BACKUP_DIR" -name "neuroscan_backup_*.sql*" -type f -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "neuroscan_backup_*.sha256" -type f -mtime +$RETENTION_DAYS -delete
    
    # List current backups
    print_status "Current backups:"
    ls -lh "$BACKUP_DIR"/neuroscan_backup_* 2>/dev/null || print_warning "No backups found"
    
    print_status "Backup completed successfully!"
    
else
    print_error "Database backup failed"
    exit 1
fi

# Optional: Upload to cloud storage (uncomment and configure as needed)
# print_status "Uploading backup to cloud storage..."
# aws s3 cp "$BACKUP_DIR/$FINAL_FILE" s3://your-backup-bucket/neuroscan/
# aws s3 cp "$BACKUP_DIR/${FINAL_FILE}.sha256" s3://your-backup-bucket/neuroscan/

# Clean up environment
unset PGPASSWORD

print_status "Backup process completed at $(date)"
