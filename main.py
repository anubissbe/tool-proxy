"""
Ollama Agent Mode Proxy for Continue and Void

This proxy server bridges Ollama with Continue extension and Void editor to enable
full agent mode functionality. It translates between different LLM API formats while
implementing tool functions for file operations, code execution, and terminal commands.
"""

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, List, Optional, Any, AsyncGenerator
import httpx
import json
import asyncio
import os
from pathlib import Path

from tool_executor import ToolExecutor
from conversation_manager import ConversationManager
from secure_executor import SecureExecutor
from metrics import request_count, request_duration, active_sessions, tool_executions
import config

# Initialize FastAPI app
app = FastAPI(
    title="Ollama Agent Mode Proxy",
    description="Proxy server for enabling agent mode with Ollama models in Continue and Void",
    version="1.0.0",
)

# Initialize components
tool_executor = ToolExecutor(workspace_path=config.WORKSPACE_PATH)
conversation_manager = ConversationManager(
    redis_host=config.REDIS_HOST,
    redis_port=config.REDIS_PORT,
    expiry_seconds=config.SESSION_EXPIRY
)
secure_executor = SecureExecutor(workspace_path=config.WORKSPACE_PATH)


def transform_to_ollama(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform OpenAI-compatible request to Ollama format.
    
    Args:
        body: The OpenAI-format request body
        
    Returns:
        The Ollama-format request body
    """
    ollama_request = {
        "model": body.get("model", config.DEFAULT_MODEL),
        "messages": body.get("messages", []),
        "stream": body.get("stream", False),
    }
    
    # Add temperature if provided
    if "temperature" in body:
        ollama_request["temperature"] = body["temperature"]
    
    # Transform tools if provided
    if "tools" in body:
        ollama_request["tools"] = body["tools"]
    
    return ollama_request


def transform_tool_calls(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform Ollama tool calls to OpenAI format.
    
    Args:
        tool_calls: Ollama-format tool calls
        
    Returns:
        OpenAI-format tool calls
    """
    return [
        {
            "id": call.get("id", f"call_{i}"),
            "type": "function",
            "function": {
                "name": call["function"]["name"],
                "arguments": json.dumps(call["function"]["arguments"])
            }
        }
        for i, call in enumerate(tool_calls)
    ]


async def transform_ollama_stream(stream) -> AsyncGenerator[str, None]:
    """
    Convert Ollama streaming format to OpenAI SSE format.
    
    Args:
        stream: The Ollama response stream
        
    Yields:
        OpenAI-compatible SSE events
    """
    async for line in stream:
        if not line.strip():
            continue
            
        try:
            chunk = json.loads(line)
            
            # Handle tool calls
            if chunk.get("message", {}).get("tool_calls"):
                openai_chunk = {
                    "id": chunk.get("id", ""),
                    "object": "chat.completion.chunk",
                    "created": chunk.get("created", 0),
                    "model": chunk.get("model", ""),
                    "choices": [{
                        "index": 0,
                        "delta": {
                            "tool_calls": transform_tool_calls(
                                chunk["message"]["tool_calls"]
                            )
                        },
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(openai_chunk)}\n\n"
            
            # Handle content
            elif chunk.get("message", {}).get("content"):
                openai_chunk = {
                    "id": chunk.get("id", ""),
                    "object": "chat.completion.chunk",
                    "created": chunk.get("created", 0),
                    "model": chunk.get("model", ""),
                    "choices": [{
                        "index": 0,
                        "delta": {
                            "content": chunk["message"]["content"]
                        },
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(openai_chunk)}\n\n"
            
            # Handle finish reason
            if chunk.get("done", False):
                openai_chunk = {
                    "id": chunk.get("id", ""),
                    "object": "chat.completion.chunk",
                    "created": chunk.get("created", 0),
                    "model": chunk.get("model", ""),
                    "choices": [{
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop"
                    }]
                }
                yield f"data: {json.dumps(openai_chunk)}\n\n"
                
        except json.JSONDecodeError:
            continue
    
    yield "data: [DONE]\n\n"


async def handle_tool_calls(
    session_id: str, 
    messages: List[Dict[str, Any]], 
    tool_calls: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Execute tool calls and create assistant and tool response messages.
    
    Args:
        session_id: Conversation session ID
        messages: Current conversation messages
        tool_calls: Tool calls to execute
        
    Returns:
        Updated messages with tool results
    """
    new_messages = messages.copy()
    
    # Add assistant message with tool calls
    assistant_message = {
        "role": "assistant",
        "tool_calls": tool_calls
    }
    new_messages.append(assistant_message)
    
    # Execute each tool call and add tool response messages
    for call in tool_calls:
        tool_name = call["function"]["name"]
        tool_arguments = json.loads(call["function"]["arguments"])
        
        # Increment tool execution metric
        tool_executions.labels(tool_name=tool_name).inc()
        
        # Execute the tool
        tool_result = await tool_executor.execute_tool(tool_name, tool_arguments)
        
        # Add tool response message
        tool_message = {
            "role": "tool",
            "tool_call_id": call["id"],
            "name": tool_name,
            "content": json.dumps(tool_result)
        }
        new_messages.append(tool_message)
    
    # Save updated conversation
    conversation_manager.save_message(session_id, new_messages)
    
    return new_messages


@app.post("/v1/chat/completions")
async def chat_completions(request: Request, background_tasks: BackgroundTasks):
    """
    Handle chat completions endpoint.
    
    This endpoint accepts OpenAI-compatible requests and translates them to Ollama format.
    It also handles tool execution and manages conversation state.
    """
    with request_duration.time():
        body = await request.json()
        
        # Get model and validate support
        model = body.get("model", config.DEFAULT_MODEL)
        if model not in config.SUPPORTED_MODELS and not model.startswith("ollama/"):
            return {"error": "Model doesn't support tool calling"}
        
        # Increment request count metric
        request_count.labels(endpoint="chat", model=model).inc()
        
        # Get session ID (create new if not provided)
        session_id = body.get("session_id", f"session_{id(body)}")
        active_sessions.inc()
        
        # Get messages
        messages = body.get("messages", [])
        
        # If tools are not provided, add default tools
        if "tools" not in body:
            body["tools"] = config.TOOL_DEFINITIONS
        
        # Load conversation history if session exists
        if conversation_manager.session_exists(session_id):
            history = conversation_manager.get_history(session_id)
            # Only use history if it starts with the same system message
            if (not messages or 
                (messages[0].get("role") == "system" and 
                 history[0].get("role") == "system" and
                 messages[0].get("content") == history[0].get("content"))):
                messages = history
        
        # Manage context window
        messages = conversation_manager.manage_context_window(messages)
        
        # Save the initial conversation
        conversation_manager.save_message(session_id, messages)
        
        # Transform request for Ollama
        ollama_request = transform_to_ollama(body)
        
        # Stream response
        if body.get("stream", False):
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST", 
                    f"{config.OLLAMA_BASE_URL}/api/chat",
                    json=ollama_request,
                    timeout=60.0
                ) as response:
                    return StreamingResponse(
                        transform_ollama_stream(response.aiter_lines()),
                        media_type="text/event-stream"
                    )
        else:
            # Non-streaming request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{config.OLLAMA_BASE_URL}/api/chat",
                    json=ollama_request,
                    timeout=60.0
                )
                
                ollama_response = response.json()
                
                # Process tool calls if present
                if ollama_response.get("message", {}).get("tool_calls"):
                    tool_calls = transform_tool_calls(ollama_response["message"]["tool_calls"])
                    
                    # Execute tools in background
                    background_tasks.add_task(
                        handle_tool_calls,
                        session_id,
                        messages,
                        tool_calls
                    )
                    
                    # Format response
                    return {
                        "id": ollama_response.get("id", ""),
                        "object": "chat.completion",
                        "created": ollama_response.get("created", 0),
                        "model": ollama_response.get("model", model),
                        "choices": [{
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "tool_calls": tool_calls
                            },
                            "finish_reason": "tool_calls"
                        }]
                    }
                
                # Regular text response
                return {
                    "id": ollama_response.get("id", ""),
                    "object": "chat.completion",
                    "created": ollama_response.get("created", 0),
                    "model": ollama_response.get("model", model),
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": ollama_response.get("message", {}).get("content", "")
                        },
                        "finish_reason": "stop"
                    }]
                }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
