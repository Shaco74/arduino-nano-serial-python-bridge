# Arduino Nano Macro Controller - User-Friendly System Plan

## Vision
Transform the current basic system into a modern, user-friendly tool with:
- Interactive GUI setup
- Easy script management
- Multi-button support (1-5 buttons)
- Cross-platform script templates
- Modern console interface

## Architecture Overview

### Core Components

1. **Setup Script** (`setup.py`)
   - Interactive GUI for configuration
   - OS detection and port discovery
   - Button-to-script binding interface
   - Config file generation

2. **Main Bridge** (`bridge.py`)
   - Reads configuration from JSON
   - Manages serial connections
   - Executes bound scripts
   - Error handling and logging

3. **Configuration System** (`config.json`)
   - Stores button mappings
   - OS and port settings
   - Script bindings and preferences

4. **Script System** (`scripts/` directory)
   - Individual Python files for each macro
   - Standard interface for all scripts
   - Metadata and OS compatibility

5. **Templates** (`templates/` directory)
   - Pre-built scripts for common tasks
   - OS-specific implementations
   - Easy to copy and customize

## User Experience Flow

### Initial Setup
1. User runs `python3 setup.py`
2. System detects OS (or asks user)
3. Scans for available Arduino ports
4. Interactive menu for button configuration
5. Script selection and binding
6. Configuration saved to `config.json`

### Daily Usage
1. User runs `python3 bridge.py`
2. System loads config and connects to Arduino(s)
3. Button presses trigger bound scripts
4. Modern console output with status updates

### Script Management
1. User can re-run setup to modify bindings
2. Add/remove scripts from `scripts/` directory
3. Enable/disable scripts without rebinding
4. Create custom scripts using templates

## Technical Implementation

### Dependencies
```bash
pip install rich inquirer pyserial click pyyaml
```

- **rich**: Modern console output, colors, progress bars, tables
- **inquirer**: Interactive prompts and menus
- **pyserial**: Arduino communication
- **click**: CLI interface and commands
- **pyyaml**: Configuration file management

### Configuration Structure
```json
{
  "os": "Darwin",
  "last_updated": "2024-01-09T10:30:00Z",
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
      "script": "logout_user",
      "enabled": false,
      "description": "Logout current user"
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
Each script in `scripts/` follows this pattern:
```python
"""
Script: open_terminal.py
Description: Opens terminal and executes a command
Author: System
"""

import subprocess
import platform

def execute():
    """Main execution function"""
    system = platform.system()
    if system == "Darwin":
        subprocess.run(["osascript", "-e", 'tell application "Terminal" to do script "echo Hello from Arduino!"'])
    elif system == "Linux":
        subprocess.run(["gnome-terminal", "--", "bash", "-c", "echo Hello from Arduino!; read"])
    elif system == "Windows":
        subprocess.run(["cmd", "/c", "start", "cmd", "/k", "echo Hello from Arduino!"])

def get_metadata():
    """Returns script metadata"""
    return {
        "name": "Open Terminal",
        "description": "Opens terminal and displays a greeting",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "system",
        "version": "1.0"
    }

def is_supported():
    """Check if script is supported on current OS"""
    return platform.system() in get_metadata()["supported_os"]
