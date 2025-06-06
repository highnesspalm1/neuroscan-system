"""
PDF Label Generator for NeuroScan Premium Product Authentication System

This module generates professional PDF labels with QR codes, product information,
and authentication details for physical product labeling.
"""

import io
import qrcode
from datetime import datetime
from typing import Optional, Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from PIL import Image as PILImage


class PDFLabelGenerator:
    """Generates professional PDF labels for product authentication."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for the PDF labels."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='LabelTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e3a8a')  # Blue color
        ))
        
        # Product name style
        self.styles.add(ParagraphStyle(
            name='ProductName',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#374151')  # Gray color
        ))
        
        # Info style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#6b7280')
        ))
        
        # QR code caption style
        self.styles.add(ParagraphStyle(
            name='QRCaption',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=3,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#9ca3af')
        ))
    
    def generate_qr_code(self, data: str, size: int = 100) -> io.BytesIO:
        """Generate QR code image as BytesIO object."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=5,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((size, size), PILImage.Resampling.LANCZOS)
        
        # Convert to BytesIO
        img_buffer = io.BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer
    
    def generate_single_label(
        self,
        product_id: str,
        product_name: str,
        product_description: str,
        verification_url: str,
        certificate_id: Optional[str] = None,
        company_name: str = "NeuroCompany",
        additional_info: Optional[Dict[str, Any]] = None
    ) -> io.BytesIO:
        """Generate a single product label PDF."""
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=(4*inch, 3*inch),  # Standard label size
            rightMargin=0.25*inch,
            leftMargin=0.25*inch,
            topMargin=0.25*inch,
            bottomMargin=0.25*inch
        )
        
        story = []
        
        # Company logo/title
        title = Paragraph(f"<b>{company_name}</b>", self.styles['LabelTitle'])
        story.append(title)
        story.append(Spacer(1, 6))
        
        # Product information
        product_title = Paragraph(f"<b>{product_name}</b>", self.styles['ProductName'])
        story.append(product_title)
        
        if product_description:
            desc = Paragraph(product_description[:100] + "..." if len(product_description) > 100 else product_description, 
                           self.styles['InfoText'])
            story.append(desc)
        
        story.append(Spacer(1, 8))
        
        # Create table for QR code and info
        qr_buffer = self.generate_qr_code(verification_url, 80)
        qr_image = Image(qr_buffer, width=80, height=80)
        
        # Product information table
        info_data = [
            ["Product ID:", product_id],
            ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M")],
        ]
        
        if certificate_id:
            info_data.append(["Certificate:", certificate_id[:12] + "..."])
        
        if additional_info:
            for key, value in additional_info.items():
                if len(info_data) < 5:  # Limit to avoid overflow
                    info_data.append([f"{key}:", str(value)[:20]])
        
        info_table = Table(info_data, colWidths=[0.8*inch, 1.2*inch])
        info_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#374151')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        # Main content table (QR code + info)
        main_table = Table(
            [[qr_image, info_table]],
            colWidths=[1*inch, 2.5*inch]
        )
        main_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(main_table)
        story.append(Spacer(1, 6))
        
        # QR code caption
        caption = Paragraph("Scan to verify authenticity", self.styles['QRCaption'])
        story.append(caption)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def generate_batch_labels(
        self,
        products: list,
        labels_per_page: int = 8,
        company_name: str = "NeuroCompany"
    ) -> io.BytesIO:
        """Generate multiple labels on a single page."""
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        story = []
        
        # Page header
        header = Paragraph(f"<b>{company_name} - Product Labels</b>", self.styles['Heading1'])
        story.append(header)
        story.append(Spacer(1, 12))
        
        # Generate labels in batches
        for i in range(0, len(products), labels_per_page):
            batch = products[i:i + labels_per_page]
            
            # Create labels for this batch
            labels_data = []
            for j in range(0, len(batch), 2):  # 2 labels per row
                row = []
                for k in range(2):
                    if j + k < len(batch):
                        product = batch[j + k]
                        label_content = self._create_mini_label(product)
                        row.append(label_content)
                    else:
                        row.append("")  # Empty cell
                labels_data.append(row)
            
            # Create table for labels
            labels_table = Table(
                labels_data,
                colWidths=[3.5*inch, 3.5*inch]
            )
            labels_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(labels_table)
            
            # Add page break if not last batch
            if i + labels_per_page < len(products):
                story.append(Spacer(1, 0.5*inch))
        
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def _create_mini_label(self, product: dict) -> list:
        """Create a mini label for batch printing."""
        elements = []
        
        # Product name
        name = Paragraph(f"<b>{product.get('name', 'Unknown Product')}</b>", 
                        self.styles['ProductName'])
        elements.append(name)
        
        # QR code (smaller for batch)
        qr_buffer = self.generate_qr_code(
            product.get('verification_url', ''), 
            size=60
        )
        qr_image = Image(qr_buffer, width=60, height=60)
        
        # Info table
        info_data = [
            ["ID:", product.get('id', 'N/A')[:10]],
            ["Date:", datetime.now().strftime("%m/%d/%Y")],
        ]
        
        info_table = Table(info_data, colWidths=[0.5*inch, 1*inch])
        info_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#6b7280')),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        # Combine QR and info
        content_table = Table(
            [[qr_image, info_table]],
            colWidths=[0.8*inch, 1.5*inch]
        )
        content_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        elements.append(content_table)
        
        return elements
    
    def generate_certificate_label(
        self,
        certificate_data: dict,
        company_name: str = "NeuroCompany"
    ) -> io.BytesIO:
        """Generate a special certificate label with enhanced security features."""
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=(4*inch, 3*inch),
            rightMargin=0.2*inch,
            leftMargin=0.2*inch,
            topMargin=0.2*inch,
            bottomMargin=0.2*inch
        )
        
        story = []
        
        # Certificate header
        header = Paragraph(f"<b>{company_name} CERTIFICATE</b>", self.styles['LabelTitle'])
        story.append(header)
        story.append(Spacer(1, 6))
        
        # Certificate ID prominently displayed
        cert_id = Paragraph(
            f"<b>Certificate: {certificate_data.get('id', 'N/A')}</b>", 
            self.styles['ProductName']
        )
        story.append(cert_id)
        story.append(Spacer(1, 8))
        
        # QR code for certificate verification
        verification_url = certificate_data.get('verification_url', '')
        qr_buffer = self.generate_qr_code(verification_url, 90)
        qr_image = Image(qr_buffer, width=90, height=90)
        
        # Certificate details
        cert_info = [
            ["Issued:", certificate_data.get('issue_date', 'N/A')],
            ["Valid Until:", certificate_data.get('expiry_date', 'N/A')],
            ["Status:", certificate_data.get('status', 'Active')],
            ["Type:", certificate_data.get('type', 'Premium')],
        ]
        
        cert_table = Table(cert_info, colWidths=[0.8*inch, 1.4*inch])
        cert_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#374151')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        # Main layout
        main_table = Table(
            [[qr_image, cert_table]],
            colWidths=[1.1*inch, 2.3*inch]
        )
        main_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(main_table)
        story.append(Spacer(1, 6))
        
        # Security notice
        security_text = Paragraph(
            "<i>Scan QR code to verify certificate authenticity</i>", 
            self.styles['QRCaption']
        )
        story.append(security_text)
        
        doc.build(story)
        buffer.seek(0)
        
        return buffer


# Convenience functions for easy import
def generate_product_label(product_data: dict) -> io.BytesIO:
    """Generate a single product label."""
    generator = PDFLabelGenerator()
    return generator.generate_single_label(**product_data)


def generate_batch_labels(products: list) -> io.BytesIO:
    """Generate batch labels for multiple products."""
    generator = PDFLabelGenerator()
    return generator.generate_batch_labels(products)


def generate_certificate_label(certificate_data: dict) -> io.BytesIO:
    """Generate a certificate label."""
    generator = PDFLabelGenerator()
    return generator.generate_certificate_label(certificate_data)
