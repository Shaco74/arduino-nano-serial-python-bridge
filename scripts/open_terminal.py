"""
Script: open_terminal.py
Description: Opens terminal and executes a command
Author: System
Platform: Cross-platform
"""

import subprocess
import platform


def execute():
    """
    Main execution function - opens terminal with a greeting message.
    
    This function opens the system terminal and displays a greeting message.
    The implementation varies by operating system.
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        subprocess.run([
            "osascript", "-e", 
            'tell application "Terminal" to do script "echo Hello from Arduino Nano Controller!"'
        ])
    elif system == "Linux":
        # Try different terminal emulators
        try:
            subprocess.run([
                "gnome-terminal", "--", "bash", "-c", 
                "echo 'Hello from Arduino Nano Controller!'; read -p 'Press Enter to close...'"
            ])
        except FileNotFoundError:
            try:
                subprocess.run([
                    "xterm", "-e", "bash", "-c",
                    "echo 'Hello from Arduino Nano Controller!'; read -p 'Press Enter to close...'"
                ])
            except FileNotFoundError:
                subprocess.run([
                    "konsole", "--noclose", "-e", "bash", "-c",
                    "echo 'Hello from Arduino Nano Controller!'"
                ])
    elif system == "Windows":
        subprocess.run([
            "cmd", "/c", "start", "cmd", "/k", 
            "echo Hello from Arduino Nano Controller!"
        ])


def get_metadata():
    """
    Returns script metadata.
    
    Returns:
        dict: Script metadata including name, description, and compatibility
    """
    return {
        "name": "Open Terminal",
        "description": "Opens terminal and displays a greeting message",
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