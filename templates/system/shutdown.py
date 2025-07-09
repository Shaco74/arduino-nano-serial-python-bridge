"""
Template: shutdown.py
Description: Shuts down the system
Author: System
Platform: Cross-platform
Category: System
"""

import subprocess
import platform


def execute():
    """
    Main execution function - shuts down the system.
    
    WARNING: This will shut down the computer immediately!
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        subprocess.run([
            "osascript", "-e", 
            'tell app "System Events" to shut down'
        ])
    elif system == "Linux":
        subprocess.run(["sudo", "shutdown", "-h", "now"])
    elif system == "Windows":
        subprocess.run(["shutdown", "/s", "/t", "0"])


def get_metadata():
    """Returns script metadata."""
    return {
        "name": "Shutdown System",
        "description": "Shuts down the computer (WARNING: Immediate shutdown)",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "system",
        "version": "1.0",
        "author": "System",
        "warning": "This will shut down the computer immediately!"
    }


def is_supported():
    """Check if script is supported on current OS."""
    return platform.system() in get_metadata()["supported_os"]