```

## Example Scripts to Implement

### System Scripts
- `open_terminal.py` - Open terminal with custom command
- `logout_user.py` - Log out current user
- `lock_screen.py` - Lock the screen
- `shutdown.py` - Shutdown system
- `restart.py` - Restart system

### Application Scripts
- `open_browser.py` - Open default browser
- `open_calculator.py` - Open calculator
- `open_notepad.py` - Open text editor
- `screenshot.py` - Take screenshot
- `volume_control.py` - Volume up/down/mute

### Development Scripts
- `open_vscode.py` - Open VS Code
- `git_status.py` - Show git status in terminal
- `npm_dev.py` - Run npm dev in current project
- `docker_compose.py` - Start/stop Docker containers

### Fun Scripts
- `rickroll.py` - Open Rick Roll video
- `random_joke.py` - Display random joke
- `weather.py` - Show weather information
- `music_control.py` - Play/pause music

## Setup Script Flow

### Main Menu
```
┌─────────────────────────────────────────┐
│     Arduino Nano Macro Controller      │
│              Setup Tool                 │
├─────────────────────────────────────────┤
│                                         │
│  [1] Configure Buttons                  │
│  [2] Manage Scripts                     │
│  [3] System Settings                    │
│  [4] Test Configuration                 │
│  [5] Exit                               │
│                                         │
└─────────────────────────────────────────┘
```

### Button Configuration
```
┌─────────────────────────────────────────┐
│          Button Configuration          │
├─────────────────────────────────────────┤
│                                         │
│  Button 1: [CONFIGURED] ✓               │
│  Port: /dev/cu.usbserial-10             │
│  Script: open_terminal                  │
│  Status: Enabled                        │
│                                         │
│  Button 2: [NOT CONFIGURED] ✗           │
│  Port: None                             │
│  Script: None                           │
│  Status: Disabled                       │
│                                         │
│  [Configure Button] [Remove Button]     │
│  [Back to Main Menu]                    │
└─────────────────────────────────────────┘
```

### Script Management
```
┌─────────────────────────────────────────┐
│           Available Scripts             │
├─────────────────────────────────────────┤
│                                         │
│  ✓ open_terminal     [System]           │
│  ✓ logout_user       [System]           │
│  ✓ screenshot        [Media]            │
│  ✗ rickroll          [Fun]              │
│  ✓ open_vscode       [Development]      │
│                                         │
│  [Enable/Disable] [View Details]        │
│  [Create New Script] [Import Template]  │
│  [Back to Main Menu]                    │
└─────────────────────────────────────────┘
```

## File Structure
```
arduino-nano-macro-controller/
├── setup.py                 # Interactive setup GUI
├── bridge.py               # Main execution engine
├── config.json             # Configuration file
├── requirements.txt        # Python dependencies
├── scripts/                # User scripts directory
│   ├── open_terminal.py
│   ├── logout_user.py
│   ├── screenshot.py
│   └── ...
├── templates/              # Script templates
│   ├── system/
│   ├── applications/
│   ├── development/
│   └── fun/
├── utils/                  # Utility modules
│   ├── config_manager.py
│   ├── script_loader.py
│   └── serial_manager.py
├── midi_controller/        # Arduino code
│   └── midi_controller.ino
└── docs/                   # Documentation
    ├── README.md
    ├── setup_guide.md
    └── CLAUDE.md
```

## Development Phases

### Phase 1: Core Infrastructure
- [ ] Setup script with basic GUI
- [ ] Configuration system
- [ ] Script loader and executor
- [ ] Serial communication manager

### Phase 2: Script System
- [ ] Script interface standard
- [ ] Basic script templates
- [ ] Script metadata system
- [ ] Error handling and validation

### Phase 3: User Experience
- [ ] Modern console interface
- [ ] Interactive menus
- [ ] Progress indicators
- [ ] Status monitoring

### Phase 4: Advanced Features
- [ ] Script editor integration
- [ ] Custom script creation wizard
- [ ] Import/export configurations
- [ ] Remote script repository

## Modern Console Features

### Rich Console Elements
- **Colors**: Different colors for different message types
- **Progress Bars**: For setup and connection processes
- **Tables**: For displaying button configurations
- **Panels**: For grouping related information
- **Spinner**: For loading operations
- **Live Updates**: Real-time status monitoring

### Interactive Elements
- **Select Lists**: For choosing scripts and ports
- **Checkboxes**: For enabling/disabling features
- **Text Input**: For custom script parameters
- **Confirmation Dialogs**: For destructive actions
- **Multi-select**: For batch operations

## Success Metrics
- User can complete setup in under 5 minutes
- Adding new scripts takes less than 1 minute
- System works reliably across all supported OS
- Console output is clear and informative
- Configuration changes are intuitive and safe