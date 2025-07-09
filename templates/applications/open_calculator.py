"""
Template: open_calculator.py
Description: Opens the system calculator
Author: System
Platform: Cross-platform
Category: Applications
"""

import subprocess
import platform


def execute():
    """
    Main execution function - opens the system calculator.
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        subprocess.run(["open", "-a", "Calculator"])
    elif system == "Linux":
        # Try different calculator applications
        calculators = ["gnome-calculator", "kcalc", "xcalc", "galculator"]
        for calc in calculators:
            try:
                subprocess.run([calc])
                return
            except FileNotFoundError:
                continue
    elif system == "Windows":
        subprocess.run(["calc.exe"])


def get_metadata():
    """Returns script metadata."""
    return {
        "name": "Open Calculator",
        "description": "Opens the system calculator application",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "application",
        "version": "1.0",
        "author": "System"
    }


def is_supported():
    """Check if script is supported on current OS."""
    return platform.system() in get_metadata()["supported_os"]