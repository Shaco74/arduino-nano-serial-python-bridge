# Arduino Nano Macro Controller

A modern, user-friendly Arduino Nano based MIDI controller that converts button presses into customizable PC macros. Perfect for productivity shortcuts, application launchers, and automated workflows.

## ✨ Features

- 🎹 **MIDI Controller**: Arduino sends MIDI Control Change messages over USB
- 🖥️ **Cross-Platform Macros**: Support for macOS, Linux, and Windows
- 🔘 **Multi-Button Support**: Configure up to 5 buttons with individual scripts
- 💡 **LED Feedback**: Visual status indicators for button states
- 🎨 **Modern Interface**: Rich console UI with colors, tables, and progress bars
- 📝 **Script Management**: Built-in script editor with validation
- 🔄 **Import/Export**: Backup and share configurations easily
- 🌐 **Remote Repository**: Download scripts from online repositories
- 🔧 **Arduino Flasher**: Built-in Arduino sketch flashing tool
- 🔌 **Plug & Play**: Simple USB connection, no additional hardware required

## 🚀 Quick Start

### 1. Hardware Setup

**Components:**
- Arduino Nano (ATmega328P)
- Breadboard
- Push buttons (1-5)
- LEDs (optional, for feedback)
- Resistors (10kΩ pull-up, 220Ω for LEDs)

**Basic Wiring (1 Button):**
```
Arduino Pin 2  ← Button 1 → GND
Arduino Pin 10 ← LED 1 (with 220Ω resistor) → GND
```

**Multi-Button Wiring (up to 5 buttons):**
```
Button 1: Pin 2 → Button → GND (LED on Pin 10)
Button 2: Pin 3 → Button → GND (LED on Pin 11)
Button 3: Pin 4 → Button → GND (LED on Pin 12)
Button 4: Pin 5 → Button → GND (LED on Pin 13)
Button 5: Pin 6 → Button → GND (LED on Pin A0)
```

See `multi_button_wiring.txt` for detailed wiring instructions.

### 2. Software Installation

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

### 3. Arduino Programming

**Easy Way (Automatic):**
```bash
python3 flash_arduino.py
```

**Manual Way:**
1. Install Arduino CLI: `brew install arduino-cli`
2. Choose your sketch:
   - `midi_controller.ino` - Single button (Pin 2)
   - `midi_controller_multi.ino` - Multi button (Pins 2-6)
3. Flash using Arduino IDE or CLI

### 4. Configuration

**Interactive Setup:**
```bash
python3 setup.py
```

**Run the Controller:**
```bash
python3 bridge.py
```

## 📋 Available Scripts

### System Scripts
- `open_terminal` - Opens terminal with greeting
- `logout_user` - Logs out current user (⚠️ with confirmation)
- `lock_screen` - Locks the screen
- `screenshot` - Takes screenshot to desktop

### Application Scripts
- `open_browser` - Opens default browser
- `open_vscode` - Launches Visual Studio Code
- `volume_control` - Controls system volume (mute/up/down)

### Media Scripts
- `music_control` - Controls music playback (play/pause/next/previous)

### Fun Scripts
- `rickroll` - Opens Rick Roll video (prank script)
- `random_joke` - Displays random programming jokes
- `weather` - Shows current weather information

### Templates
- System: shutdown, restart
- Applications: calculator, text editor, notepad
- Development: git status, npm commands
- Fun: random jokes, weather

## 🔧 Configuration

### Arduino Flasher Tool

The built-in flasher automatically handles:
- Arduino CLI installation (via Homebrew)
- Library installation (MIDI Library)
- Sketch compilation and upload
- Port detection and selection

```bash
python3 flash_arduino.py
```

### Interactive Setup Tool

The modern setup tool provides:
- **Button Configuration**: Auto-detect Arduino ports and configure buttons
- **Script Management**: View, edit, and manage available scripts
- **System Settings**: Configure serial communication and platform detection
- **Test Configuration**: Validate setup before use
- **Import/Export**: Backup and restore configurations

### Button Configuration

Each button can be configured with:
- **Port**: Arduino serial port
- **Control Number**: MIDI control change number (1-5)
- **Script**: Associated macro script
- **Status**: Enabled/disabled

Configuration is stored in `config.json`:

