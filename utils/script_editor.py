"""
Script editor utilities for Arduino Nano Macro Controller.

This module provides functionality to create, edit, and validate custom scripts.
"""

import os
import tempfile
import subprocess
import platform
from typing import Dict, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.syntax import Syntax


class ScriptEditor:
    """Provides script editing and creation functionality."""
    
    def __init__(self, scripts_dir: str = "scripts"):
        """
        Initialize the script editor.
        
        Args:
            scripts_dir: Directory containing script files
        """
        self.scripts_dir = Path(scripts_dir)
        self.console = Console()
        self.templates_dir = Path("templates")
        
        # Create directories if they don't exist
        self.scripts_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
    
    def create_script_template(self, script_name: str, category: str = "custom") -> str:
        """
        Create a basic script template.
        
        Args:
            script_name: Name of the script
            category: Script category
            
        Returns:
            Template string
        """
        template = f'''"""
Script: {script_name}.py
Description: Custom script created by user
Author: User
Platform: Cross-platform
Category: {category.title()}
"""

import subprocess
import platform


def execute():
    """
    Main execution function - implement your custom logic here.
    
    This function will be called when the button is pressed.
    Add your custom code below.
    """
    system = platform.system()
    
    # Example: Display a message
    if system == "Darwin":  # macOS
        subprocess.run([
            "osascript", "-e", 
            'display dialog "Hello from {script_name}!" with title "Custom Script" buttons {{"OK"}} default button "OK"'
        ])
    elif system == "Linux":
        try:
            subprocess.run(["notify-send", "Custom Script", "Hello from {script_name}!"])
        except FileNotFoundError:
            subprocess.run([
                "xterm", "-e", "bash", "-c", 
                'echo "Hello from {script_name}!"; read -p "Press Enter to continue..."'
            ])
    elif system == "Windows":
        subprocess.run([
            "powershell", "-Command", 
            f'Add-Type -AssemblyName System.Windows.Forms; '
            f'[System.Windows.Forms.MessageBox]::Show("Hello from {script_name}!", "Custom Script")'
        ])
    
    # Add your custom code here
    # Examples:
    # - Open applications: subprocess.run(["open", "-a", "Calculator"])
    # - Execute shell commands: subprocess.run(["echo", "hello"])
    # - Send notifications: subprocess.run(["notify-send", "Title", "Message"])


def get_metadata():
    """
    Returns script metadata.
    
    Returns:
        dict: Script metadata including name, description, and compatibility
    """
    return {{
        "name": "{script_name.title().replace('_', ' ')}",
        "description": "Custom script created by user",
        "supported_os": ["Darwin", "Linux", "Windows"],
        "category": "{category}",
        "version": "1.0",
        "author": "User"
    }}


def is_supported():
    """
    Check if script is supported on current OS.
    
    Returns:
        bool: True if script is supported on current OS, False otherwise
    """
    return platform.system() in get_metadata()["supported_os"]
'''
        return template
    
    def create_new_script(self, script_name: str, category: str = "custom") -> bool:
        """
        Create a new script file.
        
        Args:
            script_name: Name of the script
            category: Script category
            
        Returns:
            True if script created successfully, False otherwise
        """
        if not script_name.replace('_', '').isalnum():
            self.console.print("❌ Script name must contain only letters, numbers, and underscores", style="red")
            return False
        
        script_path = self.scripts_dir / f"{script_name}.py"
        
        if script_path.exists():
            if not Confirm.ask(f"Script '{script_name}' already exists. Overwrite?"):
                return False
        
        try:
            template = self.create_script_template(script_name, category)
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(template)
            
            self.console.print(f"✅ Script '{script_name}' created at {script_path}", style="green")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error creating script: {e}", style="red")
            return False
    
    def edit_script(self, script_name: str) -> bool:
        """
        Edit an existing script using system editor.
        
        Args:
            script_name: Name of the script to edit
            
        Returns:
            True if editing was successful, False otherwise
        """
        script_path = self.scripts_dir / f"{script_name}.py"
        
        if not script_path.exists():
            self.console.print(f"❌ Script '{script_name}' not found", style="red")
            return False
        
        # Determine the best editor to use
        editor = self._get_system_editor()
        
        try:
            # Open the file in the editor
            subprocess.run([editor, str(script_path)], check=True)
            self.console.print(f"✅ Script '{script_name}' edited", style="green")
            return True
            
        except subprocess.CalledProcessError:
            self.console.print(f"❌ Error opening editor: {editor}", style="red")
            return False
        except FileNotFoundError:
            self.console.print(f"❌ Editor not found: {editor}", style="red")
            return False
    
    def _get_system_editor(self) -> str:
        """
        Get the best available editor for the system.
        
        Returns:
            Editor command string
        """
        system = platform.system()
        
        # Check for environment variable first
        if 'EDITOR' in os.environ:
            return os.environ['EDITOR']
        
        # System-specific editors
        if system == "Darwin":  # macOS
            editors = ["code", "subl", "atom", "nano", "vim", "open"]
        elif system == "Linux":
            editors = ["code", "gedit", "kate", "subl", "atom", "nano", "vim"]
        elif system == "Windows":
            editors = ["code", "notepad++", "notepad", "vim"]
        else:
            editors = ["nano", "vim"]
        
        # Find the first available editor
        for editor in editors:
            try:
                subprocess.run([editor, "--version"], 
                              capture_output=True, check=True)
                return editor
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        # Fallback
        return "nano" if system != "Windows" else "notepad"
    
    def view_script(self, script_name: str) -> bool:
        """
        View script contents with syntax highlighting.
        
        Args:
            script_name: Name of the script to view
            
        Returns:
            True if script was displayed, False otherwise
        """
        script_path = self.scripts_dir / f"{script_name}.py"
        
        if not script_path.exists():
            self.console.print(f"❌ Script '{script_name}' not found", style="red")
            return False
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Display with syntax highlighting
            syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
            
            self.console.print(Panel(
                syntax,
                title=f"Script: {script_name}.py",
                border_style="blue"
            ))
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error reading script: {e}", style="red")
            return False
    
    def validate_script(self, script_name: str) -> bool:
        """
        Validate script syntax and interface.
        
        Args:
            script_name: Name of the script to validate
            
        Returns:
            True if script is valid, False otherwise
        """
        script_path = self.scripts_dir / f"{script_name}.py"
        
        if not script_path.exists():
            self.console.print(f"❌ Script '{script_name}' not found", style="red")
            return False
        
        try:
            # Check syntax
            with open(script_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            compile(code, str(script_path), 'exec')
            self.console.print(f"✅ Syntax valid", style="green")
            
            # Check required functions
            required_functions = ['execute', 'get_metadata', 'is_supported']
            
            for func_name in required_functions:
                if f"def {func_name}(" not in code:
                    self.console.print(f"❌ Missing required function: {func_name}", style="red")
                    return False
            
            self.console.print(f"✅ Interface valid", style="green")
            
            # Try to import and test metadata
            import importlib.util
            spec = importlib.util.spec_from_file_location(script_name, script_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Test metadata function
                metadata = module.get_metadata()
                if not isinstance(metadata, dict):
                    self.console.print("❌ get_metadata() must return a dictionary", style="red")
                    return False
                
                # Test is_supported function
                supported = module.is_supported()
                if not isinstance(supported, bool):
                    self.console.print("❌ is_supported() must return a boolean", style="red")
                    return False
                
                self.console.print(f"✅ Script '{script_name}' is valid", style="green")
                return True
            
        except SyntaxError as e:
            self.console.print(f"❌ Syntax error: {e}", style="red")
            return False
        except Exception as e:
            self.console.print(f"❌ Validation error: {e}", style="red")
            return False
        
        return False
    
    def duplicate_script(self, source_script: str, new_name: str) -> bool:
        """
        Duplicate an existing script.
        
        Args:
            source_script: Name of the script to duplicate
            new_name: Name for the new script
            
        Returns:
            True if duplication was successful, False otherwise
        """
        source_path = self.scripts_dir / f"{source_script}.py"
        new_path = self.scripts_dir / f"{new_name}.py"
        
        if not source_path.exists():
            self.console.print(f"❌ Source script '{source_script}' not found", style="red")
            return False
        
        if new_path.exists():
            if not Confirm.ask(f"Script '{new_name}' already exists. Overwrite?"):
                return False
        
        try:
            with open(source_path, 'r', encoding='utf-8') as src:
                content = src.read()
            
            # Update script name in the content
            content = content.replace(f"Script: {source_script}.py", f"Script: {new_name}.py")
            
            with open(new_path, 'w', encoding='utf-8') as dst:
                dst.write(content)
            
            self.console.print(f"✅ Script duplicated as '{new_name}'", style="green")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error duplicating script: {e}", style="red")
            return False
    
    def delete_script(self, script_name: str) -> bool:
        """
        Delete a script file.
        
        Args:
            script_name: Name of the script to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        script_path = self.scripts_dir / f"{script_name}.py"
        
        if not script_path.exists():
            self.console.print(f"❌ Script '{script_name}' not found", style="red")
            return False
        
        if not Confirm.ask(f"Are you sure you want to delete '{script_name}'?"):
            return False
        
        try:
            script_path.unlink()
            self.console.print(f"✅ Script '{script_name}' deleted", style="green")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error deleting script: {e}", style="red")
            return False
    
    def get_script_categories(self) -> Dict[str, int]:
        """
        Get available script categories and their counts.
        
        Returns:
            Dictionary mapping category names to script counts
        """
        categories = {}
        
        for script_file in self.scripts_dir.glob("*.py"):
            if script_file.name == "__init__.py":
                continue
                
            try:
                with open(script_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract category from the header comment
                for line in content.split('\n'):
                    if line.strip().startswith('Category:'):
                        category = line.split(':', 1)[1].strip()
                        categories[category] = categories.get(category, 0) + 1
                        break
                else:
                    # Default category if not found
                    categories['Unknown'] = categories.get('Unknown', 0) + 1
                    
            except Exception:
                categories['Unknown'] = categories.get('Unknown', 0) + 1
        
        return categories