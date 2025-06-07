#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Force Style Application - Direct Style Override for NeuroScan Desktop
This approach bypasses the global stylesheet hierarchy by applying styles directly after widget creation.
"""

from PySide6.QtWidgets import QWidget, QDialog, QApplication
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPalette, QColor


def force_auth_dialog_styles(dialog):
    """Force apply styles to authentication dialog"""
    print("🎨 Forcing auth dialog styles...")
    
    # Set dialog size first
    dialog.setFixedSize(480, 420)
    dialog.setMinimumSize(480, 420)
    
    # Apply direct stylesheet that overrides global styles
    auth_style = """
    QDialog {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(30, 35, 41, 0.95),
                   stop:1 rgba(42, 45, 53, 0.95));
        border: 2px solid rgba(100, 200, 255, 0.3);
        border-radius: 15px;
        min-width: 480px;
        min-height: 420px;
    }
    
    /* Input Fields - Direct targeting */
    QLineEdit {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px solid rgba(100, 200, 255, 0.5) !important;
        border-radius: 8px !important;
        padding: 12px 15px !important;
        font-size: 14px !important;
        color: #FFFFFF !important;
        min-height: 45px !important;
        max-height: 45px !important;
    }
    
    QLineEdit:focus {
        border: 2px solid #64C8FF !important;
        background: rgba(255, 255, 255, 0.15) !important;
    }
    
    /* Buttons - Direct targeting */
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                   stop:0 #64C8FF, stop:1 #4A9EFF) !important;
        border: none !important;
        border-radius: 8px !important;
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 14px !important;
        padding: 12px 24px !important;
        min-height: 45px !important;
    }
    
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                   stop:0 #74D8FF, stop:1 #5AAFFF) !important;
    }
    
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                   stop:0 #54B8FF, stop:1 #3A8EFF) !important;
    }
    
    /* Labels */
    QLabel {
        color: #FFFFFF !important;
        font-size: 14px !important;
    }
    """
    
    dialog.setStyleSheet(auth_style)
    
    # Force update and repaint
    dialog.update()
    dialog.repaint()
    
    print("✅ Auth dialog styles applied")


def force_cloud_status_styles(widget):
    """Force apply styles to cloud status widget"""
    print("🎨 Forcing cloud status widget styles...")
    
    # Set widget size constraints
    widget.setFixedHeight(240)
    widget.setMaximumHeight(240)
    
    # Apply direct stylesheet
    cloud_style = """
    /* Main Widget */
    QWidget {
        background: rgba(30, 35, 41, 0.8) !important;
        border: 1px solid rgba(100, 200, 255, 0.3) !important;
        border-radius: 12px !important;
        max-height: 240px !important;
    }
    
    /* Group Box */
    QGroupBox {
        font-weight: bold !important;
        font-size: 16px !important;   
        color: #64C8FF !important;
        border: 2px solid rgba(100, 200, 255, 0.3) !important;
        border-radius: 8px !important;
        margin-top: 10px !important;
        padding-top: 10px !important;
        background: rgba(42, 45, 53, 0.6) !important;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin !important;
        left: 10px !important;
        padding: 0 8px 0 8px !important;
    }
    
    /* Status Indicators */
    QFrame {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(100, 200, 255, 0.2) !important;
        border-radius: 6px !important;
        margin: 2px !important;
        max-height: 50px !important;
    }
    
    /* Buttons */
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                   stop:0 rgba(100, 200, 255, 0.8),
                   stop:1 rgba(74, 158, 255, 0.8)) !important;
        border: 1px solid rgba(100, 200, 255, 0.5) !important;
        border-radius: 6px !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        padding: 8px 16px !important;
        max-height: 35px !important;
    }
    
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                   stop:0 rgba(116, 216, 255, 0.9),
                   stop:1 rgba(90, 175, 255, 0.9)) !important;
    }
    
    /* Labels */
    QLabel {
        color: #FFFFFF !important;
        background: transparent !important;
    }
    """
    
    widget.setStyleSheet(cloud_style)
    
    # Force update and repaint
    widget.update()
    widget.repaint()
    
    print("✅ Cloud status widget styles applied")


def apply_forced_styles_after_show(main_window):
    """Apply forced styles after the main window is shown"""
    def delayed_style_application():
        print("🚀 Applying forced styles after window show...")
        
        # Find and style auth dialog if it exists
        for child in main_window.findChildren(QDialog):
            if hasattr(child, 'username_input'):  # Auth dialog identifier
                force_auth_dialog_styles(child)
        
        # Find and style cloud status widget
        for child in main_window.findChildren(QWidget):
            if child.objectName() == "CloudStatusWidget" or "cloud" in child.objectName().lower():
                force_cloud_status_styles(child)
        
        print("✅ All forced styles applied")
    
    # Apply styles with a small delay to ensure widgets are fully initialized
    QTimer.singleShot(100, delayed_style_application)


def apply_immediate_forced_styles(widget, widget_type="unknown"):
    """Apply forced styles immediately to a specific widget"""
    print(f"🎯 Applying immediate forced styles to {widget_type}...")
    
    try:
        if "auth" in widget_type.lower() or "dialog" in widget_type.lower():
            force_auth_dialog_styles(widget)
        elif "cloud" in widget_type.lower() or "status" in widget_type.lower():
            force_cloud_status_styles(widget)
        else:
            print(f"⚠️ Unknown widget type: {widget_type}")
            
    except Exception as e:
        print(f"❌ Error applying forced styles: {e}")


if __name__ == "__main__":
    print("🔧 Force Style Fix Module Loaded")
