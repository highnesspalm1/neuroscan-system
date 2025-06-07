#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Status Widget for NeuroScan Desktop Application
Shows real-time status of cloud services with glassmorphism design
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGroupBox, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPalette, QColor
from typing import Dict
from datetime import datetime

from .api_manager import CloudStatusChecker


class StatusIndicator(QFrame):
    """Individual status indicator for a service"""
    
    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name
        self.status = "unknown"
        self.message = "Checking..."
        
        self.setFixedHeight(60)
        self.setFrameStyle(QFrame.Box)
        self.setup_ui()        
    def setup_ui(self):
        """Setup the UI for the cloud status widget"""
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 18, 10, 10)
        
        # Create status indicators for each service
        self.indicators = {}
        
        services = [
            ("Backend API", self.config["api"]["base_url"]),
            ("Frontend", self.config["api"]["frontend_url"]),
            ("API Docs", self.config["api"]["docs_url"])
        ]
        
        for service_name, url in services:
            indicator = StatusIndicator(service_name)
            self.indicators[service_name] = indicator
            layout.addWidget(indicator)
            
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)
        
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setToolTip("Status aktualisieren")
        self.refresh_button.setFixedSize(30, 30)
        self.refresh_button.clicked.connect(self.manual_refresh)
        self.refresh_button.setStyleSheet("""
            CloudStatusWidget QPushButton[class="refresh"] {
                background: rgba(0, 229, 255, 0.15) !important;
                border: 1px solid rgba(0, 229, 255, 0.3) !important;
                border-radius: 6px !important;
                color: #00E5FF !important;
                font-weight: bold !important;
                font-size: 11px !important;
                max-height: 30px !important;
                min-height: 30px !important;
                max-width: 30px !important;
                min-width: 30px !important;
            }
            CloudStatusWidget QPushButton[class="refresh"]:hover {
                background: rgba(0, 229, 255, 0.25) !important;
                border-color: rgba(0, 229, 255, 0.5) !important;
            }
            CloudStatusWidget QPushButton[class="refresh"]:pressed {
                background: rgba(0, 229, 255, 0.35) !important;
            }
        """)
        self.refresh_button.setProperty("class", "refresh")
        
        self.login_button = QPushButton("🔐 Login")
        self.login_button.setFixedHeight(30)
        self.login_button.clicked.connect(self.login_requested.emit)
        self.login_button.setStyleSheet("""
            CloudStatusWidget QPushButton[class="login"] {
                background: rgba(57, 255, 20, 0.15) !important;
                border: 1px solid rgba(57, 255, 20, 0.3) !important;
                border-radius: 6px !important;
                padding: 4px 10px !important;
                color: #39FF14 !important;
                font-weight: bold !important;
                font-size: 10px !important;
                max-height: 30px !important;
                min-height: 30px !important;
            }
            CloudStatusWidget QPushButton[class="login"]:hover {
                background: rgba(57, 255, 20, 0.25) !important;
                border-color: rgba(57, 255, 20, 0.5) !important;
            }
            CloudStatusWidget QPushButton[class="login"]:pressed {
                background: rgba(57, 255, 20, 0.35) !important;
            }
        """)
        self.login_button.setProperty("class", "login")
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.login_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Overall status label
        self.overall_status = QLabel("🔄 Checking services...")
        self.overall_status.setAlignment(Qt.AlignCenter)
        self.overall_status.setMaximumHeight(25)
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.overall_status.setFont(font)
        self.overall_status.setStyleSheet("""
            CloudStatusWidget QLabel[class="status"] {
                color: #888888 !important;
                font-size: 8pt !important;
                font-weight: bold !important;
                max-height: 25px !important;
                min-height: 20px !important;
                padding: 2px !important;
            }
        """)
        self.overall_status.setProperty("class", "status")
        layout.addWidget(self.overall_status)
        """Setup the UI for the status indicator"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)
        
        # Status icon/circle
        self.status_circle = QLabel("●")
        self.status_circle.setFixedSize(18, 18)
        self.status_circle.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        self.status_circle.setFont(font)
        
        # Service information
        info_layout = QVBoxLayout()
        info_layout.setSpacing(1)
        
        self.name_label = QLabel(self.service_name)
        name_font = QFont()
        name_font.setPointSize(10)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        
        self.message_label = QLabel(self.message)
        message_font = QFont()
        message_font.setPointSize(8)
        self.message_label.setFont(message_font)
        self.message_label.setWordWrap(True)
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.message_label)
        
        # Last updated time
        self.time_label = QLabel("Never")
        time_font = QFont()
        time_font.setPointSize(7)
        self.time_label.setFont(time_font)
        self.time_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.time_label.setStyleSheet("color: #999999;")
        
        layout.addWidget(self.status_circle)
        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addWidget(self.time_label)
        
        self.update_status("unknown", "Initializing...")
        
    def update_status(self, status: str, message: str):
        """Update the status indicator"""
        self.status = status
        self.message = message
          # Update message
        self.message_label.setText(message)
        
        # Update time
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)
        
        # Update colors and style based on status
        if status == "online":
            self.status_circle.setStyleSheet("color: #00FF88;")  # Green
            self.setStyleSheet("""
                QFrame {
                    background: rgba(0, 255, 136, 0.08);
                    border: 1px solid rgba(0, 255, 136, 0.25);
                    border-radius: 10px;
                }
            """)
        elif status == "warning":
            self.status_circle.setStyleSheet("color: #FFB800;")  # Orange
            self.setStyleSheet("""
                QFrame {
                    background: rgba(255, 184, 0, 0.08);
                    border: 1px solid rgba(255, 184, 0, 0.25);
                    border-radius: 10px;
                }
            """)
        elif status == "error":
            self.status_circle.setStyleSheet("color: #FF4444;")  # Red
            self.setStyleSheet("""
                QFrame {
                    background: rgba(255, 68, 68, 0.08);
                    border: 1px solid rgba(255, 68, 68, 0.25);
                    border-radius: 10px;
                }
            """)
        else:  # unknown
            self.status_circle.setStyleSheet("color: #999999;")  # Gray
            self.setStyleSheet("""
                QFrame {
                    background: rgba(153, 153, 153, 0.08);
                    border: 1px solid rgba(153, 153, 153, 0.25);
                    border-radius: 10px;
                }
            """)


class CloudStatusWidget(QGroupBox):
    """Widget that shows the status of all cloud services"""
    
    login_requested = Signal()
    def __init__(self, config: Dict):
        super().__init__("🌐 Cloud Services Status")
        self.config = config
        self.status_checker = None
        
        # Set fixed dimensions to prevent overlapping
        self.setFixedHeight(280)
        self.setMaximumHeight(280)
        
        self.setup_ui()
        self.start_status_checking()
        
        # Set high-priority widget-specific styles to override global styles
        self.setStyleSheet("""
            CloudStatusWidget {
                max-height: 280px !important;
                min-height: 280px !important;
                font-size: 14px !important;
                font-weight: bold !important;
                color: #FFFFFF !important;
                background: rgba(255, 255, 255, 0.1) !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                border-radius: 12px !important;
                padding-top: 15px !important;
                margin-top: 8px !important;
                margin-bottom: 8px !important;
            }
            CloudStatusWidget::title {
                subcontrol-origin: margin !important;
                left: 15px !important;
                padding: 0 10px 0 10px !important;
                color: #00E5FF !important;
                font-size: 13px !important;
            }
            CloudStatusWidget QGroupBox {
                max-height: 280px !important;
                min-height: 280px !important;
                font-size: 14px !important;
                font-weight: bold !important;
                color: #FFFFFF !important;
                background: rgba(255, 255, 255, 0.1) !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                border-radius: 12px !important;
                padding-top: 15px !important;
                margin-top: 8px !important;
                margin-bottom: 8px !important;
            }
            CloudStatusWidget QGroupBox::title {
                subcontrol-origin: margin !important;
                left: 15px !important;
                padding: 0 10px 0 10px !important;
                color: #00E5FF !important;
                font-size: 13px !important;
            }
        """)
    def setup_ui(self):
        """Setup the UI for the cloud status widget"""
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 18, 10, 10)
        
        # Create status indicators for each service
        self.indicators = {}
        
        services = [
            ("Backend API", self.config["api"]["base_url"]),
            ("Frontend", self.config["api"]["frontend_url"]),
            ("API Docs", self.config["api"]["docs_url"])
        ]
        
        for service_name, url in services:
            indicator = StatusIndicator(service_name)
            self.indicators[service_name] = indicator
            layout.addWidget(indicator)
            
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)
        
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setToolTip("Status aktualisieren")
        self.refresh_button.setFixedSize(30, 30)
        self.refresh_button.clicked.connect(self.manual_refresh)
        self.refresh_button.setStyleSheet("""
            CloudStatusWidget QPushButton[class="refresh"] {
                background: rgba(0, 229, 255, 0.15) !important;
                border: 1px solid rgba(0, 229, 255, 0.3) !important;
                border-radius: 6px !important;
                color: #00E5FF !important;
                font-weight: bold !important;
                font-size: 11px !important;
                max-height: 30px !important;
                min-height: 30px !important;
                max-width: 30px !important;
                min-width: 30px !important;
            }
            CloudStatusWidget QPushButton[class="refresh"]:hover {
                background: rgba(0, 229, 255, 0.25) !important;
                border-color: rgba(0, 229, 255, 0.5) !important;
            }
            CloudStatusWidget QPushButton[class="refresh"]:pressed {
                background: rgba(0, 229, 255, 0.35) !important;
            }
        """)
        self.refresh_button.setProperty("class", "refresh")
        
        self.login_button = QPushButton("🔐 Login")
        self.login_button.setFixedHeight(30)
        self.login_button.clicked.connect(self.login_requested.emit)
        self.login_button.setStyleSheet("""
            CloudStatusWidget QPushButton[class="login"] {
                background: rgba(57, 255, 20, 0.15) !important;
                border: 1px solid rgba(57, 255, 20, 0.3) !important;
                border-radius: 6px !important;
                padding: 4px 10px !important;
                color: #39FF14 !important;
                font-weight: bold !important;
                font-size: 10px !important;
                max-height: 30px !important;
                min-height: 30px !important;
            }
            CloudStatusWidget QPushButton[class="login"]:hover {
                background: rgba(57, 255, 20, 0.25) !important;
                border-color: rgba(57, 255, 20, 0.5) !important;
            }
            CloudStatusWidget QPushButton[class="login"]:pressed {
                background: rgba(57, 255, 20, 0.35) !important;
            }
        """)
        self.login_button.setProperty("class", "login")
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.login_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Overall status label
        self.overall_status = QLabel("🔄 Checking services...")
        self.overall_status.setAlignment(Qt.AlignCenter)
        self.overall_status.setMaximumHeight(25)
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.overall_status.setFont(font)
        self.overall_status.setStyleSheet("""
            CloudStatusWidget QLabel[class="status"] {
                color: #888888 !important;
                font-size: 8pt !important;
                font-weight: bold !important;
                max-height: 25px !important;
                min-height: 20px !important;
                padding: 2px !important;
            }
        """)
        self.overall_status.setProperty("class", "status")
        layout.addWidget(self.overall_status)
        
    def start_status_checking(self):
        """Start background status checking"""
        if self.status_checker:
            self.status_checker.stop()
            
        self.status_checker = CloudStatusChecker(self.config)
        self.status_checker.status_updated.connect(self.update_service_status)
        self.status_checker.start()
        
        # Initial check
        self.manual_refresh()
        
    def stop_status_checking(self):
        """Stop background status checking"""
        if self.status_checker:
            self.status_checker.stop()
            self.status_checker = None
            
    def update_service_status(self, service_name: str, status: str, message: str):
        """Update the status of a specific service"""
        if service_name in self.indicators:
            self.indicators[service_name].update_status(status, message)
            
        # Update overall status
        self.update_overall_status()
        
    def update_overall_status(self):
        """Update the overall status based on individual services"""
        statuses = [indicator.status for indicator in self.indicators.values()]
        
        if all(status == "online" for status in statuses):
            self.overall_status.setText("✅ All services online and ready")
            self.overall_status.setStyleSheet("color: #00FF88;")
        elif any(status == "error" for status in statuses):
            error_count = sum(1 for status in statuses if status == "error")
            self.overall_status.setText(f"❌ {error_count} service(s) offline")
            self.overall_status.setStyleSheet("color: #FF4444;")
        elif any(status == "warning" for status in statuses):
            self.overall_status.setText("⚠️ Some services have warnings")
            self.overall_status.setStyleSheet("color: #FFB800;")
        else:
            self.overall_status.setText("🔄 Checking services...")
            self.overall_status.setStyleSheet("color: #888888;")
            
    def manual_refresh(self):
        """Manually refresh all service statuses"""
        if self.status_checker:
            self.status_checker.check_all_services()
            
    def closeEvent(self, event):
        """Clean up when widget is closed"""
        self.stop_status_checking()
        super().closeEvent(event)
