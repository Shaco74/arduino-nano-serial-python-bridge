# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Arduino Nano MIDI Controller project that converts button presses into PC macros. The system consists of:

1. **Arduino Code** (`midi_controller/midi_controller.ino`) - Sends MIDI Control Change messages over serial
2. **Python Bridge Scripts** - Convert MIDI messages to system macros
   - `serial_macro_bridge.py` - Direct serial communication (recommended)
   - `midi_macro_bridge.py` - MIDI port communication (optional)

## Development Commands

### Arduino Development
```bash
# Install Arduino IDE
brew install --cask arduino-ide

# Flash Arduino code
# 1. Open midi_controller/midi_controller.ino in Arduino IDE
# 2. Install MIDI Library (Tools → Manage Libraries → "MIDI Library" by FortySevenEffects)
# 3. Set Board: Arduino Nano, Processor: ATmega328P (Old Bootloader)
# 4. Upload to device
```

### Python Development
```bash
# Install dependencies
pip install pyserial

# List available serial ports
python3 serial_macro_bridge.py

# Connect to Arduino (replace with actual port)
python3 serial_macro_bridge.py "/dev/cu.usbserial-10"

# Optional MIDI dependencies
pip install mido python-rtmidi
```

### Testing
```bash
# Test hardware connection
python3 serial_macro_bridge.py "/dev/cu.usbserial-10"
# Press button → should execute macro_1 function

# Debug serial communication
# Check Arduino IDE Serial Monitor at 31250 baud
```

## Architecture

### Hardware Interface
- **Button Input**: Pin 2 (INPUT_PULLUP, debounced)
- **LED Output**: Pin 10 (visual feedback)
- **Communication**: USB Serial at 31250 baud (MIDI standard)

### Software Flow
1. Arduino detects button press → sends MIDI Control Change (0xB0, control=1, value=127/0)
2. Python bridge receives serial data → parses MIDI messages
3. Bridge executes corresponding macro function based on control number

### Macro System
- Macros are defined in `SerialMacroBridge.macros` dictionary
- Control Change number maps to macro function
- Platform-specific implementations (Darwin/Linux/Windows)
- Current macro_1: Opens Terminal with "echo hello world"

### Key Configuration
- **Serial Baud Rate**: 31250 (MIDI standard)
- **Button Pin**: 2 (with internal pullup)
- **LED Pin**: 10
- **MIDI Channel**: 1
- **Control Change Number**: 1

## Extending the System

### Adding New Buttons
1. Define new pin constants in Arduino code
2. Add button reading logic in loop()
3. Send different Control Change numbers
4. Add corresponding macro functions in Python

### Adding New Macros
1. Define new macro function in SerialMacroBridge class
2. Add entry to self.macros dictionary
3. Use platform.system() for cross-platform compatibility

### Platform Support
- **macOS**: Uses `osascript` for AppleScript automation
- **Linux**: Uses `xdotool` for keyboard/mouse simulation  
- **Windows**: Uses PowerShell SendKeys for automation