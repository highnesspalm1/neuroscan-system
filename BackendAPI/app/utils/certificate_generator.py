#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Certificate generator utilities
"""

import uuid
from datetime import datetime


def generate_serial_number(product_id: int, customer_id: int) -> str:
    """
    Generate a unique serial number for certificates
    Format: NS-YYYYMMDDHHMMSS-PPPP-CCCC-XXXXXXXX
    
    NS = NeuroScan prefix
    YYYYMMDDHHMMSS = timestamp
    PPPP = product_id (4 digits)
    CCCC = customer_id (4 digits)  
    XXXXXXXX = random component (8 chars)
    """
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8].upper()
    
    serial = f"NS-{timestamp}-{product_id:04d}-{customer_id:04d}-{unique_id}"
    
    return serial


def validate_serial_number(serial_number: str) -> bool:
    """
    Validate serial number format
    """
    if not serial_number.startswith("NS-"):
        return False
    
    parts = serial_number.split("-")
    if len(parts) != 5:
        return False
    
    try:
        # Validate timestamp part
        datetime.strptime(parts[1], "%Y%m%d%H%M%S")
        
        # Validate product and customer IDs are numeric
        int(parts[2])
        int(parts[3])
        
        # Validate unique ID is 8 characters
        if len(parts[4]) != 8:
            return False
            
        return True
    except (ValueError, IndexError):
        return False
