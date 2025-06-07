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

# Import the force style fix
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from force_style_fix import force_auth_dialog_styles
except ImportError:
    print("⚠️ Force style fix not available")
    def force_auth_dialog_styles(dialog):
        pass


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
        
        # Apply forced styles to override global styles
        QTimer.singleShot(50, lambda: force_auth_dialog_styles(self))
        
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
        header_frame.setObjectName("HeaderPanel")
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
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Melden Sie sich für Cloud-Services an")
        subtitle_label.setObjectName("SubtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
        
        # Login form
        form_frame = QFrame()
        form_frame.setObjectName("FormPanel")
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(20)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Username field
        self.username_edit = QLineEdit()
        self.username_edit.setObjectName("UsernameField")
        self.username_edit.setPlaceholderText("Benutzername eingeben")
        self.username_edit.setMinimumHeight(45)
        self.username_edit.returnPressed.connect(self.on_login)
        form_layout.addRow("Benutzername:", self.username_edit)
        
        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setObjectName("PasswordField")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Passwort eingeben")
        self.password_edit.setMinimumHeight(45)
        self.password_edit.returnPressed.connect(self.on_login)
        form_layout.addRow("Passwort:", self.password_edit)
        
        # Remember credentials checkbox
        self.remember_checkbox = QCheckBox("Anmeldedaten merken")
        self.remember_checkbox.setObjectName("RememberCheckbox")
        form_layout.addRow("", self.remember_checkbox)
        
        layout.addWidget(form_frame)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("ProgressBar")
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.setObjectName("CancelButton")
        self.cancel_button.setMinimumHeight(45)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        
        self.login_button = QPushButton("Anmelden")
        self.login_button.setObjectName("LoginButton")
        self.login_button.setMinimumHeight(45)
        self.login_button.clicked.connect(self.on_login)
        self.login_button.setDefault(True)
        button_layout.addWidget(self.login_button)
        
        layout.addLayout(button_layout)
        
        # Focus on username field
        self.username_edit.setFocus()

    def apply_styles(self):
        """Apply glassmorphism styles with high priority to override global styles"""
        # Set an objectName for this dialog to use with CSS
        self.setObjectName("AuthDialog")
        self.setStyleSheet("""
            /* Main Dialog */
            QDialog#AuthDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15, 25, 35, 0.95),
                    stop:1 rgba(25, 35, 45, 0.95));
                border: 2px solid rgba(0, 229, 255, 0.3);
                border-radius: 20px;
            }
            
            /* Panels */
            QFrame#HeaderPanel, QFrame#FormPanel {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
                padding: 20px;
                margin: 5px;
            }
            
            /* Title and Subtitle */
            QLabel#TitleLabel {
                color: #FFFFFF;
                font-weight: bold;
                margin: 10px 0;
            }
            
            QLabel#SubtitleLabel {
                color: rgba(255, 255, 255, 0.8);
                margin-bottom: 15px;
            }
            
            /* Status Label */
            QLabel#StatusLabel {
                color: #FF6B6B;
                font-weight: bold;
                margin: 10px 0;
                padding: 8px;
                border-radius: 6px;
                background: rgba(255, 107, 107, 0.1);
            }
            
            /* Form Labels */
            QFormLayout QLabel {
                color: #FFFFFF;
                font-weight: 600;
                font-size: 14px;
                min-width: 120px;
            }
            
            /* Input Fields */
            QLineEdit#UsernameField, QLineEdit#PasswordField {
                background: rgba(255, 255, 255, 0.12);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                padding: 12px 15px;
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 500;
                min-height: 45px;
            }
            
            QLineEdit#UsernameField:focus, QLineEdit#PasswordField:focus {
                border: 2px solid #00E5FF;
                background: rgba(255, 255, 255, 0.18);
                outline: none;
            }
            
            QLineEdit#UsernameField::placeholder, QLineEdit#PasswordField::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
            
            /* Checkbox */
            QCheckBox#RememberCheckbox {
                color: #FFFFFF;
                spacing: 10px;
                font-size: 14px;
                margin: 10px 0;
            }
            
            QCheckBox#RememberCheckbox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid rgba(255, 255, 255, 0.4);
                border-radius: 6px;
                background: rgba(255, 255, 255, 0.1);
            }
            
            QCheckBox#RememberCheckbox::indicator:checked {
                background: #00E5FF;
                border: 2px solid #00E5FF;
            }
            
            /* Progress Bar */
            QProgressBar#ProgressBar {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                height: 10px;
                text-align: center;
            }
            
            QProgressBar#ProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00E5FF,
                    stop:1 #4D88FF);
                border-radius: 8px;
            }
            
            /* Buttons */
            QPushButton#LoginButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00E5FF,
                    stop:1 #4D88FF);
                border: none;
                border-radius: 10px;
                padding: 12px 25px;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 15px;
                min-width: 120px;
                min-height: 45px;
            }
            
            QPushButton#LoginButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #22EBFF,
                    stop:1 #6E9FFF);
            }
            
            QPushButton#LoginButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00C2D9,
                    stop:1 #3D70D9);
            }
            
            QPushButton#CancelButton {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                padding: 12px 25px;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 15px;
                min-width: 120px;
                min-height: 45px;
            }
            
            QPushButton#CancelButton:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            
            QPushButton#CancelButton:pressed {
                background: rgba(255, 255, 255, 0.15);
            }
        """)

    def on_login(self):
        """Handle login button click"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username:
            self.show_status_message("Bitte geben Sie einen Benutzernamen ein", "error")
            self.username_edit.setFocus()
            return
        
        if not password:
            self.show_status_message("Bitte geben Sie ein Passwort ein", "error")
            self.password_edit.setFocus()
            return
        
        # Show loading state
        self.set_loading_state(True, "Anmeldung läuft...")
        
        # Start login in background
        self.login_thread = LoginThread(self.api_manager, username, password)
        self.login_thread.login_result.connect(self.on_login_result)
        self.login_thread.start()
    
    def on_login_result(self, success: bool, message: str):
        """Handle login thread result"""
        # Reset loading state
        self.set_loading_state(False)
        
        if success:
            self.show_status_message("Anmeldung erfolgreich!", "success")
            
            # Save credentials if checked
            if self.remember_checkbox.isChecked():
                self.api_manager.store_credentials(self.username_edit.text())
            
            # Close dialog with success
            QTimer.singleShot(800, self.accept)
        else:
            self.show_status_message(message, "error")
    
    def show_status_message(self, message: str, status_type: str = "info"):
        """Show status message with appropriate styling"""
        self.status_label.setText(message)
        
        if status_type == "error":
            self.status_label.setStyleSheet("""
                QLabel#StatusLabel {
                    color: #FF6B6B;
                    background: rgba(255, 107, 107, 0.1);
                    border: 1px solid rgba(255, 107, 107, 0.2);
                }
            """)
        elif status_type == "success":
            self.status_label.setStyleSheet("""
                QLabel#StatusLabel {
                    color: #00FFAA;
                    background: rgba(0, 255, 170, 0.1);
                    border: 1px solid rgba(0, 255, 170, 0.2);
                }
            """)
        else:  # info
            self.status_label.setStyleSheet("""
                QLabel#StatusLabel {
                    color: #00E5FF;
                    background: rgba(0, 229, 255, 0.1);
                    border: 1px solid rgba(0, 229, 255, 0.2);
                }
            """)
    
    def set_loading_state(self, is_loading: bool, message: str = None):
        """Set loading state for the dialog"""
        # Show/hide progress bar
        self.progress_bar.setVisible(is_loading)
        
        if is_loading:
            # Start progress bar animation
            self.progress_bar.setRange(0, 0)
            
            # Update status message if provided
            if message:
                self.show_status_message(message, "info")
            
            # Disable form controls
            self.username_edit.setEnabled(False)
            self.password_edit.setEnabled(False)
            self.login_button.setEnabled(False)
            self.remember_checkbox.setEnabled(False)
        else:
            # Reset progress bar
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            
            # Enable form controls
            self.username_edit.setEnabled(True)
            self.password_edit.setEnabled(True)
            self.login_button.setEnabled(True)
            self.remember_checkbox.setEnabled(True)
