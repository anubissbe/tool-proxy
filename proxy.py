import os
import json
import time
import uuid
import logging
from typing import Dict, Any, Optional, List, Union

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from starlette.background import BackgroundTask
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create FastAPI app explicitly
app = FastAPI()

# Add CORS middleware for development testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get Ollama host from environment, with a default fallback
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')
OLLAMA_PORT = os.getenv('OLLAMA_PORT', '11434')
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat"

# Constants
DEFAULT_MODEL = "qwen2.5-coder:7b-instruct"
DEFAULT_SYSTEM_PROMPT = "You are a helpful AI coding assistant."

# Function to list all available models
@app.get("/v1/models")
async def list_models():
    """
    List available models in OpenAI format.
    
    Returns:
        Dict[str, List[Dict]]: List of available models.
    """
    return {
        "object": "list",
        "data": [{
            "id": DEFAULT_MODEL,
            "object": "model",
            "created": int(time.time()),
            "owned_by": "ollama",
            "capabilities": {
                "agent": True
            }
        }]
    }

async def call_ollama(body: Dict[str, Any], stream: bool = False) -> Union[Dict[str, Any], httpx.Response]:
    """
    Call Ollama API and handle the response.
    
    Args:
        body (Dict[str, Any]): The request body from Continue.
        stream (bool): Whether to stream the response.
    
    Returns:
        Union[Dict[str, Any], httpx.Response]: Ollama's response.
    """
    # Add system prompt if not present
    messages = body.get("messages", [])
    if messages and not any(msg.get("role") == "system" for msg in messages):
        messages.insert(0, {"role": "system", "content": DEFAULT_SYSTEM_PROMPT})
    
    # Prepare Ollama request body
    ollama_request = {
        "model": body.get("model", DEFAULT_MODEL),
        "messages": messages,
        "stream": stream
    }
    
    logger.debug(f"Ollama Request: {json.dumps(ollama_request, indent=2)}")
    
    async with httpx.AsyncClient() as client:
        try:
            if stream:
                # Streaming response handling
                response = await client.post(
                    OLLAMA_URL, 
                    json=ollama_request, 
                    headers={"Accept": "application/json"},
                    timeout=60.0
                )
                return response
            else:
                # Non-streaming response handling
                response = await client.post(
                    OLLAMA_URL, 
                    json=ollama_request,
                    headers={"Accept": "application/json"},
                    timeout=60.0
                )
                logger.debug(f"Ollama Response Status: {response.status_code}")
                logger.debug(f"Ollama Response: {response.text}")
                return response.json()
        except Exception as e:
            logger.error(f"Ollama API Error: {str(e)}")
            raise

def transform_to_openai_format(ollama_response: Dict[str, Any], model_name: str) -> Dict[str, Any]:
    """
    Transform Ollama non-streaming response to OpenAI format.
    
    Args:
        ollama_response (Dict[str, Any]): Ollama's response.
        model_name (str): Model name.
    
    Returns:
        Dict[str, Any]: OpenAI-compatible response.
    """
    # Extract content safely with fallback to empty string
    content = ""
    if isinstance(ollama_response, dict):
        if "message" in ollama_response and isinstance(ollama_response["message"], dict):
            content = ollama_response["message"].get("content", "")
    
    # Format the response in OpenAI format
    return {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_name,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": content,
                "tool_calls": None
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }

async def process_streaming_response(response: httpx.Response, model_name: str):
    """Process a streaming response from Ollama."""
    chat_id = f"chatcmpl-{uuid.uuid4()}"
    creation_time = int(time.time())
    
    # First chunk for the role
    first_chunk = {
        "id": chat_id,
        "object": "chat.completion.chunk",
        "created": creation_time,
        "model": model_name,
        "choices": [{
            "index": 0,
            "delta": {"role": "assistant"},
            "finish_reason": None
        }]
    }
    
    yield f"data: {json.dumps(first_chunk)}\n\n"
    
    # Process the streaming content
    async for line in response.aiter_lines():
        if not line.strip():
            continue
        
        try:
            chunk_data = json.loads(line)
            content = chunk_data.get("message", {}).get("content", "")
            
            if content:
                content_chunk = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": creation_time,
                    "model": model_name,
                    "choices": [{
                        "index": 0,
                        "delta": {"content": content},
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(content_chunk)}\n\n"
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}, line: {line}")
            continue
    
    # Last chunk
    last_chunk = {
        "id": chat_id,
        "object": "chat.completion.chunk",
        "created": creation_time,
        "model": model_name,
        "choices": [{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    }
    yield f"data: {json.dumps(last_chunk)}\n\n"
    yield "data: [DONE]\n\n"

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """
    Handle chat completions with support for both streaming and non-streaming.
    
    Args:
        request (Request): Incoming HTTP request.
    
    Returns:
        Union[Dict[str, Any], StreamingResponse]: Transformed response.
    """
    try:
        body = await request.json()
        logger.debug(f"Received Chat Completion Request: {json.dumps(body, indent=2)}")
        
        # Get model name
        model_name = body.get("model", DEFAULT_MODEL)
        
        # Determine if it's a streaming request
        is_streaming = body.get("stream", False)
        
        # Handle tool_choice for agent capabilities
        tool_choice = body.get("tool_choice", None)
        
        if is_streaming:
            # Handle streaming request
            response = await call_ollama(body, stream=True)
            
            if response.status_code != 200:
                error_msg = f"Ollama API Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": error_msg}
                )
                
            # Return streaming response
            return StreamingResponse(
                process_streaming_response(response, model_name),
                media_type="text/event-stream",
                headers={
                    "Content-Type": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # Handle non-streaming request
            ollama_response = await call_ollama(body)
            response = transform_to_openai_format(ollama_response, model_name)
            logger.debug(f"Non-streaming response: {json.dumps(response, indent=2)}")
            return JSONResponse(content=response)
            
    except Exception as e:
        logger.error(f"Error in chat_completions: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )

@app.post("/v1/agent/action")
async def agent_action(request: Request):
    """
    Handle agent action requests.
    
    Args:
        request (Request): Incoming HTTP request.
    
    Returns:
        Dict[str, Any]: Agent action response.
    """
    try:
        body = await request.json()
        logger.debug(f"Received Agent Action Request: {json.dumps(body, indent=2)}")
        
        # Process the agent request (similar to chat completions)
        ollama_response = await call_ollama(body)
        
        # Extract content
        content = ""
        if isinstance(ollama_response, dict):
            if "message" in ollama_response and isinstance(ollama_response["message"], dict):
                content = ollama_response["message"].get("content", "")
        
        # Generate unique IDs
        agent_id = f"agent-{uuid.uuid4()}"
        tool_call_id = f"call-{uuid.uuid4()}"
        
        # Transform to agent action response format
        response = {
            "id": agent_id,
            "object": "agent.action",
            "created": int(time.time()),
            "model": body.get("model", DEFAULT_MODEL),
            "tool_calls": [{
                "id": tool_call_id,
                "type": "function",
                "function": {
                    "name": "agent_response",
                    "arguments": json.dumps({"response": content})
                }
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
        
        logger.debug(f"Agent action response: {json.dumps(response, indent=2)}")
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Error in agent_action: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )

# Add a simple health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("proxy:app", host="0.0.0.0", port=8000, reload=True)
    