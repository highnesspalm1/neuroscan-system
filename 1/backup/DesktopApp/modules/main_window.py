#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Window for NeuroScan Manager
Premium Glassmorphism UI with Dashboard and Management Features
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QSpacerItem, QSizePolicy, QMessageBox, QProgressBar,
    QLineEdit, QComboBox, QTextEdit, QFileDialog, QGroupBox, QFormLayout,
    QDialog, QDialogButtonBox, QApplication, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal
from PySide6.QtGui import QFont, QPixmap, QIcon
from typing import Dict, List
import os
from pathlib import Path

from .dashboard_widgets import DashboardCard, StatisticsCard, RecentActivityWidget
from .customer_manager import CustomerManagerWidget
from .certificate_manager import CertificateManagerWidget
from .pdf_generator import PDFGenerator


class MainWindow(QMainWindow):
    """Main application window with glassmorphism design"""
    
    def __init__(self, config: Dict, db_manager):
        super().__init__()
        
        self.config = config
        self.db_manager = db_manager
        self.pdf_generator = PDFGenerator(config, db_manager)
        
        self.setWindowTitle(f"{config['app_name']} - {config['company']}")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Set window icon if available
        icon_path = Path(__file__).parent.parent / "assets" / "neuroscan-icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self.init_ui()
        self.load_data()
        
        # Setup periodic refresh
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_dashboard)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        # Main content area with tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("mainTabs")
        
        # Dashboard Tab
        self.dashboard_widget = self.create_dashboard()
        self.tab_widget.addTab(self.dashboard_widget, "🏠 Dashboard")
        
        # Customer Management Tab
        self.customer_widget = CustomerManagerWidget(self.db_manager)
        self.tab_widget.addTab(self.customer_widget, "👥 Kunden")
        
        # Certificate Management Tab
        self.certificate_widget = CertificateManagerWidget(self.db_manager, self.pdf_generator)
        self.tab_widget.addTab(self.certificate_widget, "🎫 Zertifikate")
        
        # Settings Tab
        self.settings_widget = self.create_settings()
        self.tab_widget.addTab(self.settings_widget, "⚙️ Einstellungen")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.statusBar().showMessage("NeuroScan Manager bereit")
        self.statusBar().setStyleSheet("color: #FFFFFF;")
    
    def create_header(self) -> QHBoxLayout:
        """Create the application header"""
        header_layout = QHBoxLayout()
        
        # Logo and title
        title_frame = QFrame()
        title_frame.setProperty("class", "panel")
        title_layout = QHBoxLayout(title_frame)
        
        # Logo (if available)
        logo_path = Path(__file__).parent.parent / "assets" / "neuroscan-logo.png"
        if logo_path.exists():
            logo_label = QLabel()
            pixmap = QPixmap(str(logo_path))
            logo_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            title_layout.addWidget(logo_label)
        
        # Title and subtitle
        title_container = QVBoxLayout()
        
        title_label = QLabel("NeuroScan Manager")
        title_label.setProperty("class", "title")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_container.addWidget(title_label)
        
        subtitle_label = QLabel("Premium Product Authentication System")
        subtitle_label.setProperty("class", "subtitle")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        title_container.addWidget(subtitle_label)
        
        title_layout.addLayout(title_container)
        title_layout.addStretch()
        
        header_layout.addWidget(title_frame)
        
        # Quick actions
        actions_frame = QFrame()
        actions_frame.setProperty("class", "panel")
        actions_layout = QHBoxLayout(actions_frame)
        
        # Quick certificate button
        quick_cert_btn = QPushButton("🎫 Schnell-Zertifikat")
        quick_cert_btn.setProperty("class", "primary")
        quick_cert_btn.clicked.connect(self.quick_create_certificate)
        actions_layout.addWidget(quick_cert_btn)
        
        # Generate PDF button
        gen_pdf_btn = QPushButton("📄 PDF Erstellen")
        gen_pdf_btn.setProperty("class", "secondary")
        gen_pdf_btn.clicked.connect(self.batch_generate_pdfs)
        actions_layout.addWidget(gen_pdf_btn)
        
        header_layout.addWidget(actions_frame)
        
        return header_layout
    
    def create_dashboard(self) -> QWidget:
        """Create the dashboard widget"""
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        layout.setSpacing(20)
        
        # Statistics cards
        stats_layout = QGridLayout()
        
        self.stats_cards = {
            'customers': StatisticsCard("Kunden", "0", "👥", "#00E5FF"),
            'products': StatisticsCard("Produkte", "0", "📦", "#39FF14"),
            'certificates': StatisticsCard("Zertifikate", "0", "🎫", "#FF6B35"),
            'scans_today': StatisticsCard("Scans Heute", "0", "📱", "#8E44AD")
        }
        
        row = 0
        col = 0
        for card in self.stats_cards.values():
            stats_layout.addWidget(card, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        layout.addLayout(stats_layout)
        
        # Recent activity and charts
        content_layout = QHBoxLayout()
        
        # Recent activity
        self.recent_activity = RecentActivityWidget(self.db_manager)
        content_layout.addWidget(self.recent_activity, 2)
        
        # Quick stats
        quick_stats_frame = QFrame()
        quick_stats_frame.setProperty("class", "panel")
        quick_stats_layout = QVBoxLayout(quick_stats_frame)
        
        quick_stats_title = QLabel("Schnellübersicht")
        quick_stats_title.setProperty("class", "subtitle")
        quick_stats_layout.addWidget(quick_stats_title)
        
        self.weekly_scans_label = QLabel("Scans diese Woche: 0")
        self.active_certs_label = QLabel("Aktive Zertifikate: 0")
        
        quick_stats_layout.addWidget(self.weekly_scans_label)
        quick_stats_layout.addWidget(self.active_certs_label)
        quick_stats_layout.addStretch()
        
        content_layout.addWidget(quick_stats_frame, 1)
        
        layout.addLayout(content_layout)
        
        return dashboard
    
    def create_settings(self) -> QWidget:
        """Create the settings widget"""
        settings = QWidget()
        layout = QVBoxLayout(settings)
        
        # Database settings
        db_group = QGroupBox("Datenbank")
        db_layout = QFormLayout(db_group)
        
        self.db_path_edit = QLineEdit(str(self.db_manager.db_path))
        self.db_path_edit.setReadOnly(True)
        db_layout.addRow("Datenbankpfad:", self.db_path_edit)
        
        backup_btn = QPushButton("Backup erstellen")
        backup_btn.clicked.connect(self.show_backup_dialog)
        db_layout.addRow("", backup_btn)
        
        layout.addWidget(db_group)
        
        # API settings
        api_group = QGroupBox("API-Einstellungen")
        api_layout = QFormLayout(api_group)
        
        self.api_url_edit = QLineEdit(self.config.get("api", {}).get("base_url", ""))
        api_layout.addRow("API-URL:", self.api_url_edit)
        
        test_api_btn = QPushButton("Verbindung testen")
        test_api_btn.clicked.connect(self.test_api_connection)
        api_layout.addRow("", test_api_btn)
        
        layout.addWidget(api_group)
        
        # UI settings
        ui_group = QGroupBox("Benutzeroberfläche")
        ui_layout = QFormLayout(ui_group)
        
        self.animations_enabled = QComboBox()
        self.animations_enabled.addItems(["Aktiviert", "Deaktiviert"])
        ui_layout.addRow("Animationen:", self.animations_enabled)
        
        layout.addWidget(ui_group)
        
        layout.addStretch()
        
        return settings
    
    def load_data(self):
        """Load data and refresh UI"""
        self.refresh_dashboard()
        self.customer_widget.refresh_data()
        self.certificate_widget.refresh_data()
    
    def refresh_dashboard(self):
        """Refresh dashboard statistics"""
        try:
            stats = self.db_manager.get_dashboard_stats()
            
            # Update statistics cards
            self.stats_cards['customers'].update_value(str(stats['total_customers']))
            self.stats_cards['products'].update_value(str(stats['total_products']))
            self.stats_cards['certificates'].update_value(str(stats['total_certificates']))
            self.stats_cards['scans_today'].update_value(str(stats['scans_today']))
            
            # Update quick stats
            self.weekly_scans_label.setText(f"Scans diese Woche: {stats['scans_this_week']}")
            self.active_certs_label.setText(f"Aktive Zertifikate: {stats['active_certificates']}")
            
            # Refresh recent activity
            self.recent_activity.refresh_data()
            
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")
            
    def quick_create_certificate(self):
        """Quick certificate creation dialog"""
        from .dialogs import QuickCertificateDialog
        
        dialog = QuickCertificateDialog(self.db_manager, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_dashboard()
            self.certificate_widget.refresh_data()
            self.statusBar().showMessage("Zertifikat erfolgreich erstellt", 3000)
    
    def batch_generate_pdfs(self):
        """Batch generate PDFs for certificates without labels"""
        certificates = self.db_manager.get_certificates()
        pending_certs = [cert for cert in certificates if not cert.get('pdf_label_path')]
        
        if not pending_certs:
            QMessageBox.information(self, "Info", "Alle Zertifikate haben bereits PDF-Labels.")
            return
        
        reply = QMessageBox.question(
            self, "PDF-Generierung",
            f"Möchten Sie PDF-Labels für {len(pending_certs)} Zertifikate erstellen?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            from .dialogs import ProgressDialog
            progress = ProgressDialog("PDF-Labels werden erstellt...", len(pending_certs), self)
            progress.show()
            
            QApplication.processEvents()
            
            for i, cert in enumerate(pending_certs):
                try:
                    self.pdf_generator.generate_label(cert['serial_number'])
                    progress.update_progress(i + 1)
                    QApplication.processEvents()
                except Exception as e:
                    print(f"Error generating PDF for {cert['serial_number']}: {e}")
            
            progress.close()
            self.statusBar().showMessage(f"{len(pending_certs)} PDF-Labels erstellt", 5000)
            self.refresh_dashboard()
    
    def create_backup(self):
        """Create database backup"""
        try:
            backup_path, _ = QFileDialog.getSaveFileName(
                self, "Backup speichern",
                f"neuroscan_backup_{QTimer().singleShot.__name__}.db",
                "Database files (*.db)"
            )
            
            if backup_path:
                import shutil
                shutil.copy2(self.db_manager.db_path, backup_path)
                QMessageBox.information(self, "Backup", "Backup erfolgreich erstellt!")
                
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Backup-Erstellung fehlgeschlagen: {e}")
    
    def test_api_connection(self):
        """Test API connection"""
        # Placeholder for API testing
        QMessageBox.information(self, "API-Test", "API-Verbindungstest wird implementiert...")
    
    def show_settings(self):
        """Show settings dialog"""
        from .dialogs import SettingsDialog
        
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == QDialog.Accepted:
            # Reload configuration
            self.load_data()
            self.statusBar().showMessage("Einstellungen aktualisiert", 3000)
    
    def show_about(self):
        """Show about dialog"""
        from .dialogs import AboutDialog
        
        dialog = AboutDialog(self.config, self)
        dialog.exec()
    
    def show_backup_dialog(self):
        """Show backup dialog"""
        from .dialogs import BackupDialog
        
        dialog = BackupDialog(self.db_manager, self)
        dialog.exec()
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self, "Beenden",
            "Möchten Sie NeuroScan Manager wirklich beenden?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
