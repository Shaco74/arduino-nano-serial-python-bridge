"""
Template: open_notepad.py
Description: Opens the default text editor
Author: System
Platform: Cross-platform
Category: Applications
"""

import subprocess
import platform
import os


def execute():
    """
    Main execution function - opens the default text editor.
    
    This function opens the system's default text editor or notepad.
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        subprocess.run(["open", "-a", "TextEdit"])
    elif system == "Linux":
        # Try different text editors
        editors = ["gedit", "kate", "mousepad", "leafpad", "nano"]
        for editor in editors:
            try:
                subprocess.run([editor])
                return
            except FileNotFoundError:
                continue
        
        # If no GUI editor found, try nano in terminal
        try:
            subprocess.run([
                "gnome-terminal", "--", "bash", "-c", 
                "nano; read -p 'Press Enter to close...'"
            ])
        except FileNotFoundError:
            subprocess.run([
                "xterm", "-e", "bash", "-c", 
                "nano; read -p 'Press Enter to close...'"
            ])
    elif system == "Windows":
        subprocess.run(["notepad.exe"])


def get_metadata():
    """Returns script metadata."""
    return {
        "name": "Open Notepad",
        "description": "Opens the default text editor/notepad",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "application",
        "version": "1.0",
        "author": "System"
    }


def is_supported():
    """Check if script is supported on current OS."""
    return platform.system() in get_metadata()["supported_os"]