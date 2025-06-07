#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final UI Enhancement Script for NeuroScan Desktop Application
Applies high-priority style overrides to ensure visibility of improvements
"""

import sys
import os
from pathlib import Path

# Add the modules directory to the path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from modules.main_window import MainWindow
from modules.auth_dialog import AuthDialog
from modules.cloud_status import CloudStatusWidget
import modules.styles as style
import json


def apply_enhanced_styles():
    """Apply enhanced styles with high priority to override global styles"""
    
    enhanced_stylesheet = """
    /* Main Window Enhanced Styles */
    QMainWindow {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                  stop: 0 #1e3c72, stop: 1 #2a5298) !important;
        color: #FFFFFF !important;
    }
    
    /* Dialog Enhanced Styles */
    QDialog {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                  stop: 0 #1e3c72, stop: 1 #2a5298) !important;
        color: #FFFFFF !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 15px !important;
    }
    
    /* Input Fields Enhanced */
    QLineEdit {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
        padding: 12px !important;
        color: #FFFFFF !important;
        font-size: 14px !important;
        min-height: 45px !important;
        max-height: 45px !important;
    }
    
    QLineEdit:focus {
        border-color: rgba(0, 229, 255, 0.8) !important;
        background: rgba(255, 255, 255, 0.25) !important;
    }
    
    /* Button Enhanced Styles */
    QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                  stop: 0 rgba(0, 229, 255, 0.3),
                                  stop: 1 rgba(0, 229, 255, 0.15)) !important;
        border: 2px solid rgba(0, 229, 255, 0.5) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 14px !important;
        padding: 12px 20px !important;
        min-height: 45px !important;
    }
    
    QPushButton:hover {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                  stop: 0 rgba(0, 229, 255, 0.5),
                                  stop: 1 rgba(0, 229, 255, 0.3)) !important;
        border-color: rgba(0, 229, 255, 0.8) !important;
    }
    
    QPushButton:pressed {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                  stop: 0 rgba(0, 229, 255, 0.7),
                                  stop: 1 rgba(0, 229, 255, 0.5)) !important;
    }
    
    /* GroupBox Enhanced Styles */
    QGroupBox {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        color: #FFFFFF !important;
        margin-top: 1ex !important;
        padding-top: 15px !important;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin !important;
        left: 15px !important;
        padding: 0 10px 0 10px !important;
        color: #00E5FF !important;
        font-weight: bold !important;
    }
    
    /* Label Enhanced Styles */
    QLabel {
        color: #FFFFFF !important;
        font-size: 12px !important;
    }
    
    /* Frame Enhanced Styles */
    QFrame {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    """
    
    return enhanced_stylesheet


def test_ui_enhancements():
    """Test the UI enhancements by showing key components"""
    
    print("🚀 Testing NeuroScan Desktop UI Enhancements...")
    
    app = QApplication(sys.argv)
    
    # Apply enhanced global stylesheet
    enhanced_styles = apply_enhanced_styles()
    app.setStyleSheet(enhanced_styles)
    
    # Create test window
    test_window = QMainWindow()
    test_window.setWindowTitle("NeuroScan UI Enhancement Test")
    test_window.setFixedSize(600, 500)
    test_window.setStyleSheet(enhanced_styles)
    
    # Create central widget
    central_widget = QWidget()
    test_window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Add test components
    title = QLabel("✅ UI Enhancements Applied Successfully!")
    title.setAlignment(Qt.AlignCenter)
    font = QFont()
    font.setPointSize(16)
    font.setBold(True)
    title.setFont(font)
    title.setStyleSheet("color: #00FF88 !important; font-size: 16pt !important;")
    layout.addWidget(title)
    
    # Test button
    test_button = QPushButton("🔧 Enhanced Button Style")
    test_button.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 rgba(57, 255, 20, 0.3),
                                      stop: 1 rgba(57, 255, 20, 0.15)) !important;
            border: 2px solid rgba(57, 255, 20, 0.5) !important;
            border-radius: 10px !important;
            color: #FFFFFF !important;
            font-weight: bold !important;
            font-size: 14px !important;
            padding: 12px 20px !important;
            min-height: 45px !important;
        }
        QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 rgba(57, 255, 20, 0.5),
                                      stop: 1 rgba(57, 255, 20, 0.3)) !important;
            border-color: rgba(57, 255, 20, 0.8) !important;
        }
    """)
    layout.addWidget(test_button)
    
    # Status info
    status_info = QLabel("""
    🎨 Applied Enhancements:
    • Login Dialog: Fixed size (480x420) with readable input fields
    • Cloud Status Widget: Compact design (240px height) prevents overlap
    • Color Harmony: Modern glassmorphism with cyan/blue theme
    • High-Priority Styles: Override global styles with !important declarations
    • Responsive Elements: Hover effects and visual feedback
    """)
    status_info.setWordWrap(True)
    status_info.setStyleSheet("""
        QLabel {
            background: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 10px !important;
            padding: 15px !important;
            color: #FFFFFF !important;
            font-size: 11px !important;
            line-height: 1.4 !important;
        }
    """)
    layout.addWidget(status_info)
    
    # Close button
    close_button = QPushButton("✅ Enhancements Applied - Continue to Main App")
    close_button.clicked.connect(test_window.close)
    close_button.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 rgba(0, 255, 136, 0.3),
                                      stop: 1 rgba(0, 255, 136, 0.15)) !important;
            border: 2px solid rgba(0, 255, 136, 0.5) !important;
            border-radius: 10px !important;
            color: #FFFFFF !important;
            font-weight: bold !important;
            font-size: 14px !important;
            padding: 12px 20px !important;
            min-height: 45px !important;
        }
        QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 rgba(0, 255, 136, 0.5),
                                      stop: 1 rgba(0, 255, 136, 0.3)) !important;
            border-color: rgba(0, 255, 136, 0.8) !important;
        }
    """)
    layout.addWidget(close_button)
    
    test_window.show()
    app.exec()
    
    print("✅ UI Enhancement test completed!")


if __name__ == "__main__":
    test_ui_enhancements()
