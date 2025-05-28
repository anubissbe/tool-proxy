"""
Configuration for Ollama Agent Mode Proxy

This module provides configuration options for the proxy server.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Ollama configuration
OLLAMA_BASE_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
SUPPORTED_MODELS = os.environ.get("SUPPORTED_MODELS", "llama3.1,mistral,qwen2.5").split(",")
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "llama3.1")

# Workspace configuration
WORKSPACE_PATH = os.environ.get("WORKSPACE_PATH", "/tmp/agent_workspace")
Path(WORKSPACE_PATH).mkdir(parents=True, exist_ok=True)

# Redis configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
SESSION_EXPIRY = int(os.environ.get("SESSION_EXPIRY", "3600"))  # 1 hour

# Security configuration
ENABLE_DOCKER_SANDBOX = os.environ.get("ENABLE_DOCKER_SANDBOX", "true").lower() == "true"
REQUIRE_PERMISSIONS = os.environ.get("REQUIRE_PERMISSIONS", "true").lower() == "true"

# API configuration
API_PORT = int(os.environ.get("API_PORT", "8000"))
API_HOST = os.environ.get("API_HOST", "0.0.0.0")

# Debug mode
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# Logging configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Tool definitions as required by Continue/Void
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "builtin_read_file",
            "description": "Use this tool if you need to view the contents of an existing file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path of the file to read, relative to the root of the workspace (NOT uri or absolute path)"
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "builtin_edit_existing_file",
            "description": "Use this tool to edit an existing file. If you don't know the contents of the file, read it first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path of the file to edit, relative to the root of the workspace."
                    },
                    "changes": {
                        "type": "string",
                        "description": "Any modifications to the file, showing only needed changes. Do NOT wrap this in a codeblock or write anything besides the code changes. In larger files, use brief language-appropriate placeholders for large unmodified sections, e.g. '// ... existing code ...'"
                    }
                },
                "required": ["filepath", "changes"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "builtin_create_new_file",
            "description": "Create a new file. Only use this when a file doesn't exist and should be created",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path where the new file should be created, relative to the root of the workspace"
                    },
                    "contents": {
                        "type": "string",
                        "description": "The contents to write to the new file"
                    }
                },
                "required": ["filepath", "contents"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "builtin_run_terminal_command",
            "description": "Run a terminal command in the current directory. The shell is not stateful and will not remember any previous commands.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to run. This will be passed directly into the IDE shell."
                    },
                    "waitForCompletion": {
                        "type": "boolean",
                        "description": "Whether to wait for the command to complete before returning. Default is true. Set to false to run the command in the background. Set to true to run the command in the foreground and wait to collect the output."
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "builtin_grep_search",
            "description": "Perform a search over the repository using ripgrep.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to use. Must be a valid ripgrep regex expression, escaped where needed"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "builtin_file_glob_search",
            "description": "Search for files in the project",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern for file path matching"
                    }
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "builtin_search_web",
            "description": "Performs a web search, returning top results. Use this tool sparingly - only for questions that require specialized, external, and/or up-to-date knowledege.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The natural language search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "builtin_view_diff",
            "description": "View the current diff of working changes",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "builtin_read_currently_open_file",
            "description": "Read the currently open file in the IDE. If the user seems to be referring to a file that you can't see, try using this",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "builtin_ls",
            "description": "List files and folders in a given directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "dirPath": {
                        "type": "string",
                        "description": "The directory path relative to the root of the project. Always use forward slash paths like '/'. rather than e.g. '.'"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "If true, lists files and folders recursively. To prevent unexpected large results, use this sparingly"
                    }
                },
                "required": ["dirPath", "recursive"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "builtin_create_rule_block",
            "description": "Creates a persistent rule for all future conversations. For establishing code standards or preferences that should be applied consistently.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Short, descriptive name summarizing the rule's purpose (e.g. 'React Standards', 'Type Hints')"
                    },
                    "rule": {
                        "type": "string",
                        "description": "Clear, imperative instruction for future code generation (e.g. 'Use named exports', 'Add Python type hints'). Each rule should focus on one specific standard."
                    },
                    "description": {
                        "type": "string",
                        "description": "Short description of the rule"
                    },
                    "globs": {
                        "type": "string",
                        "description": "Optional file patterns to which this rule applies (e.g. ['**/*.{ts,tsx}'] or ['src/**/*.ts', 'tests/**/*.ts'])"
                    }
                },
                "required": ["name", "rule"]
            }
        }
    }
]