#!/usr/bin/env python3
"""
Customer Portal Database Migration
Comprehensive database fix for customer authentication fields
"""

import asyncio
import logging
import os
import sys
import json
from datetime import datetime
import asyncpg
import requests
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CustomerPortalMigration:
    def __init__(self):
        # Production API URL
        self.api_url = "https://neuroscan-api.onrender.com"
        
        # Database URL from Render environment
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            # Try to get from API environment info
            self.db_url = self.get_db_url_from_api()
    
    def get_db_url_from_api(self) -> Optional[str]:
        """Attempt to get database URL from API environment"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"API Health Check: {data}")
                # Database URL is not exposed in health check for security
                return None
        except Exception as e:
            logger.error(f"Failed to get API health: {e}")
            return None
    
    async def connect_to_database(self) -> Optional[asyncpg.Connection]:
        """Connect to the production database"""
        if not self.db_url:
            logger.error("No database URL available")
            return None
        
        try:
            conn = await asyncpg.connect(self.db_url)
            logger.info("Successfully connected to production database")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return None
    
    async def check_customer_table_schema(self, conn: asyncpg.Connection) -> Dict[str, Any]:
        """Check the current customer table schema"""
        try:
            # Get table columns
            columns_query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'customers'
            ORDER BY ordinal_position;
            """
            
            columns = await conn.fetch(columns_query)
            
            # Get table constraints
            constraints_query = """
            SELECT constraint_name, constraint_type, column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
            WHERE tc.table_name = 'customers';
            """
            
            constraints = await conn.fetch(constraints_query)
            
            schema_info = {
                'columns': [dict(col) for col in columns],
                'constraints': [dict(const) for const in constraints],
                'missing_auth_fields': []
            }
            
            # Check for required authentication fields
            column_names = [col['column_name'] for col in columns]
            required_auth_fields = ['username', 'hashed_password', 'is_active', 'last_login']
            
            for field in required_auth_fields:
                if field not in column_names:
                    schema_info['missing_auth_fields'].append(field)
            
            logger.info(f"Customer table schema: {len(schema_info['columns'])} columns")
            logger.info(f"Missing auth fields: {schema_info['missing_auth_fields']}")
            
            return schema_info
        
        except Exception as e:
            logger.error(f"Failed to check table schema: {e}")
            return {'error': str(e)}
    
    async def migrate_customer_table(self, conn: asyncpg.Connection) -> bool:
        """Apply database migration for customer authentication"""
        try:
            # Migration SQL
            migration_sql = """
            -- Add customer authentication fields
            ALTER TABLE customers 
            ADD COLUMN IF NOT EXISTS username VARCHAR(100) UNIQUE;
            
            ALTER TABLE customers 
            ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255);
            
            ALTER TABLE customers 
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
            
            ALTER TABLE customers 
            ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;
            
            -- Update existing customers with default authentication data
            UPDATE customers 
            SET username = COALESCE(username, LOWER(REPLACE(name, ' ', ''))),
                hashed_password = COALESCE(hashed_password, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewCfnJhCL2U8nu2u'),
                is_active = COALESCE(is_active, true)
            WHERE username IS NULL OR hashed_password IS NULL;
            
            -- Ensure username uniqueness
            UPDATE customers 
            SET username = username || '_' || id::text 
            WHERE id IN (
                SELECT id FROM (
                    SELECT id, ROW_NUMBER() OVER (PARTITION BY username ORDER BY id) as rn
                    FROM customers
                ) t WHERE rn > 1
            );
            """
            
            # Execute migration
            await conn.execute(migration_sql)
            logger.info("✅ Database migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
    
    async def verify_migration(self, conn: asyncpg.Connection) -> bool:
        """Verify the migration was successful"""
        try:
            # Check that all required fields exist
            check_query = """
            SELECT 
                COUNT(*) as total_customers,
                COUNT(username) as with_username,
                COUNT(hashed_password) as with_password,
                COUNT(CASE WHEN is_active THEN 1 END) as active_customers
            FROM customers;
            """
            
            result = await conn.fetchrow(check_query)
            
            logger.info(f"Migration verification:")
            logger.info(f"  Total customers: {result['total_customers']}")
            logger.info(f"  With username: {result['with_username']}")
            logger.info(f"  With password: {result['with_password']}")
            logger.info(f"  Active customers: {result['active_customers']}")
            
            # Verify schema
            schema_info = await self.check_customer_table_schema(conn)
            missing_fields = schema_info.get('missing_auth_fields', [])
            
            if not missing_fields:
                logger.info("✅ All required authentication fields present")
                return True
            else:
                logger.error(f"❌ Still missing fields: {missing_fields}")
                return False
                
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False
    
    async def test_customer_creation_api(self) -> bool:
        """Test customer creation via API after migration"""
        try:
            test_customer = {
                "name": "Migration Test User",
                "email": "migration.test@neuroscan.com",
                "username": "migrationtest",
                "password": "testpassword123"
            }
            
            response = requests.post(
                f"{self.api_url}/customer/create",
                json=test_customer,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Customer creation API working after migration")
                return True
            else:
                logger.error(f"❌ Customer creation still failing: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"API test failed: {e}")
            return False
    
    async def run_migration(self) -> bool:
        """Run the complete migration process"""
        logger.info("🚀 Starting Customer Portal Database Migration")
        logger.info("=" * 60)
        
        # Connect to database
        conn = await self.connect_to_database()
        if not conn:
            logger.error("Cannot proceed without database connection")
            return False
        
        try:
            # Check current schema
            logger.info("📊 Checking current database schema...")
            schema_info = await self.check_customer_table_schema(conn)
            
            if schema_info.get('missing_auth_fields'):
                logger.info(f"🔧 Missing fields detected: {schema_info['missing_auth_fields']}")
                
                # Run migration
                logger.info("🔄 Applying database migration...")
                migration_success = await self.migrate_customer_table(conn)
                
                if migration_success:
                    # Verify migration
                    logger.info("✅ Verifying migration...")
                    verification_success = await self.verify_migration(conn)
                    
                    if verification_success:
                        logger.info("🎉 Migration completed successfully!")
                        
                        # Test API
                        logger.info("🧪 Testing customer creation API...")
                        api_success = await self.test_customer_creation_api()
                        
                        return api_success
                    else:
                        logger.error("❌ Migration verification failed")
                        return False
                else:
                    logger.error("❌ Migration failed")
                    return False
            else:
                logger.info("✅ All authentication fields already present")
                
                # Still test API
                logger.info("🧪 Testing customer creation API...")
                api_success = await self.test_customer_creation_api()
                return api_success
                
        finally:
            await conn.close()
            logger.info("Database connection closed")

async def main():
    """Main migration function"""
    migrator = CustomerPortalMigration()
    success = await migrator.run_migration()
    
    if success:
        print("\n🎉 CUSTOMER PORTAL MIGRATION SUCCESSFUL! 🎉")
        print("The customer portal should now be fully functional.")
        print(f"Test it at: https://neuroscan-system.vercel.app/customer/login")
    else:
        print("\n❌ MIGRATION FAILED")
        print("Manual intervention may be required.")
        print("Check the logs above for details.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
