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

## Quick Start

### Unix/Linux
```bash
# Basic startup
./start.sh

# Start with GPU support
./start.sh --gpu

# Start and show logs
./start.sh --logs
```

### Windows

```powershell
# Basic startup
.\start.ps1

# Start with GPU support
.\start.ps1 -Gpu

# Start and show logs
.\start.ps1 -Logs
```

## Startup Script Features

### Dependency Checking
- Validates Docker installation
- Checks NVIDIA Container Toolkit (for GPU)
- Verifies Docker Compose

### Environment Setup
- Creates `.env` file from template
- Sets up workspace directory
- Guides API key configuration

### Service Management
- Builds Docker containers
- Starts services
- Displays access points
- Optional log streaming

## Prerequisites

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

## Docker Deployment

Full Docker deployment guide is available in the [Architecture Documentation](docs/ARCHITECTURE.md).
```bash
# Build Docker image
docker build -t ollama-agent-proxy:latest .

# Run with Docker Compose
docker-compose up -d
```

## GPU Support and MCP Server

### Prerequisites for GPU Acceleration

1. NVIDIA GPU
2. NVIDIA Container Toolkit
3. Docker with NVIDIA runtime

### Installation Steps
```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Configuring MCP (Model Context Protocol) Server

1. Obtain Google Custom Search API Key:
   - Go to Google Cloud Console
   - Enable Custom Search API
   - Create credentials
   - Copy API Key and Custom Search Engine ID

2. Update `.env` file:
```bash
SEARCH_API_KEY=your_google_api_key
SEARCH_CX=your_custom_search_engine_id
```

### Running with GPU Support

```bash
# Build GPU-enabled containers
docker-compose -f docker-compose.yml build

# Start services
docker-compose up -d
```

### MCP Server Capabilities

The MCP Server provides:
- Internet search functionality
- Tool request processing
- Secure, async communication
- Caching mechanisms

### Verifying GPU Support

```bash
# Check GPU detection
docker run --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# Verify Ollama GPU usage
docker logs ollama
```

## Troubleshooting GPU Issues

- Ensure latest NVIDIA drivers
- Check Docker NVIDIA runtime
- Verify container capabilities
- Review system CUDA version

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
- Email: nosupport@dontemailme.com

---

**Empowering Developers with AI-Driven Coding Assistance** 🚀
