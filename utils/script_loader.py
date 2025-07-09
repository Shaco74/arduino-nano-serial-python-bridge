"""
Script loader and executor for Arduino Nano Macro Controller.

This module handles loading, validating, and executing user scripts.
"""

import os
import sys
import importlib.util
import inspect
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from rich.console import Console


class ScriptLoader:
    """Manages loading and execution of user scripts."""
    
    def __init__(self, scripts_dir: str = "scripts"):
        """
        Initialize the script loader.
        
        Args:
            scripts_dir: Directory containing script files
        """
        self.scripts_dir = Path(scripts_dir)
        self.console = Console()
        self.loaded_scripts: Dict[str, Dict[str, Any]] = {}
        self.script_modules: Dict[str, Any] = {}
        
        # Create scripts directory if it doesn't exist
        self.scripts_dir.mkdir(exist_ok=True)
    
    def discover_scripts(self) -> List[str]:
        """
        Discover all Python script files in the scripts directory.
        
        Returns:
            List of script names (without .py extension)
        """
        scripts = []
        for file_path in self.scripts_dir.glob("*.py"):
            if file_path.name != "__init__.py":
                scripts.append(file_path.stem)
        return scripts
    
    def load_script(self, script_name: str) -> bool:
        """
        Load a script module and validate its interface.
        
        Args:
            script_name: Name of the script (without .py extension)
            
        Returns:
            True if script loaded successfully, False otherwise
        """
        script_path = self.scripts_dir / f"{script_name}.py"
        
        if not script_path.exists():
            self.console.print(f"✗ Script not found: {script_name}", style="red")
            return False
        
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(script_name, script_path)
            if spec is None or spec.loader is None:
                self.console.print(f"✗ Failed to load spec for: {script_name}", style="red")
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Validate required functions
            if not self._validate_script_interface(module, script_name):
                return False
            
            # Store module and metadata
            self.script_modules[script_name] = module
            
            # Get script metadata
            metadata = self._get_script_metadata(module, script_name)
            self.loaded_scripts[script_name] = metadata
            
            self.console.print(f"✓ Loaded script: {script_name}", style="green")
            return True
            
        except Exception as e:
            self.console.print(f"✗ Error loading script {script_name}: {e}", style="red")
            return False
    
    def _validate_script_interface(self, module: Any, script_name: str) -> bool:
        """
        Validate that a script module has the required interface.
        
        Args:
            module: The loaded module
            script_name: Name of the script
            
        Returns:
            True if interface is valid, False otherwise
        """
        required_functions = ["execute", "get_metadata", "is_supported"]
        
        for func_name in required_functions:
            if not hasattr(module, func_name):
                self.console.print(
                    f"✗ Script {script_name} missing required function: {func_name}",
                    style="red"
                )
                return False
            
            # Check if it's callable
            if not callable(getattr(module, func_name)):
                self.console.print(
                    f"✗ Script {script_name} {func_name} is not callable",
                    style="red"
                )
                return False
        
        return True
    
    def _get_script_metadata(self, module: Any, script_name: str) -> Dict[str, Any]:
        """
        Get metadata from a script module.
        
        Args:
            module: The loaded module
            script_name: Name of the script
            
        Returns:
            Script metadata dictionary
        """
        try:
            metadata = module.get_metadata()
            
            # Add additional info
            metadata["script_name"] = script_name
            metadata["is_supported"] = module.is_supported()
            metadata["file_path"] = str(self.scripts_dir / f"{script_name}.py")
            
            # Get docstring if available
            if hasattr(module, "__doc__") and module.__doc__:
                metadata["docstring"] = module.__doc__.strip()
            
            return metadata
            
        except Exception as e:
            self.console.print(f"✗ Error getting metadata for {script_name}: {e}", style="red")
            return {
                "name": script_name,
                "description": "No description available",
                "supported_os": [],
                "category": "unknown",
                "version": "unknown",
                "script_name": script_name,
                "is_supported": False,
                "file_path": str(self.scripts_dir / f"{script_name}.py")
            }
    
    def load_all_scripts(self) -> int:
        """
        Load all scripts from the scripts directory.
        
        Returns:
            Number of successfully loaded scripts
        """
        scripts = self.discover_scripts()
        loaded_count = 0
        
        for script_name in scripts:
            if self.load_script(script_name):
                loaded_count += 1
        
        self.console.print(f"📦 Loaded {loaded_count}/{len(scripts)} scripts", style="blue")
        return loaded_count
    
    def execute_script(self, script_name: str, **kwargs) -> bool:
        """
        Execute a loaded script.
        
        Args:
            script_name: Name of the script to execute
            **kwargs: Additional arguments to pass to the script
            
        Returns:
            True if script executed successfully, False otherwise
        """
        if script_name not in self.script_modules:
            self.console.print(f"✗ Script not loaded: {script_name}", style="red")
            return False
        
        if script_name not in self.loaded_scripts:
            self.console.print(f"✗ Script metadata not available: {script_name}", style="red")
            return False
        
        # Check if script is supported on current OS
        if not self.loaded_scripts[script_name]["is_supported"]:
            self.console.print(f"✗ Script not supported on current OS: {script_name}", style="red")
            return False
        
        try:
            module = self.script_modules[script_name]
            
            # Get the execute function signature
            execute_func = getattr(module, "execute")
            sig = inspect.signature(execute_func)
            
            # Filter kwargs to only include parameters the function accepts
            filtered_kwargs = {}
            for param_name in sig.parameters:
                if param_name in kwargs:
                    filtered_kwargs[param_name] = kwargs[param_name]
            
            # Execute the script
            result = execute_func(**filtered_kwargs)
            
            self.console.print(f"✓ Executed script: {script_name}", style="green")
            return True
            
        except Exception as e:
            self.console.print(f"✗ Error executing script {script_name}: {e}", style="red")
            return False
    
    def get_script_metadata(self, script_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific script.
        
        Args:
            script_name: Name of the script
            
        Returns:
            Script metadata or None if not found
        """
        return self.loaded_scripts.get(script_name)
    
    def get_all_scripts(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all loaded scripts.
        
        Returns:
            Dictionary of script metadata
        """
        return self.loaded_scripts.copy()
    
    def get_scripts_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """
        Get scripts filtered by category.
        
        Args:
            category: Category name to filter by
            
        Returns:
            Dictionary of matching scripts
        """
        filtered = {}
        for script_name, metadata in self.loaded_scripts.items():
            if metadata.get("category", "").lower() == category.lower():
                filtered[script_name] = metadata
        return filtered
    
    def get_supported_scripts(self) -> Dict[str, Dict[str, Any]]:
        """
        Get only scripts that are supported on the current OS.
        
        Returns:
            Dictionary of supported scripts
        """
        supported = {}
        for script_name, metadata in self.loaded_scripts.items():
            if metadata.get("is_supported", False):
                supported[script_name] = metadata
        return supported
    
    def reload_script(self, script_name: str) -> bool:
        """
        Reload a script (useful for development).
        
        Args:
            script_name: Name of the script to reload
            
        Returns:
            True if reload successful, False otherwise
        """
        # Remove from loaded scripts
        if script_name in self.loaded_scripts:
            del self.loaded_scripts[script_name]
        
        if script_name in self.script_modules:
            del self.script_modules[script_name]
        
        # Reload
        return self.load_script(script_name)
    
    def unload_script(self, script_name: str) -> None:
        """
        Unload a script from memory.
        
        Args:
            script_name: Name of the script to unload
        """
        if script_name in self.loaded_scripts:
            del self.loaded_scripts[script_name]
        
        if script_name in self.script_modules:
            del self.script_modules[script_name]
        
        self.console.print(f"📤 Unloaded script: {script_name}", style="yellow")
    
    def validate_script_file(self, script_path: Path) -> bool:
        """
        Validate a script file without loading it.
        
        Args:
            script_path: Path to the script file
            
        Returns:
            True if script is valid, False otherwise
        """
        if not script_path.exists():
            return False
        
        try:
            # Try to compile the file
            with open(script_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            compile(code, str(script_path), 'exec')
            return True
            
        except Exception as e:
            self.console.print(f"✗ Script validation failed for {script_path}: {e}", style="red")
            return False