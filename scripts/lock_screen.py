"""
Script: lock_screen.py
Description: Locks the screen
Author: System
Platform: Cross-platform
"""

import subprocess
import platform


def execute():
    """
    Main execution function - locks the screen.
    
    This function locks the screen/desktop, requiring the user to enter
    their password to unlock it.
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        subprocess.run([
            "osascript", "-e", 
            'tell application "System Events" to keystroke "q" using {control down, command down}'
        ])
    elif system == "Linux":
        # Try different lock commands
        try:
            subprocess.run(["gnome-screensaver-command", "--lock"])
        except FileNotFoundError:
            try:
                subprocess.run(["xdg-screensaver", "lock"])
            except FileNotFoundError:
                try:
                    subprocess.run(["dm-tool", "lock"])
                except FileNotFoundError:
                    subprocess.run(["xset", "s", "activate"])
    elif system == "Windows":
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])


def get_metadata():
    """
    Returns script metadata.
    
    Returns:
        dict: Script metadata including name, description, and compatibility
    """
    return {
        "name": "Lock Screen",
        "description": "Locks the screen requiring password to unlock",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "system",
        "version": "1.0",
        "author": "System"
    }


def is_supported():
    """
    Check if script is supported on current OS.
    
    Returns:
        bool: True if script is supported on current OS, False otherwise
    """
    return platform.system() in get_metadata()["supported_os"]