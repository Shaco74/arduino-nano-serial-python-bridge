#!/usr/bin/env python3
import mido
import subprocess
import sys
import time
import platform

class MidiMacroBridge:
    def __init__(self):
        self.macros = {
            1: self.macro_1,
        }
        self.system = platform.system()
        
    def macro_1(self):
        """Beispiel Macro - öffnet Spotlight/Alfred auf Mac"""
        if self.system == "Darwin":
            subprocess.run(["osascript", "-e", 'tell application "System Events" to keystroke space using command down'])
        elif self.system == "Linux":
            subprocess.run(["xdotool", "key", "ctrl+alt+t"])
        elif self.system == "Windows":
            subprocess.run(["powershell", "-Command", "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^{ESC}')"])
    
    def execute_macro(self, control_number, value):
        if value == 127 and control_number in self.macros:
            print(f"Executing macro {control_number}")
            self.macros[control_number]()
    
    def list_midi_ports(self):
        print("Available MIDI input ports:")
        for i, port in enumerate(mido.get_input_names()):
            print(f"{i}: {port}")
        
        print("\nAvailable serial ports (for Arduino):")
        import serial.tools.list_ports
        for port in serial.tools.list_ports.comports():
            print(f"  {port.device} - {port.description}")
    
    def run(self, port_name=None):
        if port_name is None:
            self.list_midi_ports()
            return
            
        try:
            with mido.open_input(port_name) as inport:
                print(f"Listening on {port_name}")
                print("Press Ctrl+C to stop")
                
                for msg in inport:
                    if msg.type == 'control_change':
                        print(f"CC: {msg.control}, Value: {msg.value}")
                        self.execute_macro(msg.control, msg.value)
                        
        except KeyboardInterrupt:
            print("\nStopping...")
        except Exception as e:
            print(f"Error: {e}")

def main():
    bridge = MidiMacroBridge()
    
    if len(sys.argv) > 1:
        port_name = sys.argv[1]
        bridge.run(port_name)
    else:
        bridge.list_midi_ports()
        print("\nUsage: python midi_macro_bridge.py <port_name>")

if __name__ == "__main__":
    main()