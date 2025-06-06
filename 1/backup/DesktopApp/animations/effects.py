#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Animations Module for NeuroScan Manager
Smooth transitions and effects with glassmorphism
"""

from PySide6.QtCore import (
    QPropertyAnimation, QEasingCurve, QRect, QPoint, QSize,
    QParallelAnimationGroup, QSequentialAnimationGroup, QTimer,
    pyqtProperty, Signal, QObject, QAbstractAnimation
)
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PySide6.QtGui import QColor
from typing import Optional, Callable


class AnimationManager(QObject):
    """Central animation manager for coordinating effects"""
    
    def __init__(self):
        super().__init__()
        self.animations = []
        self.enabled = True
    
    def set_enabled(self, enabled: bool):
        """Enable or disable animations globally"""
        self.enabled = enabled
    
    def add_animation(self, animation: QPropertyAnimation):
        """Add animation to manager"""
        self.animations.append(animation)
        animation.finished.connect(lambda: self.remove_animation(animation))
    
    def remove_animation(self, animation: QPropertyAnimation):
        """Remove animation from manager"""
        if animation in self.animations:
            self.animations.remove(animation)
    
    def stop_all(self):
        """Stop all running animations"""
        for animation in self.animations[:]:
            animation.stop()
            self.remove_animation(animation)


class FadeAnimation:
    """Fade in/out animation utility"""
    
    @staticmethod
    def fade_in(widget: QWidget, duration: int = 300, callback: Optional[Callable] = None) -> QPropertyAnimation:
        """Fade in widget"""
        # Ensure widget has opacity effect
        if not widget.graphicsEffect():
            effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(effect)
        
        effect = widget.graphicsEffect()
        effect.setOpacity(0.0)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        if callback:
            animation.finished.connect(callback)
        
        animation.start()
        return animation
    
    @staticmethod
    def fade_out(widget: QWidget, duration: int = 300, callback: Optional[Callable] = None) -> QPropertyAnimation:
        """Fade out widget"""
        # Ensure widget has opacity effect
        if not widget.graphicsEffect():
            effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(effect)
        
        effect = widget.graphicsEffect()
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(effect.opacity())
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        if callback:
            animation.finished.connect(callback)
        
        animation.start()
        return animation


class SlideAnimation:
    """Slide animation utility"""
    
    @staticmethod
    def slide_in_from_left(widget: QWidget, duration: int = 400) -> QPropertyAnimation:
        """Slide widget in from left"""
        start_pos = widget.geometry()
        start_pos.moveLeft(-widget.width())
        
        end_pos = widget.geometry()
        
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.OutQuart)
        
        widget.setGeometry(start_pos)
        animation.start()
        return animation
    
    @staticmethod
    def slide_in_from_right(widget: QWidget, duration: int = 400) -> QPropertyAnimation:
        """Slide widget in from right"""
        parent_width = widget.parent().width() if widget.parent() else 1920
        
        start_pos = widget.geometry()
        start_pos.moveLeft(parent_width)
        
        end_pos = widget.geometry()
        
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.OutQuart)
        
        widget.setGeometry(start_pos)
        animation.start()
        return animation
    
    @staticmethod
    def slide_in_from_top(widget: QWidget, duration: int = 400) -> QPropertyAnimation:
        """Slide widget in from top"""
        start_pos = widget.geometry()
        start_pos.moveTop(-widget.height())
        
        end_pos = widget.geometry()
        
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.OutQuart)
        
        widget.setGeometry(start_pos)
        animation.start()
        return animation
    
    @staticmethod
    def slide_in_from_bottom(widget: QWidget, duration: int = 400) -> QPropertyAnimation:
        """Slide widget in from bottom"""
        parent_height = widget.parent().height() if widget.parent() else 1080
        
        start_pos = widget.geometry()
        start_pos.moveTop(parent_height)
        
        end_pos = widget.geometry()
        
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.OutQuart)
        
        widget.setGeometry(start_pos)
        animation.start()
        return animation


class ScaleAnimation:
    """Scale animation utility"""
    
    @staticmethod
    def scale_in(widget: QWidget, duration: int = 300) -> QPropertyAnimation:
        """Scale widget in from center"""
        center = widget.geometry().center()
        
        start_rect = QRect(center.x(), center.y(), 0, 0)
        end_rect = widget.geometry()
        
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        animation.setEasingCurve(QEasingCurve.OutBack)
        
        widget.setGeometry(start_rect)
        animation.start()
        return animation
    
    @staticmethod
    def scale_out(widget: QWidget, duration: int = 300, callback: Optional[Callable] = None) -> QPropertyAnimation:
        """Scale widget out to center"""
        center = widget.geometry().center()
        
        start_rect = widget.geometry()
        end_rect = QRect(center.x(), center.y(), 0, 0)
        
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        animation.setEasingCurve(QEasingCurve.InBack)
        
        if callback:
            animation.finished.connect(callback)
        
        animation.start()
        return animation


class PulseAnimation:
    """Pulse animation for highlighting"""
    
    def __init__(self, widget: QWidget, duration: int = 1000):
        self.widget = widget
        self.duration = duration
        self.animation_group = QSequentialAnimationGroup()
        self.running = False
        
        # Create opacity effect if not exists
        if not widget.graphicsEffect():
            effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(effect)
        
        self.setup_animation()
    
    def setup_animation(self):
        """Setup pulse animation sequence"""
        effect = self.widget.graphicsEffect()
        
        # Fade out
        fade_out = QPropertyAnimation(effect, b"opacity")
        fade_out.setDuration(self.duration // 2)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.3)
        fade_out.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Fade in
        fade_in = QPropertyAnimation(effect, b"opacity")
        fade_in.setDuration(self.duration // 2)
        fade_in.setStartValue(0.3)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.InOutQuad)
        
        self.animation_group.addAnimation(fade_out)
        self.animation_group.addAnimation(fade_in)
        self.animation_group.setLoopCount(-1)  # Infinite loop
    
    def start(self):
        """Start pulsing"""
        if not self.running:
            self.running = True
            self.animation_group.start()
    
    def stop(self):
        """Stop pulsing"""
        if self.running:
            self.running = False
            self.animation_group.stop()
            # Reset opacity
            effect = self.widget.graphicsEffect()
            if effect:
                effect.setOpacity(1.0)


class GlowAnimation:
    """Glow effect animation"""
    
    def __init__(self, widget: QWidget):
        self.widget = widget
        self.original_style = widget.styleSheet()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_glow)
        self.glow_intensity = 0
        self.glow_direction = 1
        self.running = False
    
    def start(self, color: str = "#00E5FF"):
        """Start glow animation"""
        if not self.running:
            self.running = True
            self.color = color
            self.timer.start(50)  # 50ms intervals
    
    def stop(self):
        """Stop glow animation"""
        if self.running:
            self.running = False
            self.timer.stop()
            self.widget.setStyleSheet(self.original_style)
    
    def update_glow(self):
        """Update glow effect"""
        self.glow_intensity += self.glow_direction * 5
        
        if self.glow_intensity >= 100:
            self.glow_intensity = 100
            self.glow_direction = -1
        elif self.glow_intensity <= 0:
            self.glow_intensity = 0
            self.glow_direction = 1
        
        alpha = self.glow_intensity / 100.0
        glow_style = f"""
            border: 2px solid rgba({self._hex_to_rgb(self.color)}, {alpha});
            box-shadow: 0 0 20px rgba({self._hex_to_rgb(self.color)}, {alpha * 0.5});
        """
        
        self.widget.setStyleSheet(self.original_style + glow_style)
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB string"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"{rgb[0]}, {rgb[1]}, {rgb[2]}"


class BounceAnimation:
    """Bounce animation for buttons"""
    
    @staticmethod
    def bounce_click(widget: QWidget) -> QSequentialAnimationGroup:
        """Create bounce click animation"""
        original_size = widget.size()
        
        # Scale down
        scale_down = QPropertyAnimation(widget, b"size")
        scale_down.setDuration(100)
        scale_down.setStartValue(original_size)
        scale_down.setEndValue(QSize(
            int(original_size.width() * 0.95),
            int(original_size.height() * 0.95)
        ))
        scale_down.setEasingCurve(QEasingCurve.OutQuad)
        
        # Scale back up
        scale_up = QPropertyAnimation(widget, b"size")
        scale_up.setDuration(100)
        scale_up.setStartValue(QSize(
            int(original_size.width() * 0.95),
            int(original_size.height() * 0.95)
        ))
        scale_up.setEndValue(original_size)
        scale_up.setEasingCurve(QEasingCurve.OutBounce)
        
        animation_group = QSequentialAnimationGroup()
        animation_group.addAnimation(scale_down)
        animation_group.addAnimation(scale_up)
        
        animation_group.start()
        return animation_group


class LoadingAnimation:
    """Loading spinner animation"""
    
    def __init__(self, widget: QWidget):
        self.widget = widget
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        self.rotation = 0
        self.running = False
    
    def start(self):
        """Start loading animation"""
        if not self.running:
            self.running = True
            self.timer.start(50)  # 50ms intervals for smooth rotation
    
    def stop(self):
        """Stop loading animation"""
        if self.running:
            self.running = False
            self.timer.stop()
            self.rotation = 0
            self.widget.update()
    
    def rotate(self):
        """Rotate the widget"""
        self.rotation = (self.rotation + 10) % 360
        
        # Apply rotation transformation
        transform_style = f"transform: rotate({self.rotation}deg);"
        current_style = self.widget.styleSheet()
        
        # Remove old transform
        lines = current_style.split('\n')
        filtered_lines = [line for line in lines if 'transform:' not in line]
        new_style = '\n'.join(filtered_lines) + f"\n{transform_style}"
        
        self.widget.setStyleSheet(new_style)


class PageTransition:
    """Page transition animations for tab changes"""
    
    @staticmethod
    def slide_transition(old_widget: QWidget, new_widget: QWidget, direction: str = "left") -> QParallelAnimationGroup:
        """Create slide transition between widgets"""
        parent = old_widget.parent()
        if not parent:
            return None
        
        parent_width = parent.width()
        
        # Setup new widget position
        if direction == "left":
            new_start_x = parent_width
            old_end_x = -parent_width
        else:  # right
            new_start_x = -parent_width
            old_end_x = parent_width
        
        # Old widget animation
        old_start_pos = old_widget.geometry()
        old_end_pos = QRect(old_end_x, old_start_pos.y(), old_start_pos.width(), old_start_pos.height())
        
        old_animation = QPropertyAnimation(old_widget, b"geometry")
        old_animation.setDuration(300)
        old_animation.setStartValue(old_start_pos)
        old_animation.setEndValue(old_end_pos)
        old_animation.setEasingCurve(QEasingCurve.OutQuart)
        
        # New widget animation
        new_start_pos = QRect(new_start_x, old_start_pos.y(), old_start_pos.width(), old_start_pos.height())
        new_end_pos = old_start_pos
        
        new_animation = QPropertyAnimation(new_widget, b"geometry")
        new_animation.setDuration(300)
        new_animation.setStartValue(new_start_pos)
        new_animation.setEndValue(new_end_pos)
        new_animation.setEasingCurve(QEasingCurve.OutQuart)
        
        # Setup new widget
        new_widget.setGeometry(new_start_pos)
        new_widget.show()
        
        # Parallel animation group
        animation_group = QParallelAnimationGroup()
        animation_group.addAnimation(old_animation)
        animation_group.addAnimation(new_animation)
        
        # Hide old widget when done
        animation_group.finished.connect(lambda: old_widget.hide())
        
        animation_group.start()
        return animation_group


class CounterAnimation:
    """Animated counter for statistics"""
    
    def __init__(self, label_widget, duration: int = 1000):
        self.label = label_widget
        self.duration = duration
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_counter)
        self.start_value = 0
        self.end_value = 0
        self.current_value = 0
        self.steps = 0
        self.current_step = 0
    
    def animate_to(self, target_value: int):
        """Animate counter to target value"""
        if self.timer.isActive():
            self.timer.stop()
        
        self.start_value = self.current_value
        self.end_value = target_value
        self.steps = max(1, abs(target_value - self.start_value))
        self.current_step = 0
        
        # Calculate interval for smooth animation
        interval = max(1, self.duration // self.steps)
        self.timer.start(interval)
    
    def update_counter(self):
        """Update counter value"""
        progress = self.current_step / self.steps
        eased_progress = self.ease_out_cubic(progress)
        
        self.current_value = int(self.start_value + (self.end_value - self.start_value) * eased_progress)
        self.label.setText(str(self.current_value))
        
        self.current_step += 1
        
        if self.current_step >= self.steps:
            self.current_value = self.end_value
            self.label.setText(str(self.end_value))
            self.timer.stop()
    
    def ease_out_cubic(self, t: float) -> float:
        """Cubic easing out function"""
        return 1 - pow(1 - t, 3)


# Global animation manager instance
animation_manager = AnimationManager()


def animate_widget_entrance(widget: QWidget, animation_type: str = "fade"):
    """Convenience function to animate widget entrance"""
    if not animation_manager.enabled:
        return
    
    if animation_type == "fade":
        return FadeAnimation.fade_in(widget)
    elif animation_type == "slide_left":
        return SlideAnimation.slide_in_from_left(widget)
    elif animation_type == "slide_right":
        return SlideAnimation.slide_in_from_right(widget)
    elif animation_type == "slide_top":
        return SlideAnimation.slide_in_from_top(widget)
    elif animation_type == "slide_bottom":
        return SlideAnimation.slide_in_from_bottom(widget)
    elif animation_type == "scale":
        return ScaleAnimation.scale_in(widget)


def animate_button_click(button: QWidget):
    """Convenience function to animate button clicks"""
    if not animation_manager.enabled:
        return
    
    return BounceAnimation.bounce_click(button)
