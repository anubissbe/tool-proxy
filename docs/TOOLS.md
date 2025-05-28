# Tool Execution Framework

## Overview

The Tool Execution Framework provides a secure, flexible mechanism for performing actions within a controlled environment.

## Built-in Tools

### 1. File Management Tools

#### `list_files`
- **Description**: List files in a specified directory
- **Parameters**:
  - `directory`: Path to the directory
- **Security**: Limited to defined workspace
- **Example**:
  ```python
  result = await tool_executor.execute_tool('list_files', {
      'directory': '/project/src'
  })
  ```

#### `read_file`
- **Description**: Read contents of a specific file
- **Parameters**:
  - `filepath`: Full path to the file
- **Security**: 
  - Read-only access
  - Restricted to workspace
- **Example**:
  ```python
  result = await tool_executor.execute_tool('read_file', {
      'filepath': '/project/README.md'
  })
  ```

#### `write_file`
- **Description**: Create or modify files
- **Parameters**:
  - `filepath`: Destination file path
  - `content`: File contents
- **Security**:
  - Write permissions limited to workspace
  - Prevents overwriting system files
- **Example**:
  ```python
  result = await tool_executor.execute_tool('write_file', {
      'filepath': '/project/new_script.py',
      'content': 'print("Hello, World!")'
  })
  ```

### 2. System Interaction Tools

#### `run_command`
- **Description**: Execute shell commands
- **Parameters**:
  - `command`: Shell command to execute
  - `require_permission`: Mandatory user confirmation
- **Security**:
  - Sandboxed execution
  - Limited command set
  - Detailed logging
- **Example**:
  ```python
  result = await tool_executor.execute_tool('run_command', {
      'command': 'pip list',
      'require_permission': True
  })
  ```

#### `create_directory`
- **Description**: Create new directories
- **Parameters**:
  - `path`: Directory path to create
- **Security**:
  - Limited to workspace
  - Prevents nested directory creation
- **Example**:
  ```python
  result = await tool_executor.execute_tool('create_directory', {
      'path': '/project/new_module'
  })
  ```

### 3. Search and Discovery Tools

#### `search_files`
- **Description**: Search files containing specific content
- **Parameters**:
  - `directory`: Search starting point
  - `query`: Search term
- **Security**:
  - Limited search depth
  - Workspace restrictions
- **Example**:
  ```python
  result = await tool_executor.execute_tool('search_files', {
      'directory': '/project',
      'query': 'authentication'
  })
  ```

## Custom Tool Development

### Extending Tool Executor

```python
class CustomToolExecutor(ToolExecutor):
    async def database_migration_tool(self, **kwargs):
        """
        Custom tool for database migrations
        Implement secure, controlled migration logic
        """
        # Implement tool-specific logic
        pass
```

## Tool Execution Workflow

1. Tool request received
2. Permission check
3. Workspace validation
4. Secure execution
5. Result sanitization
6. Logging and metrics

## Best Practices

- Always validate input parameters
- Implement strict permission checks
- Use minimal privilege principle
- Log all tool executions
- Provide clear error messages

## Error Handling

- Comprehensive error tracking
- Sanitized error responses
- Detailed logging for debugging