"""
Serial communication manager for Arduino Nano Macro Controller.

This module handles serial port discovery, connection, and MIDI message parsing.
"""

import serial
import serial.tools.list_ports
import time
import platform
from typing import List, Optional, Dict, Any, Callable
from threading import Thread, Event
from rich.console import Console


class SerialManager:
    """Manages serial communication with Arduino devices."""
    
    def __init__(self, baud_rate: int = 31250, timeout: float = 1.0):
        """
        Initialize the serial manager.
        
        Args:
            baud_rate: Serial communication baud rate (MIDI standard is 31250)
            timeout: Serial read timeout in seconds
        """
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.console = Console()
        self.connections: Dict[str, serial.Serial] = {}
        self.running = False
        self.stop_event = Event()
        self.message_handlers: Dict[str, Callable] = {}
        self.monitor_thread: Optional[Thread] = None
    
    def discover_ports(self) -> List[Dict[str, str]]:
        """
        Discover available serial ports.
        
        Returns:
            List of dictionaries containing port information
        """
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append({
                "device": port.device,
                "description": port.description,
                "manufacturer": getattr(port, 'manufacturer', 'Unknown')
            })
        return ports
    
    def filter_arduino_ports(self, ports: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Filter ports that are likely Arduino devices.
        
        Args:
            ports: List of port dictionaries
            
        Returns:
            Filtered list of Arduino-like ports
        """
        arduino_keywords = ['arduino', 'nano', 'usb', 'serial', 'ch340', 'ftdi']
        filtered = []
        
        for port in ports:
            description = port['description'].lower() if port['description'] else ''
            manufacturer = port.get('manufacturer', '') or ''
            manufacturer = manufacturer.lower()
            
            if any(keyword in description or keyword in manufacturer 
                   for keyword in arduino_keywords):
                filtered.append(port)
        
        return filtered
    
    def connect_to_port(self, port_name: str) -> bool:
        """
        Connect to a specific serial port.
        
        Args:
            port_name: Name of the serial port
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if port_name in self.connections:
                self.disconnect_from_port(port_name)
            
            connection = serial.Serial(
                port=port_name,
                baudrate=self.baud_rate,
                timeout=self.timeout
            )
            
            # Wait for Arduino to initialize
            time.sleep(2)
            
            self.connections[port_name] = connection
            self.console.print(f"✓ Connected to {port_name}", style="green")
            return True
            
        except Exception as e:
            self.console.print(f"✗ Failed to connect to {port_name}: {e}", style="red")
            return False
    
    def disconnect_from_port(self, port_name: str) -> None:
        """
        Disconnect from a specific serial port.
        
        Args:
            port_name: Name of the serial port
        """
        if port_name in self.connections:
            try:
                self.connections[port_name].close()
                del self.connections[port_name]
                self.console.print(f"✓ Disconnected from {port_name}", style="yellow")
            except Exception as e:
                self.console.print(f"✗ Error disconnecting from {port_name}: {e}", style="red")
    
    def disconnect_all(self) -> None:
        """Disconnect from all serial ports."""
        for port_name in list(self.connections.keys()):
            self.disconnect_from_port(port_name)
    
    def register_message_handler(self, port_name: str, handler: Callable) -> None:
        """
        Register a message handler for a specific port.
        
        Args:
            port_name: Serial port name
            handler: Function to handle incoming messages
        """
        self.message_handlers[port_name] = handler
    
    def parse_midi_message(self, data: bytes) -> Optional[Dict[str, int]]:
        """
        Parse MIDI Control Change message from serial data.
        
        Args:
            data: Raw serial data
            
        Returns:
            Dictionary with MIDI message info or None if invalid
        """
        if len(data) < 3:
            return None
        
        # MIDI Control Change: 0xB0 + channel, control, value
        if data[0] == 0xB0:  # Control Change on channel 1
            return {
                "type": "control_change",
                "channel": 1,
                "control": data[1],
                "value": data[2]
            }
        
        return None
    
    def _monitor_serial_data(self) -> None:
        """Monitor serial data in a separate thread."""
        while not self.stop_event.is_set():
            for port_name, connection in self.connections.items():
                try:
                    if connection.in_waiting > 0:
                        data = connection.read(connection.in_waiting)
                        
                        # Parse MIDI messages
                        midi_message = self.parse_midi_message(data)
                        if midi_message:
                            # Call registered handler
                            if port_name in self.message_handlers:
                                self.message_handlers[port_name](midi_message)
                            else:
                                # Default logging
                                self.console.print(
                                    f"MIDI [{port_name}]: Control {midi_message['control']}, "
                                    f"Value {midi_message['value']}"
                                )
                
                except Exception as e:
                    self.console.print(f"Error reading from {port_name}: {e}", style="red")
            
            time.sleep(0.01)  # Small delay to prevent excessive CPU usage
    
    def start_monitoring(self) -> None:
        """Start monitoring serial data."""
        if self.running:
            return
        
        self.running = True
        self.stop_event.clear()
        self.monitor_thread = Thread(target=self._monitor_serial_data, daemon=True)
        self.monitor_thread.start()
        self.console.print("📡 Serial monitoring started", style="blue")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring serial data."""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.console.print("📡 Serial monitoring stopped", style="blue")
    
    def send_data(self, port_name: str, data: bytes) -> bool:
        """
        Send data to a specific port.
        
        Args:
            port_name: Serial port name
            data: Data to send
            
        Returns:
            True if successful, False otherwise
        """
        if port_name not in self.connections:
            return False
        
        try:
            self.connections[port_name].write(data)
            return True
        except Exception as e:
            self.console.print(f"Error sending data to {port_name}: {e}", style="red")
            return False
    
    def is_connected(self, port_name: str) -> bool:
        """
        Check if a port is connected.
        
        Args:
            port_name: Serial port name
            
        Returns:
            True if connected, False otherwise
        """
        return port_name in self.connections and self.connections[port_name].is_open
    
    def get_connected_ports(self) -> List[str]:
        """
        Get list of connected port names.
        
        Returns:
            List of connected port names
        """
        return list(self.connections.keys())
    
    def test_port_connection(self, port_name: str) -> bool:
        """
        Test if a port can be connected to.
        
        Args:
            port_name: Serial port name
            
        Returns:
            True if port is accessible, False otherwise
        """
        try:
            test_connection = serial.Serial(
                port=port_name,
                baudrate=self.baud_rate,
                timeout=0.5
            )
            test_connection.close()
            return True
        except Exception:
            return False