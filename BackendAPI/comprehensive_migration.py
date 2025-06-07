#!/usr/bin/env python3
"""
Comprehensive database migration to sync schema with models.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import text
from app.core.database import engine

def comprehensive_migration():
    """Migrate database schema to match current models."""
    
    try:
        with engine.connect() as connection:
            print("🔄 Starting comprehensive database migration...")
            
            # Products table migrations
            print("\n📦 Updating products table...")
            product_migrations = [
                "ALTER TABLE products ADD COLUMN sku VARCHAR",
                "ALTER TABLE products ADD COLUMN category VARCHAR", 
                "ALTER TABLE products ADD COLUMN price VARCHAR",
                "ALTER TABLE products ADD COLUMN updated_at DATETIME"
            ]
            
            for migration in product_migrations:
                try:
                    connection.execute(text(migration))
                    print(f"   ✓ {migration}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"   ⚠ Column already exists: {migration}")
                    else:
                        print(f"   ❌ Failed: {migration} - {e}")
            
            # Certificates table migrations  
            print("\n🎫 Updating certificates table...")
            cert_migrations = [
                "ALTER TABLE certificates ADD COLUMN issued_at DATETIME",
                "ALTER TABLE certificates ADD COLUMN expires_at DATETIME"
            ]
            
            for migration in cert_migrations:
                try:
                    connection.execute(text(migration))
                    print(f"   ✓ {migration}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"   ⚠ Column already exists: {migration}")
                    else:
                        print(f"   ❌ Failed: {migration} - {e}")
            
            # Scan logs table migrations
            print("\n📊 Updating scan_logs table...")
            scan_migrations = [
                "ALTER TABLE scan_logs ADD COLUMN certificate_id INTEGER",
                "ALTER TABLE scan_logs ADD COLUMN scanned_at DATETIME"
            ]
            
            for migration in scan_migrations:
                try:
                    connection.execute(text(migration))
                    print(f"   ✓ {migration}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"   ⚠ Column already exists: {migration}")
                    else:
                        print(f"   ❌ Failed: {migration} - {e}")
            
            # Create indexes
            print("\n🗂️ Creating indexes...")
            index_migrations = [
                "CREATE INDEX IF NOT EXISTS idx_product_sku ON products(sku)",
                "CREATE INDEX IF NOT EXISTS idx_product_category ON products(category)",
                "CREATE INDEX IF NOT EXISTS idx_certificate_status ON certificates(status)",
                "CREATE INDEX IF NOT EXISTS idx_scan_log_certificate ON scan_logs(certificate_id)"
            ]
            
            for migration in index_migrations:
                try:
                    connection.execute(text(migration))
                    print(f"   ✓ {migration}")
                except Exception as e:
                    print(f"   ⚠ Index warning: {migration} - {e}")
            
            connection.commit()
            print("\n✅ Comprehensive migration completed!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = comprehensive_migration()
    if not success:
        sys.exit(1)
