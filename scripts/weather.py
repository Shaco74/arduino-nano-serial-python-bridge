"""
Script: weather.py
Description: Shows current weather information
Author: System
Platform: Cross-platform
"""

import subprocess
import platform
import urllib.request
import json


def execute(city="Berlin"):
    """
    Main execution function - shows weather information.
    
    Args:
        city (str): City name to get weather for
    
    This function fetches and displays weather information.
    """
    system = platform.system()
    
    try:
        # Try to get weather from wttr.in (simple text-based weather)
        weather_url = f"https://wttr.in/{city}?format=3"
        
        with urllib.request.urlopen(weather_url, timeout=5) as response:
            weather_text = response.read().decode('utf-8').strip()
        
        # Display weather based on OS
        if system == "Darwin":  # macOS
            subprocess.run([
                "osascript", "-e", 
                f'display dialog "{weather_text}" with title "Weather" buttons {{"OK"}} default button "OK"'
            ])
        elif system == "Linux":
            try:
                subprocess.run(["notify-send", "Weather", weather_text])
            except FileNotFoundError:
                subprocess.run([
                    "xterm", "-e", "bash", "-c", 
                    f'echo "{weather_text}"; read -p "Press Enter to continue..."'
                ])
        elif system == "Windows":
            subprocess.run([
                "powershell", "-Command", 
                f'Add-Type -AssemblyName System.Windows.Forms; '
                f'[System.Windows.Forms.MessageBox]::Show("{weather_text}", "Weather")'
            ])
    
    except Exception as e:
        # Fallback message
        error_msg = f"Could not fetch weather for {city}. Check your internet connection."
        
        if system == "Darwin":
            subprocess.run([
                "osascript", "-e", 
                f'display dialog "{error_msg}" with title "Weather Error" buttons {{"OK"}} default button "OK"'
            ])
        elif system == "Linux":
            try:
                subprocess.run(["notify-send", "Weather Error", error_msg])
            except FileNotFoundError:
                subprocess.run([
                    "xterm", "-e", "bash", "-c", 
                    f'echo "{error_msg}"; read -p "Press Enter to continue..."'
                ])
        elif system == "Windows":
            subprocess.run([
                "powershell", "-Command", 
                f'Add-Type -AssemblyName System.Windows.Forms; '
                f'[System.Windows.Forms.MessageBox]::Show("{error_msg}", "Weather Error")'
            ])


def get_metadata():
    """
    Returns script metadata.
    
    Returns:
        dict: Script metadata including name, description, and compatibility
    """
    return {
        "name": "Weather",
        "description": "Shows current weather information for Berlin",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "fun",
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