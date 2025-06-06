#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Certificate Manager Widget for NeuroScan
Manages certificates and generates PDF labels
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView, QFrame, QGroupBox,
    QFormLayout, QComboBox, QMessageBox, QDialog, QDialogButtonBox,
    QAbstractItemView, QMenu, QProgressBar, QApplication, QCheckBox,
    QSpinBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QAction, QFont
from typing import Dict, List, Optional
from pathlib import Path
import os


class CertificateManagerWidget(QWidget):
    """Widget for managing certificates"""
    
    certificate_updated = Signal()
    
    def __init__(self, db_manager, pdf_generator):
        super().__init__()
        self.db_manager = db_manager
        self.pdf_generator = pdf_generator
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🎫 Zertifikatsverwaltung")
        title_label.setProperty("class", "title")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Quick actions
        batch_create_btn = QPushButton("➕ Batch Erstellen")
        batch_create_btn.setProperty("class", "secondary")
        batch_create_btn.clicked.connect(self.batch_create_certificates)
        header_layout.addWidget(batch_create_btn)
        
        create_btn = QPushButton("🎫 Einzelzertifikat")
        create_btn.setProperty("class", "primary")
        create_btn.clicked.connect(self.create_certificate)
        header_layout.addWidget(create_btn)
        
        layout.addLayout(header_layout)
        
        # Filters
        filter_frame = QFrame()
        filter_frame.setProperty("class", "panel")
        filter_layout = QHBoxLayout(filter_frame)
        
        # Search
        search_label = QLabel("🔍 Suchen:")
        filter_layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Seriennummer oder Kunde...")
        self.search_edit.textChanged.connect(self.filter_certificates)
        filter_layout.addWidget(self.search_edit)
        
        # Customer filter
        customer_label = QLabel("Kunde:")
        filter_layout.addWidget(customer_label)
        
        self.customer_filter = QComboBox()
        self.customer_filter.addItem("Alle Kunden", None)
        self.customer_filter.currentTextChanged.connect(self.filter_certificates)
        filter_layout.addWidget(self.customer_filter)
        
        # Status filter
        status_label = QLabel("Status:")
        filter_layout.addWidget(status_label)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Alle", "Aktiv", "Inaktiv"])
        self.status_filter.currentTextChanged.connect(self.filter_certificates)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch()
        
        # Actions
        export_btn = QPushButton("📤 Exportieren")
        export_btn.clicked.connect(self.export_certificates)
        filter_layout.addWidget(export_btn)
        
        refresh_btn = QPushButton("🔄 Aktualisieren")
        refresh_btn.clicked.connect(self.refresh_data)
        filter_layout.addWidget(refresh_btn)
        
        layout.addWidget(filter_frame)
        
        # Certificates table
        self.certificates_table = QTableWidget()
        self.certificates_table.setAlternatingRowColors(True)
        self.certificates_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.certificates_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.certificates_table.customContextMenuRequested.connect(self.show_context_menu)
        self.certificates_table.doubleClicked.connect(self.view_certificate)
        
        # Table headers
        headers = [
            "ID", "Seriennummer", "Kunde", "Produkt", "Status", 
            "QR-Code", "PDF-Label", "Erstellt", "Verifiziert"
        ]
        self.certificates_table.setColumnCount(len(headers))
        self.certificates_table.setHorizontalHeaderLabels(headers)
        
        # Column widths
        header = self.certificates_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Seriennummer
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Kunde
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Produkt
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # QR-Code
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # PDF-Label
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Erstellt
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Verifiziert
        
        layout.addWidget(self.certificates_table)
        
        # Statistics
        stats_layout = QHBoxLayout()
        
        self.stats_label = QLabel("0 Zertifikate")
        self.stats_label.setProperty("class", "subtitle")
        stats_layout.addWidget(self.stats_label)
        
        stats_layout.addStretch()
        
        self.pdf_stats_label = QLabel("0 PDFs erstellt")
        self.pdf_stats_label.setStyleSheet("color: #39FF14;")
        stats_layout.addWidget(self.pdf_stats_label)
        
        layout.addLayout(stats_layout)
    
    def refresh_data(self):
        """Refresh certificate data"""
        try:
            # Load customers for filter
            customers = self.db_manager.get_customers()
            self.customer_filter.clear()
            self.customer_filter.addItem("Alle Kunden", None)
            for customer in customers:
                self.customer_filter.addItem(customer['name'], customer['id'])
            
            # Load certificates
            certificates = self.db_manager.get_certificates()
            self.populate_table(certificates)
            
            # Update statistics
            total_certs = len(certificates)
            pdf_count = len([cert for cert in certificates if cert.get('pdf_label_path')])
            
            self.stats_label.setText(f"{total_certs} Zertifikat{'e' if total_certs != 1 else ''}")
            self.pdf_stats_label.setText(f"{pdf_count} PDF-Label{'s' if pdf_count != 1 else ''} erstellt")
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Zertifikate: {e}")
    
    def populate_table(self, certificates: List[Dict]):
        """Populate the certificates table"""
        self.certificates_table.setRowCount(len(certificates))
        
        for row, cert in enumerate(certificates):
            # ID
            id_item = QTableWidgetItem(str(cert['id']))
            id_item.setData(Qt.UserRole, cert)
            self.certificates_table.setItem(row, 0, id_item)
            
            # Serial Number
            serial_item = QTableWidgetItem(cert['serial_number'])
            serial_item.setFont(QFont("Consolas", 9))
            self.certificates_table.setItem(row, 1, serial_item)
            
            # Customer
            customer_item = QTableWidgetItem(cert.get('customer_name', ''))
            self.certificates_table.setItem(row, 2, customer_item)
            
            # Product
            product_item = QTableWidgetItem(cert.get('product_name', ''))
            self.certificates_table.setItem(row, 3, product_item)
            
            # Status
            status_item = QTableWidgetItem(cert['status'])
            if cert['status'] == 'active':
                status_item.setText("✅ Aktiv")
                status_item.setStyleSheet("color: #39FF14;")
            else:
                status_item.setText("❌ Inaktiv")
                status_item.setStyleSheet("color: #FF6B6B;")
            status_item.setTextAlignment(Qt.AlignCenter)
            self.certificates_table.setItem(row, 4, status_item)
            
            # QR Code
            qr_item = QTableWidgetItem("✅" if cert.get('qr_code_path') else "❌")
            qr_item.setTextAlignment(Qt.AlignCenter)
            self.certificates_table.setItem(row, 5, qr_item)
            
            # PDF Label
            pdf_item = QTableWidgetItem("✅" if cert.get('pdf_label_path') else "❌")
            pdf_item.setTextAlignment(Qt.AlignCenter)
            self.certificates_table.setItem(row, 6, pdf_item)
            
            # Created
            created_item = QTableWidgetItem(cert['created_at'][:10])
            self.certificates_table.setItem(row, 7, created_item)
            
            # Verified
            verified_item = QTableWidgetItem(cert.get('verified_at', '')[:10] if cert.get('verified_at') else '')
            self.certificates_table.setItem(row, 8, verified_item)
    
    def filter_certificates(self):
        """Filter certificates based on search and filters"""
        search_text = self.search_edit.text().lower()
        selected_customer_id = self.customer_filter.currentData()
        selected_status = self.status_filter.currentText()
        
        for row in range(self.certificates_table.rowCount()):
            should_show = True
            cert_data = self.certificates_table.item(row, 0).data(Qt.UserRole)
            
            # Search filter
            if search_text:
                serial_match = search_text in cert_data['serial_number'].lower()
                customer_match = search_text in cert_data.get('customer_name', '').lower()
                product_match = search_text in cert_data.get('product_name', '').lower()
                
                should_show = should_show and (serial_match or customer_match or product_match)
            
            # Customer filter
            if selected_customer_id is not None:
                should_show = should_show and (cert_data['customer_id'] == selected_customer_id)
            
            # Status filter
            if selected_status != "Alle":
                if selected_status == "Aktiv":
                    should_show = should_show and (cert_data['status'] == 'active')
                elif selected_status == "Inaktiv":
                    should_show = should_show and (cert_data['status'] != 'active')
            
            self.certificates_table.setRowHidden(row, not should_show)
    
    def show_context_menu(self, position):
        """Show context menu for certificate actions"""
        if self.certificates_table.itemAt(position) is None:
            return
        
        cert_data = self.certificates_table.itemAt(position).data(Qt.UserRole)
        if not cert_data:
            return
        
        menu = QMenu(self)
        
        # View/Edit
        view_action = QAction("👁️ Details anzeigen", self)
        view_action.triggered.connect(self.view_certificate)
        menu.addAction(view_action)
        
        menu.addSeparator()
        
        # Generate QR Code
        if not cert_data.get('qr_code_path'):
            qr_action = QAction("📱 QR-Code erstellen", self)
            qr_action.triggered.connect(self.generate_qr_code)
            menu.addAction(qr_action)
        
        # Generate PDF Label
        if not cert_data.get('pdf_label_path'):
            pdf_action = QAction("📄 PDF-Label erstellen", self)
            pdf_action.triggered.connect(self.generate_pdf_label)
            menu.addAction(pdf_action)
        else:
            open_pdf_action = QAction("📄 PDF öffnen", self)
            open_pdf_action.triggered.connect(self.open_pdf_label)
            menu.addAction(open_pdf_action)
        
        menu.addSeparator()
        
        # Status toggle
        if cert_data['status'] == 'active':
            deactivate_action = QAction("❌ Deaktivieren", self)
            deactivate_action.triggered.connect(self.toggle_certificate_status)
            menu.addAction(deactivate_action)
        else:
            activate_action = QAction("✅ Aktivieren", self)
            activate_action.triggered.connect(self.toggle_certificate_status)
            menu.addAction(activate_action)
        
        # View scans
        scans_action = QAction("📊 Scans anzeigen", self)
        scans_action.triggered.connect(self.view_certificate_scans)
        menu.addAction(scans_action)
        
        menu.addSeparator()
        
        # Delete
        delete_action = QAction("🗑️ Löschen", self)
        delete_action.triggered.connect(self.delete_certificate)
        menu.addAction(delete_action)
        
        menu.exec(self.certificates_table.mapToGlobal(position))
    
    def create_certificate(self):
        """Create a single certificate"""
        dialog = CertificateDialog(self.db_manager, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_data()
            self.certificate_updated.emit()
    
    def batch_create_certificates(self):
        """Create multiple certificates"""
        dialog = BatchCertificateDialog(self.db_manager, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_data()
            self.certificate_updated.emit()
    
    def view_certificate(self):
        """View certificate details"""
        current_row = self.certificates_table.currentRow()
        if current_row < 0:
            return
        
        cert_data = self.certificates_table.item(current_row, 0).data(Qt.UserRole)
        dialog = CertificateDetailsDialog(cert_data, self.db_manager, parent=self)
        dialog.exec()
    
    def generate_qr_code(self):
        """Generate QR code for selected certificate"""
        current_row = self.certificates_table.currentRow()
        if current_row < 0:
            return
        
        cert_data = self.certificates_table.item(current_row, 0).data(Qt.UserRole)
        
        try:
            qr_path = self.pdf_generator.generate_qr_code(cert_data['serial_number'])
            QMessageBox.information(self, "Erfolg", f"QR-Code erstellt: {qr_path}")
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"QR-Code-Erstellung fehlgeschlagen: {e}")
    
    def generate_pdf_label(self):
        """Generate PDF label for selected certificate"""
        current_row = self.certificates_table.currentRow()
        if current_row < 0:
            return
        
        cert_data = self.certificates_table.item(current_row, 0).data(Qt.UserRole)
        
        try:
            pdf_path = self.pdf_generator.generate_label(cert_data['serial_number'])
            QMessageBox.information(self, "Erfolg", f"PDF-Label erstellt: {pdf_path}")
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"PDF-Label-Erstellung fehlgeschlagen: {e}")
    
    def open_pdf_label(self):
        """Open PDF label file"""
        current_row = self.certificates_table.currentRow()
        if current_row < 0:
            return
        
        cert_data = self.certificates_table.item(current_row, 0).data(Qt.UserRole)
        pdf_path = cert_data.get('pdf_label_path')
        
        if pdf_path and Path(pdf_path).exists():
            os.startfile(pdf_path)  # Windows
        else:
            QMessageBox.warning(self, "Fehler", "PDF-Datei nicht gefunden.")
    
    def toggle_certificate_status(self):
        """Toggle certificate active/inactive status"""
        current_row = self.certificates_table.currentRow()
        if current_row < 0:
            return
        
        cert_data = self.certificates_table.item(current_row, 0).data(Qt.UserRole)
        
        # TODO: Implement status toggle
        QMessageBox.information(self, "Info", "Status-Änderung wird implementiert...")
    
    def view_certificate_scans(self):
        """View scan logs for certificate"""
        current_row = self.certificates_table.currentRow()
        if current_row < 0:
            return
        
        cert_data = self.certificates_table.item(current_row, 0).data(Qt.UserRole)
        scans = self.db_manager.get_scan_logs(cert_data['serial_number'])
        
        dialog = ScanLogsDialog(cert_data['serial_number'], scans, parent=self)
        dialog.exec()
    
    def delete_certificate(self):
        """Delete selected certificate"""
        current_row = self.certificates_table.currentRow()
        if current_row < 0:
            return
        
        cert_data = self.certificates_table.item(current_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, "Zertifikat löschen",
            f"Möchten Sie das Zertifikat '{cert_data['serial_number']}' wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # TODO: Implement certificate deletion
            QMessageBox.information(self, "Info", "Löschfunktion wird implementiert...")
    
    def export_certificates(self):
        """Export certificates to CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Zertifikate exportieren",
            "certificates_export.csv",
            "CSV files (*.csv)"
        )
        
        if file_path:
            try:
                # TODO: Implement CSV export
                QMessageBox.information(self, "Info", "Export-Funktion wird implementiert...")
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Export fehlgeschlagen: {e}")


class CertificateDialog(QDialog):
    """Dialog for creating a new certificate"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        
        self.setWindowTitle("Neues Zertifikat erstellen")
        self.setModal(True)
        self.resize(400, 300)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Form
        form_group = QGroupBox("Zertifikatsinformationen")
        form_layout = QFormLayout(form_group)
        
        # Customer selection
        self.customer_combo = QComboBox()
        customers = self.db_manager.get_customers()
        for customer in customers:
            self.customer_combo.addItem(customer['name'], customer['id'])
        self.customer_combo.currentTextChanged.connect(self.load_products)
        form_layout.addRow("Kunde *:", self.customer_combo)
        
        # Product selection
        self.product_combo = QComboBox()
        form_layout.addRow("Produkt *:", self.product_combo)
        
        # Generate files
        self.generate_qr = QCheckBox("QR-Code erstellen")
        self.generate_qr.setChecked(True)
        form_layout.addRow("", self.generate_qr)
        
        self.generate_pdf = QCheckBox("PDF-Label erstellen")
        self.generate_pdf.setChecked(True)
        form_layout.addRow("", self.generate_pdf)
        
        layout.addWidget(form_group)
        
        # Load initial products
        if self.customer_combo.count() > 0:
            self.load_products()
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def load_products(self):
        """Load products for selected customer"""
        self.product_combo.clear()
        
        customer_id = self.customer_combo.currentData()
        if customer_id:
            products = self.db_manager.get_products(customer_id)
            for product in products:
                self.product_combo.addItem(product['name'], product['id'])
    
    def accept(self):
        """Create the certificate"""
        customer_id = self.customer_combo.currentData()
        product_id = self.product_combo.currentData()
        
        if not customer_id or not product_id:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie Kunde und Produkt aus.")
            return
        
        try:
            # Create certificate
            cert_id, serial_number = self.db_manager.create_certificate(product_id, customer_id)
            
            # Generate files if requested
            if self.generate_qr.isChecked():
                # TODO: Generate QR code
                pass
            
            if self.generate_pdf.isChecked():
                # TODO: Generate PDF label
                pass
            
            QMessageBox.information(
                self, "Erfolg",
                f"Zertifikat erstellt!\nSeriennummer: {serial_number}"
            )
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Erstellen: {e}")


class BatchCertificateDialog(QDialog):
    """Dialog for batch creating certificates"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        
        self.setWindowTitle("Batch-Zertifikatserstellung")
        self.setModal(True)
        self.resize(400, 250)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Form
        form_group = QGroupBox("Batch-Parameter")
        form_layout = QFormLayout(form_group)
        
        # Customer selection
        self.customer_combo = QComboBox()
        customers = self.db_manager.get_customers()
        for customer in customers:
            self.customer_combo.addItem(customer['name'], customer['id'])
        self.customer_combo.currentTextChanged.connect(self.load_products)
        form_layout.addRow("Kunde *:", self.customer_combo)
        
        # Product selection
        self.product_combo = QComboBox()
        form_layout.addRow("Produkt *:", self.product_combo)
        
        # Quantity
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1000)
        self.quantity_spin.setValue(10)
        form_layout.addRow("Anzahl *:", self.quantity_spin)
        
        # Options
        self.generate_files = QCheckBox("QR-Codes und PDF-Labels erstellen")
        self.generate_files.setChecked(True)
        form_layout.addRow("", self.generate_files)
        
        layout.addWidget(form_group)
        
        # Load initial products
        if self.customer_combo.count() > 0:
            self.load_products()
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def load_products(self):
        """Load products for selected customer"""
        self.product_combo.clear()
        
        customer_id = self.customer_combo.currentData()
        if customer_id:
            products = self.db_manager.get_products(customer_id)
            for product in products:
                self.product_combo.addItem(product['name'], product['id'])
    
    def accept(self):
        """Create batch certificates"""
        customer_id = self.customer_combo.currentData()
        product_id = self.product_combo.currentData()
        quantity = self.quantity_spin.value()
        
        if not customer_id or not product_id:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie Kunde und Produkt aus.")
            return
        
        # TODO: Implement batch creation with progress dialog
        QMessageBox.information(self, "Info", f"Batch-Erstellung von {quantity} Zertifikaten wird implementiert...")
        super().accept()


class CertificateDetailsDialog(QDialog):
    """Dialog showing certificate details"""
    
    def __init__(self, cert_data: Dict, db_manager, parent=None):
        super().__init__(parent)
        self.cert_data = cert_data
        self.db_manager = db_manager
        
        self.setWindowTitle(f"Zertifikat Details - {cert_data['serial_number']}")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Certificate info
        info_group = QGroupBox("Zertifikatsinformationen")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("Seriennummer:", QLabel(self.cert_data['serial_number']))
        info_layout.addRow("Kunde:", QLabel(self.cert_data.get('customer_name', '')))
        info_layout.addRow("Produkt:", QLabel(self.cert_data.get('product_name', '')))
        info_layout.addRow("Status:", QLabel(self.cert_data['status']))
        info_layout.addRow("Erstellt:", QLabel(self.cert_data['created_at']))
        
        layout.addWidget(info_group)
        
        # Files
        files_group = QGroupBox("Dateien")
        files_layout = QFormLayout(files_group)
        
        qr_status = "✅ Erstellt" if self.cert_data.get('qr_code_path') else "❌ Nicht erstellt"
        files_layout.addRow("QR-Code:", QLabel(qr_status))
        
        pdf_status = "✅ Erstellt" if self.cert_data.get('pdf_label_path') else "❌ Nicht erstellt"
        files_layout.addRow("PDF-Label:", QLabel(pdf_status))
        
        layout.addWidget(files_group)
        
        # Recent scans
        scans = self.db_manager.get_scan_logs(self.cert_data['serial_number'], days=30)
        scans_group = QGroupBox(f"Letzte Scans ({len(scans)})")
        scans_layout = QVBoxLayout(scans_group)
        
        if scans:
            for scan in scans[:5]:  # Show last 5 scans
                scan_text = f"{scan['scan_time'][:16]} - IP: {scan.get('ip_address', 'Unbekannt')}"
                scans_layout.addWidget(QLabel(scan_text))
        else:
            scans_layout.addWidget(QLabel("Keine Scans gefunden"))
        
        layout.addWidget(scans_group)
        
        # Close button
        close_btn = QPushButton("Schließen")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class ScanLogsDialog(QDialog):
    """Dialog showing scan logs for a certificate"""
    
    def __init__(self, serial_number: str, scans: List[Dict], parent=None):
        super().__init__(parent)
        self.serial_number = serial_number
        self.scans = scans
        
        self.setWindowTitle(f"Scan-Logs - {serial_number}")
        self.setModal(True)
        self.resize(600, 400)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(f"Scan-Logs für Zertifikat: {self.serial_number}")
        header_label.setProperty("class", "subtitle")
        layout.addWidget(header_label)
        
        # Scans table
        scans_table = QTableWidget()
        scans_table.setColumnCount(4)
        scans_table.setHorizontalHeaderLabels(["Zeitpunkt", "IP-Adresse", "User-Agent", "Status"])
        
        header = scans_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        scans_table.setRowCount(len(self.scans))
        
        for row, scan in enumerate(self.scans):
            scans_table.setItem(row, 0, QTableWidgetItem(scan['scan_time']))
            scans_table.setItem(row, 1, QTableWidgetItem(scan.get('ip_address', '')))
            scans_table.setItem(row, 2, QTableWidgetItem(scan.get('user_agent', '')))
            scans_table.setItem(row, 3, QTableWidgetItem(scan['status']))
        
        layout.addWidget(scans_table)
        
        # Close button
        close_btn = QPushButton("Schließen")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
