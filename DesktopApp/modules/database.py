#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Manager for NeuroScan
Handles SQLite database operations
"""

import sqlite3
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class DatabaseManager:
    """Manages the local SQLite database for NeuroScan"""
    
    def __init__(self, db_path: str = "neuroscan.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    logo_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            """)
            
            # Certificates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS certificates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    serial_number TEXT UNIQUE NOT NULL,
                    product_id INTEGER NOT NULL,
                    customer_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'active',
                    qr_code_path TEXT,
                    pdf_label_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified_at TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id),
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            """)
            
            # Scan logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    serial_number TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'success',
                    location TEXT,
                    FOREIGN KEY (serial_number) REFERENCES certificates (serial_number)
                )
            """)
            
            conn.commit()
    
    # Customer management
    def add_customer(self, name: str, email: str = None, logo_path: str = None) -> int:
        """Add a new customer"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO customers (name, email, logo_path)
                VALUES (?, ?, ?)
            """, (name, email, logo_path))
            conn.commit()
            return cursor.lastrowid
    
    def get_customers(self) -> List[Dict]:
        """Get all customers"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def update_customer(self, customer_id: int, name: str = None, email: str = None, logo_path: str = None):
        """Update customer information"""
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        if logo_path is not None:
            updates.append("logo_path = ?")
            params.append(logo_path)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(customer_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    UPDATE customers 
                    SET {', '.join(updates)}
                    WHERE id = ?
                """, params)
                conn.commit()
    
    # Product management
    def add_product(self, customer_id: int, name: str, description: str = None) -> int:
        """Add a new product"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (customer_id, name, description)
                VALUES (?, ?, ?)
            """, (customer_id, name, description))
            conn.commit()
            return cursor.lastrowid
    
    def get_products(self, customer_id: int = None) -> List[Dict]:
        """Get products, optionally filtered by customer"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if customer_id:
                cursor.execute("""
                    SELECT p.*, c.name as customer_name 
                    FROM products p 
                    JOIN customers c ON p.customer_id = c.id 
                    WHERE p.customer_id = ?
                    ORDER BY p.name
                """, (customer_id,))
            else:
                cursor.execute("""
                    SELECT p.*, c.name as customer_name 
                    FROM products p 
                    JOIN customers c ON p.customer_id = c.id 
                    ORDER BY c.name, p.name
                """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    # Certificate management
    def generate_serial_number(self, product_id: int, customer_id: int) -> str:
        """Generate a unique serial number"""
        # Create a unique identifier based on timestamp, product, and random component
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8].upper()
        
        # Format: NS-YYYYMMDDHHMMSS-PRODUCTID-UNIQUEID
        serial = f"NS-{timestamp}-{product_id:04d}-{unique_id}"
        
        # Ensure uniqueness
        while self.get_certificate_by_serial(serial):
            unique_id = str(uuid.uuid4())[:8].upper()
            serial = f"NS-{timestamp}-{product_id:04d}-{unique_id}"
        
        return serial
    
    def create_certificate(self, product_id: int, customer_id: int) -> Tuple[int, str]:
        """Create a new certificate"""
        serial_number = self.generate_serial_number(product_id, customer_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO certificates (serial_number, product_id, customer_id)
                VALUES (?, ?, ?)
            """, (serial_number, product_id, customer_id))
            conn.commit()
            return cursor.lastrowid, serial_number
    
    def get_certificates(self, customer_id: int = None, product_id: int = None) -> List[Dict]:
        """Get certificates with optional filters"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT c.*, p.name as product_name, cust.name as customer_name
                FROM certificates c
                JOIN products p ON c.product_id = p.id
                JOIN customers cust ON c.customer_id = cust.id
            """
            
            conditions = []
            params = []
            
            if customer_id:
                conditions.append("c.customer_id = ?")
                params.append(customer_id)
            
            if product_id:
                conditions.append("c.product_id = ?")
                params.append(product_id)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY c.created_at DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_certificate_by_serial(self, serial_number: str) -> Optional[Dict]:
        """Get certificate by serial number"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, p.name as product_name, cust.name as customer_name, cust.logo_path
                FROM certificates c
                JOIN products p ON c.product_id = p.id
                JOIN customers cust ON c.customer_id = cust.id
                WHERE c.serial_number = ?
            """, (serial_number,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_certificate_paths(self, serial_number: str, qr_code_path: str = None, pdf_label_path: str = None):
        """Update certificate file paths"""
        updates = []
        params = []
        
        if qr_code_path:
            updates.append("qr_code_path = ?")
            params.append(qr_code_path)
        
        if pdf_label_path:
            updates.append("pdf_label_path = ?")
            params.append(pdf_label_path)
        
        if updates:
            params.append(serial_number)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    UPDATE certificates 
                    SET {', '.join(updates)}
                    WHERE serial_number = ?
                """, params)
                conn.commit()
    
    # Scan logging
    def log_scan(self, serial_number: str, ip_address: str = None, user_agent: str = None, location: str = None):
        """Log a certificate scan"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scan_logs (serial_number, ip_address, user_agent, location)
                VALUES (?, ?, ?, ?)
            """, (serial_number, ip_address, user_agent, location))
            conn.commit()
    
    def get_scan_logs(self, serial_number: str = None, days: int = 30) -> List[Dict]:
        """Get scan logs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if serial_number:
                cursor.execute("""
                    SELECT * FROM scan_logs 
                    WHERE serial_number = ?
                    AND scan_time >= datetime('now', '-{} days')
                    ORDER BY scan_time DESC
                """.format(days), (serial_number,))
            else:
                cursor.execute("""
                    SELECT * FROM scan_logs 
                    WHERE scan_time >= datetime('now', '-{} days')
                    ORDER BY scan_time DESC
                """.format(days))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # Statistics
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total customers
            cursor.execute("SELECT COUNT(*) FROM customers")
            stats['total_customers'] = cursor.fetchone()[0]
            
            # Total products
            cursor.execute("SELECT COUNT(*) FROM products")
            stats['total_products'] = cursor.fetchone()[0]
            
            # Total certificates
            cursor.execute("SELECT COUNT(*) FROM certificates")
            stats['total_certificates'] = cursor.fetchone()[0]
            
            # Active certificates
            cursor.execute("SELECT COUNT(*) FROM certificates WHERE status = 'active'")
            stats['active_certificates'] = cursor.fetchone()[0]
            
            # Scans today
            cursor.execute("""
                SELECT COUNT(*) FROM scan_logs 
                WHERE date(scan_time) = date('now')
            """)
            stats['scans_today'] = cursor.fetchone()[0]
            
            # Scans this week
            cursor.execute("""
                SELECT COUNT(*) FROM scan_logs 
                WHERE scan_time >= datetime('now', '-7 days')
            """)
            stats['scans_this_week'] = cursor.fetchone()[0]
            
            return stats
