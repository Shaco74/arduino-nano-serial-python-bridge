#!/usr/bin/env python3
"""
Interactive setup tool for Arduino Nano Macro Controller.

This script provides a modern, user-friendly interface for configuring
buttons, managing scripts, and system settings.
"""

import sys
import os
import platform
from typing import Dict, Any, List, Optional

import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.columns import Columns
from rich.align import Align

from utils.config_manager import ConfigManager
from utils.serial_manager import SerialManager
from utils.script_loader import ScriptLoader


class SetupTool:
    """Interactive setup tool for the Arduino Nano Macro Controller."""
    
    def __init__(self):
        """Initialize the setup tool."""
        self.console = Console()
        self.config_manager = ConfigManager()
        self.serial_manager = SerialManager()
        self.script_loader = ScriptLoader()
        
        # Load configuration
        self.config = self.config_manager.load_config()
        
        # Load scripts
        self.script_loader.load_all_scripts()
    
    def _print_welcome(self) -> None:
        """Print welcome message."""
        welcome_text = Text("Arduino Nano Macro Controller", style="bold blue")
        subtitle = Text("Interactive Setup Tool", style="dim")
        
        self.console.print(Panel(
            Align.center(welcome_text + "\n" + subtitle),
            title="🚀 Welcome",
            border_style="blue",
            padding=(1, 2)
        ))
    
    def _show_main_menu(self) -> str:
        """Show main menu and get user choice."""
        choices = [
            "🔘 Configure Buttons",
            "📝 Manage Scripts", 
            "⚙️  System Settings",
            "🧪 Test Configuration",
            "📋 View Current Setup",
            "🚪 Exit"
        ]
        
        questions = [
            inquirer.List(
                'choice',
                message="What would you like to do?",
                choices=choices,
                carousel=True
            )
        ]
        
        answers = inquirer.prompt(questions)
        return answers['choice'] if answers else "🚪 Exit"
    
    def _discover_and_show_ports(self) -> List[Dict[str, str]]:
        """Discover and display available serial ports."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Discovering serial ports...", total=None)
            
            all_ports = self.serial_manager.discover_ports()
            arduino_ports = self.serial_manager.filter_arduino_ports(all_ports)
            
            progress.update(task, completed=True)
        
        if not all_ports:
            self.console.print("❌ No serial ports found", style="red")
            return []
        
        # Show ports in a table
        table = Table(title="Available Serial Ports", show_header=True)
        table.add_column("Port", style="cyan")
        table.add_column("Description", style="magenta")
        table.add_column("Arduino?", style="green")
        
        for port in all_ports:
            is_arduino = "🟢 Likely" if port in arduino_ports else "🔴 No"
            table.add_row(port["device"], port["description"], is_arduino)
        
        self.console.print(table)
        return all_ports
    
    def _configure_single_button(self, button_id: str) -> None:
        """Configure a single button."""
        self.console.print(f"\n🔧 Configuring Button {button_id}", style="bold blue")
        
        current_config = self.config_manager.get_button_config(button_id)
        
        if current_config:
            # Show current configuration
            self.console.print(f"Current configuration:", style="yellow")
            self.console.print(f"  Port: {current_config.get('port', 'None')}")
            self.console.print(f"  Script: {current_config.get('script', 'None')}")
            self.console.print(f"  Status: {'Enabled' if current_config.get('enabled') else 'Disabled'}")
            
            if not Confirm.ask("Do you want to reconfigure this button?"):
                return
        
        # Get available ports
        ports = self._discover_and_show_ports()
        if not ports:
            return
        
        # Port selection
        port_choices = [f"{port['device']} - {port['description']}" for port in ports]
        port_choices.append("🔙 Back to menu")
        
        questions = [
            inquirer.List(
                'port',
                message=f"Select port for Button {button_id}:",
                choices=port_choices
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers or answers['port'] == "🔙 Back to menu":
            return
        
        selected_port = answers['port'].split(" - ")[0]
        
        # Test port connection
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(f"Testing connection to {selected_port}...", total=None)
            
            can_connect = self.serial_manager.test_port_connection(selected_port)
            progress.update(task, completed=True)
        
        if not can_connect:
            self.console.print(f"❌ Cannot connect to {selected_port}", style="red")
            return
        
        # Control number selection
        control_number = Prompt.ask(
            f"Enter MIDI control number for Button {button_id}",
            default=button_id
        )
        
        try:
            control_number = int(control_number)
            if control_number < 1 or control_number > 127:
                raise ValueError()
        except ValueError:
            self.console.print("❌ Invalid control number. Must be 1-127", style="red")
            return
        
        # Script selection
        self._show_available_scripts()
        
        script_choices = list(self.script_loader.get_supported_scripts().keys())
        script_choices.append("🔙 Back to menu")
        
        questions = [
            inquirer.List(
                'script',
                message=f"Select script for Button {button_id}:",
                choices=script_choices,
                carousel=True
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers or answers['script'] == "🔙 Back to menu":
            return
        
        selected_script = answers['script']
        
        # Enable/disable option
        enabled = Confirm.ask(f"Enable Button {button_id}?", default=True)
        
        # Get script description for the button
        script_metadata = self.script_loader.get_script_metadata(selected_script)
        description = script_metadata.get('description', 'No description') if script_metadata else 'No description'
        
        # Save configuration
        button_config = {
            "port": selected_port,
            "control_number": control_number,
            "script": selected_script,
            "enabled": enabled,
            "description": description
        }
        
        self.config_manager.set_button_config(button_id, button_config)
        
        self.console.print(f"✅ Button {button_id} configured successfully!", style="green")
    
    def _configure_buttons(self) -> None:
        """Configure button mappings."""
        self.console.print("\n🔘 Button Configuration", style="bold blue")
        
        # Show current button status
        self._show_button_status()
        
        while True:
            choices = [
                "🔘 Configure Button 1",
                "🔘 Configure Button 2", 
                "🔘 Configure Button 3",
                "🔘 Configure Button 4",
                "🔘 Configure Button 5",
                "🗑️  Remove Button Configuration",
                "🔙 Back to Main Menu"
            ]
            
            questions = [
                inquirer.List(
                    'choice',
                    message="Button Configuration:",
                    choices=choices
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers or answers['choice'] == "🔙 Back to Main Menu":
                break
            
            choice = answers['choice']
            
            if choice.startswith("🔘 Configure Button"):
                button_id = choice.split()[-1]
                self._configure_single_button(button_id)
            elif choice == "🗑️  Remove Button Configuration":
                self._remove_button_configuration()
            
            # Show updated status
            self._show_button_status()
    
    def _remove_button_configuration(self) -> None:
        """Remove button configuration."""
        configured_buttons = self.config_manager.get_all_buttons()
        
        if not configured_buttons:
            self.console.print("❌ No buttons configured", style="red")
            return
        
        choices = [f"Button {bid}" for bid in configured_buttons.keys()]
        choices.append("🔙 Cancel")
        
        questions = [
            inquirer.List(
                'button',
                message="Select button to remove:",
                choices=choices
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers or answers['button'] == "🔙 Cancel":
            return
        
        button_id = answers['button'].split()[-1]
        
        if Confirm.ask(f"Remove configuration for Button {button_id}?"):
            self.config_manager.remove_button_config(button_id)
            self.console.print(f"✅ Button {button_id} configuration removed", style="green")
    
    def _show_button_status(self) -> None:
        """Show current button configuration status."""
        buttons = self.config_manager.get_all_buttons()
        
        table = Table(title="Button Configuration Status", show_header=True)
        table.add_column("Button", style="cyan")
        table.add_column("Port", style="magenta")
        table.add_column("Script", style="green")
        table.add_column("Status", style="yellow")
        
        for i in range(1, 6):
            button_id = str(i)
            if button_id in buttons:
                config = buttons[button_id]
                status = "🟢 Enabled" if config.get("enabled", False) else "🔴 Disabled"
                table.add_row(
                    f"Button {button_id}",
                    config.get("port", "N/A"),
                    config.get("script", "N/A"),
                    status
                )
            else:
                table.add_row(f"Button {button_id}", "Not configured", "-", "🔴 Disabled")
        
        self.console.print(table)
    
    def _show_available_scripts(self) -> None:
        """Show available scripts in a formatted table."""
        scripts = self.script_loader.get_all_scripts()
        
        if not scripts:
            self.console.print("❌ No scripts found", style="red")
            return
        
        # Group scripts by category
        categories = {}
        for script_name, metadata in scripts.items():
            category = metadata.get('category', 'unknown').title()
            if category not in categories:
                categories[category] = []
            categories[category].append((script_name, metadata))
        
        # Create tables for each category
        for category, script_list in categories.items():
            table = Table(title=f"{category} Scripts", show_header=True)
            table.add_column("Script", style="cyan")
            table.add_column("Description", style="magenta")
            table.add_column("Supported", style="green")
            
            for script_name, metadata in script_list:
                supported = "✅ Yes" if metadata.get('is_supported', False) else "❌ No"
                table.add_row(
                    script_name,
                    metadata.get('description', 'No description'),
                    supported
                )
            
            self.console.print(table)
    
    def _manage_scripts(self) -> None:
        """Manage script collection."""
        self.console.print("\n📝 Script Management", style="bold blue")
        
        while True:
            choices = [
                "📋 View All Scripts",
                "🔍 View Script Details",
                "🔄 Reload Scripts",
                "📁 Import from Templates",
                "🔙 Back to Main Menu"
            ]
            
            questions = [
                inquirer.List(
                    'choice',
                    message="Script Management:",
                    choices=choices
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers or answers['choice'] == "🔙 Back to Main Menu":
                break
            
            choice = answers['choice']
            
            if choice == "📋 View All Scripts":
                self._show_available_scripts()
            elif choice == "🔍 View Script Details":
                self._show_script_details()
            elif choice == "🔄 Reload Scripts":
                self._reload_scripts()
            elif choice == "📁 Import from Templates":
                self._import_from_templates()
    
    def _show_script_details(self) -> None:
        """Show detailed information about a specific script."""
        scripts = self.script_loader.get_all_scripts()
        
        if not scripts:
            self.console.print("❌ No scripts found", style="red")
            return
        
        script_choices = list(scripts.keys())
        script_choices.append("🔙 Back")
        
        questions = [
            inquirer.List(
                'script',
                message="Select script to view details:",
                choices=script_choices
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers or answers['script'] == "🔙 Back":
            return
        
        script_name = answers['script']
        metadata = scripts[script_name]
        
        # Create detailed panel
        details = []
        details.append(f"[bold]Name:[/bold] {metadata.get('name', script_name)}")
        details.append(f"[bold]Description:[/bold] {metadata.get('description', 'No description')}")
        details.append(f"[bold]Category:[/bold] {metadata.get('category', 'Unknown')}")
        details.append(f"[bold]Version:[/bold] {metadata.get('version', 'Unknown')}")
        details.append(f"[bold]Author:[/bold] {metadata.get('author', 'Unknown')}")
        details.append(f"[bold]Supported OS:[/bold] {', '.join(metadata.get('supported_os', []))}")
        details.append(f"[bold]Currently Supported:[/bold] {'✅ Yes' if metadata.get('is_supported', False) else '❌ No'}")
        
        if metadata.get('warning'):
            details.append(f"[bold red]Warning:[/bold red] {metadata['warning']}")
        
        details.append(f"[bold]File Path:[/bold] {metadata.get('file_path', 'Unknown')}")
        
        self.console.print(Panel(
            "\n".join(details),
            title=f"Script Details: {script_name}",
            border_style="blue"
        ))
    
    def _reload_scripts(self) -> None:
        """Reload all scripts."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Reloading scripts...", total=None)
            
            loaded_count = self.script_loader.load_all_scripts()
            progress.update(task, completed=True)
        
        self.console.print(f"✅ Reloaded {loaded_count} scripts", style="green")
    
    def _import_from_templates(self) -> None:
        """Import scripts from templates directory."""
        templates_dir = "templates"
        
        if not os.path.exists(templates_dir):
            self.console.print("❌ Templates directory not found", style="red")
            return
        
        # Find all template files
        template_files = []
        for root, dirs, files in os.walk(templates_dir):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    rel_path = os.path.relpath(os.path.join(root, file), templates_dir)
                    template_files.append(rel_path)
        
        if not template_files:
            self.console.print("❌ No template files found", style="red")
            return
        
        # Show available templates
        template_choices = template_files + ["🔙 Back"]
        
        questions = [
            inquirer.List(
                'template',
                message="Select template to import:",
                choices=template_choices
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers or answers['template'] == "🔙 Back":
            return
        
        selected_template = answers['template']
        template_path = os.path.join(templates_dir, selected_template)
        script_name = os.path.splitext(os.path.basename(selected_template))[0]
        
        # Copy template to scripts directory
        scripts_dir = "scripts"
        dest_path = os.path.join(scripts_dir, f"{script_name}.py")
        
        if os.path.exists(dest_path):
            if not Confirm.ask(f"Script '{script_name}' already exists. Overwrite?"):
                return
        
        try:
            with open(template_path, 'r') as src, open(dest_path, 'w') as dst:
                dst.write(src.read())
            
            # Reload scripts to include the new one
            self.script_loader.load_script(script_name)
            
            self.console.print(f"✅ Template '{script_name}' imported successfully", style="green")
            
        except Exception as e:
            self.console.print(f"❌ Error importing template: {e}", style="red")
    
    def _system_settings(self) -> None:
        """Configure system settings."""
        self.console.print("\n⚙️ System Settings", style="bold blue")
        
        while True:
            choices = [
                "🔧 Serial Settings",
                "🖥️  OS Detection",
                "🐛 Debug Mode",
                "🔙 Back to Main Menu"
            ]
            
            questions = [
                inquirer.List(
                    'choice',
                    message="System Settings:",
                    choices=choices
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers or answers['choice'] == "🔙 Back to Main Menu":
                break
            
            choice = answers['choice']
            
            if choice == "🔧 Serial Settings":
                self._configure_serial_settings()
            elif choice == "🖥️  OS Detection":
                self._configure_os_detection()
            elif choice == "🐛 Debug Mode":
                self._toggle_debug_mode()
    
    def _configure_serial_settings(self) -> None:
        """Configure serial communication settings."""
        current_baud = self.config_manager.get_setting('baud_rate')
        current_timeout = self.config_manager.get_setting('serial_timeout')
        
        self.console.print(f"Current baud rate: {current_baud}")
        self.console.print(f"Current timeout: {current_timeout}s")
        
        # Baud rate selection
        baud_choices = ["31250 (MIDI Standard)", "9600", "115200", "Keep current"]
        
        questions = [
            inquirer.List(
                'baud',
                message="Select baud rate:",
                choices=baud_choices
            )
        ]
        
        answers = inquirer.prompt(questions)
        if answers and answers['baud'] != "Keep current":
            new_baud = int(answers['baud'].split()[0])
            self.config_manager.set_setting('baud_rate', new_baud)
            self.console.print(f"✅ Baud rate set to {new_baud}", style="green")
        
        # Timeout setting
        new_timeout = Prompt.ask(
            "Enter serial timeout (seconds)",
            default=str(current_timeout)
        )
        
        try:
            timeout_val = float(new_timeout)
            self.config_manager.set_setting('serial_timeout', timeout_val)
            self.console.print(f"✅ Timeout set to {timeout_val}s", style="green")
        except ValueError:
            self.console.print("❌ Invalid timeout value", style="red")
    
    def _configure_os_detection(self) -> None:
        """Configure OS detection settings."""
        current_os = self.config_manager.config.get('os', 'auto')
        detected_os = platform.system()
        
        self.console.print(f"Currently configured: {current_os}")
        self.console.print(f"Auto-detected: {detected_os}")
        
        os_choices = ["Auto-detect", "Darwin (macOS)", "Linux", "Windows"]
        
        questions = [
            inquirer.List(
                'os',
                message="Select OS setting:",
                choices=os_choices
            )
        ]
        
        answers = inquirer.prompt(questions)
        if answers:
            if answers['os'] == "Auto-detect":
                self.config_manager.config['os'] = platform.system()
            else:
                self.config_manager.config['os'] = answers['os'].split()[0]
            
            self.config_manager.save_config()
            self.console.print(f"✅ OS setting updated", style="green")
    
    def _toggle_debug_mode(self) -> None:
        """Toggle debug mode."""
        current_debug = self.config_manager.get_setting('debug_mode')
        
        new_debug = Confirm.ask(
            f"Debug mode is currently {'ON' if current_debug else 'OFF'}. Toggle?",
            default=not current_debug
        )
        
        self.config_manager.set_setting('debug_mode', new_debug)
        self.console.print(
            f"✅ Debug mode {'enabled' if new_debug else 'disabled'}", 
            style="green"
        )
    
    def _test_configuration(self) -> None:
        """Test the current configuration."""
        self.console.print("\n🧪 Testing Configuration", style="bold blue")
        
        # Test script loading
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task1 = progress.add_task("Testing script loading...", total=None)
            
            scripts = self.script_loader.get_supported_scripts()
            progress.update(task1, completed=True)
            
            self.console.print(f"✅ {len(scripts)} scripts loaded and supported", style="green")
        
        # Test port connections
        configured_buttons = self.config_manager.get_configured_buttons()
        
        if not configured_buttons:
            self.console.print("❌ No buttons configured", style="red")
            return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task2 = progress.add_task("Testing port connections...", total=None)
            
            tested_ports = set()
            connection_results = {}
            
            for button_id, config in configured_buttons.items():
                port = config.get('port')
                if port and port not in tested_ports:
                    can_connect = self.serial_manager.test_port_connection(port)
                    connection_results[port] = can_connect
                    tested_ports.add(port)
            
            progress.update(task2, completed=True)
        
        # Show results
        for port, can_connect in connection_results.items():
            status = "✅ OK" if can_connect else "❌ Failed"
            self.console.print(f"Port {port}: {status}")
        
        # Test script execution (optional)
        if Confirm.ask("Test script execution? (Will execute open_terminal if available)"):
            if 'open_terminal' in scripts:
                self.console.print("🔄 Executing open_terminal script...")
                success = self.script_loader.execute_script('open_terminal')
                if success:
                    self.console.print("✅ Script executed successfully", style="green")
                else:
                    self.console.print("❌ Script execution failed", style="red")
            else:
                self.console.print("❌ open_terminal script not available", style="red")
    
    def _view_current_setup(self) -> None:
        """View current setup summary."""
        self.console.print("\n📋 Current Setup", style="bold blue")
        
        # System info
        system_info = Table(title="System Information", show_header=True)
        system_info.add_column("Setting", style="cyan")
        system_info.add_column("Value", style="magenta")
        
        system_info.add_row("Operating System", self.config.get('os', 'Unknown'))
        system_info.add_row("Baud Rate", str(self.config_manager.get_setting('baud_rate')))
        system_info.add_row("Serial Timeout", f"{self.config_manager.get_setting('serial_timeout')}s")
        system_info.add_row("Debug Mode", "ON" if self.config_manager.get_setting('debug_mode') else "OFF")
        system_info.add_row("Last Updated", self.config.get('last_updated', 'Unknown'))
        
        self.console.print(system_info)
        
        # Button configuration
        self._show_button_status()
        
        # Script summary
        scripts = self.script_loader.get_all_scripts()
        supported_scripts = self.script_loader.get_supported_scripts()
        
        script_summary = Table(title="Script Summary", show_header=True)
        script_summary.add_column("Category", style="cyan")
        script_summary.add_column("Total", style="magenta")
        script_summary.add_column("Supported", style="green")
        
        categories = {}
        for script_name, metadata in scripts.items():
            category = metadata.get('category', 'unknown').title()
            if category not in categories:
                categories[category] = {'total': 0, 'supported': 0}
            categories[category]['total'] += 1
            if script_name in supported_scripts:
                categories[category]['supported'] += 1
        
        for category, counts in categories.items():
            script_summary.add_row(
                category,
                str(counts['total']),
                str(counts['supported'])
            )
        
        self.console.print(script_summary)
    
    def run(self) -> None:
        """Run the interactive setup tool."""
        self._print_welcome()
        
        while True:
            choice = self._show_main_menu()
            
            if choice == "🔘 Configure Buttons":
                self._configure_buttons()
            elif choice == "📝 Manage Scripts":
                self._manage_scripts()
            elif choice == "⚙️  System Settings":
                self._system_settings()
            elif choice == "🧪 Test Configuration":
                self._test_configuration()
            elif choice == "📋 View Current Setup":
                self._view_current_setup()
            elif choice == "🚪 Exit":
                self.console.print("\n👋 Goodbye!", style="blue")
                break
            
            # Wait for user to continue
            if choice != "🚪 Exit":
                self.console.print("\nPress Enter to continue...")
                input()


def main():
    """Main entry point."""
    setup = SetupTool()
    setup.run()


if __name__ == "__main__":
    main()