"""
Configuration export/import utilities for Arduino Nano Macro Controller.

This module provides functionality to export and import configurations
for backup and sharing purposes.
"""

import json
import os
import shutil
import zipfile
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


class ConfigExporter:
    """Handles configuration export and import operations."""
    
    def __init__(self, config_manager, script_loader):
        """
        Initialize the configuration exporter.
        
        Args:
            config_manager: ConfigManager instance
            script_loader: ScriptLoader instance
        """
        self.config_manager = config_manager
        self.script_loader = script_loader
        self.console = Console()
        
        # Create exports directory
        self.exports_dir = Path("exports")
        self.exports_dir.mkdir(exist_ok=True)
    
    def export_configuration(self, include_scripts: bool = True, 
                           export_name: Optional[str] = None) -> Optional[str]:
        """
        Export current configuration to a zip file.
        
        Args:
            include_scripts: Whether to include script files
            export_name: Optional name for the export file
            
        Returns:
            Path to the exported file or None if failed
        """
        if not export_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_name = f"arduino_config_{timestamp}"
        
        export_path = self.exports_dir / f"{export_name}.zip"
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Exporting configuration...", total=None)
                
                with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Export configuration
                    config_data = self.config_manager.config.copy()
                    
                    # Add export metadata
                    config_data['export_info'] = {
                        'exported_at': datetime.now().isoformat(),
                        'version': '1.0',
                        'include_scripts': include_scripts,
                        'platform': self.config_manager.config.get('os', 'Unknown')
                    }
                    
                    # Write config to zip
                    config_json = json.dumps(config_data, indent=2)
                    zipf.writestr('config.json', config_json)
                    
                    # Export scripts if requested
                    if include_scripts:
                        scripts_dir = Path("scripts")
                        if scripts_dir.exists():
                            for script_file in scripts_dir.glob("*.py"):
                                if script_file.name != "__init__.py":
                                    zipf.write(script_file, f"scripts/{script_file.name}")
                    
                    # Export script metadata
                    scripts_metadata = {}
                    for script_name, metadata in self.script_loader.get_all_scripts().items():
                        scripts_metadata[script_name] = metadata
                    
                    metadata_json = json.dumps(scripts_metadata, indent=2)
                    zipf.writestr('scripts_metadata.json', metadata_json)
                    
                    # Export system info
                    system_info = {
                        'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
                        'platform': os.name,
                        'export_tool_version': '1.0'
                    }
                    
                    system_json = json.dumps(system_info, indent=2)
                    zipf.writestr('system_info.json', system_json)
                
                progress.update(task, completed=True)
            
            self.console.print(f"✅ Configuration exported to {export_path}", style="green")
            return str(export_path)
            
        except Exception as e:
            self.console.print(f"❌ Export failed: {e}", style="red")
            return None
    
    def import_configuration(self, import_path: str, 
                           merge_with_existing: bool = False) -> bool:
        """
        Import configuration from a zip file.
        
        Args:
            import_path: Path to the import file
            merge_with_existing: Whether to merge with existing config
            
        Returns:
            True if import was successful, False otherwise
        """
        import_file = Path(import_path)
        
        if not import_file.exists():
            self.console.print(f"❌ Import file not found: {import_path}", style="red")
            return False
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Importing configuration...", total=None)
                
                with zipfile.ZipFile(import_file, 'r') as zipf:
                    # Check if it's a valid export
                    if 'config.json' not in zipf.namelist():
                        self.console.print("❌ Invalid export file: config.json not found", style="red")
                        return False
                    
                    # Read configuration
                    config_data = json.loads(zipf.read('config.json').decode('utf-8'))
                    
                    # Validate export info
                    if 'export_info' not in config_data:
                        self.console.print("⚠️  Warning: No export info found", style="yellow")
                    else:
                        export_info = config_data['export_info']
                        self.console.print(f"📦 Importing config from {export_info.get('exported_at', 'Unknown date')}")
                        
                        # Check platform compatibility
                        source_platform = export_info.get('platform', 'Unknown')
                        current_platform = self.config_manager.config.get('os', 'Unknown')
                        
                        if source_platform != current_platform:
                            self.console.print(
                                f"⚠️  Platform mismatch: Source={source_platform}, Current={current_platform}",
                                style="yellow"
                            )
                    
                    # Backup current config
                    backup_path = self.exports_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                    self.export_configuration(include_scripts=True, 
                                            export_name=backup_path.stem)
                    
                    # Remove export_info from config before importing
                    if 'export_info' in config_data:
                        del config_data['export_info']
                    
                    # Import configuration
                    if merge_with_existing:
                        # Merge with existing config
                        current_config = self.config_manager.config.copy()
                        
                        # Merge buttons
                        if 'buttons' in config_data:
                            if 'buttons' not in current_config:
                                current_config['buttons'] = {}
                            current_config['buttons'].update(config_data['buttons'])
                        
                        # Merge settings
                        if 'settings' in config_data:
                            if 'settings' not in current_config:
                                current_config['settings'] = {}
                            current_config['settings'].update(config_data['settings'])
                        
                        # Update other fields
                        for key, value in config_data.items():
                            if key not in ['buttons', 'settings']:
                                current_config[key] = value
                        
                        self.config_manager.config = current_config
                    else:
                        # Replace entire config
                        self.config_manager.config = config_data
                    
                    # Save the new configuration
                    self.config_manager.save_config()
                    
                    # Import scripts if available
                    scripts_imported = 0
                    if 'scripts/' in str(zipf.namelist()):
                        scripts_dir = Path("scripts")
                        scripts_dir.mkdir(exist_ok=True)
                        
                        for file_info in zipf.infolist():
                            if file_info.filename.startswith('scripts/') and file_info.filename.endswith('.py'):
                                script_name = Path(file_info.filename).name
                                if script_name != "__init__.py":
                                    # Extract script file
                                    script_content = zipf.read(file_info).decode('utf-8')
                                    script_path = scripts_dir / script_name
                                    
                                    with open(script_path, 'w', encoding='utf-8') as f:
                                        f.write(script_content)
                                    
                                    scripts_imported += 1
                    
                    # Reload scripts
                    self.script_loader.load_all_scripts()
                
                progress.update(task, completed=True)
            
            self.console.print(f"✅ Configuration imported successfully", style="green")
            if scripts_imported > 0:
                self.console.print(f"📦 {scripts_imported} scripts imported", style="blue")
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Import failed: {e}", style="red")
            return False
    
    def list_exports(self) -> Dict[str, Dict[str, Any]]:
        """
        List available export files with their metadata.
        
        Returns:
            Dictionary mapping export names to their metadata
        """
        exports = {}
        
        for export_file in self.exports_dir.glob("*.zip"):
            try:
                with zipfile.ZipFile(export_file, 'r') as zipf:
                    if 'config.json' in zipf.namelist():
                        config_data = json.loads(zipf.read('config.json').decode('utf-8'))
                        export_info = config_data.get('export_info', {})
                        
                        exports[export_file.name] = {
                            'path': str(export_file),
                            'size': export_file.stat().st_size,
                            'created': datetime.fromtimestamp(export_file.stat().st_ctime),
                            'exported_at': export_info.get('exported_at', 'Unknown'),
                            'include_scripts': export_info.get('include_scripts', False),
                            'platform': export_info.get('platform', 'Unknown'),
                            'version': export_info.get('version', 'Unknown')
                        }
                        
            except Exception:
                # Skip invalid files
                continue
        
        return exports
    
    def delete_export(self, export_name: str) -> bool:
        """
        Delete an export file.
        
        Args:
            export_name: Name of the export file to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        export_path = self.exports_dir / export_name
        
        if not export_path.exists():
            self.console.print(f"❌ Export file not found: {export_name}", style="red")
            return False
        
        try:
            export_path.unlink()
            self.console.print(f"✅ Export file deleted: {export_name}", style="green")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error deleting export: {e}", style="red")
            return False
    
    def validate_export(self, export_path: str) -> bool:
        """
        Validate an export file.
        
        Args:
            export_path: Path to the export file
            
        Returns:
            True if export is valid, False otherwise
        """
        try:
            with zipfile.ZipFile(export_path, 'r') as zipf:
                # Check required files
                required_files = ['config.json']
                for required_file in required_files:
                    if required_file not in zipf.namelist():
                        self.console.print(f"❌ Missing required file: {required_file}", style="red")
                        return False
                
                # Validate config.json
                config_data = json.loads(zipf.read('config.json').decode('utf-8'))
                
                # Check basic structure
                if not isinstance(config_data, dict):
                    self.console.print("❌ Invalid config format", style="red")
                    return False
                
                # Check for required keys
                if 'buttons' not in config_data and 'settings' not in config_data:
                    self.console.print("❌ No configuration data found", style="red")
                    return False
                
                self.console.print("✅ Export file is valid", style="green")
                return True
                
        except zipfile.BadZipFile:
            self.console.print("❌ Invalid zip file", style="red")
            return False
        except json.JSONDecodeError:
            self.console.print("❌ Invalid JSON in config file", style="red")
            return False
        except Exception as e:
            self.console.print(f"❌ Validation error: {e}", style="red")
            return False
    
    def get_export_info(self, export_path: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about an export file.
        
        Args:
            export_path: Path to the export file
            
        Returns:
            Export information dictionary or None if failed
        """
        try:
            with zipfile.ZipFile(export_path, 'r') as zipf:
                config_data = json.loads(zipf.read('config.json').decode('utf-8'))
                
                # Count files
                script_count = len([f for f in zipf.namelist() if f.startswith('scripts/') and f.endswith('.py')])
                
                # Get export info
                export_info = config_data.get('export_info', {})
                
                # Count buttons
                button_count = len(config_data.get('buttons', {}))
                
                return {
                    'export_info': export_info,
                    'button_count': button_count,
                    'script_count': script_count,
                    'file_count': len(zipf.namelist()),
                    'file_size': Path(export_path).stat().st_size
                }
                
        except Exception as e:
            self.console.print(f"❌ Error reading export info: {e}", style="red")
            return None