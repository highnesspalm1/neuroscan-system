#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Widgets for NeuroScan Manager
Premium Glassmorphism UI Components
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QWidget,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, Signal
from PySide6.QtGui import QFont, QPainter, QPen, QBrush, QColor
from typing import Dict, List
from datetime import datetime, timedelta


class DashboardCard(QFrame):
    """Base dashboard card with glassmorphism effect"""
    
    def __init__(self, title: str, content_widget: QWidget = None):
        super().__init__()
        self.setProperty("class", "panel")
        self.setFixedHeight(200)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel(title)
        title_label.setProperty("class", "subtitle")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # Content
        if content_widget:
            layout.addWidget(content_widget)
        else:
            layout.addStretch()


class StatisticsCard(QFrame):
    """Statistics card with animated counter"""
    
    def __init__(self, title: str, value: str, icon: str, color: str):
        super().__init__()
        self.setProperty("class", "panel")
        self.setFixedHeight(150)
        self.setMinimumWidth(250)
        
        self.current_value = 0
        self.target_value = 0
        self.color = color
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_value)
        
        self.init_ui(title, value, icon)
    
    def init_ui(self, title: str, value: str, icon: str):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        icon_label.setStyleSheet(f"color: {self.color};")
        header_layout.addWidget(icon_label)
        
        header_layout.addStretch()
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        header_layout.addWidget(title_label)
        
        layout.addLayout(header_layout)
        
        # Value
        self.value_label = QLabel("0")
        self.value_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {self.color};")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        layout.addStretch()
    
    def update_value(self, new_value: str):
        """Update the displayed value with animation"""
        try:
            self.target_value = int(new_value)
            if self.target_value != self.current_value:
                self.animation_timer.start(50)  # Update every 50ms
        except ValueError:
            self.value_label.setText(new_value)
    
    def animate_value(self):
        """Animate the value change"""
        if self.current_value < self.target_value:
            step = max(1, (self.target_value - self.current_value) // 10)
            self.current_value = min(self.current_value + step, self.target_value)
        elif self.current_value > self.target_value:
            step = max(1, (self.current_value - self.target_value) // 10)
            self.current_value = max(self.current_value - step, self.target_value)
        
        self.value_label.setText(str(self.current_value))
        
        if self.current_value == self.target_value:
            self.animation_timer.stop()


class RecentActivityWidget(QFrame):
    """Widget showing recent certificate and scan activity"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setProperty("class", "panel")
        
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🕒 Letzte Aktivitäten")
        title_label.setProperty("class", "subtitle")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(30, 30)
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setToolTip("Aktualisieren")
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Activity list
        self.activity_widget = QWidget()
        self.activity_layout = QVBoxLayout(self.activity_widget)
        self.activity_layout.setSpacing(8)
        
        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.activity_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        layout.addWidget(scroll_area)
    
    def refresh_data(self):
        """Refresh activity data"""
        # Clear existing items
        for i in reversed(range(self.activity_layout.count())):
            child = self.activity_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        try:
            # Get recent certificates
            certificates = self.db_manager.get_certificates()
            recent_certs = sorted(certificates, key=lambda x: x['created_at'], reverse=True)[:5]
            
            # Get recent scans
            scan_logs = self.db_manager.get_scan_logs(days=7)
            recent_scans = scan_logs[:5]
            
            # Combine and sort by time
            activities = []
            
            for cert in recent_certs:
                activities.append({
                    'type': 'certificate',
                    'icon': '🎫',
                    'title': f"Zertifikat erstellt: {cert['serial_number'][:15]}...",
                    'subtitle': f"{cert['customer_name']} - {cert['product_name']}",
                    'time': cert['created_at'],
                    'color': '#00E5FF'
                })
            
            for scan in recent_scans:
                activities.append({
                    'type': 'scan',
                    'icon': '📱',
                    'title': f"Scan: {scan['serial_number'][:15]}...",
                    'subtitle': f"IP: {scan.get('ip_address', 'Unbekannt')}",
                    'time': scan['scan_time'],
                    'color': '#39FF14'
                })
            
            # Sort by time (most recent first)
            activities.sort(key=lambda x: x['time'], reverse=True)
            
            # Add activity items
            for activity in activities[:10]:  # Show max 10 items
                self.add_activity_item(activity)
            
            if not activities:
                no_activity_label = QLabel("Keine aktuellen Aktivitäten")
                no_activity_label.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-style: italic;")
                no_activity_label.setAlignment(Qt.AlignCenter)
                self.activity_layout.addWidget(no_activity_label)
            
            self.activity_layout.addStretch()
            
        except Exception as e:
            error_label = QLabel(f"Fehler beim Laden der Aktivitäten: {e}")
            error_label.setStyleSheet("color: #FF6B6B;")
            self.activity_layout.addWidget(error_label)
    
    def add_activity_item(self, activity: Dict):
        """Add an activity item to the list"""
        item_frame = QFrame()
        item_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 5px;
            }
            QFrame:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.2);
            }
        """)
        item_frame.setFixedHeight(60)
        
        item_layout = QHBoxLayout(item_frame)
        item_layout.setContentsMargins(10, 5, 10, 5)
        
        # Icon
        icon_label = QLabel(activity['icon'])
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignCenter)
        item_layout.addWidget(icon_label)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        # Title
        title_label = QLabel(activity['title'])
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_label.setStyleSheet(f"color: {activity['color']};")
        content_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel(activity['subtitle'])
        subtitle_label.setFont(QFont("Segoe UI", 8))
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
        content_layout.addWidget(subtitle_label)
        
        item_layout.addLayout(content_layout)
        
        # Time
        try:
            time_obj = datetime.fromisoformat(activity['time'].replace('Z', '+00:00'))
            time_diff = datetime.now() - time_obj.replace(tzinfo=None)
            
            if time_diff.days > 0:
                time_text = f"{time_diff.days}d"
            elif time_diff.seconds > 3600:
                time_text = f"{time_diff.seconds // 3600}h"
            elif time_diff.seconds > 60:
                time_text = f"{time_diff.seconds // 60}m"
            else:
                time_text = "Jetzt"
        except:
            time_text = "?"
        
        time_label = QLabel(time_text)
        time_label.setFont(QFont("Segoe UI", 8))
        time_label.setStyleSheet("color: rgba(255, 255, 255, 0.5);")
        time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item_layout.addWidget(time_label)
        
        self.activity_layout.addWidget(item_frame)


