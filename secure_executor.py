"""
Secure Executor for Ollama Agent Mode Proxy

This module provides secure execution of terminal commands in isolated
Docker containers to prevent security issues.
"""

import docker
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional


class SecureExecutor:
    """
    Handles secure execution of terminal commands in isolated containers.
    
    This class provides a sandboxed environment for running potentially
    dangerous commands using Docker containers.
    """
    
    def __init__(self, workspace_path: str = "/tmp/agent_workspace"):
        """
        Initialize the secure executor.
        
        Args:
            workspace_path: Path to the workspace directory
        """
        self.workspace = Path(workspace_path)
        try:
            self.docker = docker.from_env()
        except:
            # Docker might not be available, so we'll fall back to a mock implementation
            self.docker = None
    
    async def run_command(self, command: str, require_permission: bool = True) -> Dict[str, Any]:
        """
        Run a command in a secure container.
        
        Args:
            command: Command to run
            require_permission: Whether to require user permission
            
        Returns:
            Command output or error
        """
        # In a real implementation, we would show a UI prompt for permission
        # For now, we'll just log the permission check
        if require_permission:
            print(f"[PERMISSION REQUIRED] Command: {command}")
        
        # If Docker is not available, fall back to regular execution
        if not self.docker:
            return await self._fallback_execution(command)
        
        try:
            # Run in isolated container
            container = self.docker.containers.run(
                "python:3.11-slim",
                command=command,
                working_dir="/workspace",
                volumes={str(self.workspace): {"bind": "/workspace", "mode": "rw"}},
                mem_limit="512m",
                cpu_quota=50000,
                network_disabled=True,
                remove=True,
                detach=True
            )
            
            # Wait for result (with timeout)
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < 10:
                try:
                    container_info = self.docker.containers.get(container.id)
                    if container_info.status not in ("created", "running"):
                        break
                except docker.errors.NotFound:
                    # Container completed and was removed
                    break
                
                await asyncio.sleep(0.1)
            
            # Get result
            try:
                logs = container.logs().decode()
                result = container.wait(timeout=1)
                return {"output": logs, "exit_code": result["StatusCode"]}
            except Exception:
                # Container might have been removed
                return {"output": "", "exit_code": -1, "message": "Container execution completed"}
            
        except Exception as e:
            return {"error": f"Secure execution failed: {str(e)}"}
    
    async def _fallback_execution(self, command: str) -> Dict[str, Any]:
        """
        Fallback execution when Docker is not available.
        
        Args:
            command: Command to run
            
        Returns:
            Command output
        """
        try:
            # Use asyncio subprocess with strict timeout
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace)
            )
            
            # Wait with timeout
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
                
                return {
                    "output": stdout.decode() if stdout else "",
                    "error": stderr.decode() if stderr else "",
                    "exit_code": process.returncode,
                    "warning": "Executed without container isolation (Docker not available)"
                }
            except asyncio.TimeoutError:
                # Kill the process if it times out
                try:
                    process.kill()
                except:
                    pass
                
                return {
                    "error": "Command execution timed out after 10 seconds",
                    "warning": "Executed without container isolation (Docker not available)"
                }
            
        except Exception as e:
            return {"error": f"Execution failed: {str(e)}"}
    
    async def get_user_permission(self, command: str) -> bool:
        """
        Get user permission for executing a command.
        
        Args:
            command: Command to execute
            
        Returns:
            Whether permission was granted
        """
        # In a real implementation, this would show a UI prompt
        # For now, just return True
        print(f"[PERMISSION CHECK] Would ask for permission to run: {command}")
        return True