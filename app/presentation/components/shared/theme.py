"""Timetable System theme configuration and component defaults.

This module defines the timetable system brand colors and global component defaults
using Faststrap's theming system.
"""

from faststrap import create_theme, set_component_defaults


# Timetable System Brand Colors (from design spec)
TIMETABLE_THEME = create_theme(
    primary="#2C3E50",      # Primary Dark - Navbar, headers, primary buttons
    secondary="#3498DB",    # Primary Blue - Links, active states, call-to-action
    success="#27AE60",      # Success Green - Success messages, generate button
    danger="#E74C3C",       # Danger Red - Errors, conflict indicators, delete actions
    warning="#F39C12",      # Warning Orange - Warnings, pending actions
    light="#ECF0F1",        # Light Gray - Backgrounds, table alternating rows
    dark="#2C3E50"          # Dark - Text, navbar
)


def setup_timetable_defaults():
    """Configure global component defaults for timetable application.
    
    This ensures consistent styling across all components without
    needing to specify variants/sizes repeatedly.
    """
    # Buttons
    set_component_defaults("Button", variant="primary", size="md")
    
    # Inputs
    set_component_defaults("Input", size="md")
    
    # Cards
    set_component_defaults("Card", header_cls="bg-light border-bottom")
    
    # Badges
    set_component_defaults("Badge", pill=True)
    
    # Alerts
    set_component_defaults("Alert", dismissible=True)
    
    # Progress bars
    set_component_defaults("Progress", variant="success", height="12px")
    
    # Tables
    set_component_defaults("Table", striped=True, hover=True, responsive=True)


# Color constants for direct use
COLORS = {
    "primary": "#2C3E50",
    "secondary": "#3498DB",
    "success": "#27AE60",
    "danger": "#E74C3C",
    "warning": "#F39C12",
    "light": "#ECF0F1",
    "dark": "#2C3E50",
    "text_primary": "#2C3E50",
    "text_secondary": "#7F8C8D"
}
