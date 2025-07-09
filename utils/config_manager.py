"""
Configuration manager for Arduino Nano Macro Controller.

This module handles loading, saving, and validating configuration files.
"""

import json
import os
import platform
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages configuration file operations and validation."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._default_config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration structure.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "os": platform.system(),
            "last_updated": datetime.now().isoformat(),
            "buttons": {},
            "settings": {
                "serial_timeout": 1,
                "baud_rate": 31250,
                "debug_mode": False
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default if not exists.
        
        Returns:
            Configuration dictionary
        """
        if not self.config_path.exists():
            self.config = self._default_config.copy()
            self.save_config()
        else:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # Validate and merge with defaults
                self._validate_config()
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading config: {e}")
                self.config = self._default_config.copy()
                self.save_config()
        
        return self.config
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        self.config["last_updated"] = datetime.now().isoformat()
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _validate_config(self) -> None:
        """Validate configuration and merge with defaults for missing keys."""
        # Ensure all required top-level keys exist
        for key, value in self._default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # Validate settings section
        if "settings" not in self.config:
            self.config["settings"] = self._default_config["settings"]
        else:
            for key, value in self._default_config["settings"].items():
                if key not in self.config["settings"]:
                    self.config["settings"][key] = value
    
    def get_button_config(self, button_id: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific button.
        
        Args:
            button_id: Button identifier (1-5)
            
        Returns:
            Button configuration or None if not found
        """
        return self.config.get("buttons", {}).get(button_id)
    
    def set_button_config(self, button_id: str, config: Dict[str, Any]) -> None:
        """
        Set configuration for a specific button.
        
        Args:
            button_id: Button identifier (1-5)
            config: Button configuration dictionary
        """
        if "buttons" not in self.config:
            self.config["buttons"] = {}
        
        self.config["buttons"][button_id] = config
        self.save_config()
    
    def remove_button_config(self, button_id: str) -> None:
        """
        Remove configuration for a specific button.
        
        Args:
            button_id: Button identifier to remove
        """
        if "buttons" in self.config and button_id in self.config["buttons"]:
            del self.config["buttons"][button_id]
            self.save_config()
    
    def get_all_buttons(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all button configurations.
        
        Returns:
            Dictionary of all button configurations
        """
        return self.config.get("buttons", {})
    
    def get_setting(self, key: str) -> Any:
        """
        Get a specific setting value.
        
        Args:
            key: Setting key name
            
        Returns:
            Setting value or None if not found
        """
        return self.config.get("settings", {}).get(key)
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a specific setting value.
        
        Args:
            key: Setting key name
            value: Setting value
        """
        if "settings" not in self.config:
            self.config["settings"] = {}
        
        self.config["settings"][key] = value
        self.save_config()
    
    def is_button_configured(self, button_id: str) -> bool:
        """
        Check if a button is configured.
        
        Args:
            button_id: Button identifier
            
        Returns:
            True if button is configured, False otherwise
        """
        button_config = self.get_button_config(button_id)
        return button_config is not None and button_config.get("enabled", False)
    
    def get_configured_buttons(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all configured and enabled buttons.
        
        Returns:
            Dictionary of configured buttons
        """
        configured = {}
        for button_id, config in self.get_all_buttons().items():
            if config.get("enabled", False):
                configured[button_id] = config
        return configured