"""
Script: music_control.py
Description: Controls music playback (play/pause)
Author: System
Platform: Cross-platform
"""

import subprocess
import platform


def execute(action="toggle"):
    """
    Main execution function - controls music playback.
    
    Args:
        action (str): Music action - "play", "pause", "toggle", "next", "previous"
    
    This function controls music playback using system-specific commands.
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        if action == "toggle" or action == "play" or action == "pause":
            subprocess.run([
                "osascript", "-e", 
                'tell application "Music" to playpause'
            ])
        elif action == "next":
            subprocess.run([
                "osascript", "-e", 
                'tell application "Music" to next track'
            ])
        elif action == "previous":
            subprocess.run([
                "osascript", "-e", 
                'tell application "Music" to previous track'
            ])
    elif system == "Linux":
        # Try different media players
        if action == "toggle" or action == "play" or action == "pause":
            try:
                subprocess.run(["playerctl", "play-pause"])
            except FileNotFoundError:
                try:
                    subprocess.run(["dbus-send", "--print-reply", "--dest=org.mpris.MediaPlayer2.spotify", 
                                   "/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player.PlayPause"])
                except FileNotFoundError:
                    pass
        elif action == "next":
            try:
                subprocess.run(["playerctl", "next"])
            except FileNotFoundError:
                pass
        elif action == "previous":
            try:
                subprocess.run(["playerctl", "previous"])
            except FileNotFoundError:
                pass
    elif system == "Windows":
        # Windows media key simulation
        if action == "toggle" or action == "play" or action == "pause":
            subprocess.run([
                "powershell", "-Command", 
                "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; "
                "public class MediaKeys { [DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo); "
                "public static void PlayPause() { keybd_event(0xB3, 0, 0, UIntPtr.Zero); keybd_event(0xB3, 0, 2, UIntPtr.Zero); } }'; "
                "[MediaKeys]::PlayPause()"
            ])
        elif action == "next":
            subprocess.run([
                "powershell", "-Command", 
                "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; "
                "public class MediaKeys { [DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo); "
                "public static void NextTrack() { keybd_event(0xB0, 0, 0, UIntPtr.Zero); keybd_event(0xB0, 0, 2, UIntPtr.Zero); } }'; "
                "[MediaKeys]::NextTrack()"
            ])
        elif action == "previous":
            subprocess.run([
                "powershell", "-Command", 
                "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; "
                "public class MediaKeys { [DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo); "
                "public static void PreviousTrack() { keybd_event(0xB1, 0, 0, UIntPtr.Zero); keybd_event(0xB1, 0, 2, UIntPtr.Zero); } }'; "
                "[MediaKeys]::PreviousTrack()"
            ])


def get_metadata():
    """
    Returns script metadata.
    
    Returns:
        dict: Script metadata including name, description, and compatibility
    """
    return {
        "name": "Music Control",
        "description": "Controls music playback (play/pause by default)",
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