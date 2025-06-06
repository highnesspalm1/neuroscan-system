#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Animations Package for NeuroScan Manager
"""

from .effects import (
    AnimationManager, FadeAnimation, SlideAnimation, ScaleAnimation,
    PulseAnimation, GlowAnimation, BounceAnimation, LoadingAnimation,
    PageTransition, CounterAnimation, animation_manager,
    animate_widget_entrance, animate_button_click
)

__all__ = [
    'AnimationManager', 'FadeAnimation', 'SlideAnimation', 'ScaleAnimation',
    'PulseAnimation', 'GlowAnimation', 'BounceAnimation', 'LoadingAnimation',
    'PageTransition', 'CounterAnimation', 'animation_manager',
    'animate_widget_entrance', 'animate_button_click'
]
