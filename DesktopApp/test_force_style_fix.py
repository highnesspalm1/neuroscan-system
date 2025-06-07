#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script with Force Style Application
This script specifically tests the forced style application approach.
"""

import sys
import os
from pathlib import Path

# Add the DesktopApp directory to the Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QDialog
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPalette, QColor

# Import the modules
from modules.auth_dialog import AuthDialog
from modules.cloud_status import CloudStatusWidget
from modules.api_manager import APIManager
from force_style_fix import apply_immediate_forced_styles, force_auth_dialog_styles, force_cloud_status_styles

# Sample configuration
CONFIG = {
    "api": {
        "base_url": "https://api.neuroscan.example.com",
        "frontend_url": "https://app.neuroscan.example.com", 
        "docs_url": "https://docs.neuroscan.example.com",
        "timeout": 30,
        "max_retries": 3
    }
}


class TestMainWindow(QMainWindow):
    """Test main window to display the enhanced widgets"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeuroScan UI Test - Force Style Fix")
        self.setGeometry(100, 100, 800, 600)
        
        # Set up central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Apply a simple dark theme to test contrast
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
            }
        """)
        
        # Create cloud status widget
        print("🔧 Creating CloudStatusWidget...")
        self.cloud_widget = CloudStatusWidget(CONFIG)
        layout.addWidget(self.cloud_widget)
        
        # Apply forced styles immediately after creation
        print("🎨 Applying forced styles to CloudStatusWidget...")
        force_cloud_status_styles(self.cloud_widget)
        
        # Create API manager for auth dialog
        self.api_manager = APIManager(CONFIG)
        
        # Button to show auth dialog
        from PySide6.QtWidgets import QPushButton
        auth_button = QPushButton("📝 Test Auth Dialog")
        auth_button.clicked.connect(self.show_auth_dialog)
        auth_button.setFixedHeight(40)
        layout.addWidget(auth_button)
        
        print("✅ Test window initialized")
    
    def show_auth_dialog(self):
        """Show the authentication dialog with forced styles"""
        print("🔧 Creating AuthDialog...")
        dialog = AuthDialog(self.api_manager, self)
        
        print("🎨 Applying forced styles to AuthDialog...")
        force_auth_dialog_styles(dialog)
        
        # Show dialog
        dialog.exec()


def main():
    """Main function to run the test"""
    print("🚀 Starting NeuroScan UI Force Style Test...")
    
    # Create application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern style
    
    # Set application-wide dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(45, 45, 45))
    palette.setColor(QPalette.AlternateBase, QColor(60, 60, 60))
    palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    # Create and show test window
    window = TestMainWindow()
    window.show()
    
    # Additional delayed style application
    def apply_delayed_styles():
        print("🔧 Applying delayed forced styles...")
        force_cloud_status_styles(window.cloud_widget)
        print("✅ Delayed forced styles applied")
    
    QTimer.singleShot(200, apply_delayed_styles)
    
    print("✨ UI Test window displayed!")
    print("💡 Test the following:")
    print("   1. Cloud Status Widget should be compact (240px height)")
    print("   2. Cloud Status Widget should have blue glassmorphism styling")
    print("   3. Click 'Test Auth Dialog' to test login dialog")
    print("   4. Auth Dialog should be 480x420 with readable input fields")
    print("   5. Auth Dialog should have glassmorphism styling")
    
    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
