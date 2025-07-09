"""
Script: screenshot.py
Description: Takes a screenshot
Author: System
Platform: Cross-platform
"""

import subprocess
import platform
import os
from datetime import datetime


def execute():
    """
    Main execution function - takes a screenshot.
    
    This function captures a screenshot of the current screen and saves it
    to the desktop or a screenshots folder.
    """
    system = platform.system()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if system == "Darwin":  # macOS
        # Use macOS built-in screenshot tool
        desktop_path = os.path.expanduser("~/Desktop")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(desktop_path, filename)
        
        subprocess.run([
            "screencapture", "-x", filepath
        ])
    elif system == "Linux":
        # Try different screenshot tools
        desktop_path = os.path.expanduser("~/Desktop")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(desktop_path, filename)
        
        try:
            subprocess.run(["gnome-screenshot", "-f", filepath])
        except FileNotFoundError:
            try:
                subprocess.run(["scrot", filepath])
            except FileNotFoundError:
                try:
                    subprocess.run(["import", "-window", "root", filepath])
                except FileNotFoundError:
                    # Use xwd as last resort
                    subprocess.run(["xwd", "-root", "-out", filepath])
    elif system == "Windows":
        # Use Windows built-in screenshot tool
        subprocess.run([
            "powershell", "-Command", 
            f"Add-Type -AssemblyName System.Windows.Forms; "
            f"[System.Windows.Forms.SendKeys]::SendWait('%{{PRTSC}}')"
        ])


def get_metadata():
    """
    Returns script metadata.
    
    Returns:
        dict: Script metadata including name, description, and compatibility
    """
    return {
        "name": "Screenshot",
        "description": "Takes a screenshot and saves it to desktop",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "media",
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