
    -- Add customer authentication fields if they don't exist
    DO $$
    BEGIN
        -- Add username column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'customers' AND column_name = 'username'
        ) THEN
            ALTER TABLE customers ADD COLUMN username VARCHAR UNIQUE;
            CREATE INDEX IF NOT EXISTS idx_customers_username ON customers(username);
        END IF;
        
        -- Add hashed_password column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'customers' AND column_name = 'hashed_password'
        ) THEN
            ALTER TABLE customers ADD COLUMN hashed_password VARCHAR;
        END IF;
        
        -- Add is_active column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'customers' AND column_name = 'is_active'
        ) THEN
            ALTER TABLE customers ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
            CREATE INDEX IF NOT EXISTS idx_customers_is_active ON customers(is_active);
        END IF;
        
        -- Add last_login column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'customers' AND column_name = 'last_login'
        ) THEN
            ALTER TABLE customers ADD COLUMN last_login TIMESTAMP WITH TIME ZONE;
        END IF;
        
        -- Add created_at column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'customers' AND column_name = 'created_at'
        ) THEN
            ALTER TABLE customers ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        END IF;
        
        -- Add updated_at column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'customers' AND column_name = 'updated_at'
        ) THEN
            ALTER TABLE customers ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE;
        END IF;
        
    END $$;
    