"""
Script: open_vscode.py
Description: Opens Visual Studio Code
Author: System
Platform: Cross-platform
"""

import subprocess
import platform
import os


def execute(path=None):
    """
    Main execution function - opens Visual Studio Code.
    
    Args:
        path (str): Optional path to open in VS Code. Defaults to current directory.
    
    This function opens Visual Studio Code, optionally with a specific file or folder.
    """
    system = platform.system()
    
    if path is None:
        path = os.getcwd()
    
    try:
        # Try using the 'code' command first (most common)
        subprocess.run(["code", path])
    except FileNotFoundError:
        # Fallback to system-specific methods
        if system == "Darwin":  # macOS
            try:
                subprocess.run(["open", "-a", "Visual Studio Code", path])
            except FileNotFoundError:
                # Try common installation paths
                vscode_paths = [
                    "/Applications/Visual Studio Code.app",
                    "/usr/local/bin/code"
                ]
                for vscode_path in vscode_paths:
                    if os.path.exists(vscode_path):
                        subprocess.run([vscode_path, path])
                        return
                raise FileNotFoundError("Visual Studio Code not found")
        elif system == "Linux":
            try:
                subprocess.run(["code-insiders", path])
            except FileNotFoundError:
                subprocess.run(["snap", "run", "code", path])
        elif system == "Windows":
            try:
                subprocess.run(["code.exe", path])
            except FileNotFoundError:
                # Try common installation paths
                vscode_paths = [
                    "C:\\Program Files\\Microsoft VS Code\\Code.exe",
                    "C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe",
                    os.path.expanduser("~\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
                ]
                for vscode_path in vscode_paths:
                    if os.path.exists(vscode_path):
                        subprocess.run([vscode_path, path])
                        return
                raise FileNotFoundError("Visual Studio Code not found")


def get_metadata():
    """
    Returns script metadata.
    
    Returns:
        dict: Script metadata including name, description, and compatibility
    """
    return {
        "name": "Open VS Code",
        "description": "Opens Visual Studio Code in the current directory",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "development",
        "version": "1.0",
        "author": "System"
    }


def is_supported():
    """
    Check if script is supported on current OS.
    
    Returns:
        bool: True if script is supported on current OS, False otherwise
    """
    system = platform.system()
    if system not in get_metadata()["supported_os"]:
        return False
    
    # Check if VS Code is actually installed
    try:
        subprocess.run(["code", "--version"], capture_output=True)
        return True
    except FileNotFoundError:
        # Check system-specific paths
        if system == "Darwin":
            return os.path.exists("/Applications/Visual Studio Code.app")
        elif system == "Linux":
            return (os.path.exists("/usr/bin/code") or 
                   os.path.exists("/snap/bin/code"))
        elif system == "Windows":
            return (os.path.exists("C:\\Program Files\\Microsoft VS Code\\Code.exe") or
                   os.path.exists("C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe"))
    
    return False