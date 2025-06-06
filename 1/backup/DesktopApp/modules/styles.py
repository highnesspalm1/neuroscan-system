#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glassmorphism Style for NeuroScan
Premium UI styling with transparency and blur effects
"""

from typing import Dict


class GlassmorphismStyle:
    """Premium Glassmorphism styling for NeuroScan"""
    
    def __init__(self, colors: Dict[str, str]):
        self.colors = colors
    
    def get_stylesheet(self) -> str:
        """Generate the complete stylesheet for glassmorphism design"""
        return f"""
/* Global Application Styling */
QMainWindow {{
    background-color: {self.colors['background']};
    color: #FFFFFF;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}}

/* Panel Styling (Glassmorphism Effect) */
QFrame.panel {{
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
}}

QFrame.panel:hover {{
    background-color: rgba(255, 255, 255, 0.15);
    border-color: {self.colors['accent']};
    transition: all 0.3s ease;
}}

/* Button Styling */
QPushButton {{
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    color: #FFFFFF;
    font-weight: 600;
    padding: 10px 20px;
    min-height: 16px;
}}

QPushButton:hover {{
    background-color: {self.colors['accent']};
    border-color: {self.colors['accent']};
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
    transform: translateY(-1px);
}}

QPushButton:pressed {{
    background-color: rgba(0, 229, 255, 0.8);
    transform: translateY(0px);
}}

QPushButton:disabled {{
    background-color: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.5);
}}

/* Primary Button (Accent) */
QPushButton.primary {{
    background-color: {self.colors['accent']};
    border-color: {self.colors['accent']};
    font-weight: 700;
}}

QPushButton.primary:hover {{
    background-color: #00D4E6;
    box-shadow: 0 0 30px rgba(0, 229, 255, 0.6);
}}

/* Secondary Button */
QPushButton.secondary {{
    background-color: {self.colors.get('secondary', '#39FF14')};
    border-color: {self.colors.get('secondary', '#39FF14')};
    color: #000000;
}}

QPushButton.secondary:hover {{
    background-color: #32E612;
    box-shadow: 0 0 25px rgba(57, 255, 20, 0.5);
}}

/* Input Fields */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 6px;
    color: #FFFFFF;
    padding: 8px 12px;
    font-size: 14px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {self.colors['accent']};
    background-color: rgba(255, 255, 255, 0.15);
    box-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
}}

QLineEdit::placeholder, QTextEdit::placeholder {{
    color: rgba(255, 255, 255, 0.6);
}}

/* ComboBox */
QComboBox {{
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 6px;
    color: #FFFFFF;
    padding: 8px 12px;
    min-width: 120px;
}}

QComboBox:hover {{
    border-color: {self.colors['accent']};
    background-color: rgba(255, 255, 255, 0.15);
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFISURBVBiVY/j//z8DAwMDw////xkYGBgY/v//z8DAwMDw////DAwMDAz///9nYGBgYPj//z8DAwMDw////xkYGBgY/v//z8DAwMDw////DAwMDAz///9n+A8F////Z2BgYGD4////GRgYGBj+////DAwMDAz///9nYGBgYPj//z8DAwMDw////xkYGBgY/v//z8DAwMDw////DAwMDAz///9nYGBgYPj//z8DAwMDw////xkYGBgY/v//z8DAwMDw////DAwMDAz///9nYGBgYPj//z8DAwMDw////xkYGBgY/v//z8DAwMDw////DAwMDAz///9nYGBgYPj//z8DAwMDw////xkYGBgY/v//z8DAwMDw////DAwMDAz///9nYGBgYPj//z8DAwMDw////xkYGBgY/v//z8DAwMDw////DAwMDAz///9nYGBgYPj//z8DAwMDw////xkYGBgY/v//z8DAwMDw////DA==);
    width: 8px;
    height: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: rgba(30, 35, 41, 0.95);
    border: 1px solid {self.colors['accent']};
    border-radius: 6px;
    color: #FFFFFF;
    selection-background-color: {self.colors['accent']};
}}

/* Table Widget */
QTableWidget {{
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    gridline-color: rgba(255, 255, 255, 0.1);
    color: #FFFFFF;
}}

QTableWidget::item {{
    padding: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}}

QTableWidget::item:selected {{
    background-color: rgba(0, 229, 255, 0.3);
}}

QTableWidget::item:hover {{
    background-color: rgba(255, 255, 255, 0.1);
}}

QHeaderView::section {{
    background-color: rgba(255, 255, 255, 0.1);
    border: none;
    border-bottom: 2px solid {self.colors['accent']};
    color: #FFFFFF;
    font-weight: 600;
    padding: 10px;
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    background-color: rgba(255, 255, 255, 0.05);
}}

QTabBar::tab {{
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-bottom: none;
    color: #FFFFFF;
    padding: 10px 20px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background-color: {self.colors['accent']};
    color: #000000;
    font-weight: 600;
}}

QTabBar::tab:hover:!selected {{
    background-color: rgba(255, 255, 255, 0.15);
}}

/* Progress Bar */
QProgressBar {{
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 6px;
    text-align: center;
    color: #FFFFFF;
}}

QProgressBar::chunk {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
        stop:0 {self.colors['accent']}, 
        stop:1 {self.colors.get('secondary', '#39FF14')});
    border-radius: 6px;
}}

/* Menu Bar */
QMenuBar {{
    background-color: rgba(255, 255, 255, 0.1);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    color: #FFFFFF;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 8px 16px;
}}

QMenuBar::item:selected {{
    background-color: {self.colors['accent']};
    color: #000000;
}}

QMenu {{
    background-color: rgba(30, 35, 41, 0.95);
    border: 1px solid {self.colors['accent']};
    border-radius: 6px;
    color: #FFFFFF;
}}

QMenu::item {{
    padding: 8px 20px;
}}

QMenu::item:selected {{
    background-color: {self.colors['accent']};
    color: #000000;
}}

/* Status Bar */
QStatusBar {{
    background-color: rgba(255, 255, 255, 0.1);
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    color: #FFFFFF;
}}

/* Group Box */
QGroupBox {{
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    margin-top: 10px;
    font-weight: 600;
    color: #FFFFFF;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px 0 8px;
    color: {self.colors['accent']};
}}

/* Scroll Bar */
QScrollBar:vertical {{
    background-color: rgba(255, 255, 255, 0.1);
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {self.colors['accent']};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #00D4E6;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    border: none;
    background: none;
}}

/* Labels */
QLabel {{
    color: #FFFFFF;
}}

QLabel.title {{
    font-size: 24px;
    font-weight: 700;
    color: {self.colors['accent']};
    margin-bottom: 10px;
}}

QLabel.subtitle {{
    font-size: 16px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.8);
}}

QLabel.accent {{
    color: {self.colors['accent']};
    font-weight: 600;
}}

/* Animated Elements */
@keyframes glow {{
    0% {{ box-shadow: 0 0 5px {self.colors['accent']}; }}
    50% {{ box-shadow: 0 0 20px {self.colors['accent']}, 0 0 30px {self.colors['accent']}; }}
    100% {{ box-shadow: 0 0 5px {self.colors['accent']}; }}
}}

.animated-glow {{
    animation: glow 2s infinite;
}}

/* Tool Tips */
QToolTip {{
    background-color: rgba(30, 35, 41, 0.95);
    border: 1px solid {self.colors['accent']};
    border-radius: 6px;
    color: #FFFFFF;
    padding: 8px;
}}
"""
