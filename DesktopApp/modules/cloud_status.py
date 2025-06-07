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

# Import the force style fix
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from force_style_fix import force_cloud_status_styles
except ImportError:
    print("⚠️ Force style fix not available")
    def force_cloud_status_styles(widget):
        pass


class StatusIndicator(QFrame):
    """Individual status indicator for a service"""
    
    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name
        self.status = "unknown"
        self.message = "Checking..."
        
        self.setFixedHeight(50)  # Reduced height for more compact look
        self.setFrameStyle(QFrame.Box)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI for the status indicator"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)  # Reduced margins
        layout.setSpacing(8)
        
        # Status icon/circle
        self.status_circle = QLabel("●")
        self.status_circle.setFixedSize(16, 16)
        self.status_circle.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        self.status_circle.setFont(font)
        
        # Service information
        info_layout = QVBoxLayout()
        info_layout.setSpacing(1)
        
        self.name_label = QLabel(self.service_name)
        name_font = QFont()
        name_font.setPointSize(9)  # Slightly smaller font
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        
        self.message_label = QLabel(self.message)
        message_font = QFont()
        message_font.setPointSize(7)  # Smaller font
        self.message_label.setFont(message_font)
        self.message_label.setWordWrap(True)
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.message_label)
        
        # Last updated time
        self.time_label = QLabel("Never")
        time_font = QFont()
        time_font.setPointSize(6)  # Smaller font
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
        self.time_label.setText(current_time)        # Update colors and style based on status
        if status == "online":
            self.status_circle.setStyleSheet("color: #00FF88;")  # Green
            self.setObjectName("StatusIndicatorOnline")
            self.setStyleSheet("""
                QFrame#StatusIndicatorOnline {
                    background: rgba(0, 255, 136, 0.08);
                    border: 1px solid rgba(0, 255, 136, 0.25);
                    border-radius: 8px;
                }
            """)
        elif status == "warning":
            self.status_circle.setStyleSheet("color: #FFB800;")  # Orange
            self.setObjectName("StatusIndicatorWarning")
            self.setStyleSheet("""
                QFrame#StatusIndicatorWarning {
                    background: rgba(255, 184, 0, 0.08);
                    border: 1px solid rgba(255, 184, 0, 0.25);
                    border-radius: 8px;
                }
            """)
        elif status == "error":
            self.status_circle.setStyleSheet("color: #FF4444;")  # Red
            self.setObjectName("StatusIndicatorError")
            self.setStyleSheet("""
                QFrame#StatusIndicatorError {
                    background: rgba(255, 68, 68, 0.08);
                    border: 1px solid rgba(255, 68, 68, 0.25);
                    border-radius: 8px;
                }
            """)
        else:  # unknown
            self.status_circle.setStyleSheet("color: #999999;")  # Gray
            self.setObjectName("StatusIndicatorUnknown")
            self.setStyleSheet("""
                QFrame#StatusIndicatorUnknown {
                    background: rgba(153, 153, 153, 0.08);
                    border: 1px solid rgba(153, 153, 153, 0.25);
                    border-radius: 8px;
                }
            """)


class CloudStatusWidget(QGroupBox):
    """Widget that shows the status of all cloud services"""
    
    login_requested = Signal()
    def __init__(self, config: Dict):
        super().__init__("🌐 Cloud Services Status")
        self.config = config
        self.status_checker = None
        
        # Set fixed dimensions to prevent overlapping - much more compact
        self.setFixedHeight(240)
        self.setMaximumHeight(240)
        
        self.setup_ui()
        self.start_status_checking()
        
        # Apply forced styles to override global styles
        QTimer.singleShot(50, lambda: force_cloud_status_styles(self))
          # Set high-priority widget-specific styles to override global styles
        self.setObjectName("CloudStatusWidget")
        self.setStyleSheet("""
            QGroupBox#CloudStatusWidget {
                max-height: 240px !important;
                min-height: 240px !important;
                font-size: 13px !important;
                font-weight: bold !important;
                color: #FFFFFF !important;
                background: rgba(255, 255, 255, 0.1) !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                border-radius: 10px !important;
                padding-top: 12px !important;
                margin-top: 6px !important;
                margin-bottom: 6px !important;
            }
            QGroupBox#CloudStatusWidget::title {
                subcontrol-origin: margin !important;
                left: 12px !important;
                padding: 0 8px 0 8px !important;
                color: #00E5FF !important;
                font-size: 12px !important;
            }
            QGroupBox#CloudStatusWidget > QPushButton {
                color: #FFFFFF !important;
                font-weight: bold !important;
                font-size: 11px !important;
                border-radius: 5px !important;
            }
            QGroupBox#CloudStatusWidget > QFrame {
                background: rgba(255, 255, 255, 0.08) !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                border-radius: 8px !important;
            }
        """)
        
    def setup_ui(self):
        """Setup the UI for the cloud status widget"""
        layout = QVBoxLayout(self)
        layout.setSpacing(4)  # Reduced spacing
        layout.setContentsMargins(8, 15, 8, 8)  # Reduced margins
        
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
        button_layout.setSpacing(4)
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setToolTip("Status aktualisieren")
        self.refresh_button.setFixedSize(26, 26)  # Smaller buttons
        self.refresh_button.clicked.connect(self.manual_refresh)
        self.refresh_button.setObjectName("RefreshButton")
        self.refresh_button.setStyleSheet("""
            QPushButton#RefreshButton {
                background: rgba(0, 229, 255, 0.15);
                border: 1px solid rgba(0, 229, 255, 0.3);
                border-radius: 5px;
                color: #00E5FF;
                font-weight: bold;
                font-size: 10px;
                max-height: 26px;
                min-height: 26px;
                max-width: 26px;
                min-width: 26px;
            }
            QPushButton#RefreshButton:hover {
                background: rgba(0, 229, 255, 0.25);
                border-color: rgba(0, 229, 255, 0.5);
            }
            QPushButton#RefreshButton:pressed {
                background: rgba(0, 229, 255, 0.35);
            }
        """)
        self.login_button = QPushButton("🔐 Login")
        self.login_button.setFixedHeight(26)  # Smaller button
        self.login_button.clicked.connect(self.login_requested.emit)
        self.login_button.setObjectName("LoginButton")
        self.login_button.setStyleSheet("""
            QPushButton#LoginButton {
                background: rgba(57, 255, 20, 0.15);
                border: 1px solid rgba(57, 255, 20, 0.3);
                border-radius: 5px;
                padding: 3px 8px;
                color: #39FF14;
                font-weight: bold;
                font-size: 9px;
                max-height: 26px;
                min-height: 26px;
            }
            QPushButton#LoginButton:hover {
                background: rgba(57, 255, 20, 0.25);
                border-color: rgba(57, 255, 20, 0.5);
            }
            QPushButton#LoginButton:pressed {
                background: rgba(57, 255, 20, 0.35);
            }
        """)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.login_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
          # Overall status label
        self.overall_status = QLabel("🔄 Checking services...")
        self.overall_status.setAlignment(Qt.AlignCenter)
        self.overall_status.setMaximumHeight(20)  # Smaller height
        font = QFont()
        font.setPointSize(7)  # Smaller font
        font.setBold(True)
        self.overall_status.setFont(font)
        self.overall_status.setObjectName("StatusLabel")
        self.overall_status.setStyleSheet("""
            QLabel#StatusLabel {
                color: #888888;
                font-size: 7pt;
                font-weight: bold;
                max-height: 20px;
                min-height: 18px;
                padding: 1px;
            }
        """)
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
