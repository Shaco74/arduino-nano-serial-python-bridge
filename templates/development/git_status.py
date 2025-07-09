"""
Template: git_status.py
Description: Shows git status in terminal
Author: System
Platform: Cross-platform
Category: Development
"""

import subprocess
import platform
import os


def execute():
    """
    Main execution function - shows git status in terminal.
    """
    system = platform.system()
    
    # Check if we're in a git repository
    try:
        subprocess.run(["git", "rev-parse", "--git-dir"], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        # Not in a git repository
        if system == "Darwin":
            subprocess.run([
                "osascript", "-e", 
                'display dialog "Not in a git repository!" with title "Git Status" buttons {"OK"} default button "OK"'
            ])
        elif system == "Linux":
            try:
                subprocess.run(["notify-send", "Git Status", "Not in a git repository!"])
            except FileNotFoundError:
                subprocess.run([
                    "xterm", "-e", "bash", "-c", 
                    'echo "Not in a git repository!"; read -p "Press Enter to continue..."'
                ])
        elif system == "Windows":
            subprocess.run([
                "powershell", "-Command", 
                '[System.Windows.Forms.MessageBox]::Show("Not in a git repository!", "Git Status")'
            ])
        return
    
    # Show git status in terminal
    if system == "Darwin":  # macOS
        subprocess.run([
            "osascript", "-e", 
            'tell application "Terminal" to do script "cd ' + os.getcwd() + '; git status; read -p \\"Press Enter to continue...\\""'
        ])
    elif system == "Linux":
        try:
            subprocess.run([
                "gnome-terminal", "--", "bash", "-c", 
                f"cd {os.getcwd()}; git status; read -p 'Press Enter to continue...'"
            ])
        except FileNotFoundError:
            subprocess.run([
                "xterm", "-e", "bash", "-c", 
                f"cd {os.getcwd()}; git status; read -p 'Press Enter to continue...'"
            ])
    elif system == "Windows":
        subprocess.run([
            "cmd", "/c", "start", "cmd", "/k", 
            f"cd /d {os.getcwd()} && git status"
        ])


def get_metadata():
    """Returns script metadata."""
    return {
        "name": "Git Status",
        "description": "Shows git status in terminal for current directory",
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
    
    # Check if git is installed
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False