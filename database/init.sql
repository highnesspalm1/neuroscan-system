-- NeuroScan Database Initialization Script
-- This script creates the initial database structure and sample data

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    serial_number VARCHAR(255) UNIQUE,
    batch_number VARCHAR(255),
    manufacturing_date DATE,
    expiry_date DATE,
    price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    qr_code VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create certificates table
CREATE TABLE IF NOT EXISTS certificates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    certificate_number VARCHAR(255) UNIQUE NOT NULL,
    certificate_type VARCHAR(100) NOT NULL,
    issuing_authority VARCHAR(255),
    issue_date DATE NOT NULL,
    expiry_date DATE,
    verification_url TEXT,
    pdf_path VARCHAR(500),
    status VARCHAR(50) DEFAULT 'valid',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create verification_logs table
CREATE TABLE IF NOT EXISTS verification_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id),
    qr_code VARCHAR(255) NOT NULL,
    verification_result VARCHAR(50) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    location_data JSONB,
    verified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_qr_code ON products(qr_code);
CREATE INDEX IF NOT EXISTS idx_products_serial_number ON products(serial_number);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at);
CREATE INDEX IF NOT EXISTS idx_certificates_product_id ON certificates(product_id);
CREATE INDEX IF NOT EXISTS idx_certificates_certificate_number ON certificates(certificate_number);
CREATE INDEX IF NOT EXISTS idx_verification_logs_product_id ON verification_logs(product_id);
CREATE INDEX IF NOT EXISTS idx_verification_logs_verified_at ON verification_logs(verified_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_certificates_updated_at BEFORE UPDATE ON certificates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123)
INSERT INTO users (id, username, email, password_hash, full_name, is_admin)
VALUES (
    uuid_generate_v4(),
    'admin',
    'admin@neuroscan.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewLVkoBo/BoL.v8G',
    'System Administrator',
    true
) ON CONFLICT (username) DO NOTHING;

-- Insert sample products
INSERT INTO products (name, description, category, manufacturer, model, serial_number, qr_code, created_by)
VALUES 
    (
        'NeuroScan Pro Scanner',
        'Professional grade scanner for authenticity verification',
        'Medical Equipment',
        'NeuroCompany',
        'NS-PRO-2025',
        'NS2025001',
        'NS_PRO_SCANNER_001',
        (SELECT id FROM users WHERE username = 'admin')
    ),
    (
        'Verification Module V2',
        'Advanced verification module with quantum encryption',
        'Security Module',
        'NeuroCompany',
        'VM-V2-2025',
        'VM2025001',
        'NS_VERIFICATION_MODULE_001',
        (SELECT id FROM users WHERE username = 'admin')
    )
ON CONFLICT (serial_number) DO NOTHING;

-- Create a view for product statistics
CREATE OR REPLACE VIEW product_stats AS
SELECT 
    COUNT(*) as total_products,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_products,
    COUNT(CASE WHEN status = 'inactive' THEN 1 END) as inactive_products,
    COUNT(DISTINCT category) as categories,
    COUNT(DISTINCT manufacturer) as manufacturers
FROM products;

-- Create a view for verification statistics
CREATE OR REPLACE VIEW verification_stats AS
SELECT 
    COUNT(*) as total_verifications,
    COUNT(CASE WHEN verification_result = 'valid' THEN 1 END) as valid_verifications,
    COUNT(CASE WHEN verification_result = 'invalid' THEN 1 END) as invalid_verifications,
    DATE_TRUNC('day', verified_at) as verification_date,
    COUNT(*) as daily_count
FROM verification_logs
GROUP BY DATE_TRUNC('day', verified_at)
ORDER BY verification_date DESC;

-- Grant permissions (adjust as needed for your security requirements)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO neuroscan;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO neuroscan;
