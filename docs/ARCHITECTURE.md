# System Architecture

## Overview

The Ollama Agent Mode Proxy is designed as a sophisticated middleware solution that bridges the gap between Ollama language models and agent-driven development environments.

## High-Level Architecture

```
[Client Tools]
    ↓
[Ollama Agent Mode Proxy]
    ├── API Translation Layer
    ├── Tool Execution Engine
    ├── Conversation Manager
    └── Security Sandbox
    ↓
[Ollama Language Model]
    ↓
[File System / Terminal]
```

## Core Components

### 1. API Translation Layer
- Converts between OpenAI and Ollama API formats
- Handles streaming and non-streaming responses
- Manages tool calling protocols

### 2. Tool Execution Engine
- Implements secure, sandboxed tool execution
- Supports file, system, and custom tools
- Provides permission-based access control

### 3. Conversation Manager
- Tracks conversation state
- Manages context windows
- Implements session persistence via Redis

### 4. Security Sandbox
- Implements workspace isolation
- Prevents unauthorized file system access
- Provides granular permission controls

## Communication Flow

1. Client sends OpenAI-compatible request
2. Proxy translates request to Ollama format
3. Request sent to Ollama model
4. Tool calls processed securely
5. Response translated back to OpenAI format
6. Result returned to client

## Technology Stack

- **Backend**: FastAPI
- **Language Model**: Ollama
- **Caching**: Redis
- **Containerization**: Docker
- **Metrics**: Prometheus
- **Security**: Containerized execution

## Performance Considerations

- Async programming model
- Connection pooling
- Minimal overhead translation
- Efficient context management

## Security Design

- Workspace path isolation
- Containerized tool execution
- Fine-grained permission controls
- Comprehensive logging
- Rate limiting mechanisms