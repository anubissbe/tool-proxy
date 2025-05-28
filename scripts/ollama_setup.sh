#!/bin/bash

# Ollama Model Management Script

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# List of recommended models
RECOMMENDED_MODELS=(
    "llama3"
    "mistral"
    "codellama"
)

# Function to check if Ollama is installed
check_ollama_installed() {
    if ! command -v ollama &> /dev/null; then
        echo -e "${YELLOW}Ollama is not installed. Installing...${NC}"
        install_ollama
    else
        echo -e "${GREEN}Ollama is already installed.${NC}"
    fi
}

# Function to install Ollama
install_ollama() {
    curl https://ollama.ai/install.sh | sh
}

# Function to pull recommended models
pull_recommended_models() {
    for model in "${RECOMMENDED_MODELS[@]}"; do
        echo -e "${YELLOW}Pulling model: ${model}${NC}"
        ollama pull "$model"
    done
}

# Function to list available models
list_models() {
    echo -e "${GREEN}Installed Ollama Models:${NC}"
    ollama list
}

# Function to run a model
run_model() {
    if [ -z "$1" ]; then
        echo -e "${YELLOW}Please specify a model to run.${NC}"
        list_models
        exit 1
    fi

    ollama run "$1"
}

# Main script
main() {
    case "$1" in
        "install")
            check_ollama_installed
            ;;
        "pull")
            pull_recommended_models
            ;;
        "list")
            list_models
            ;;
        "run")
            run_model "$2"
            ;;
        *)
            echo "Usage: $0 {install|pull|list|run <model>}"
            exit 1
            ;;
    esac
}

main "$@"