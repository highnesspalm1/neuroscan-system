#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Customer Manager Widget for NeuroScan
Manages customer data with glassmorphism UI
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView, QFrame, QGroupBox,
    QFormLayout, QFileDialog, QMessageBox, QDialog, QDialogButtonBox,
    QTextEdit, QAbstractItemView, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QAction, QIcon
from typing import Dict, List, Optional
from pathlib import Path
import shutil


class CustomerManagerWidget(QWidget):
    """Widget for managing customers"""
    
    customer_updated = Signal()
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("👥 Kundenverwaltung")
        title_label.setProperty("class", "title")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add customer button
        add_btn = QPushButton("➕ Neuer Kunde")
        add_btn.setProperty("class", "primary")
        add_btn.clicked.connect(self.add_customer)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Search and filters
        filter_frame = QFrame()
        filter_frame.setProperty("class", "panel")
        filter_layout = QHBoxLayout(filter_frame)
        
        # Search
        search_label = QLabel("🔍 Suchen:")
        filter_layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Name oder E-Mail eingeben...")
        self.search_edit.textChanged.connect(self.filter_customers)
        filter_layout.addWidget(self.search_edit)
        
        filter_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Aktualisieren")
        refresh_btn.clicked.connect(self.refresh_data)
        filter_layout.addWidget(refresh_btn)
        
        layout.addWidget(filter_frame)
        
        # Customers table
        self.customers_table = QTableWidget()
        self.customers_table.setAlternatingRowColors(True)
        self.customers_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.customers_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customers_table.customContextMenuRequested.connect(self.show_context_menu)
        self.customers_table.doubleClicked.connect(self.edit_customer)
        
        # Table headers
        headers = ["ID", "Name", "E-Mail", "Logo", "Erstellt", "Aktualisiert"]
        self.customers_table.setColumnCount(len(headers))
        self.customers_table.setHorizontalHeaderLabels(headers)
        
        # Column widths
        header = self.customers_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Name
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # E-Mail
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Logo
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Erstellt
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Aktualisiert
        
        layout.addWidget(self.customers_table)
        
        # Statistics
        self.stats_label = QLabel("0 Kunden")
        self.stats_label.setProperty("class", "subtitle")
        layout.addWidget(self.stats_label)
    
    def refresh_data(self):
        """Refresh customer data"""
        try:
            customers = self.db_manager.get_customers()
            self.populate_table(customers)
            self.stats_label.setText(f"{len(customers)} Kunde{'n' if len(customers) != 1 else ''}")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Kunden: {e}")
    
    def populate_table(self, customers: List[Dict]):
        """Populate the customers table"""
        self.customers_table.setRowCount(len(customers))
        
        for row, customer in enumerate(customers):
            # ID
            id_item = QTableWidgetItem(str(customer['id']))
            id_item.setData(Qt.UserRole, customer)
            self.customers_table.setItem(row, 0, id_item)
            
            # Name
            name_item = QTableWidgetItem(customer['name'])
            self.customers_table.setItem(row, 1, name_item)
            
            # E-Mail
            email_item = QTableWidgetItem(customer.get('email', ''))
            self.customers_table.setItem(row, 2, email_item)
            
            # Logo
            logo_item = QTableWidgetItem("✅" if customer.get('logo_path') else "❌")
            logo_item.setTextAlignment(Qt.AlignCenter)
            self.customers_table.setItem(row, 3, logo_item)
            
            # Created
            created_item = QTableWidgetItem(customer['created_at'][:10])
            self.customers_table.setItem(row, 4, created_item)
            
            # Updated
            updated_item = QTableWidgetItem(customer['updated_at'][:10])
            self.customers_table.setItem(row, 5, updated_item)
    
    def filter_customers(self):
        """Filter customers based on search text"""
        search_text = self.search_edit.text().lower()
        
        for row in range(self.customers_table.rowCount()):
            should_show = True
            
            if search_text:
                name_item = self.customers_table.item(row, 1)
                email_item = self.customers_table.item(row, 2)
                
                name_match = search_text in name_item.text().lower() if name_item else False
                email_match = search_text in email_item.text().lower() if email_item else False
                
                should_show = name_match or email_match
            
            self.customers_table.setRowHidden(row, not should_show)
    
    def show_context_menu(self, position):
        """Show context menu for customer actions"""
        if self.customers_table.itemAt(position) is None:
            return
        
        menu = QMenu(self)
        
        edit_action = QAction("✏️ Bearbeiten", self)
        edit_action.triggered.connect(self.edit_customer)
        menu.addAction(edit_action)
        
        view_products_action = QAction("📦 Produkte anzeigen", self)
        view_products_action.triggered.connect(self.view_customer_products)
        menu.addAction(view_products_action)
        
        menu.addSeparator()
        
        delete_action = QAction("🗑️ Löschen", self)
        delete_action.triggered.connect(self.delete_customer)
        menu.addAction(delete_action)
        
        menu.exec(self.customers_table.mapToGlobal(position))
    
    def add_customer(self):
        """Add a new customer"""
        dialog = CustomerDialog(self.db_manager, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_data()
            self.customer_updated.emit()
    
    def edit_customer(self):
        """Edit selected customer"""
        current_row = self.customers_table.currentRow()
        if current_row < 0:
            return
        
        customer_data = self.customers_table.item(current_row, 0).data(Qt.UserRole)
        dialog = CustomerDialog(self.db_manager, customer_data, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_data()
            self.customer_updated.emit()
    
    def delete_customer(self):
        """Delete selected customer"""
        current_row = self.customers_table.currentRow()
        if current_row < 0:
            return
        
        customer_data = self.customers_table.item(current_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, "Kunde löschen",
            f"Möchten Sie den Kunden '{customer_data['name']}' wirklich löschen?\n\n"
            "Warnung: Alle zugehörigen Produkte und Zertifikate werden ebenfalls gelöscht!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # TODO: Implement customer deletion with cascade
                QMessageBox.information(self, "Info", "Löschfunktion wird implementiert...")
                # self.db_manager.delete_customer(customer_data['id'])
                # self.refresh_data()
                # self.customer_updated.emit()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Löschen: {e}")
    
    def view_customer_products(self):
        """View products for selected customer"""
        current_row = self.customers_table.currentRow()
        if current_row < 0:
            return
        
        customer_data = self.customers_table.item(current_row, 0).data(Qt.UserRole)
        
        # TODO: Switch to products tab with customer filter
        QMessageBox.information(
            self, "Produkte",
            f"Produkte für Kunde '{customer_data['name']}' werden angezeigt..."
        )


class CustomerDialog(QDialog):
    """Dialog for adding/editing customers"""
    
    def __init__(self, db_manager, customer_data: Optional[Dict] = None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.customer_data = customer_data
        self.logo_path = None
        
        self.setWindowTitle("Kunde bearbeiten" if customer_data else "Neuen Kunden hinzufügen")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
        
        if customer_data:
            self.load_customer_data()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Form
        form_group = QGroupBox("Kundeninformationen")
        form_layout = QFormLayout(form_group)
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Firmenname oder Kundenname")
        form_layout.addRow("Name *:", self.name_edit)
        
        # E-Mail
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("kontakt@firma.de")
        form_layout.addRow("E-Mail:", self.email_edit)
        
        # Logo
        logo_layout = QHBoxLayout()
        
        self.logo_path_edit = QLineEdit()
        self.logo_path_edit.setReadOnly(True)
        self.logo_path_edit.setPlaceholderText("Kein Logo ausgewählt")
        logo_layout.addWidget(self.logo_path_edit)
        
        self.browse_logo_btn = QPushButton("📁 Durchsuchen")
        self.browse_logo_btn.clicked.connect(self.browse_logo)
        logo_layout.addWidget(self.browse_logo_btn)
        
        self.clear_logo_btn = QPushButton("🗑️")
        self.clear_logo_btn.clicked.connect(self.clear_logo)
        self.clear_logo_btn.setFixedWidth(40)
        logo_layout.addWidget(self.clear_logo_btn)
        
        form_layout.addRow("Logo:", logo_layout)
        
        # Logo preview
        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(150, 150)
        self.logo_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.05);
            }
        """)
        self.logo_preview.setAlignment(Qt.AlignCenter)
        self.logo_preview.setText("Kein Logo")
        form_layout.addRow("Vorschau:", self.logo_preview)
        
        layout.addWidget(form_group)
        
        # Notes
        notes_group = QGroupBox("Notizen")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Optional: Zusätzliche Informationen zum Kunden...")
        self.notes_edit.setMaximumHeight(100)
        notes_layout.addWidget(self.notes_edit)
        
        layout.addWidget(notes_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Style the buttons
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("💾 Speichern")
        ok_button.setProperty("class", "primary")
        
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setText("❌ Abbrechen")
        
        layout.addWidget(button_box)
    
    def load_customer_data(self):
        """Load existing customer data into form"""
        if self.customer_data:
            self.name_edit.setText(self.customer_data.get('name', ''))
            self.email_edit.setText(self.customer_data.get('email', ''))
            
            logo_path = self.customer_data.get('logo_path')
            if logo_path and Path(logo_path).exists():
                self.logo_path = logo_path
                self.logo_path_edit.setText(logo_path)
                self.update_logo_preview()
    
    def browse_logo(self):
        """Browse for logo file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Logo auswählen",
            "", "Bilder (*.png *.jpg *.jpeg *.bmp *.gif *.svg)"
        )
        
        if file_path:
            # Copy logo to assets folder
            assets_dir = Path(__file__).parent.parent / "assets" / "customer_logos"
            assets_dir.mkdir(exist_ok=True)
            
            logo_filename = f"customer_{hash(file_path)}_{Path(file_path).name}"
            logo_dest = assets_dir / logo_filename
            
            try:
                shutil.copy2(file_path, logo_dest)
                self.logo_path = str(logo_dest)
                self.logo_path_edit.setText(str(logo_dest))
                self.update_logo_preview()
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Logo konnte nicht kopiert werden: {e}")
    
    def clear_logo(self):
        """Clear logo selection"""
        self.logo_path = None
        self.logo_path_edit.clear()
        self.logo_preview.clear()
        self.logo_preview.setText("Kein Logo")
    
    def update_logo_preview(self):
        """Update logo preview"""
        if self.logo_path and Path(self.logo_path).exists():
            pixmap = QPixmap(self.logo_path)
            scaled_pixmap = pixmap.scaled(
                140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.logo_preview.setPixmap(scaled_pixmap)
        else:
            self.logo_preview.clear()
            self.logo_preview.setText("Kein Logo")
    
    def accept(self):
        """Save customer data"""
        # Validate required fields
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie einen Namen ein.")
            return
        
        email = self.email_edit.text().strip()
        
        try:
            if self.customer_data:
                # Update existing customer
                self.db_manager.update_customer(
                    self.customer_data['id'],
                    name=name,
                    email=email or None,
                    logo_path=self.logo_path
                )
            else:
                # Add new customer
                self.db_manager.add_customer(
                    name=name,
                    email=email or None,
                    logo_path=self.logo_path
                )
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {e}")
