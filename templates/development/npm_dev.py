"""
Template: npm_dev.py
Description: Runs npm dev command in current directory
Author: System
Platform: Cross-platform
Category: Development
"""

import subprocess
import platform
import os


def execute():
    """
    Main execution function - runs npm dev command.
    
    This function opens a terminal and runs 'npm run dev' in the current directory.
    Useful for starting development servers.
    """
    system = platform.system()
    current_dir = os.getcwd()
    
    # Check if package.json exists
    if not os.path.exists(os.path.join(current_dir, "package.json")):
        error_msg = "No package.json found in current directory!"
        
        if system == "Darwin":
            subprocess.run([
                "osascript", "-e", 
                f'display dialog "{error_msg}" with title "NPM Dev" buttons {{"OK"}} default button "OK"'
            ])
        elif system == "Linux":
            try:
                subprocess.run(["notify-send", "NPM Dev", error_msg])
            except FileNotFoundError:
                subprocess.run([
                    "xterm", "-e", "bash", "-c", 
                    f'echo "{error_msg}"; read -p "Press Enter to continue..."'
                ])
        elif system == "Windows":
            subprocess.run([
                "powershell", "-Command", 
                f'Add-Type -AssemblyName System.Windows.Forms; '
                f'[System.Windows.Forms.MessageBox]::Show("{error_msg}", "NPM Dev")'
            ])
        return
    
    # Run npm dev command
    if system == "Darwin":  # macOS
        subprocess.run([
            "osascript", "-e", 
            f'tell application "Terminal" to do script "cd {current_dir} && npm run dev"'
        ])
    elif system == "Linux":
        try:
            subprocess.run([
                "gnome-terminal", "--", "bash", "-c", 
                f"cd {current_dir} && npm run dev; read -p 'Press Enter to close...'"
            ])
        except FileNotFoundError:
            subprocess.run([
                "xterm", "-e", "bash", "-c", 
                f"cd {current_dir} && npm run dev; read -p 'Press Enter to close...'"
            ])
    elif system == "Windows":
        subprocess.run([
            "cmd", "/c", "start", "cmd", "/k", 
            f"cd /d {current_dir} && npm run dev"
        ])


def get_metadata():
    """Returns script metadata."""
    return {
        "name": "NPM Dev",
        "description": "Runs 'npm run dev' in current directory",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "development",
        "version": "1.0",
        "author": "System"
    }


def is_supported():
    """Check if script is supported on current OS."""
    system = platform.system()
    if system not in get_metadata()["supported_os"]:
        return False
    
    # Check if npm is available
    try:
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False