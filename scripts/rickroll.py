"""
Script: rickroll.py
Description: Opens Rick Roll video in default browser
Author: System
Platform: Cross-platform
"""

import webbrowser
import platform


def execute():
    """
    Main execution function - opens Rick Roll video.
    
    This function opens the classic Rick Roll video in the default browser.
    Use with caution - this is a prank script! 😄
    """
    rick_roll_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        webbrowser.open(rick_roll_url)
    except Exception:
        # Fallback to system-specific commands
        system = platform.system()
        
        if system == "Darwin":  # macOS
            import subprocess
            subprocess.run(["open", rick_roll_url])
        elif system == "Linux":
            import subprocess
            subprocess.run(["xdg-open", rick_roll_url])
        elif system == "Windows":
            import subprocess
            subprocess.run(["start", rick_roll_url], shell=True)


def get_metadata():
    """
    Returns script metadata.
    
    Returns:
        dict: Script metadata including name, description, and compatibility
    """
    return {
        "name": "Rick Roll",
        "description": "Opens the classic Rick Roll video (prank script)",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "fun",
        "version": "1.0",
        "author": "System",
        "warning": "This is a prank script - use responsibly!"
    }


def is_supported():
    """
    Check if script is supported on current OS.
    
    Returns:
        bool: True if script is supported on current OS, False otherwise
    """
    return platform.system() in get_metadata()["supported_os"]