```json
{
  "os": "Darwin",
  "buttons": {
    "1": {
      "port": "/dev/cu.usbserial-10",
      "control_number": 1,
      "script": "open_terminal",
      "enabled": true,
      "description": "Open Terminal with hello world"
    },
    "2": {
      "port": "/dev/cu.usbserial-10", 
      "control_number": 2,
      "script": "screenshot",
      "enabled": true,
      "description": "Take screenshot"
    }
  },
  "settings": {
    "serial_timeout": 1,
    "baud_rate": 31250,
    "debug_mode": false
  }
}
```

## 📝 Creating Custom Scripts

### Using the Script Editor

```bash
python3 setup.py
# Select "Manage Scripts" → "Create New Script"
```

### Manual Script Creation

Create a new `.py` file in the `scripts/` directory:

```python
"""
Script: my_custom_script.py
Description: My custom automation
Author: Your Name
"""

import subprocess
import platform

def execute():
    """Main execution function"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        subprocess.run(["open", "-a", "Calculator"])
    elif system == "Linux":
        subprocess.run(["gnome-calculator"])
    elif system == "Windows":
        subprocess.run(["calc.exe"])

def get_metadata():
    """Returns script metadata"""
    return {
        "name": "My Custom Script",
        "description": "Opens calculator application",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "application",
        "version": "1.0",
        "author": "Your Name"
    }

def is_supported():
    """Check if script is supported on current OS"""
    return platform.system() in get_metadata()["supported_os"]
```

## 🔧 Arduino Sketches

### Single Button Controller (`midi_controller.ino`)
- **Buttons**: 1 button on Pin 2
- **LEDs**: 1 LED on Pin 10
- **MIDI**: Control Change 1

### Multi Button Controller (`midi_controller_multi.ino`)
- **Buttons**: Up to 5 buttons on Pins 2-6
- **LEDs**: Up to 5 LEDs on Pins 10-13, A0
- **MIDI**: Control Changes 1-5

## 🌐 Remote Repository

Download scripts from online repositories:

```bash
python3 setup.py
# Select "Manage Scripts" → "Remote Repository"
```

## 🔄 Import/Export

### Export Configuration
```bash
python3 setup.py
# Select "System Settings" → "Export Configuration"
```

### Import Configuration
```bash
python3 setup.py
# Select "System Settings" → "Import Configuration"
```

## 🛠️ Advanced Usage

### Multiple Button Example

```json
{
  "buttons": {
    "1": {"port": "/dev/cu.usbserial-10", "script": "open_terminal", "control_number": 1},
    "2": {"port": "/dev/cu.usbserial-10", "script": "screenshot", "control_number": 2},
    "3": {"port": "/dev/cu.usbserial-10", "script": "volume_control", "control_number": 3},
    "4": {"port": "/dev/cu.usbserial-10", "script": "music_control", "control_number": 4},
    "5": {"port": "/dev/cu.usbserial-10", "script": "weather", "control_number": 5}
  }
}
```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
python3 setup.py
# Select "System Settings" → "Debug Mode"
```

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Arduino not detected | Check drivers, try different USB port |
| Button not responding | Verify wiring, check pull-up resistors |
| Script fails to execute | Check script syntax, verify OS compatibility |
| Multiple buttons not working | Flash multi-button sketch (`midi_controller_multi.ino`) |
| Permission denied | Run with appropriate permissions |

### Debug Commands

```bash
# Test serial connection
python3 -c "from utils.serial_manager import SerialManager; sm = SerialManager(); print(sm.discover_ports())"

# Flash Arduino automatically
python3 flash_arduino.py

# Validate script
python3 -c "from utils.script_loader import ScriptLoader; sl = ScriptLoader(); print(sl.validate_script_file('scripts/my_script.py'))"

# Check configuration
python3 -c "from utils.config_manager import ConfigManager; cm = ConfigManager(); print(cm.load_config())"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

### Script Contributions

Share your custom scripts:

1. Create script following the standard interface
2. Add to `templates/` directory
3. Include documentation and examples
4. Test on multiple platforms

## 📄 License

Open Source - Free for personal and commercial use.

## 🙏 Acknowledgments

- Built with [Rich](https://rich.readthedocs.io/) for beautiful console output
- [Inquirer](https://python-inquirer.readthedocs.io/) for interactive prompts
- [PySerial](https://pyserial.readthedocs.io/) for Arduino communication
- [Arduino CLI](https://arduino.github.io/arduino-cli/) for automated flashing
- MIDI Library by FortySevenEffects for Arduino

## 📞 Support

- 📖 Documentation: See `docs/` directory
- 🐛 Issues: Report on GitHub
- 💬 Discussions: GitHub Discussions
- 📧 Email: Support via GitHub

---

*Created with ❤️ for makers, developers, and productivity enthusiasts*