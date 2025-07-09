# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modern, user-friendly Arduino Nano MIDI Controller system that converts button presses into customizable PC macros. The system has evolved from a basic serial communication setup to a comprehensive automation platform.

### Architecture Components

1. **Arduino Code** (`midi_controller/midi_controller.ino`) - MIDI Control Change messages over USB serial
2. **Core Infrastructure** (`utils/`) - Configuration, serial communication, and script management
3. **Main Applications** - Interactive setup tool and runtime bridge
4. **Script System** - Plugin-based macro execution with templates and remote repository support
5. **Advanced Features** - Script editor, import/export, and repository management

## Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Interactive setup (modern UI)
python3 setup.py

# Run main application
python3 bridge.py
```

### Arduino Development
```bash
# Install Arduino IDE
brew install --cask arduino-ide

# Upload process:
# 1. Open midi_controller/midi_controller.ino
# 2. Install MIDI Library (Tools → Manage Libraries → "MIDI Library")
# 3. Board: Arduino Nano, Processor: ATmega328P (Old Bootloader)
# 4. Upload to device
```

### Development and Testing
```bash
# Test serial connection
python3 -c "from utils.serial_manager import SerialManager; sm = SerialManager(); print(sm.discover_ports())"

# Validate script
python3 -c "from utils.script_loader import ScriptLoader; sl = ScriptLoader(); print(sl.validate_script_file('scripts/my_script.py'))"

# Check configuration
python3 -c "from utils.config_manager import ConfigManager; cm = ConfigManager(); print(cm.load_config())"

# Run specific script
python3 -c "from utils.script_loader import ScriptLoader; sl = ScriptLoader(); sl.load_script('script_name'); sl.execute_script('script_name')"
```

## System Architecture

### Core Infrastructure (Phase 1)
- **ConfigManager** (`utils/config_manager.py`) - JSON-based configuration with validation
- **SerialManager** (`utils/serial_manager.py`) - Thread-safe Arduino communication with MIDI parsing
- **ScriptLoader** (`utils/script_loader.py`) - Dynamic script loading with interface validation
- **Main Bridge** (`bridge.py`) - Runtime application with Rich UI and live monitoring

### Script System (Phase 2)
- **Standard Interface** - All scripts implement `execute()`, `get_metadata()`, `is_supported()`
- **Cross-Platform Support** - macOS, Linux, Windows implementations
- **Categories** - System, Application, Development, Fun, Custom
- **Templates** - Pre-built examples in `templates/` directory
- **Core Scripts** - Essential automation in `scripts/` directory

### User Experience (Phase 3)
- **Interactive Setup** (`setup.py`) - Modern console UI with Rich and Inquirer
- **Live Monitoring** - Real-time status display with connection and button states
- **Error Handling** - Comprehensive validation and user feedback
- **Multi-Platform** - Auto-detection and platform-specific optimizations

### Advanced Features (Phase 4)
- **Script Editor** (`utils/script_editor.py`) - Create, edit, validate custom scripts
- **Config Export** (`utils/config_export.py`) - Backup and sharing with ZIP format
- **Remote Repository** (`utils/remote_repository.py`) - Download scripts from online repos
- **Extensibility** - Plugin architecture for future enhancements

## Key Configuration

### Hardware Interface
- **Button Pins**: 2, 3, 4, 5, 6 (configurable, with INPUT_PULLUP)
- **LED Pins**: 10, 11, 12, 13, A0 (configurable outputs)
- **Serial Communication**: 31250 baud (MIDI standard)
- **MIDI Channel**: 1 (configurable)

### Software Configuration
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

### Script Interface Standard
```python
def execute(**kwargs):
    """Main execution function - called on button press"""
    pass

def get_metadata():
    """Returns script metadata dictionary"""
    return {
        "name": "Script Name",
        "description": "What the script does",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "system|application|development|fun|custom",
        "version": "1.0",
        "author": "Author Name"
    }

def is_supported():
    """Check if script is supported on current OS"""
    return platform.system() in get_metadata()["supported_os"]
```

## Extending the System

### Adding New Scripts
1. Create `.py` file in `scripts/` directory
2. Implement standard interface (execute, get_metadata, is_supported)
3. Add cross-platform implementations
4. Test with `setup.py` → "Test Configuration"

### Adding New Hardware
1. Update Arduino code with new pin definitions
2. Send different MIDI Control Change numbers
3. Add button configuration in `setup.py`
4. Test serial communication

### Adding New Features
1. Create utility module in `utils/`
2. Add to main applications (`setup.py`, `bridge.py`)
3. Update configuration schema if needed
4. Add tests and documentation

## File Structure
```
arduino-nano-macro-controller/
├── setup.py                    # Interactive setup tool
├── bridge.py                   # Main runtime application
├── config.json                 # Configuration (generated)
├── requirements.txt            # Python dependencies
├── utils/                      # Core infrastructure
│   ├── config_manager.py       # Configuration management
│   ├── serial_manager.py       # Arduino communication
│   ├── script_loader.py        # Script loading and execution
│   ├── script_editor.py        # Script creation and editing
│   ├── config_export.py        # Import/export functionality
│   └── remote_repository.py    # Remote script downloads
├── scripts/                    # User scripts
│   ├── open_terminal.py        # Terminal launcher
│   ├── screenshot.py           # Screen capture
│   ├── volume_control.py       # System volume
│   └── ...                     # Additional scripts
├── templates/                  # Script templates
│   ├── system/                 # System automation
│   ├── applications/           # App launchers
│   ├── development/            # Dev tools
│   └── fun/                    # Entertainment
├── midi_controller/            # Arduino code
│   └── midi_controller.ino     # Main sketch
├── exports/                    # Configuration exports
├── .cache/                     # Repository cache
└── docs/                       # Documentation
```

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use type hints for function parameters and returns
- Include comprehensive docstrings
- Handle exceptions gracefully with user-friendly messages

### Error Handling
- Use Rich console for consistent error display
- Provide actionable error messages
- Include debug information when debug_mode is enabled
- Graceful degradation when features are unavailable

### Cross-Platform Considerations
- Test on macOS, Linux, and Windows
- Use `platform.system()` for OS detection
- Provide fallbacks for missing system tools
- Handle path differences properly

### Security
- Validate all user inputs
- Sanitize file paths and script names
- Use subprocess.run() with explicit arguments
- Never execute arbitrary code strings

## Testing

### Manual Testing
1. Test setup.py interactive flows
2. Verify Arduino communication on multiple ports
3. Test script execution on different platforms
4. Validate import/export functionality

### Automated Testing
1. Script interface validation
2. Configuration file integrity
3. Serial communication mocking
4. Cross-platform compatibility

## Performance Considerations

- Script loading is cached after first load
- Serial monitoring runs in separate thread
- Configuration is saved only when changed
- Remote repository responses are cached
- Large exports are streamed to avoid memory issues