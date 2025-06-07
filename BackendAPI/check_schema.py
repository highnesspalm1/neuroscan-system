#!/usr/bin/env python3
"""
Check current database schema to understand what columns exist.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import text
from app.core.database import engine

def check_schema():
    """Check the current database schema."""
    
    with engine.connect() as connection:
        # Check customers table
        print("🔍 Customers table schema:")
        result = connection.execute(text("PRAGMA table_info(customers)"))
        for row in result.fetchall():
            print(f"   {row[1]} ({row[2]}) - Nullable: {not row[3]} - Default: {row[4]}")
        
        print("\n🔍 Products table schema:")
        result = connection.execute(text("PRAGMA table_info(products)"))
        for row in result.fetchall():
            print(f"   {row[1]} ({row[2]}) - Nullable: {not row[3]} - Default: {row[4]}")
            
        print("\n🔍 Certificates table schema:")
        result = connection.execute(text("PRAGMA table_info(certificates)"))
        for row in result.fetchall():
            print(f"   {row[1]} ({row[2]}) - Nullable: {not row[3]} - Default: {row[4]}")
            
        print("\n🔍 Scan_logs table schema:")
        try:
            result = connection.execute(text("PRAGMA table_info(scan_logs)"))
            for row in result.fetchall():
                print(f"   {row[1]} ({row[2]}) - Nullable: {not row[3]} - Default: {row[4]}")
        except Exception as e:
            print(f"   ⚠ Table might not exist: {e}")

if __name__ == "__main__":
    check_schema()
