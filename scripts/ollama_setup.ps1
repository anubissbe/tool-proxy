#!/usr/bin/env pwsh

# Ollama Model Management Script

# Recommended models
$RECOMMENDED_MODELS = @(
    "llama3",
    "mistral",
    "codellama"
)

# Function to check if Ollama is installed
function Check-OllamaInstalled {
    try {
        $ollamaVersion = ollama --version
        Write-Host "Ollama is already installed. Version: $ollamaVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Ollama is not installed. Installing..." -ForegroundColor Yellow
        Install-Ollama
        return $false
    }
}

# Function to install Ollama
function Install-Ollama {
    Invoke-WebRequest -Uri https://ollama.ai/install.ps1 | Invoke-Expression
}

# Function to pull recommended models
function Pull-RecommendedModels {
    foreach ($model in $RECOMMENDED_MODELS) {
        Write-Host "Pulling model: $model" -ForegroundColor Yellow
        ollama pull $model
    }
}

# Function to list available models
function List-Models {
    Write-Host "Installed Ollama Models:" -ForegroundColor Green
    ollama list
}

# Function to run a model
function Run-Model {
    param([string]$ModelName)

    if ([string]::IsNullOrWhiteSpace($ModelName)) {
        Write-Host "Please specify a model to run." -ForegroundColor Yellow
        List-Models
        exit 1
    }

    ollama run $ModelName
}

# Main script logic
function Main {
    param([string]$Command, [string]$Arg)

    switch ($Command) {
        "install" { Check-OllamaInstalled }
        "pull" { Pull-RecommendedModels }
        "list" { List-Models }
        "run" { Run-Model -ModelName $Arg }
        default { 
            Write-Host "Usage: .\ollama_setup.ps1 {install|pull|list|run <model>}"
            exit 1 
        }
    }
}

# Execute main function with script arguments
Main -Command $args[0] -Arg $args[1]