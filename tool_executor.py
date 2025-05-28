"""
Tool Executor for Ollama Agent Mode Proxy

This module implements the execution of tools required by Continue and Void
for agent mode capabilities.
"""

import os
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import shutil
import glob


class ToolExecutor:
    """
    Handles execution of built-in tools for agent mode.
    
    This class implements all Continue built-in tools including file operations,
    terminal commands, and search functionality.
    """
    
    def __init__(self, workspace_path: str = "/tmp/agent_workspace"):
        """
        Initialize the tool executor.
        
        Args:
            workspace_path: Path to the workspace directory
        """
        self.workspace = Path(workspace_path)
        self.workspace.mkdir(exist_ok=True, parents=True)
        
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool based on its name and arguments.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments for the tool
            
        Returns:
            Tool execution result
        """
        handlers = {
            "builtin_read_file": self.read_file,
            "builtin_edit_existing_file": self.edit_existing_file,
            "builtin_create_new_file": self.create_new_file,
            "builtin_run_terminal_command": self.run_terminal_command,
            "builtin_grep_search": self.grep_search,
            "builtin_file_glob_search": self.file_glob_search,
            "builtin_search_web": self.search_web,
            "builtin_view_diff": self.view_diff,
            "builtin_read_currently_open_file": self.read_currently_open_file,
            "builtin_ls": self.list_directory,
            "builtin_create_rule_block": self.create_rule_block,
        }
        
        handler = handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
            
        try:
            return await handler(**arguments)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    async def read_file(self, filepath: str) -> Dict[str, Any]:
        """
        Read a file from the workspace.
        
        Args:
            filepath: Path to the file relative to workspace
            
        Returns:
            File content or error
        """
        try:
            path = self._resolve_path(filepath)
            if not path.exists():
                return {"error": f"File not found: {filepath}"}
            
            return {"content": path.read_text()}
        except Exception as e:
            return {"error": str(e)}
    
    async def edit_existing_file(self, filepath: str, changes: str) -> Dict[str, Any]:
        """
        Edit an existing file in the workspace.
        
        Args:
            filepath: Path to the file relative to workspace
            changes: Changes to apply to the file
            
        Returns:
            Success message or error
        """
        try:
            path = self._resolve_path(filepath)
            if not path.exists():
                return {"error": f"File not found: {filepath}"}
            
            # Apply the changes
            path.write_text(changes)
            
            return {"success": True, "message": f"File {filepath} updated successfully"}
        except Exception as e:
            return {"error": str(e)}
    
    async def create_new_file(self, filepath: str, contents: str) -> Dict[str, Any]:
        """
        Create a new file in the workspace.
        
        Args:
            filepath: Path to the file relative to workspace
            contents: Contents of the new file
            
        Returns:
            Success message or error
        """
        try:
            path = self._resolve_path(filepath)
            
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the contents
            path.write_text(contents)
            
            return {"success": True, "message": f"File {filepath} created successfully"}
        except Exception as e:
            return {"error": str(e)}
    
    async def run_terminal_command(self, command: str, waitForCompletion: bool = True) -> Dict[str, Any]:
        """
        Run a terminal command in the workspace.
        
        Args:
            command: Command to run
            waitForCompletion: Whether to wait for the command to complete
            
        Returns:
            Command output or process ID
        """
        try:
            # Create a process
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace)
            )
            
            if waitForCompletion:
                # Wait for completion and get output
                stdout, stderr = await process.communicate()
                
                return {
                    "stdout": stdout.decode() if stdout else "",
                    "stderr": stderr.decode() if stderr else "",
                    "exit_code": process.returncode
                }
            else:
                # Return process ID for background processes
                return {
                    "pid": process.pid,
                    "message": f"Command started with PID {process.pid}"
                }
        except Exception as e:
            return {"error": str(e)}
    
    async def grep_search(self, query: str) -> Dict[str, Any]:
        """
        Search for text in files using ripgrep.
        
        Args:
            query: Search query
            
        Returns:
            Search results
        """
        try:
            # Run ripgrep command
            process = await asyncio.create_subprocess_shell(
                f'rg -n "{query}" --json',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0 and process.returncode != 1:  # 1 means no matches
                return {"error": f"Search failed: {stderr.decode()}"}
            
            # Parse results
            results = []
            for line in stdout.decode().splitlines():
                if line.strip():
                    try:
                        result = json.loads(line)
                        if result.get("type") == "match":
                            results.append({
                                "file": result.get("data", {}).get("path", {}).get("text", ""),
                                "line": result.get("data", {}).get("line_number", 0),
                                "content": result.get("data", {}).get("lines", {}).get("text", "")
                            })
                    except json.JSONDecodeError:
                        continue
            
            return {"results": results}
        except Exception as e:
            return {"error": str(e)}
    
    async def file_glob_search(self, pattern: str) -> Dict[str, Any]:
        """
        Search for files matching a glob pattern.
        
        Args:
            pattern: Glob pattern
            
        Returns:
            Matching files
        """
        try:
            matches = []
            for file_path in glob.glob(str(self.workspace / pattern), recursive=True):
                rel_path = os.path.relpath(file_path, str(self.workspace))
                matches.append(rel_path)
            
            return {"files": matches}
        except Exception as e:
            return {"error": str(e)}
    
    async def search_web(self, query: str) -> Dict[str, Any]:
        """
        Search the web (mock implementation).
        
        Args:
            query: Search query
            
        Returns:
            Mock search results
        """
        # Note: This is a mock implementation
        # In a real implementation, you would use a search API
        return {
            "results": [
                {
                    "title": "Mock search result 1",
                    "url": "https://example.com/1",
                    "snippet": f"This is a mock result for the query: {query}"
                },
                {
                    "title": "Mock search result 2",
                    "url": "https://example.com/2",
                    "snippet": f"Another mock result for: {query}"
                }
            ]
        }
    
    async def view_diff(self) -> Dict[str, Any]:
        """
        View the current diff of working changes.
        
        Returns:
            Diff output
        """
        try:
            # Run git diff command
            process = await asyncio.create_subprocess_shell(
                "git diff",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {"error": f"Diff failed: {stderr.decode()}"}
            
            return {"diff": stdout.decode()}
        except Exception as e:
            return {"error": str(e)}
    
    async def read_currently_open_file(self) -> Dict[str, Any]:
        """
        Read the currently open file in the IDE (mock implementation).
        
        Returns:
            Mock file content
        """
        # This is a mock implementation
        # In a real implementation, you would need to track the currently open file
        return {
            "content": "This is a mock implementation of reading the currently open file.",
            "filepath": "mock_file.txt"
        }
    
    async def list_directory(self, dirPath: str, recursive: bool = False) -> Dict[str, Any]:
        """
        List files and folders in a directory.
        
        Args:
            dirPath: Directory path relative to workspace
            recursive: Whether to list recursively
            
        Returns:
            Directory contents
        """
        try:
            path = self._resolve_path(dirPath)
            if not path.exists() or not path.is_dir():
                return {"error": f"Directory not found: {dirPath}"}
            
            if recursive:
                files = []
                for root, dirs, files_list in os.walk(path):
                    rel_root = os.path.relpath(root, str(self.workspace))
                    for file in files_list:
                        rel_path = os.path.join(rel_root, file)
                        files.append(rel_path)
            else:
                files = [
                    f.name for f in path.iterdir()
                ]
            
            return {"files": files}
        except Exception as e:
            return {"error": str(e)}
    
    async def create_rule_block(self, name: str, rule: str, description: str = "", globs: str = "") -> Dict[str, Any]:
        """
        Create a persistent rule for future conversations.
        
        Args:
            name: Rule name
            rule: Rule content
            description: Rule description
            globs: File patterns to which the rule applies
            
        Returns:
            Success message
        """
        try:
            rules_file = self.workspace / ".rules.json"
            
            # Load existing rules
            rules = []
            if rules_file.exists():
                try:
                    rules = json.loads(rules_file.read_text())
                except json.JSONDecodeError:
                    rules = []
            
            # Add new rule
            rules.append({
                "name": name,
                "rule": rule,
                "description": description,
                "globs": globs.split(",") if globs else []
            })
            
            # Save rules
            rules_file.write_text(json.dumps(rules, indent=2))
            
            return {"success": True, "message": f"Rule '{name}' created successfully"}
        except Exception as e:
            return {"error": str(e)}
    
    def _resolve_path(self, filepath: str) -> Path:
        """
        Resolve a path relative to the workspace.
        
        Args:
            filepath: Path relative to workspace
            
        Returns:
            Absolute path
            
        Raises:
            ValueError: If path traversal is detected
        """
        path = (self.workspace / filepath).resolve()
        
        # Prevent path traversal
        if not str(path).startswith(str(self.workspace.resolve())):
            raise ValueError(f"Path traversal detected: {filepath}")
        
        return path