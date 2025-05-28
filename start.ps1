#!/usr/bin/env pwsh

# Function to check dependencies
function Check-Dependencies {
    Write-Host "Checking system dependencies..." -ForegroundColor Yellow

    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Host "Docker is installed: $dockerVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "Docker is not installed!" -ForegroundColor Red
        Write-Host "Please install Docker from https://docs.docker.com/get-docker/"
        exit 1
    }

    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version
        Write-Host "Docker Compose is installed: $composeVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "Docker Compose is not installed!" -ForegroundColor Red
        Write-Host "Please install Docker Compose from https://docs.docker.com/compose/install/"
        exit 1
    }
}

# Function to setup environment
function Setup-Environment {
    Write-Host "Setting up environment..." -ForegroundColor Yellow

    # Create .env file if not exists
    if (-not (Test-Path .env)) {
        Copy-Item .env.example .env
        Write-Host ".env file created from template." -ForegroundColor Green
        Write-Host "Please edit .env and add your Google Custom Search API key and Custom Search Engine ID." -ForegroundColor Yellow
    }

    # Create workspace directory
    if (-not (Test-Path workspace)) {
        New-Item -ItemType Directory -Path workspace
    }
}

# Function to build and start services
function Start-Services {
    param(
        [bool]$UseGpu = $false
    )

    Write-Host "Starting services..." -ForegroundColor Yellow

    if ($UseGpu) {
        Write-Host "Starting with GPU support" -ForegroundColor Green
        docker-compose -f docker-compose.yml build
        docker-compose -f docker-compose.yml up -d
    }
    else {
        Write-Host "Starting without GPU support" -ForegroundColor Green
        docker-compose -f docker-compose.yml build
        docker-compose -f docker-compose.yml up -d
    }
}

# Function to check service status
function Check-ServiceStatus {
    Write-Host "Checking service status..." -ForegroundColor Yellow
    docker-compose ps
}

# Function to show logs
function Show-Logs {
    Write-Host "Showing service logs..." -ForegroundColor Yellow
    docker-compose logs -f
}

# Main script function
function Main {
    param(
        [switch]$Gpu,
        [switch]$Logs
    )

    # Run setup steps
    Check-Dependencies
    Setup-Environment
    Start-Services -UseGpu:$Gpu.IsPresent
    Check-ServiceStatus

    # Show logs if requested
    if ($Logs.IsPresent) {
        Show-Logs
    }

    Write-Host "Setup complete! Services are running." -ForegroundColor Green
    Write-Host "Access points:" -ForegroundColor Yellow
    Write-Host "- Ollama: http://localhost:11434"
    Write-Host "- MCP Server: http://localhost:8765"
    Write-Host "- Proxy Server: http://localhost:8000"
}

# Make script executable
chmod +x start.ps1

# Execute main function with parameters
Main @args