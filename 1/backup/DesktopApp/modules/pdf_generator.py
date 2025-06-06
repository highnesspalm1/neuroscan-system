#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Generator for NeuroScan
Generates QR codes and PDF labels with customer branding
"""

import qrcode
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from pathlib import Path
from PIL import Image as PILImage
import io
import tempfile
from typing import Dict, Optional, Tuple
import os


class PDFGenerator:
    """Generates QR codes and PDF labels for certificates"""
    
    def __init__(self, config: Dict, db_manager):
        self.config = config
        self.db_manager = db_manager
        
        # Create output directories
        self.output_dir = Path(__file__).parent.parent / "output"
        self.qr_dir = self.output_dir / "qr_codes"
        self.pdf_dir = self.output_dir / "pdf_labels"
        
        self.qr_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_qr_code(self, serial_number: str, size: int = None) -> str:
        """Generate QR code for a certificate"""
        if size is None:
            size = self.config.get("pdf", {}).get("qr_size", 100)
        
        # Create verification URL
        base_url = self.config.get("api", {}).get("verify_url", "https://verify.neuroscan.com")
        verify_url = f"{base_url}/{serial_number}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verify_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Resize to specified size
        qr_image = qr_image.resize((size, size), PILImage.Resampling.LANCZOS)
        
        # Save QR code
        qr_filename = f"qr_{serial_number}.png"
        qr_path = self.qr_dir / qr_filename
        qr_image.save(qr_path, "PNG")
        
        # Update database
        self.db_manager.update_certificate_paths(serial_number, qr_code_path=str(qr_path))
        
        return str(qr_path)
    
    def generate_label(self, serial_number: str, template: str = "standard") -> str:
        """Generate PDF label for a certificate"""
        # Get certificate data
        cert_data = self.db_manager.get_certificate_by_serial(serial_number)
        if not cert_data:
            raise ValueError(f"Certificate not found: {serial_number}")
        
        # Generate QR code if not exists
        qr_path = cert_data.get('qr_code_path')
        if not qr_path or not Path(qr_path).exists():
            qr_path = self.generate_qr_code(serial_number)
        
        # Generate PDF based on template
        if template == "standard":
            pdf_path = self._generate_standard_label(cert_data, qr_path)
        elif template == "compact":
            pdf_path = self._generate_compact_label(cert_data, qr_path)
        else:
            pdf_path = self._generate_standard_label(cert_data, qr_path)
        
        # Update database
        self.db_manager.update_certificate_paths(serial_number, pdf_label_path=pdf_path)
        
        return pdf_path
    
    def _generate_standard_label(self, cert_data: Dict, qr_path: str) -> str:
        """Generate standard PDF label (85mm x 55mm business card size)"""
        # PDF settings
        pdf_filename = f"label_{cert_data['serial_number']}.pdf"
        pdf_path = self.pdf_dir / pdf_filename
        
        # Create PDF with custom page size (business card size)
        width = 85 * mm
        height = 55 * mm
        
        c = canvas.Canvas(str(pdf_path), pagesize=(width, height))
        
        # Colors
        bg_color = colors.Color(0.067, 0.094, 0.125)  # #111820
        accent_color = colors.Color(0, 0.898, 1)       # #00E5FF
        text_color = colors.white
        
        # Background
        c.setFillColor(bg_color)
        c.rect(0, 0, width, height, fill=1)
        
        # Border with gradient effect
        c.setStrokeColor(accent_color)
        c.setLineWidth(1)
        c.rect(2*mm, 2*mm, width-4*mm, height-4*mm, fill=0)
        
        # QR Code
        qr_size = 25*mm
        qr_x = 5*mm
        qr_y = height - qr_size - 5*mm
        
        if Path(qr_path).exists():
            c.drawImage(qr_path, qr_x, qr_y, qr_size, qr_size)
        
        # NeuroScan branding
        c.setFillColor(accent_color)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(qr_x + qr_size + 3*mm, height - 8*mm, "NeuroScan")
        c.setFont("Helvetica", 6)
        c.drawString(qr_x + qr_size + 3*mm, height - 12*mm, "by NeuroCompany")
        
        # Customer logo (if available)
        logo_path = cert_data.get('logo_path')
        if logo_path and Path(logo_path).exists():
            try:
                logo_size = 15*mm
                logo_x = width - logo_size - 5*mm
                logo_y = height - logo_size - 5*mm
                c.drawImage(logo_path, logo_x, logo_y, logo_size, logo_size, 
                          preserveAspectRatio=True, mask='auto')
            except Exception as e:
                print(f"Error loading logo: {e}")
        
        # Serial number (prominent)
        c.setFillColor(text_color)
        c.setFont("Helvetica-Bold", 10)
        serial_text = cert_data['serial_number']
        # Split serial number for better readability
        if len(serial_text) > 15:
            serial_line1 = serial_text[:15]
            serial_line2 = serial_text[15:]
            c.drawString(5*mm, 25*mm, serial_line1)
            c.drawString(5*mm, 20*mm, serial_line2)
        else:
            c.drawString(5*mm, 22*mm, serial_text)
        
        # Product information
        c.setFillColor(colors.Color(0.8, 0.8, 0.8))
        c.setFont("Helvetica", 8)
        c.drawString(5*mm, 15*mm, f"Produkt: {cert_data.get('product_name', 'N/A')}")
        c.drawString(5*mm, 11*mm, f"Kunde: {cert_data.get('customer_name', 'N/A')}")
        
        # Verification info
        c.setFillColor(accent_color)
        c.setFont("Helvetica", 6)
        c.drawString(5*mm, 6*mm, "Scannen Sie den QR-Code zur Verifizierung")
        c.drawString(5*mm, 3*mm, "verify.neuroscan.com")
        
        # Security features
        c.setStrokeColor(colors.Color(0.2, 0.2, 0.2))
        c.setLineWidth(0.5)
        # Micro-pattern for security
        for i in range(0, int(width/mm), 2):
            c.line(i*mm, 0, i*mm, 1*mm)
        
        c.save()
        return str(pdf_path)
    
    def _generate_compact_label(self, cert_data: Dict, qr_path: str) -> str:
        """Generate compact PDF label (50mm x 25mm)"""
        # PDF settings
        pdf_filename = f"label_compact_{cert_data['serial_number']}.pdf"
        pdf_path = self.pdf_dir / pdf_filename
        
        # Create PDF with compact size
        width = 50 * mm
        height = 25 * mm
        
        c = canvas.Canvas(str(pdf_path), pagesize=(width, height))
        
        # Colors
        bg_color = colors.Color(0.067, 0.094, 0.125)  # #111820
        accent_color = colors.Color(0, 0.898, 1)       # #00E5FF
        text_color = colors.white
        
        # Background
        c.setFillColor(bg_color)
        c.rect(0, 0, width, height, fill=1)
        
        # QR Code (smaller)
        qr_size = 15*mm
        qr_x = 2*mm
        qr_y = height - qr_size - 2*mm
        
        if Path(qr_path).exists():
            c.drawImage(qr_path, qr_x, qr_y, qr_size, qr_size)
        
        # Serial number
        c.setFillColor(text_color)
        c.setFont("Helvetica-Bold", 6)
        serial_text = cert_data['serial_number']
        if len(serial_text) > 12:
            # Truncate for compact label
            serial_text = serial_text[:12] + "..."
        c.drawString(qr_x + qr_size + 2*mm, height - 5*mm, serial_text)
        
        # NeuroScan branding
        c.setFillColor(accent_color)
        c.setFont("Helvetica", 4)
        c.drawString(qr_x + qr_size + 2*mm, height - 8*mm, "NeuroScan")
        
        # Product
        c.setFillColor(colors.Color(0.8, 0.8, 0.8))
        c.setFont("Helvetica", 4)
        product_name = cert_data.get('product_name', 'N/A')
        if len(product_name) > 20:
            product_name = product_name[:20] + "..."
        c.drawString(2*mm, 3*mm, product_name)
        
        c.save()
        return str(pdf_path)
    
    def generate_batch_labels(self, serial_numbers: list, template: str = "standard") -> list:
        """Generate multiple PDF labels"""
        generated_pdfs = []
        
        for serial_number in serial_numbers:
            try:
                pdf_path = self.generate_label(serial_number, template)
                generated_pdfs.append(pdf_path)
            except Exception as e:
                print(f"Error generating label for {serial_number}: {e}")
        
        return generated_pdfs
    
    def create_sheet_layout(self, serial_numbers: list, labels_per_row: int = 2, 
                           labels_per_col: int = 5) -> str:
        """Create a sheet with multiple labels for printing"""
        # PDF settings for A4 sheet
        pdf_filename = f"label_sheet_{len(serial_numbers)}_labels.pdf"
        pdf_path = self.pdf_dir / pdf_filename
        
        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4,
                              rightMargin=20*mm, leftMargin=20*mm,
                              topMargin=20*mm, bottomMargin=20*mm)
        
        # Calculate label dimensions
        usable_width = A4[0] - 40*mm  # Subtract margins
        usable_height = A4[1] - 40*mm
        
        label_width = usable_width / labels_per_row
        label_height = usable_height / labels_per_col
        
        story = []
        
        # Title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            textColor=colors.Color(0, 0.898, 1)
        )
        
        title = Paragraph("NeuroScan Zertifikat-Labels", title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Create table data
        table_data = []
        row = []
        
        for i, serial_number in enumerate(serial_numbers):
            # Generate individual label as image
            try:
                # Create temporary label
                cert_data = self.db_manager.get_certificate_by_serial(serial_number)
                if cert_data:
                    # Create mini label content
                    label_content = [
                        Paragraph(f"<b>{serial_number}</b>", styles['Normal']),
                        Paragraph(f"{cert_data.get('product_name', 'N/A')}", styles['Normal']),
                        Paragraph(f"{cert_data.get('customer_name', 'N/A')}", styles['Normal'])
                    ]
                    
                    row.append(label_content)
                    
                    if len(row) == labels_per_row:
                        table_data.append(row)
                        row = []
            except Exception as e:
                print(f"Error creating label for {serial_number}: {e}")
        
        # Add remaining labels
        if row:
            while len(row) < labels_per_row:
                row.append("")
            table_data.append(row)
        
        # Create table
        if table_data:
            table = Table(table_data, colWidths=[label_width] * labels_per_row)
            table.setStyle(TableStyle([
                ('BORDER', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(table)
        
        # Build PDF
        doc.build(story)
        return str(pdf_path)
    
    def get_label_preview(self, serial_number: str) -> Optional[str]:
        """Generate a preview image of the label"""
        try:
            # Generate temporary PDF
            temp_pdf = self.generate_label(serial_number)
            
            # Convert first page to image (requires additional libraries)
            # This is a placeholder - actual implementation would need pdf2image
            return temp_pdf
        except Exception as e:
            print(f"Error generating preview: {e}")
            return None
    
    def cleanup_old_files(self, days: int = 30):
        """Clean up old QR codes and PDF files"""
        import time
        current_time = time.time()
        
        for directory in [self.qr_dir, self.pdf_dir]:
            for file_path in directory.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > days * 24 * 3600:  # Convert days to seconds
                        try:
                            file_path.unlink()
                            print(f"Deleted old file: {file_path}")
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")
