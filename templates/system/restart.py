"""
Template: restart.py
Description: Restarts the system
Author: System
Platform: Cross-platform
Category: System
"""

import subprocess
import platform


def execute():
    """
    Main execution function - restarts the system.
    
    WARNING: This will restart the computer immediately!
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        subprocess.run([
            "osascript", "-e", 
            'tell app "System Events" to restart'
        ])
    elif system == "Linux":
        subprocess.run(["sudo", "reboot"])
    elif system == "Windows":
        subprocess.run(["shutdown", "/r", "/t", "0"])


def get_metadata():
    """Returns script metadata."""
    return {
        "name": "Restart System",
        "description": "Restarts the computer (WARNING: Immediate restart)",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "system",
        "version": "1.0",
        "author": "System",
        "warning": "This will restart the computer immediately!"
    }


def is_supported():
    """Check if script is supported on current OS."""
    return platform.system() in get_metadata()["supported_os"]