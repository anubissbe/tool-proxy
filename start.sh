#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check dependencies
check_dependencies() {
    echo -e "${YELLOW}Checking system dependencies...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed!${NC}"
        echo "Please install Docker from https://docs.docker.com/get-docker/"
        exit 1
    fi

    # Check NVIDIA Docker support if GPU flag is set
    if [[ "$USE_GPU" == "true" ]]; then
        if ! command -v nvidia-docker2 &> /dev/null; then
            echo -e "${RED}NVIDIA Container Toolkit is not installed!${NC}"
            echo "Install with:"
            echo "distribution=$(. /etc/os-release;echo $ID$VERSION_ID)"
            echo "curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -"
            echo "curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list"
            echo "sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit"
            exit 1
        fi
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Docker Compose is not installed!${NC}"
        echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
        exit 1
    fi
}

# Function to setup environment
setup_environment() {
    echo -e "${YELLOW}Setting up environment...${NC}"
    
    # Create .env file if not exists
    if [[ ! -f .env ]]; then
        cp .env.example .env
        echo -e "${GREEN}.env file created from template.${NC}"
        echo -e "${YELLOW}Please edit .env and add your Google Custom Search API key and Custom Search Engine ID.${NC}"
    fi

    # Create workspace directory
    mkdir -p workspace
}

# Function to build and start services
start_services() {
    echo -e "${YELLOW}Starting services...${NC}"
    
    # Determine GPU flag
    if [[ "$USE_GPU" == "true" ]]; then
        echo -e "${GREEN}Starting with GPU support${NC}"
        docker-compose -f docker-compose.yml build
        docker-compose -f docker-compose.yml up -d
    else
        echo -e "${GREEN}Starting without GPU support${NC}"
        docker-compose -f docker-compose.yml build
        docker-compose -f docker-compose.yml up -d
    fi
}

# Function to check service status
check_service_status() {
    echo -e "${YELLOW}Checking service status...${NC}"
    docker-compose ps
}

# Function to show logs
show_logs() {
    echo -e "${YELLOW}Showing service logs...${NC}"
    docker-compose logs -f
}

# Main script
main() {
    # Default to CPU mode
    USE_GPU=false

    # Parse command line arguments
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            --gpu) USE_GPU=true ;;
            --logs) SHOW_LOGS=true ;;
            *) echo "Unknown parameter: $1"; exit 1 ;;
        esac
        shift
    done

    # Run setup steps
    check_dependencies
    setup_environment
    start_services
    check_service_status

    # Show logs if requested
    if [[ "$SHOW_LOGS" == "true" ]]; then
        show_logs
    fi

    echo -e "${GREEN}Setup complete! Services are running.${NC}"
    echo -e "${YELLOW}Access points:${NC}"
    echo "- Ollama: http://localhost:11434"
    echo "- MCP Server: http://localhost:8765"
    echo "- Proxy Server: http://localhost:8000"
}

# Execute main function
main "$@"