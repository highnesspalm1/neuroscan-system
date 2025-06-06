#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions for the NeuroScan API
"""

from .certificate_generator import generate_serial_number, validate_serial_number

__all__ = ["generate_serial_number", "validate_serial_number"]
