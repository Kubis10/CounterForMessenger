"""
Base utilities for the CounterForMessenger application.
This module re-exports all utilities to maintain backward compatibility.
"""
from utils.general_utils import set_icon, set_resolution, existing_languages, PREFIX
from utils.theme_manager import ThemeManager

# Re-export all utilities
__all__ = ['set_icon', 'set_resolution', 'existing_languages', 'PREFIX', 'ThemeManager']