class ChartWidget(QFrame):
    """Custom chart widget for displaying statistics"""
    
    def __init__(self, title: str, data: List[Dict]):
        super().__init__()
        self.setProperty("class", "panel")
        self.title = title
        self.data = data
        self.setMinimumHeight(250)
    
    def paintEvent(self, event):
        """Custom paint event for drawing charts"""
        super().paintEvent(event)
        
        if not self.data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get drawing area
        rect = self.rect()
        margin = 30
        chart_rect = QRect(margin, margin + 30, rect.width() - 2*margin, rect.height() - 2*margin - 30)
        
        # Draw title
        painter.setPen(QPen(QColor("#FFFFFF")))
        painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
        painter.drawText(rect.x() + margin, rect.y() + 20, self.title)
        
        # Draw simple bar chart
        if self.data:
            max_value = max(item['value'] for item in self.data)
            if max_value > 0:
                bar_width = chart_rect.width() // len(self.data) - 10
                
                for i, item in enumerate(self.data):
                    x = chart_rect.x() + i * (bar_width + 10)
                    height = int((item['value'] / max_value) * chart_rect.height())
                    y = chart_rect.bottom() - height
                    
                    # Draw bar
                    painter.setBrush(QBrush(QColor("#00E5FF")))
                    painter.setPen(QPen(QColor("#00E5FF")))
                    painter.drawRect(x, y, bar_width, height)
                    
                    # Draw label
                    painter.setPen(QPen(QColor("#FFFFFF")))
                    painter.setFont(QFont("Segoe UI", 8))
                    painter.drawText(x, chart_rect.bottom() + 15, str(item['label']))
