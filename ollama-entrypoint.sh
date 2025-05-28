#!/bin/bash
set -e

# Start Ollama server in the background
ollama serve &

# Wait for the server to start
sleep 5

# Pull default models
ollama pull llama3 || true
ollama pull codellama || true

# Keep the container running
wait