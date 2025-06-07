#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication Dialog for NeuroScan Manager
Login dialog for API authentication
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QPushButton, QLineEdit, QFrame, QMessageBox, QProgressBar,
    QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap
from typing import Dict, Optional, Tuple
import logging
from pathlib import Path

from .api_manager import APIManager


class LoginThread(QThread):
    """Background thread for login authentication"""
    
    login_result = Signal(bool, str)  # success, message
    
    def __init__(self, api_manager: APIManager, username: str, password: str):
        super().__init__()
        self.api_manager = api_manager
        self.username = username
        self.password = password
    def run(self):
        """Execute login in background"""
        try:
            success, message = self.api_manager.login(self.username, self.password)
            self.login_result.emit(success, message)
        except Exception as e:
            logging.error(f"Login error: {e}")
            self.login_result.emit(False, f"Fehler beim Anmelden: {str(e)}")


class AuthDialog(QDialog):
    """Authentication dialog for API login"""
    
    def __init__(self, api_manager: APIManager, parent=None):
        super().__init__(parent)
        
        self.api_manager = api_manager
        self.login_thread = None
        self.setWindowTitle("NeuroScan - Anmeldung")
        self.setModal(True)
        self.setFixedSize(480, 420)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        self.init_ui()
        self.apply_styles()
        
        # Center the dialog
        if parent:
            self.move(
                parent.x() + (parent.width() - self.width()) // 2,
                parent.y() + (parent.height() - self.height()) // 2
            )
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "panel")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(15)
        
        # Logo (if available)
        logo_path = Path(__file__).parent.parent / "assets" / "neuroscan-logo.png"
        if logo_path.exists():
            logo_label = QLabel()
            pixmap = QPixmap(str(logo_path))
            logo_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(logo_label)
        
        # Title
        title_label = QLabel("NeuroScan Anmeldung")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title_label.setProperty("class", "title")
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Melden Sie sich für Cloud-Services an")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setProperty("class", "subtitle")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
          # Login form
        form_frame = QFrame()
        form_frame.setProperty("class", "panel")
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(20)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Username field
        self.username_edit = QLineEdit()
        self.username_edit.setProperty("class", "input")
        self.username_edit.setPlaceholderText("Benutzername eingeben")
        self.username_edit.setMinimumHeight(45)
        self.username_edit.returnPressed.connect(self.on_login)
        form_layout.addRow("Benutzername:", self.username_edit)
        
        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setProperty("class", "input")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Passwort eingeben")
        self.password_edit.setMinimumHeight(45)
        self.password_edit.returnPressed.connect(self.on_login)
        form_layout.addRow("Passwort:", self.password_edit)
        
        # Remember credentials checkbox
        self.remember_checkbox = QCheckBox("Anmeldedaten merken")
        self.remember_checkbox.setProperty("class", "checkbox")
        form_layout.addRow("", self.remember_checkbox)
        
        layout.addWidget(form_frame)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setProperty("class", "progress")
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setProperty("class", "status")
        layout.addWidget(self.status_label)
          # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.setProperty("class", "secondary")
        self.cancel_button.setMinimumHeight(45)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        
        self.login_button = QPushButton("Anmelden")
        self.login_button.setProperty("class", "primary")
        self.login_button.setMinimumHeight(45)
        self.login_button.clicked.connect(self.on_login)        self.login_button.setDefault(True)
        button_layout.addWidget(self.login_button)
        
        layout.addLayout(button_layout)
        
        # Focus on username field
        self.username_edit.setFocus()def apply_styles(self):
        """Apply glassmorphism styles with high priority to override global styles"""
        # Set an objectName for this dialog to use with CSS
        self.setObjectName("AuthDialog")
        self.setStyleSheet("""
            /* Force high specificity to override global styles */
            QDialog#AuthDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15, 25, 35, 0.95),
                    stop:1 rgba(25, 35, 45, 0.95));
                border: 2px solid rgba(0, 229, 255, 0.3);
                border-radius: 20px;
            }
            
            AuthDialog QFrame[class="panel"] {
                background: rgba(255, 255, 255, 0.08) !important;
                border: 1px solid rgba(255, 255, 255, 0.15) !important;
                border-radius: 12px !important;
                padding: 20px !important;
                margin: 5px !important;
            }
            
            AuthDialog QLabel[class="title"] {
                color: #FFFFFF !important;
                font-weight: bold !important;
                margin: 10px 0 !important;
            }
            
            AuthDialog QLabel[class="subtitle"] {
                color: rgba(255, 255, 255, 0.8) !important;
                margin-bottom: 15px !important;
            }
            
            AuthDialog QLabel[class="status"] {
                color: #FF6B6B !important;
                font-weight: bold !important;
                margin: 10px 0 !important;
                padding: 8px !important;
                border-radius: 6px !important;
                background: rgba(255, 107, 107, 0.1) !important;
            }
            
            AuthDialog QFormLayout QLabel {
                color: #FFFFFF !important;
                font-weight: 600 !important;
                font-size: 14px !important;
                min-width: 120px !important;
            }
            
            AuthDialog QLineEdit[class="input"] {
                background: rgba(255, 255, 255, 0.12) !important;
                border: 2px solid rgba(255, 255, 255, 0.2) !important;
                border-radius: 10px !important;
                padding: 12px 15px !important;
                color: #FFFFFF !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                min-height: 45px !important;
            }
            
            AuthDialog QLineEdit[class="input"]:focus {
                border: 2px solid #00E5FF !important;
                background: rgba(255, 255, 255, 0.18) !important;
                outline: none !important;
            }
            
            AuthDialog QLineEdit[class="input"]::placeholder {
                color: rgba(255, 255, 255, 0.5) !important;
            }
            
            AuthDialog QCheckBox[class="checkbox"] {
                color: #FFFFFF !important;
                spacing: 10px !important;
                font-size: 14px !important;
                margin: 10px 0 !important;
            }
            
            AuthDialog QCheckBox[class="checkbox"]::indicator {
                width: 20px !important;
                height: 20px !important;
                border: 2px solid rgba(255, 255, 255, 0.4) !important;
                border-radius: 6px !important;
                background: rgba(255, 255, 255, 0.1) !important;
            }
            
            AuthDialog QCheckBox[class="checkbox"]::indicator:checked {
                background: #00E5FF !important;
                border: 2px solid #00E5FF !important;
                image: url(data:image/svg+xml;charset=utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>) !important;
            }
            
            AuthDialog QPushButton[class="primary"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00E5FF, stop:1 #0099CC) !important;
                border: none !important;
                border-radius: 10px !important;
                color: white !important;
                padding: 15px 30px !important;
                font-weight: bold !important;
                font-size: 14px !important;
                min-width: 120px !important;
                min-height: 45px !important;
            }
            
            AuthDialog QPushButton[class="primary"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #33EAFF, stop:1 #00B8E6) !important;
                transform: translateY(-1px) !important;
            }
            
            AuthDialog QPushButton[class="primary"]:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0099CC, stop:1 #006699) !important;
            }
            
            AuthDialog QPushButton[class="primary"]:disabled {
                background: rgba(255, 255, 255, 0.2) !important;
                color: rgba(255, 255, 255, 0.5) !important;
            }
            
            AuthDialog QPushButton[class="secondary"] {
                background: rgba(255, 255, 255, 0.1) !important;
                border: 2px solid rgba(255, 255, 255, 0.3) !important;
                border-radius: 10px !important;
                color: #FFFFFF !important;
                padding: 15px 30px !important;
                font-weight: bold !important;
                font-size: 14px !important;
                min-width: 120px !important;
                min-height: 45px !important;
            }
            
            AuthDialog QPushButton[class="secondary"]:hover {
                background: rgba(255, 255, 255, 0.2) !important;
                border: 2px solid rgba(255, 255, 255, 0.5) !important;
            }
            
            AuthDialog QPushButton[class="secondary"]:pressed {
                background: rgba(255, 255, 255, 0.3) !important;
            }
            
            AuthDialog QProgressBar[class="progress"] {
                border: 2px solid rgba(0, 229, 255, 0.3) !important;
                border-radius: 10px !important;
                background: rgba(255, 255, 255, 0.1) !important;
                text-align: center !important;
                color: #FFFFFF !important;
                font-weight: bold !important;
                min-height: 25px !important;
            }
            
            AuthDialog QProgressBar[class="progress"]::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00E5FF, stop:1 #0099CC) !important;
                border-radius: 8px !important;
                margin: 2px !important;
            }
        """)
    
    def on_login(self):
        """Handle login button click"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        if not username or not password:
            self.show_message("Bitte Benutzername und Passwort eingeben", "error")
            return
        
        # Disable UI during login
        self.set_ui_enabled(False)
        self.show_progress("Anmeldung läuft...")
        
        # Start login in background thread
        self.login_thread = LoginThread(self.api_manager, username, password)
        self.login_thread.login_result.connect(self.on_login_result)
        self.login_thread.start()
    
    def on_login_result(self, success: bool, message: str):
        """Handle login result from background thread"""
        self.hide_progress()
        self.set_ui_enabled(True)
        
        if success:
            self.show_message(message, "success")
            # Close dialog after short delay
            QTimer.singleShot(1000, self.accept)
        else:
            self.show_message(message, "error")
            self.password_edit.clear()
            self.password_edit.setFocus()
    
    def show_message(self, message: str, msg_type: str = "info"):
        """Show status message"""
        self.status_label.setText(message)
        
        if msg_type == "error":
            self.status_label.setStyleSheet("color: #FF6B6B; font-weight: bold;")
        elif msg_type == "success":
            self.status_label.setStyleSheet("color: #4ECDC4; font-weight: bold;")
        else:
            self.status_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")
    
    def show_progress(self, message: str):
        """Show progress bar with message"""
        self.status_label.setText(message)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
    
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.setVisible(False)
    
    def set_ui_enabled(self, enabled: bool):
        """Enable/disable UI elements"""
        self.username_edit.setEnabled(enabled)
        self.password_edit.setEnabled(enabled)
        self.remember_checkbox.setEnabled(enabled)
        self.login_button.setEnabled(enabled)
        self.cancel_button.setEnabled(enabled)
    
    def get_credentials(self) -> Tuple[str, str, bool]:
        """Get entered credentials"""
        return (
            self.username_edit.text().strip(),
            self.password_edit.text().strip(),
            self.remember_checkbox.isChecked()
        )
