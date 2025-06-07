#!/usr/bin/env python3
"""
Database migration script to add customer authentication fields.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import text
from app.core.database import engine

def migrate_customer_auth():
    """Add authentication fields to the customers table."""
    
    migration_sql = """
    -- Add authentication fields to customers table
    ALTER TABLE customers ADD COLUMN username TEXT;
    ALTER TABLE customers ADD COLUMN hashed_password TEXT;
    ALTER TABLE customers ADD COLUMN is_active BOOLEAN DEFAULT 1;
    ALTER TABLE customers ADD COLUMN last_login DATETIME;
    
    -- Create unique index on username
    CREATE UNIQUE INDEX idx_customer_username ON customers(username);
    """
    
    try:
        with engine.connect() as connection:
            # Check if username column already exists
            result = connection.execute(text("PRAGMA table_info(customers)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'username' in columns:
                print("✅ Customer authentication fields already exist!")
                return True
                
            print("🔄 Adding customer authentication fields...")
            
            # Execute migration SQL line by line to handle SQLite limitations
            statements = [
                "ALTER TABLE customers ADD COLUMN username TEXT",
                "ALTER TABLE customers ADD COLUMN hashed_password TEXT",
                "ALTER TABLE customers ADD COLUMN is_active BOOLEAN DEFAULT 1",
                "ALTER TABLE customers ADD COLUMN last_login DATETIME"
            ]
            
            for statement in statements:
                try:
                    connection.execute(text(statement))
                    print(f"   ✓ {statement}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"   ⚠ Column already exists: {statement}")
                    else:
                        raise e
            
            # Create unique index
            try:
                connection.execute(text("CREATE UNIQUE INDEX idx_customer_username ON customers(username)"))
                print("   ✓ Created unique index on username")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("   ⚠ Index already exists")
                else:
                    print(f"   ⚠ Index creation warning: {e}")
            
            connection.commit()
            print("✅ Customer authentication migration completed!")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_customer_auth()
    if not success:
        sys.exit(1)
