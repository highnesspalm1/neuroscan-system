-- Database Migration: Add new fields to products table
-- Date: 2025-06-07 21:39:18
-- Purpose: Add SKU, Category, Price, and Updated_at fields

-- Add new columns to products table
ALTER TABLE products ADD COLUMN IF NOT EXISTS sku VARCHAR(255);
ALTER TABLE products ADD COLUMN IF NOT EXISTS category VARCHAR(255);
ALTER TABLE products ADD COLUMN IF NOT EXISTS price VARCHAR(50);
ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

-- Update existing products with default updated_at
UPDATE products SET updated_at = created_at WHERE updated_at IS NULL;

-- Verification query
SELECT 
    column_name, 
    data_type, 
    is_nullable 
FROM information_schema.columns 
WHERE table_name = 'products' 
ORDER BY ordinal_position;
