"""
Remote repository utilities for Arduino Nano Macro Controller.

This module provides functionality to download and manage scripts
from remote repositories.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, DownloadColumn, TextColumn, BarColumn, TaskProgressColumn


class RemoteRepository:
    """Manages remote script repositories."""
    
    def __init__(self, scripts_dir: str = "scripts"):
        """
        Initialize the remote repository manager.
        
        Args:
            scripts_dir: Directory to store downloaded scripts
        """
        self.scripts_dir = Path(scripts_dir)
        self.console = Console()
        self.cache_dir = Path(".cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Default repositories
        self.repositories = {
            "official": {
                "name": "Official Arduino Nano Scripts",
                "url": "https://raw.githubusercontent.com/arduino-nano-controller/scripts/main/",
                "index_url": "https://raw.githubusercontent.com/arduino-nano-controller/scripts/main/index.json"
            }
        }
    
    def add_repository(self, name: str, url: str, index_url: str) -> None:
        """
        Add a new remote repository.
        
        Args:
            name: Repository name
            url: Base URL for scripts
            index_url: URL for the repository index
        """
        self.repositories[name] = {
            "name": name,
            "url": url,
            "index_url": index_url
        }
        
        self.console.print(f"✅ Repository '{name}' added", style="green")
    
    def remove_repository(self, name: str) -> bool:
        """
        Remove a repository.
        
        Args:
            name: Repository name to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        if name in self.repositories:
            del self.repositories[name]
            self.console.print(f"✅ Repository '{name}' removed", style="green")
            return True
        else:
            self.console.print(f"❌ Repository '{name}' not found", style="red")
            return False
    
    def fetch_repository_index(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the index from a remote repository.
        
        Args:
            repo_name: Name of the repository
            
        Returns:
            Repository index or None if failed
        """
        if repo_name not in self.repositories:
            self.console.print(f"❌ Repository '{repo_name}' not found", style="red")
            return None
        
        repo = self.repositories[repo_name]
        index_url = repo["index_url"]
        
        try:
            with urllib.request.urlopen(index_url, timeout=10) as response:
                index_data = json.loads(response.read().decode('utf-8'))
                
                # Cache the index
                cache_file = self.cache_dir / f"{repo_name}_index.json"
                with open(cache_file, 'w') as f:
                    json.dump(index_data, f, indent=2)
                
                return index_data
                
        except urllib.error.URLError as e:
            self.console.print(f"❌ Failed to fetch index from '{repo_name}': {e}", style="red")
            return None
        except json.JSONDecodeError as e:
            self.console.print(f"❌ Invalid JSON in repository index: {e}", style="red")
            return None
        except Exception as e:
            self.console.print(f"❌ Error fetching repository index: {e}", style="red")
            return None
    
    def get_cached_index(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Get cached repository index.
        
        Args:
            repo_name: Name of the repository
            
        Returns:
            Cached index or None if not available
        """
        cache_file = self.cache_dir / f"{repo_name}_index.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def list_available_scripts(self, repo_name: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        List available scripts from a repository.
        
        Args:
            repo_name: Name of the repository
            use_cache: Whether to use cached index
            
        Returns:
            Dictionary of available scripts or None if failed
        """
        # Try cache first if requested
        if use_cache:
            index = self.get_cached_index(repo_name)
            if index:
                return index.get('scripts', {})
        
        # Fetch from remote
        index = self.fetch_repository_index(repo_name)
        if index:
            return index.get('scripts', {})
        
        return None
    
    def download_script(self, repo_name: str, script_name: str, 
                       overwrite: bool = False) -> bool:
        """
        Download a script from a remote repository.
        
        Args:
            repo_name: Name of the repository
            script_name: Name of the script to download
            overwrite: Whether to overwrite existing script
            
        Returns:
            True if download was successful, False otherwise
        """
        if repo_name not in self.repositories:
            self.console.print(f"❌ Repository '{repo_name}' not found", style="red")
            return False
        
        # Get script info from index
        scripts = self.list_available_scripts(repo_name)
        if not scripts or script_name not in scripts:
            self.console.print(f"❌ Script '{script_name}' not found in repository", style="red")
            return False
        
        script_info = scripts[script_name]
        script_url = self.repositories[repo_name]["url"] + script_info["filename"]
        
        # Check if script already exists
        local_path = self.scripts_dir / f"{script_name}.py"
        if local_path.exists() and not overwrite:
            self.console.print(f"❌ Script '{script_name}' already exists. Use overwrite=True to replace.", style="red")
            return False
        
        try:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TaskProgressColumn(),
                console=self.console
            ) as progress:
                
                # Start download
                task = progress.add_task(f"Downloading {script_name}...", total=None)
                
                with urllib.request.urlopen(script_url, timeout=30) as response:
                    total_size = int(response.headers.get('content-length', 0))
                    
                    if total_size > 0:
                        progress.update(task, total=total_size)
                    
                    content = b""
                    downloaded = 0
                    
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        
                        content += chunk
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress.update(task, completed=downloaded)
                    
                    # Write to file
                    with open(local_path, 'wb') as f:
                        f.write(content)
                
                progress.update(task, completed=True)
            
            self.console.print(f"✅ Script '{script_name}' downloaded successfully", style="green")
            return True
            
        except urllib.error.URLError as e:
            self.console.print(f"❌ Download failed: {e}", style="red")
            return False
        except Exception as e:
            self.console.print(f"❌ Error downloading script: {e}", style="red")
            return False
    
    def search_scripts(self, query: str, repo_name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for scripts across repositories.
        
        Args:
            query: Search query
            repo_name: Optional repository name to search in
            
        Returns:
            Dictionary mapping repository names to matching scripts
        """
        results = {}
        query_lower = query.lower()
        
        repos_to_search = [repo_name] if repo_name else list(self.repositories.keys())
        
        for repo in repos_to_search:
            if repo not in self.repositories:
                continue
                
            scripts = self.list_available_scripts(repo)
            if not scripts:
                continue
            
            matches = []
            for script_name, script_info in scripts.items():
                # Search in name, description, and tags
                if (query_lower in script_name.lower() or
                    query_lower in script_info.get('description', '').lower() or
                    any(query_lower in tag.lower() for tag in script_info.get('tags', []))):
                    
                    matches.append({
                        'name': script_name,
                        'info': script_info
                    })
            
            if matches:
                results[repo] = matches
        
        return results
    
    def get_script_info(self, repo_name: str, script_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a script.
        
        Args:
            repo_name: Name of the repository
            script_name: Name of the script
            
        Returns:
            Script information or None if not found
        """
        scripts = self.list_available_scripts(repo_name)
        if scripts and script_name in scripts:
            return scripts[script_name]
        return None
    
    def update_all_repositories(self) -> int:
        """
        Update indexes for all repositories.
        
        Returns:
            Number of repositories successfully updated
        """
        updated_count = 0
        
        for repo_name in self.repositories:
            self.console.print(f"🔄 Updating repository '{repo_name}'...")
            
            if self.fetch_repository_index(repo_name):
                updated_count += 1
                self.console.print(f"✅ Repository '{repo_name}' updated", style="green")
            else:
                self.console.print(f"❌ Failed to update repository '{repo_name}'", style="red")
        
        return updated_count
    
    def list_repositories(self) -> Dict[str, Dict[str, str]]:
        """
        List all configured repositories.
        
        Returns:
            Dictionary of repository configurations
        """
        return self.repositories.copy()
    
    def is_online(self) -> bool:
        """
        Check if internet connection is available.
        
        Returns:
            True if online, False otherwise
        """
        try:
            urllib.request.urlopen('https://www.google.com', timeout=5)
            return True
        except urllib.error.URLError:
            return False
    
    def get_repository_stats(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a repository.
        
        Args:
            repo_name: Name of the repository
            
        Returns:
            Repository statistics or None if failed
        """
        scripts = self.list_available_scripts(repo_name)
        if not scripts:
            return None
        
        # Count by category
        categories = {}
        total_scripts = len(scripts)
        
        for script_info in scripts.values():
            category = script_info.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        
        return {
            'total_scripts': total_scripts,
            'categories': categories,
            'repository_name': self.repositories[repo_name]['name']
        }