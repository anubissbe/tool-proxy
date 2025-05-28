# Ollama Management Scripts

## Overview

These scripts help manage Ollama models and integrations.

## Usage

### Installation

```bash
# Make the script executable
chmod +x ollama_setup.sh

# Install Ollama
./ollama_setup.sh install
```

### Pulling Models

```bash
# Pull recommended models
./ollama_setup.sh pull
```

### List Installed Models

```bash
./ollama_setup.sh list
```

### Run a Specific Model

```bash
./ollama_setup.sh run llama3
```

## Recommended Models

- `llama3`: Latest Llama model
- `mistral`: Efficient language model
- `codellama`: Code generation specialist

## Docker Integration

The included `docker-compose.yml` provides a complete setup with:
- Ollama service
- Redis cache
- Proxy server
- Optional Prometheus monitoring

### Starting All Services

```bash
docker-compose up -d
```

## Troubleshooting

- Ensure Docker is installed
- Check network connectivity
- Verify model download permissions