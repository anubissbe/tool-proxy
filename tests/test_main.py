"""
Test suite for Ollama Agent Mode Proxy
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_completions_basic():
    """Test basic chat completions endpoint"""
    payload = {
        "model": "ollama/llama3",
        "messages": [
            {"role": "user", "content": "Hello, world!"}
        ]
    }
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    
    # Basic response structure validation
    data = response.json()
    assert "choices" in data
    assert len(data["choices"]) > 0
    assert "message" in data["choices"][0]