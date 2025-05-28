# 🤖 Ollama Agent Mode Proxy

## Purpose

This project creates a flexible proxy server that transforms Ollama's API into a fully-functional agent mode compatible with Continue IDE and other development tools, enabling AI-powered code generation and interaction.

## Problem Solved

Developers often face limitations with AI coding assistants:
- Inconsistent tool support across platforms
- Limited file and system interaction
- Complex API translations
- Lack of secure execution environments

Our proxy provides a unified solution that:
- Translates between Ollama and OpenAI-compatible APIs
- Implements secure, sandboxed tool execution
- Manages conversational context
- Supports advanced code generation workflows
## Key Features

🔄 **Protocol Translation**
- Convert between OpenAI and Ollama API formats
- Support for streaming and non-streaming responses

🛠️ **Dynamic Tool Execution**
- Built-in tools for file and system operations
- Secure, permission-based tool execution
- Extensible tool framework

📦 **Conversation Management**
- Stateful conversation tracking
- Context window optimization
- Multi-session support via Redis

🔒 **Advanced Security**
- Workspace-limited execution
- Containerized tool execution
- Permission-based access control

📊 **Comprehensive Monitoring**
- Prometheus metrics
- Request tracking
- Tool execution logging

## Quick Start Guide

### Prerequisites

- Python 3.10+
- Ollama (https://ollama.com)
- Redis
- Docker (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ollama-agent-mode-proxy.git
cd ollama-agent-mode-proxy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3

# Proxy Server
API_HOST=0.0.0.0
API_PORT=8000

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Workspace Configuration
WORKSPACE_PATH=/path/to/secure/workspace
```

### Running the Proxy

```bash
# Development Mode
python main.py

# Production Mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Supported Tools

### Built-in Tools

1. `list_files`: List directory contents
2. `read_file`: Read file contents
3. `write_file`: Create or modify files
4. `run_command`: Execute shell commands

## Integration Examples

### Continue IDE Configuration

```json
{
  "models": [{
    "title": "Ollama Agent",
    "provider": "openai",
    "model": "llama3",
    "apiBase": "http://localhost:8000/v1",
    "apiKey": "dummy"
  }]
}
```

## Example Use Cases

### Code Generation Workflow

```python
# Complex code generation request
response = requests.post('http://localhost:8000/v1/chat/completions', json={
    "model": "ollama/llama3",
    "messages": [
        {
            "role": "system",
            "content": "You are a Python developer assistant"
        },
        {
            "role": "user",
            "content": "Create a FastAPI endpoint for user registration"
        }
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write generated code to a file"
            }
        }
    ]
})
```
## Security Features

- Workspace path isolation
- Containerized tool execution
- Permission-based access control
- Comprehensive logging
- Rate limiting mechanisms

## Performance Optimization

- Async design with FastAPI
- Redis-based caching
- Prometheus metrics tracking
- Connection pooling

## Advanced Configuration

### Custom Tool Development

Extend the `ToolExecutor` to add custom tools.

## Monitoring and Observability

Prometheus metrics are exposed tracking:
- Request counts
- Execution durations
- Active sessions
- Tool execution statistics

## Troubleshooting

### Common Issues

1. **Ollama Not Running**
2. **Tool Execution Failures**
3. **Redis Connection Problems**

## Development & Contributing

### Running Tests

```bash
# Unit tests
pytest

# Type checking
mypy .

# Code style
flake8 .
```

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch
3. Implement your feature/fix
4. Write corresponding tests
5. Ensure all tests pass
6. Submit a pull request

## Roadmap

- [ ] Enhanced tool validation
- [ ] More language model integrations
- [ ] Advanced conversation management
- [ ] Improved security features
- [ ] Web-based configuration interface

## License

MIT License

## Support

For issues, feature requests, or contributions:
- Open a GitHub Issue
- Join our Discord community
- Email: support@example.com

---

**Empowering Developers with AI-Driven Coding Assistance** 🚀
