# DEPLOYMENT TRIGGER - Customer Portal Fix
Created: 2025-06-07 22:02:52
Purpose: Force database schema recreation for customer authentication

This file triggers a fresh deployment to ensure PostgreSQL schema includes:
- customers.username (String, unique, indexed)
- customers.hashed_password (String)  
- customers.is_active (Boolean, default=True)
- customers.last_login (DateTime)
