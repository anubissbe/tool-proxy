# Contributing to Ollama Agent Mode Proxy

## Welcome Contributors! 🌟

We're excited that you're interested in contributing to our project. This document provides guidelines for contributing effectively.

## Development Setup

### Prerequisites
- Python 3.10+
- Docker
- NVIDIA Container Toolkit (for GPU support)
- Git

### Local Development

1. Clone the repository
```bash
git clone https://github.com/yourusername/ollama-agent-mode-proxy.git
cd ollama-agent-mode-proxy
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Unix/macOS
# or
venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
pip install -r mcp_server/requirements.txt
pip install -r dev-requirements.txt
```

## Development Workflow

### Branch Strategy
- `main`: Stable release branch
- `develop`: Integration branch for features
- `feature/`: New feature branches
- `bugfix/`: Bug fix branches

### Contribution Process
1. Fork the repository
2. Create a feature/bugfix branch
3. Make your changes
4. Write/update tests
5. Run tests and linters
6. Submit a Pull Request

## Code Standards

### Python Guidelines
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions/classes
- Maintain 80-character line limit

### Testing
- Write unit tests for new features
- Maintain >80% test coverage
- Use `pytest` for testing
- Use `mypy` for type checking

### Documentation
- Update relevant documentation
- Add comments for complex logic
- Keep README and docs updated

## Code Review Process

1. CI checks must pass
2. At least one maintainer review required
3. Discussion and iterative improvements

## Reporting Issues

### Bug Reports
- Use GitHub Issues template
- Provide detailed description
- Include reproduction steps
- Share error logs/screenshots

### Feature Requests
- Explain the use case
- Provide potential implementation details
- Discuss potential impact

## Development Tools

### Recommended VSCode Extensions
- Python
- Docker
- Pylance
- GitHub Pull Requests

### Linting and Formatting
```bash
# Run linters
flake8 .
mypy .
black .
isort .
```

## Performance Considerations

- Optimize async code
- Minimize external API calls
- Use efficient data structures
- Implement caching strategies

## Security Best Practices

- Never commit secrets
- Use environment variables
- Implement input validation
- Follow principle of least privilege

## Community

- Be respectful and inclusive
- Help others
- Share knowledge
- Collaborate

## Licensing

By contributing, you agree to license your changes under the MIT License.

## Questions?

Open an issue or discuss in our community channels.

Happy Coding! 🚀