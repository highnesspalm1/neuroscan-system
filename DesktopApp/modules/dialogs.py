#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialogs Module for NeuroScan Manager
Custom dialogs with glassmorphism design
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QSpinBox, QCheckBox, QTextEdit, QGroupBox,
    QDialogButtonBox, QMessageBox, QProgressDialog, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QTabWidget,
    QScrollArea, QWidget, QFileDialog, QDateEdit, QTimeEdit, QApplication
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPixmap, QIcon, QPainter, QBrush, QColor
from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime


class QuickCertificateDialog(QDialog):
    """Quick certificate creation dialog"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        
        self.setWindowTitle("🚀 Schnell-Zertifikat erstellen")
        self.setModal(True)
        self.resize(450, 350)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("🚀 Schnell-Zertifikat")
        header_label.setProperty("class", "title")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Form
        form_group = QGroupBox("Zertifikatsdaten")
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
        self.quantity_spin.setRange(1, 100)
        self.quantity_spin.setValue(1)
        form_layout.addRow("Anzahl:", self.quantity_spin)
        
        # Options
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
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        create_btn = QPushButton("🚀 Erstellen")
        create_btn.setProperty("class", "primary")
        create_btn.clicked.connect(self.create_certificates)
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)
    
    def load_products(self):
        """Load products for selected customer"""
        self.product_combo.clear()
        
        customer_id = self.customer_combo.currentData()
        if customer_id:
            products = self.db_manager.get_products(customer_id)
            for product in products:
                self.product_combo.addItem(product['name'], product['id'])
    
    def create_certificates(self):
        """Create certificates"""
        customer_id = self.customer_combo.currentData()
        product_id = self.product_combo.currentData()
        quantity = self.quantity_spin.value()
        
        if not customer_id or not product_id:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie Kunde und Produkt aus.")
            return
        
        try:
            # Create progress dialog
            progress = QProgressDialog("Erstelle Zertifikate...", "Abbrechen", 0, quantity, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setAutoClose(True)
            progress.setAutoReset(True)
            
            created_count = 0
            
            for i in range(quantity):
                if progress.wasCanceled():
                    break
                
                # Create certificate
                cert_id = self.db_manager.add_certificate(
                    customer_id=customer_id,
                    product_id=product_id,
                    generate_qr=self.generate_qr.isChecked(),
                    generate_pdf=self.generate_pdf.isChecked()
                )
                
                if cert_id:
                    created_count += 1
                
                progress.setValue(i + 1)
                QApplication.processEvents()
            
            if created_count > 0:
                QMessageBox.information(
                    self, "Erfolg",
                    f"{created_count} Zertifikat(e) erfolgreich erstellt!"
                )
                self.accept()
            else:
                QMessageBox.warning(self, "Fehler", "Keine Zertifikate erstellt.")
        
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Erstellen: {e}")


class ProductDialog(QDialog):
    """Dialog for adding/editing products"""
    
    def __init__(self, db_manager, customer_id, product_data: Optional[Dict] = None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.customer_id = customer_id
        self.product_data = product_data
        
        self.setWindowTitle("Produkt bearbeiten" if product_data else "Neues Produkt hinzufügen")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
        
        if product_data:
            self.load_product_data()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Form
        form_group = QGroupBox("Produktinformationen")
        form_layout = QFormLayout(form_group)
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Produktname")
        form_layout.addRow("Name *:", self.name_edit)
        
        # SKU
        self.sku_edit = QLineEdit()
        self.sku_edit.setPlaceholderText("SKU/Artikelnummer")
        form_layout.addRow("SKU:", self.sku_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Produktbeschreibung...")
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("Beschreibung:", self.description_edit)
        
        # Category
        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("Kategorie")
        form_layout.addRow("Kategorie:", self.category_edit)
        
        # Price
        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("0.00")
        form_layout.addRow("Preis (€):", self.price_edit)
        
        layout.addWidget(form_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept_dialog)
        button_box.rejected.connect(self.reject)
        
        # Style the buttons
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("💾 Speichern")
        ok_button.setProperty("class", "primary")
        
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setText("❌ Abbrechen")
        
        layout.addWidget(button_box)
    
    def load_product_data(self):
        """Load existing product data into form"""
        if self.product_data:
            self.name_edit.setText(self.product_data.get('name', ''))
            self.sku_edit.setText(self.product_data.get('sku', ''))
            self.description_edit.setText(self.product_data.get('description', ''))
            self.category_edit.setText(self.product_data.get('category', ''))
            if self.product_data.get('price'):
                self.price_edit.setText(str(self.product_data['price']))
    
    def accept_dialog(self):
        """Save product data"""
        # Validate required fields
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie einen Produktnamen ein.")
            return
        
        sku = self.sku_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        category = self.category_edit.text().strip()
        
        try:
            price = float(self.price_edit.text()) if self.price_edit.text() else None
        except ValueError:
            price = None
        
        try:
            if self.product_data:
                # Update existing product
                self.db_manager.update_product(
                    self.product_data['id'],
                    name=name,
                    sku=sku or None,
                    description=description or None,
                    category=category or None,
                    price=price
                )
            else:
                # Add new product
                self.db_manager.add_product(
                    customer_id=self.customer_id,
                    name=name,
                    sku=sku or None,
                    description=description or None,
                    category=category or None,
                    price=price
                )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {e}")


class SettingsDialog(QDialog):
    """Application settings dialog"""
    
    def __init__(self, config: Dict, parent=None):
        super().__init__(parent)
        self.config = config
        
        self.setWindowTitle("⚙️ Einstellungen")
        self.setModal(True)
        self.resize(600, 500)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # General settings
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "🏠 Allgemein")
        
        # API settings
        api_tab = self.create_api_tab()
        tab_widget.addTab(api_tab, "🌐 API")
        
        # UI settings
        ui_tab = self.create_ui_tab()
        tab_widget.addTab(ui_tab, "🎨 Oberfläche")
        
        # Export settings
        export_tab = self.create_export_tab()
        tab_widget.addTab(export_tab, "📄 Export")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Reset button
        reset_btn = QPushButton("🔄 Zurücksetzen")
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        # Cancel and Save buttons
        cancel_btn = QPushButton("❌ Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setProperty("class", "primary")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def create_general_tab(self) -> QWidget:
        """Create general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Company info
        company_group = QGroupBox("Firmeninformationen")
        company_layout = QFormLayout(company_group)
        
        self.company_name_edit = QLineEdit(self.config.get("company", ""))
        company_layout.addRow("Firmenname:", self.company_name_edit)
        
        self.company_address_edit = QTextEdit()
        self.company_address_edit.setMaximumHeight(80)
        self.company_address_edit.setPlainText(self.config.get("address", ""))
        company_layout.addRow("Adresse:", self.company_address_edit)
        
        layout.addWidget(company_group)
        
        # Database settings
        db_group = QGroupBox("Datenbank")
        db_layout = QFormLayout(db_group)
        
        self.db_path_edit = QLineEdit(self.config.get("database", {}).get("path", ""))
        db_path_btn = QPushButton("📁")
        db_path_btn.clicked.connect(self.browse_db_path)
        
        db_path_layout = QHBoxLayout()
        db_path_layout.addWidget(self.db_path_edit)
        db_path_layout.addWidget(db_path_btn)
        
        db_layout.addRow("Datenbankpfad:", db_path_layout)
        
        layout.addWidget(db_group)
        
        layout.addStretch()
        
        return tab
    
    def create_api_tab(self) -> QWidget:
        """Create API settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # API settings
        api_group = QGroupBox("API-Konfiguration")
        api_layout = QFormLayout(api_group)
        
        self.api_url_edit = QLineEdit(self.config.get("api", {}).get("base_url", ""))
        api_layout.addRow("Basis-URL:", self.api_url_edit)
        
        self.api_key_edit = QLineEdit(self.config.get("api", {}).get("key", ""))
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        api_layout.addRow("API-Schlüssel:", self.api_key_edit)
        
        self.api_timeout_spin = QSpinBox()
        self.api_timeout_spin.setRange(5, 120)
        self.api_timeout_spin.setValue(self.config.get("api", {}).get("timeout", 30))
        self.api_timeout_spin.setSuffix(" Sek.")
        api_layout.addRow("Timeout:", self.api_timeout_spin)
        
        layout.addWidget(api_group)
        
        # Test connection
        test_btn = QPushButton("🔗 Verbindung testen")
        test_btn.clicked.connect(self.test_api_connection)
        layout.addWidget(test_btn)
        
        layout.addStretch()
        
        return tab
    
    def create_ui_tab(self) -> QWidget:
        """Create UI settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme settings
        theme_group = QGroupBox("Design")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Glassmorphism Dark", "Glassmorphism Light"])
        theme_layout.addRow("Theme:", self.theme_combo)
        
        self.animations_check = QCheckBox("Animationen aktivieren")
        self.animations_check.setChecked(self.config.get("ui", {}).get("animations", True))
        theme_layout.addRow("", self.animations_check)
        
        self.sound_check = QCheckBox("Töne aktivieren")
        self.sound_check.setChecked(self.config.get("ui", {}).get("sounds", False))
        theme_layout.addRow("", self.sound_check)
        
        layout.addWidget(theme_group)
        
        # Font settings
        font_group = QGroupBox("Schriftart")
        font_layout = QFormLayout(font_group)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(self.config.get("ui", {}).get("font_size", 10))
        font_layout.addRow("Schriftgröße:", self.font_size_spin)
        
        layout.addWidget(font_group)
        
        layout.addStretch()
        
        return tab
    
    def create_export_tab(self) -> QWidget:
        """Create export settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # PDF settings
        pdf_group = QGroupBox("PDF-Einstellungen")
        pdf_layout = QFormLayout(pdf_group)
        
        self.pdf_template_combo = QComboBox()
        self.pdf_template_combo.addItems(["Standard", "Kompakt", "Premium"])
        pdf_layout.addRow("PDF-Template:", self.pdf_template_combo)
        
        self.include_logo_check = QCheckBox("Kundenlogo einbinden")
        self.include_logo_check.setChecked(True)
        pdf_layout.addRow("", self.include_logo_check)
        
        self.qr_size_spin = QSpinBox()
        self.qr_size_spin.setRange(50, 300)
        self.qr_size_spin.setValue(100)
        self.qr_size_spin.setSuffix(" px")
        pdf_layout.addRow("QR-Code Größe:", self.qr_size_spin)
        
        layout.addWidget(pdf_group)
        
        # Export paths
        paths_group = QGroupBox("Export-Pfade")
        paths_layout = QFormLayout(paths_group)
        
        self.qr_path_edit = QLineEdit(self.config.get("paths", {}).get("qr_codes", ""))
        qr_path_btn = QPushButton("📁")
        qr_path_layout = QHBoxLayout()
        qr_path_layout.addWidget(self.qr_path_edit)
        qr_path_layout.addWidget(qr_path_btn)
        paths_layout.addRow("QR-Codes:", qr_path_layout)
        
        self.pdf_path_edit = QLineEdit(self.config.get("paths", {}).get("pdf_labels", ""))
        pdf_path_btn = QPushButton("📁")
        pdf_path_layout = QHBoxLayout()
        pdf_path_layout.addWidget(self.pdf_path_edit)
        pdf_path_layout.addWidget(pdf_path_btn)
        paths_layout.addRow("PDF-Labels:", pdf_path_layout)
        
        layout.addWidget(paths_group)
        
        layout.addStretch()
        
        return tab
    
    def browse_db_path(self):
        """Browse for database path"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Datenbank speichern als",
            self.db_path_edit.text(),
            "SQLite Datenbank (*.db)"
        )
        if file_path:
            self.db_path_edit.setText(file_path)
    
    def test_api_connection(self):
        """Test API connection"""
        # TODO: Implement API connection test
        QMessageBox.information(self, "API-Test", "API-Verbindungstest wird implementiert...")
    
    def reset_settings(self):
        """Reset settings to default"""
        reply = QMessageBox.question(
            self, "Einstellungen zurücksetzen",
            "Möchten Sie alle Einstellungen auf die Standardwerte zurücksetzen?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset to default values
            self.company_name_edit.setText("NeuroCompany")
            self.company_address_edit.setPlainText("")
            self.api_url_edit.setText("")
            self.api_key_edit.setText("")
            self.animations_check.setChecked(True)
            self.sound_check.setChecked(False)
            self.font_size_spin.setValue(10)
    
    def save_settings(self):
        """Save settings"""
        try:
            # Update config
            self.config["company"] = self.company_name_edit.text()
            self.config["address"] = self.company_address_edit.toPlainText()
            
            if "database" not in self.config:
                self.config["database"] = {}
            self.config["database"]["path"] = self.db_path_edit.text()
            
            if "api" not in self.config:
                self.config["api"] = {}
            self.config["api"]["base_url"] = self.api_url_edit.text()
            self.config["api"]["key"] = self.api_key_edit.text()
            self.config["api"]["timeout"] = self.api_timeout_spin.value()
            
            if "ui" not in self.config:
                self.config["ui"] = {}
            self.config["ui"]["animations"] = self.animations_check.isChecked()
            self.config["ui"]["sounds"] = self.sound_check.isChecked()
            self.config["ui"]["font_size"] = self.font_size_spin.value()
            
            # Save to file
            config_path = Path(__file__).parent.parent / "config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "Einstellungen", "Einstellungen erfolgreich gespeichert!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {e}")


class BackupDialog(QDialog):
    """Database backup dialog"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        
        self.setWindowTitle("💾 Datenbank-Backup")
        self.setModal(True)
        self.resize(500, 300)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("💾 Datenbank-Backup erstellen")
        header_label.setProperty("class", "title")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Options
        options_group = QGroupBox("Backup-Optionen")
        options_layout = QFormLayout(options_group)
        
        # Backup path
        self.backup_path_edit = QLineEdit()
        backup_path = Path.home() / f"neuroscan_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        self.backup_path_edit.setText(str(backup_path))
        
        browse_btn = QPushButton("📁")
        browse_btn.clicked.connect(self.browse_backup_path)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.backup_path_edit)
        path_layout.addWidget(browse_btn)
        
        options_layout.addRow("Backup-Pfad:", path_layout)
        
        # Include files
        self.include_files_check = QCheckBox("QR-Codes und PDF-Dateien einschließen")
        self.include_files_check.setChecked(True)
        options_layout.addRow("", self.include_files_check)
        
        # Compress
        self.compress_check = QCheckBox("Backup komprimieren (ZIP)")
        self.compress_check.setChecked(True)
        options_layout.addRow("", self.compress_check)
        
        layout.addWidget(options_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        self.backup_btn = QPushButton("💾 Backup erstellen")
        self.backup_btn.setProperty("class", "primary")
        self.backup_btn.clicked.connect(self.create_backup)
        button_layout.addWidget(self.backup_btn)
        
        layout.addLayout(button_layout)
    
    def browse_backup_path(self):
        """Browse for backup path"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Backup speichern als",
            self.backup_path_edit.text(),
            "SQLite Datenbank (*.db);;ZIP Archiv (*.zip)"
        )
        if file_path:
            self.backup_path_edit.setText(file_path)
    
    def create_backup(self):
        """Create database backup"""
        backup_path = self.backup_path_edit.text()
        if not backup_path:
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie einen Backup-Pfad an.")
            return
        
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.backup_btn.setEnabled(False)
            
            # TODO: Implement actual backup logic
            QTimer.singleShot(2000, self.backup_complete)
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Backup-Fehler: {e}")
            self.progress_bar.setVisible(False)
            self.backup_btn.setEnabled(True)
    
    def backup_complete(self):
        """Handle backup completion"""
        self.progress_bar.setVisible(False)
        self.backup_btn.setEnabled(True)
        
        QMessageBox.information(
            self, "Backup erfolgreich",
            f"Backup wurde erfolgreich erstellt:\n{self.backup_path_edit.text()}"
        )
        self.accept()


