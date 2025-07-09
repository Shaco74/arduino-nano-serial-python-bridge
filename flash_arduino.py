#!/usr/bin/env python3
"""
Arduino flasher utility for Arduino Nano Macro Controller.

This script helps flash Arduino sketches using Arduino CLI.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table

from utils.serial_manager import SerialManager


class ArduinoFlasher:
    """Handles Arduino sketch compilation and flashing."""
    
    def __init__(self):
        """Initialize the Arduino flasher."""
        self.console = Console()
        self.serial_manager = SerialManager()
        self.sketches_dir = Path("midi_controller")
        
        # Available sketches
        self.sketches = {
            "single": {
                "file": "midi_controller.ino",
                "name": "Single Button Controller",
                "description": "Supports 1 button on Pin 2 with LED on Pin 10",
                "buttons": 1
            },
            "multi": {
                "file": "midi_controller_multi.ino", 
                "name": "Multi Button Controller",
                "description": "Supports up to 5 buttons on Pins 2-6 with LEDs on Pins 10-13,A0",
                "buttons": 5
            }
        }
    
    def check_arduino_cli(self) -> bool:
        """
        Check if Arduino CLI is installed.
        
        Returns:
            True if Arduino CLI is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["arduino-cli", "version"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            self.console.print(f"✅ Arduino CLI found: {result.stdout.strip()}", style="green")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def install_arduino_cli(self) -> bool:
        """
        Install Arduino CLI using Homebrew (macOS).
        
        Returns:
            True if installation succeeded, False otherwise
        """
        if not Confirm.ask("Arduino CLI not found. Install it now?"):
            return False
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Installing Arduino CLI...", total=None)
                
                result = subprocess.run(
                    ["brew", "install", "arduino-cli"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                progress.update(task, completed=True)
            
            self.console.print("✅ Arduino CLI installed successfully", style="green")
            return True
            
        except subprocess.CalledProcessError as e:
            self.console.print(f"❌ Failed to install Arduino CLI: {e}", style="red")
            self.console.print("Please install manually from: https://arduino.github.io/arduino-cli/", style="yellow")
            return False
        except FileNotFoundError:
            self.console.print("❌ Homebrew not found. Please install Arduino CLI manually.", style="red")
            return False
    
    def setup_arduino_cli(self) -> bool:
        """
        Setup Arduino CLI configuration.
        
        Returns:
            True if setup succeeded, False otherwise
        """
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task1 = progress.add_task("Initializing Arduino CLI config...", total=None)
                
                # Initialize config
                subprocess.run(["arduino-cli", "config", "init"], check=True, capture_output=True)
                progress.update(task1, completed=True)
                
                task2 = progress.add_task("Updating core index...", total=None)
                
                # Update core index
                subprocess.run(["arduino-cli", "core", "update-index"], check=True, capture_output=True)
                progress.update(task2, completed=True)
                
                task3 = progress.add_task("Installing Arduino AVR core...", total=None)
                
                # Install Arduino AVR core
                subprocess.run(["arduino-cli", "core", "install", "arduino:avr"], check=True, capture_output=True)
                progress.update(task3, completed=True)
                
                task4 = progress.add_task("Installing MIDI Library...", total=None)
                
                # Install MIDI Library
                subprocess.run(["arduino-cli", "lib", "install", "MIDI Library"], check=True, capture_output=True)
                progress.update(task4, completed=True)
            
            self.console.print("✅ Arduino CLI setup completed", style="green")
            return True
            
        except subprocess.CalledProcessError as e:
            self.console.print(f"❌ Arduino CLI setup failed: {e}", style="red")
            return False
    
    def detect_arduino_ports(self) -> list:
        """
        Detect connected Arduino boards.
        
        Returns:
            List of detected Arduino ports
        """
        ports = self.serial_manager.discover_ports()
        arduino_ports = self.serial_manager.filter_arduino_ports(ports)
        
        return arduino_ports
    
    def show_sketch_selection(self) -> Optional[str]:
        """
        Show sketch selection menu.
        
        Returns:
            Selected sketch key or None if cancelled
        """
        table = Table(title="Available Arduino Sketches", show_header=True)
        table.add_column("Sketch", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="green")
        table.add_column("Buttons", style="yellow")
        
        for key, sketch in self.sketches.items():
            table.add_row(
                key,
                sketch["name"],
                sketch["description"],
                str(sketch["buttons"])
            )
        
        self.console.print(table)
        
        choice = Prompt.ask(
            "Select sketch to flash",
            choices=list(self.sketches.keys()) + ["cancel"],
            default="multi"
        )
        
        return choice if choice != "cancel" else None
    
    def flash_sketch(self, sketch_key: str, port: str) -> bool:
        """
        Flash a sketch to Arduino.
        
        Args:
            sketch_key: Sketch identifier
            port: Arduino port name
            
        Returns:
            True if flashing succeeded, False otherwise
        """
        sketch = self.sketches[sketch_key]
        sketch_path = self.sketches_dir / sketch["file"]
        
        if not sketch_path.exists():
            self.console.print(f"❌ Sketch file not found: {sketch_path}", style="red")
            return False
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task1 = progress.add_task("Compiling sketch...", total=None)
                
                # Compile sketch
                compile_result = subprocess.run([
                    "arduino-cli", "compile",
                    "--fqbn", "arduino:avr:nano:cpu=atmega328old",
                    str(sketch_path)
                ], capture_output=True, text=True, check=True)
                
                progress.update(task1, completed=True)
                
                task2 = progress.add_task("Flashing to Arduino...", total=None)
                
                # Upload sketch
                upload_result = subprocess.run([
                    "arduino-cli", "upload",
                    "--fqbn", "arduino:avr:nano:cpu=atmega328old",
                    "--port", port,
                    str(sketch_path)
                ], capture_output=True, text=True, check=True)
                
                progress.update(task2, completed=True)
            
            self.console.print(f"✅ Successfully flashed {sketch['name']}", style="green")
            return True
            
        except subprocess.CalledProcessError as e:
            self.console.print(f"❌ Flashing failed: {e}", style="red")
            if e.stderr:
                self.console.print(f"Error details: {e.stderr}", style="red")
            return False
    
    def run(self):
        """Run the Arduino flasher."""
        self.console.print(Panel(
            "Arduino Nano Macro Controller Flasher",
            title="🔧 Arduino Flasher",
            border_style="blue"
        ))
        
        # Check Arduino CLI
        if not self.check_arduino_cli():
            if not self.install_arduino_cli():
                self.console.print("❌ Cannot proceed without Arduino CLI", style="red")
                return
        
        # Setup Arduino CLI
        if not self.setup_arduino_cli():
            self.console.print("❌ Arduino CLI setup failed", style="red")
            return
        
        # Detect Arduino ports
        self.console.print("🔍 Detecting Arduino boards...")
        arduino_ports = self.detect_arduino_ports()
        
        if not arduino_ports:
            self.console.print("❌ No Arduino boards detected", style="red")
            self.console.print("Please connect your Arduino Nano and try again", style="yellow")
            return
        
        # Show detected ports
        port_table = Table(title="Detected Arduino Boards", show_header=True)
        port_table.add_column("Port", style="cyan")
        port_table.add_column("Description", style="magenta")
        
        for port in arduino_ports:
            port_table.add_row(port["device"], port["description"])
        
        self.console.print(port_table)
        
        # Port selection
        if len(arduino_ports) == 1:
            selected_port = arduino_ports[0]["device"]
            self.console.print(f"📍 Using port: {selected_port}", style="blue")
        else:
            port_choices = [port["device"] for port in arduino_ports]
            selected_port = Prompt.ask(
                "Select Arduino port",
                choices=port_choices,
                default=port_choices[0]
            )
        
        # Sketch selection
        sketch_key = self.show_sketch_selection()
        if not sketch_key:
            self.console.print("❌ No sketch selected", style="yellow")
            return
        
        # Flash confirmation
        sketch = self.sketches[sketch_key]
        if not Confirm.ask(f"Flash '{sketch['name']}' to {selected_port}?"):
            self.console.print("❌ Flashing cancelled", style="yellow")
            return
        
        # Flash the sketch
        if self.flash_sketch(sketch_key, selected_port):
            self.console.print(Panel(
                f"✅ Arduino flashed successfully!\n\n"
                f"Sketch: {sketch['name']}\n"
                f"Buttons: {sketch['buttons']}\n"
                f"Port: {selected_port}\n\n"
                f"You can now run 'python3 setup.py' to configure your buttons.",
                title="🎉 Success",
                border_style="green"
            ))
        else:
            self.console.print("❌ Flashing failed", style="red")


def main():
    """Main entry point."""
    flasher = ArduinoFlasher()
    flasher.run()


if __name__ == "__main__":
    main()