#!/usr/bin/env python3
"""
Main bridge application for Arduino Nano Macro Controller.

This script loads configuration, connects to Arduino devices, and executes
scripts based on button presses.
"""

import sys
import signal
import time
from typing import Dict, Any
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text

from utils.config_manager import ConfigManager
from utils.serial_manager import SerialManager
from utils.script_loader import ScriptLoader


class MacroBridge:
    """Main application class for the macro bridge."""
    
    def __init__(self):
        """Initialize the macro bridge."""
        self.console = Console()
        self.config_manager = ConfigManager()
        self.serial_manager = SerialManager()
        self.script_loader = ScriptLoader()
        self.running = False
        
        # Load configuration
        self.config = self.config_manager.load_config()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.console.print("\n🛑 Shutting down...", style="yellow")
        self.stop()
        sys.exit(0)
    
    def _create_status_display(self) -> Layout:
        """Create the status display layout."""
        layout = Layout()
        
        # Create main sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        # Split main into left and right
        layout["main"].split_row(
            Layout(name="buttons", ratio=1),
            Layout(name="logs", ratio=1)
        )
        
        return layout
    
    def _update_status_display(self, layout: Layout) -> None:
        """Update the status display with current information."""
        # Header
        header_text = Text("Arduino Nano Macro Controller", style="bold blue")
        layout["header"].update(Panel(header_text, title="Status", border_style="blue"))
        
        # Button status table
        button_table = Table(title="Button Configuration", show_header=True)
        button_table.add_column("Button", style="cyan")
        button_table.add_column("Port", style="magenta")
        button_table.add_column("Script", style="green")
        button_table.add_column("Status", style="yellow")
        
        buttons = self.config_manager.get_all_buttons()
        for button_id, config in buttons.items():
            status = "🟢 Enabled" if config.get("enabled", False) else "🔴 Disabled"
            port = config.get("port", "N/A")
            script = config.get("script", "N/A")
            button_table.add_row(f"Button {button_id}", port, script, status)
        
        if not buttons:
            button_table.add_row("No buttons configured", "-", "-", "🔴 Disabled")
        
        layout["buttons"].update(button_table)
        
        # Connection status
        connected_ports = self.serial_manager.get_connected_ports()
        if connected_ports:
            status_text = f"📡 Connected to {len(connected_ports)} port(s)"
            status_style = "green"
        else:
            status_text = "📡 No connections"
            status_style = "red"
        
        layout["logs"].update(
            Panel(
                Text(status_text, style=status_style),
                title="Connection Status",
                border_style="green" if connected_ports else "red"
            )
        )
        
        # Footer
        footer_text = Text("Press Ctrl+C to exit", style="dim")
        layout["footer"].update(Panel(footer_text, border_style="dim"))
    
    def _handle_midi_message(self, port_name: str, message: Dict[str, Any]) -> None:
        """
        Handle incoming MIDI messages from Arduino.
        
        Args:
            port_name: Name of the serial port
            message: MIDI message dictionary
        """
        if message["type"] != "control_change":
            return
        
        control_number = message["control"]
        value = message["value"]
        
        # Find button configuration for this control number
        button_config = None
        button_id = None
        
        for bid, config in self.config_manager.get_all_buttons().items():
            if (config.get("port") == port_name and 
                config.get("control_number") == control_number):
                button_config = config
                button_id = bid
                break
        
        if not button_config:
            self.console.print(
                f"⚠️  No button configured for control {control_number} on {port_name}",
                style="yellow"
            )
            return
        
        # Only execute on button press (value 127)
        if value != 127:
            return
        
        if not button_config.get("enabled", False):
            self.console.print(
                f"⚠️  Button {button_id} is disabled",
                style="yellow"
            )
            return
        
        script_name = button_config.get("script")
        if not script_name:
            self.console.print(
                f"⚠️  No script assigned to button {button_id}",
                style="yellow"
            )
            return
        
        # Execute the script
        self.console.print(
            f"🔄 Button {button_id} pressed - executing '{script_name}'",
            style="blue"
        )
        
        success = self.script_loader.execute_script(script_name)
        if success:
            self.console.print(
                f"✅ Script '{script_name}' executed successfully",
                style="green"
            )
        else:
            self.console.print(
                f"❌ Script '{script_name}' failed to execute",
                style="red"
            )
    
    def _connect_to_configured_ports(self) -> bool:
        """
        Connect to all configured ports.
        
        Returns:
            True if at least one connection succeeded, False otherwise
        """
        buttons = self.config_manager.get_configured_buttons()
        connected_ports = set()
        
        for button_id, config in buttons.items():
            port_name = config.get("port")
            if port_name and port_name not in connected_ports:
                if self.serial_manager.connect_to_port(port_name):
                    connected_ports.add(port_name)
                    # Register message handler
                    self.serial_manager.register_message_handler(
                        port_name, 
                        lambda msg, pname=port_name: self._handle_midi_message(pname, msg)
                    )
        
        return len(connected_ports) > 0
    
    def start(self) -> None:
        """Start the macro bridge."""
        self.console.print(Panel(
            "Starting Arduino Nano Macro Controller",
            title="🚀 Startup",
            border_style="green"
        ))
        
        # Load scripts
        self.console.print("📦 Loading scripts...")
        loaded_scripts = self.script_loader.load_all_scripts()
        
        if loaded_scripts == 0:
            self.console.print("⚠️  No scripts loaded. Please add scripts to the 'scripts' directory.", style="yellow")
        
        # Connect to configured ports
        self.console.print("🔌 Connecting to configured ports...")
        if not self._connect_to_configured_ports():
            self.console.print("❌ No ports connected. Please check your configuration.", style="red")
            return
        
        # Start serial monitoring
        self.serial_manager.start_monitoring()
        
        # Show status
        self.running = True
        layout = self._create_status_display()
        
        try:
            with Live(layout, refresh_per_second=2, screen=True):
                while self.running:
                    self._update_status_display(layout)
                    time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the macro bridge."""
        if not self.running:
            return
        
        self.running = False
        self.serial_manager.stop_monitoring()
        self.serial_manager.disconnect_all()
        
        self.console.print("👋 Macro bridge stopped", style="blue")


def main():
    """Main entry point."""
    console = Console()
    
    # Check if configuration exists
    if not Path("config.json").exists():
        console.print(Panel(
            "No configuration found. Please run 'python3 setup.py' first.",
            title="⚠️  Configuration Required",
            border_style="yellow"
        ))
        sys.exit(1)
    
    # Create and start the bridge
    bridge = MacroBridge()
    bridge.start()


if __name__ == "__main__":
    main()