#!/usr/bin/env python3
import serial
import subprocess
import sys
import time
import platform
import serial.tools.list_ports

class SerialMacroBridge:
    def __init__(self):
        self.macros = {
            1: self.macro_1,
        }
        self.system = platform.system()
        
    def macro_1(self):
        """Beispiel Macro - öffnet Spotlight/Alfred auf Mac"""
        if self.system == "Darwin":
            subprocess.run(["osascript", "-e", 'tell application "Terminal" to do script "echo hello world"'])
        elif self.system == "Linux":
            subprocess.run(["xdotool", "key", "ctrl+alt+t"])
        elif self.system == "Windows":
            subprocess.run(["powershell", "-Command", "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^{ESC}')"])
    
    def execute_macro(self, control_number, value):
        if value == 127 and control_number in self.macros:
            print(f"Executing macro {control_number}")
            self.macros[control_number]()
    
    def list_serial_ports(self):
        print("Available serial ports:")
        for port in serial.tools.list_ports.comports():
            print(f"  {port.device} - {port.description}")
    
    def run(self, port_name=None):
        if port_name is None:
            self.list_serial_ports()
            return
            
        try:
            with serial.Serial(port_name, 31250, timeout=1) as ser:
                print(f"Connected to {port_name}")
                print("Press Ctrl+C to stop")
                
                while True:
                    if ser.in_waiting > 0:
                        data = ser.read(ser.in_waiting)
                        # MIDI Control Change: 0xB0 + channel, control, value
                        if len(data) >= 3:
                            if data[0] == 0xB0:  # Control Change on channel 1
                                control = data[1]
                                value = data[2]
                                print(f"CC: {control}, Value: {value}")
                                self.execute_macro(control, value)
                    
                    time.sleep(0.01)
                        
        except KeyboardInterrupt:
            print("\nStopping...")
        except Exception as e:
            print(f"Error: {e}")

def main():
    bridge = SerialMacroBridge()
    
    if len(sys.argv) > 1:
        port_name = sys.argv[1]
        bridge.run(port_name)
    else:
        bridge.list_serial_ports()
        print("\nUsage: python serial_macro_bridge.py <port_name>")
        print("Example: python serial_macro_bridge.py /dev/cu.usbserial-...")

if __name__ == "__main__":
    main()