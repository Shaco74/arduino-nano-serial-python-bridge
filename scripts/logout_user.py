"""
Script: logout_user.py
Description: Logs out the current user
Author: System
Platform: Cross-platform
"""

import subprocess
import platform


def execute():
    """
    Main execution function - logs out the current user.
    
    This function logs out the current user from the system.
    The implementation varies by operating system.
    
    Warning: This will close all applications and log out the user!
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        subprocess.run([
            "osascript", "-e", 
            'tell application "System Events" to log out'
        ])
    elif system == "Linux":
        # Try different logout commands
        try:
            subprocess.run(["gnome-session-quit", "--logout", "--no-prompt"])
        except FileNotFoundError:
            try:
                subprocess.run(["loginctl", "terminate-user", "$USER"])
            except FileNotFoundError:
                subprocess.run(["pkill", "-KILL", "-u", "$USER"])
    elif system == "Windows":
        subprocess.run(["shutdown", "/l", "/f"])


def get_metadata():
    """
    Returns script metadata.
    
    Returns:
        dict: Script metadata including name, description, and compatibility
    """
    return {
        "name": "Logout User",
        "description": "Logs out the current user (WARNING: Closes all applications)",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "system",
        "version": "1.0",
        "author": "System",
        "warning": "This will close all applications and log out the user!"
    }


def is_supported():
    """
    Check if script is supported on current OS.
    
    Returns:
        bool: True if script is supported on current OS, False otherwise
    """
    return platform.system() in get_metadata()["supported_os"]