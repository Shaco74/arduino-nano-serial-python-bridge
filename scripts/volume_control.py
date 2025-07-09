"""
Script: volume_control.py
Description: Controls system volume
Author: System
Platform: Cross-platform
"""

import subprocess
import platform


def execute(action="toggle"):
    """
    Main execution function - controls system volume.
    
    Args:
        action (str): Volume action - "up", "down", "mute", or "toggle"
    
    This function controls the system volume based on the specified action.
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        if action == "up":
            subprocess.run([
                "osascript", "-e", 
                "set volume output volume (output volume of (get volume settings) + 10)"
            ])
        elif action == "down":
            subprocess.run([
                "osascript", "-e", 
                "set volume output volume (output volume of (get volume settings) - 10)"
            ])
        elif action == "mute" or action == "toggle":
            subprocess.run([
                "osascript", "-e", 
                "set volume output muted (not (output muted of (get volume settings)))"
            ])
    elif system == "Linux":
        if action == "up":
            try:
                subprocess.run(["amixer", "-q", "sset", "Master", "5%+"])
            except FileNotFoundError:
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"])
        elif action == "down":
            try:
                subprocess.run(["amixer", "-q", "sset", "Master", "5%-"])
            except FileNotFoundError:
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"])
        elif action == "mute" or action == "toggle":
            try:
                subprocess.run(["amixer", "-q", "sset", "Master", "toggle"])
            except FileNotFoundError:
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
    elif system == "Windows":
        if action == "up":
            subprocess.run([
                "powershell", "-Command", 
                "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; "
                "public class Volume { [DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo); "
                "public static void VolumeUp() { keybd_event(0xAF, 0, 0, UIntPtr.Zero); keybd_event(0xAF, 0, 2, UIntPtr.Zero); } }'; "
                "[Volume]::VolumeUp()"
            ])
        elif action == "down":
            subprocess.run([
                "powershell", "-Command", 
                "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; "
                "public class Volume { [DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo); "
                "public static void VolumeDown() { keybd_event(0xAE, 0, 0, UIntPtr.Zero); keybd_event(0xAE, 0, 2, UIntPtr.Zero); } }'; "
                "[Volume]::VolumeDown()"
            ])
        elif action == "mute" or action == "toggle":
            subprocess.run([
                "powershell", "-Command", 
                "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; "
                "public class Volume { [DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo); "
                "public static void Mute() { keybd_event(0xAD, 0, 0, UIntPtr.Zero); keybd_event(0xAD, 0, 2, UIntPtr.Zero); } }'; "
                "[Volume]::Mute()"
            ])


def get_metadata():
    """
    Returns script metadata.
    
    Returns:
        dict: Script metadata including name, description, and compatibility
    """
    return {
        "name": "Volume Control",
        "description": "Controls system volume (toggle mute by default)",
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