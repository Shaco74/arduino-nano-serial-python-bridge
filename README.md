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
- 🔌 **Plug & Play**: Simple USB connection, no additional hardware required

## 🚀 Quick Start

### 1. Hardware Setup

**Components:**
- Arduino Nano (ATmega328P)
- Breadboard
- Push buttons (1-5)
- LEDs (optional, for feedback)
- Resistors (10kΩ pull-up, 220Ω for LEDs)

**Basic Wiring:**
```
Arduino Pin 2  ← Button 1 → GND
Arduino Pin 10 ← LED 1 (with 220Ω resistor) → GND
```

See `wiring_diagram.txt` for detailed wiring instructions.

### 2. Software Installation

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

**Install Arduino IDE:**
```bash
# macOS
brew install --cask arduino-ide

# Or download from https://www.arduino.cc/en/software
```

### 3. Arduino Programming

1. Open `midi_controller/midi_controller.ino` in Arduino IDE
2. Install MIDI Library: Tools → Manage Libraries → Search "MIDI Library"
3. Select Board: Arduino Nano
4. Select Processor: ATmega328P (Old Bootloader)
5. Upload the code

### 4. Configuration

**Interactive Setup:**
```bash
python3 setup.py
```

**Manual Configuration:**
```bash
# Test connection
python3 bridge.py

# If no config exists, create one first with setup.py
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

### Templates
- System: shutdown, restart
- Applications: calculator, text editor
- Development: git status, npm commands
- Fun: random jokes, quotes

## 🔧 Configuration

### Interactive Setup Tool

The modern setup tool provides:

- **Button Configuration**: Auto-detect Arduino ports and configure buttons
- **Script Management**: View, edit, and manage available scripts
- **System Settings**: Configure serial communication and platform detection
- **Test Configuration**: Validate setup before use
- **Import/Export**: Backup and restore configurations

### Manual Configuration

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

## 🌐 Remote Repository

Download scripts from online repositories:

```bash
python3 setup.py
# Select "Manage Scripts" → "Remote Repository"
```

Features:
- Search across multiple repositories
- Download progress tracking
- Automatic updates
- Repository statistics

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

Export files include:
- Complete configuration
- All custom scripts
- System metadata
- Platform information

## 🛠️ Advanced Usage

### Multiple Arduino Devices

Configure multiple Arduino Nanos on different ports:

```json
{
  "buttons": {
    "1": {"port": "/dev/cu.usbserial-10", "script": "open_terminal"},
    "2": {"port": "/dev/cu.usbserial-20", "script": "screenshot"}
  }
}
```

### Script Parameters

Pass parameters to scripts:

```python
def execute(volume_level=50):
    """Script with parameters"""
    # Use volume_level parameter
    pass
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
| Permission denied | Run with appropriate permissions |

### Debug Commands

```bash
# Test serial connection
python3 -c "from utils.serial_manager import SerialManager; sm = SerialManager(); print(sm.discover_ports())"

# Validate script
python3 -c "from utils.script_loader import ScriptLoader; sl = ScriptLoader(); print(sl.validate_script_file('scripts/my_script.py'))"

# Check configuration
python3 -c "from utils.config_manager import ConfigManager; cm = ConfigManager(); print(cm.load_config())"
```

### Log Files

- Configuration: `config.json`
- Exports: `exports/` directory
- Cache: `.cache/` directory

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
- MIDI Library by FortySevenEffects for Arduino

## 📞 Support

- 📖 Documentation: See `docs/` directory
- 🐛 Issues: Report on GitHub
- 💬 Discussions: GitHub Discussions
- 📧 Email: Support via GitHub

---

*Created with ❤️ for makers, developers, and productivity enthusiasts*