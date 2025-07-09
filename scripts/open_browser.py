"""
Script: open_browser.py
Description: Opens the default web browser
Author: System
Platform: Cross-platform
"""

import subprocess
import platform
import webbrowser


def execute(url="https://www.google.com"):
    """
    Main execution function - opens the default web browser.
    
    Args:
        url (str): URL to open in the browser. Defaults to Google.
    
    This function opens the default web browser and navigates to the specified URL.
    """
    system = platform.system()
    
    try:
        # Use Python's webbrowser module for cross-platform compatibility
        webbrowser.open(url)
    except Exception:
        # Fallback to system-specific commands
        if system == "Darwin":  # macOS
            subprocess.run(["open", url])
        elif system == "Linux":
            subprocess.run(["xdg-open", url])
        elif system == "Windows":
            subprocess.run(["start", url], shell=True)


def get_metadata():
    """
    Returns script metadata.
    
    Returns:
        dict: Script metadata including name, description, and compatibility
    """
    return {
        "name": "Open Browser",
        "description": "Opens the default web browser with Google",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "application",
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