class AboutDialog(QDialog):
    """About dialog"""
    
    def __init__(self, config: Dict, parent=None):
        super().__init__(parent)
        self.config = config
        
        self.setWindowTitle("📋 Über NeuroScan Manager")
        self.setModal(True)
        self.resize(450, 350)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Logo and title
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        # App icon/logo
        icon_label = QLabel("🧠")
        icon_label.setFont(QFont("Segoe UI Emoji", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(icon_label)
        
        # App name
        name_label = QLabel("NeuroScan Manager")
        name_label.setProperty("class", "title")
        name_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(name_label)
        
        # Version
        version_label = QLabel(f"Version {self.config.get('version', '1.0.0')}")
        version_label.setProperty("class", "subtitle")
        version_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(version_label)
        
        layout.addLayout(header_layout)
        
        # Description
        description = """
        <p><b>NeuroScan Manager</b> ist eine Premium-Lösung für die Verwaltung 
        und Authentifizierung von Produktzertifikaten.</p>
        
        <p><b>Features:</b></p>
        <ul>
        <li>📋 Kundenverwaltung</li>
        <li>🎫 Zertifikatserstellung</li>
        <li>📱 QR-Code Generation</li>
        <li>📄 PDF-Label Export</li>
        <li>🌐 Web-Verifizierung</li>
        <li>🎨 Glassmorphism Design</li>
        </ul>
        """
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        layout.addWidget(desc_label)
        
        # Copyright
        copyright_label = QLabel(f"© 2025 {self.config.get('company', 'NeuroCompany')}. Alle Rechte vorbehalten.")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 9px;")
        layout.addWidget(copyright_label)
        
        # Close button
        close_btn = QPushButton("Schließen")
        close_btn.setProperty("class", "primary")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
