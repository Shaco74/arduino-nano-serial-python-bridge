"""
Template: random_joke.py
Description: Displays a random joke
Author: System
Platform: Cross-platform
Category: Fun
"""

import random
import subprocess
import platform


def execute():
    """
    Main execution function - displays a random joke.
    """
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "Why don't eggs tell jokes? They'd crack each other up!",
        "What do you call a fake noodle? An impasta!",
        "Why did the math book look so sad? Because it had too many problems!",
        "What do you call a bear with no teeth? A gummy bear!",
        "Why don't programmers like nature? It has too many bugs!",
        "What's the best thing about Switzerland? I don't know, but the flag is a big plus!",
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "How do you organize a space party? You planet!"
    ]
    
    joke = random.choice(jokes)
    system = platform.system()
    
    if system == "Darwin":  # macOS
        subprocess.run([
            "osascript", "-e", 
            f'display dialog "{joke}" with title "Random Joke" buttons {{"OK"}} default button "OK"'
        ])
    elif system == "Linux":
        try:
            subprocess.run(["notify-send", "Random Joke", joke])
        except FileNotFoundError:
            # Fallback to terminal
            subprocess.run([
                "xterm", "-e", "bash", "-c", 
                f'echo "{joke}"; read -p "Press Enter to continue..."'
            ])
    elif system == "Windows":
        subprocess.run([
            "powershell", "-Command", 
            f'Add-Type -AssemblyName System.Windows.Forms; '
            f'[System.Windows.Forms.MessageBox]::Show("{joke}", "Random Joke")'
        ])


def get_metadata():
    """Returns script metadata."""
    return {
        "name": "Random Joke",
        "description": "Displays a random programming/general joke",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "fun",
        "version": "1.0",
        "author": "System"
    }


def is_supported():
    """Check if script is supported on current OS."""
    return platform.system() in get_metadata()["supported_os"]