# Ollama Agent Mode Proxy 🤖

## Documentation

- [**System Architecture**](docs/ARCHITECTURE.md)
- [**Tool Execution Framework**](docs/TOOLS.md)
- [**Security Design**](docs/SECURITY.md)
- [**Performance Optimization**](docs/PERFORMANCE.md)
- [**Integrations Guide**](docs/INTEGRATIONS.md)

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

Detailed configuration instructions are available in our [Architecture Documentation](docs/ARCHITECTURE.md).

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

## Docker Deployment

Full Docker deployment guide is available in the [Architecture Documentation](docs/ARCHITECTURE.md).
```bash
# Build Docker image
docker build -t ollama-agent-proxy:latest .

# Run with Docker Compose
docker-compose up -d
```

## Key Features

- 🔄 OpenAI-to-Ollama API Translation
- 🛠️ Dynamic Tool Execution
- 📦 Conversation Management
- 🔒 Secure Execution Environment
- 📊 Prometheus Metrics Tracking
## Supported Tools

See our comprehensive [Tools Documentation](docs/TOOLS.md) for detailed information about built-in and custom tools.

## Security

We take security seriously. Our [Security Documentation](docs/SECURITY.md) provides an in-depth look at our security design.

## Performance

Performance is a key focus. Check out our [Performance Optimization Guide](docs/PERFORMANCE.md) for details.

## Integrations

Learn about supported development environments and integration patterns in our [Integrations Guide](docs/INTEGRATIONS.md).

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
