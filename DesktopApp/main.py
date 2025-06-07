#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuroScan Manager - Desktop Application
Copyright (c) 2025 NeuroCompany
MIT License
"""

import sys
import os
import json
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QStyleOptionViewItem
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPalette, QColor

# Import our modules
from modules.database import DatabaseManager
from modules.main_window import MainWindow
from modules.styles import GlassmorphismStyle

# Import force style fix
from force_style_fix import apply_forced_styles_after_show


class NeuroScanApp(QApplication):
    """Main Application Class with Glassmorphism Styling"""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Load configuration
        self.config = self.load_config()
        
        # Set application properties
        self.setApplicationName(self.config["app_name"])
        self.setApplicationVersion(self.config["version"])
        self.setOrganizationName(self.config["company"])
        
        # Apply glassmorphism style
        self.apply_glassmorphism_style()
        
        # Initialize database
        self.db_manager = DatabaseManager(self.config["database"]["path"])
          # Create main window
        self.main_window = MainWindow(self.config, self.db_manager)
        
        # Apply force styles after window creation
        self.setup_force_styles()
        
    def load_config(self):
        """Load configuration from config.json"""
        config_path = Path(__file__).parent / "config.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default fallback config
            return {
                "app_name": "NeuroScan Manager",
                "version": "1.0.0",
                "company": "NeuroCompany",
                "database": {"path": "neuroscan.db"},
                "ui": {
                    "theme": "glassmorphism_dark",
                    "colors": {
                        "background": "#111820",
                        "accent": "#00E5FF"
                    }
                }
            }
    
    def apply_glassmorphism_style(self):
        """Apply the premium glassmorphism styling"""
        # Set application icon (if available)
        icon_path = Path(__file__).parent / "assets" / "neuroscan-icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Apply custom stylesheet
        style = GlassmorphismStyle(self.config["ui"]["colors"])
        self.setStyleSheet(style.get_stylesheet())
        
        # Set dark palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(self.config["ui"]["colors"]["background"]))
        palette.setColor(QPalette.WindowText, QColor("#FFFFFF"))
        palette.setColor(QPalette.Base, QColor("#1E2329"))
        palette.setColor(QPalette.AlternateBase, QColor("#2A2D35"))
        palette.setColor(QPalette.Text, QColor("#FFFFFF"))
        palette.setColor(QPalette.Button, QColor("#2A2D35"))
        palette.setColor(QPalette.ButtonText, QColor("#FFFFFF"))
        palette.setColor(QPalette.Highlight, QColor(self.config["ui"]["colors"]["accent"]))
        palette.setColor(QPalette.HighlightedText, QColor("#000000"))
        
        self.setPalette(palette)
        
    def setup_force_styles(self):
        """Setup force style application for enhanced visual improvements"""
        # Apply forced styles after the main window is shown
        def apply_on_show():
            apply_forced_styles_after_show(self.main_window)
            
        # Connect to main window show event
        QTimer.singleShot(200, apply_on_show)


def main():
    """Main entry point"""
    # Enable high DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create and run application
    app = NeuroScanApp(sys.argv)
    
    # Show main window
    app.main_window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
