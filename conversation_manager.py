"""
Conversation Manager for Ollama Agent Mode Proxy

This module handles conversation state management, including storage and
context window optimization.
"""

from typing import Dict, List, Any, Optional
import json
import os
from pathlib import Path
import time
import re

# Try to import redis, but don't fail if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class ConversationManager:
    """
    Manages conversation state and history.
    
    This class handles saving and retrieving conversation history, along with
    context window management to prevent exceeding model token limits.
    """
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, expiry_seconds: int = 3600):
        """
        Initialize the conversation manager.
        
        Args:
            redis_host: Redis host address
            redis_port: Redis port
            expiry_seconds: Session expiry time in seconds
        """
        self.expiry = expiry_seconds
        
        # Try to connect to Redis if available
        if REDIS_AVAILABLE:
            try:
                redis_host = os.environ.get("REDIS_HOST", redis_host)
                redis_port = int(os.environ.get("REDIS_PORT", redis_port))
                self.redis = redis.Redis(
                    host=redis_host, 
                    port=redis_port,
                    decode_responses=True
                )
                # Test connection
                self.redis.ping()
                self.use_redis = True
            except Exception as e:
                print(f"Redis connection failed: {e}. Using file-based storage.")
                self.use_redis = False
        else:
            self.use_redis = False
        
        # Set up file-based storage as fallback
        if not self.use_redis:
            self.storage_dir = Path("/tmp/ollama_proxy_conversations")
            self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_message(self, session_id: str, messages: List[Dict[str, Any]]) -> None:
        """
        Save messages for a session.
        
        Args:
            session_id: Session ID
            messages: List of messages
        """
        if self.use_redis:
            key = f"conversation:{session_id}"
            self.redis.set(key, json.dumps(messages))
            self.redis.expire(key, self.expiry)
        else:
            # File-based storage
            session_file = self.storage_dir / f"{session_id}.json"
            with open(session_file, "w") as f:
                json.dump(messages, f)
    
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get message history for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of messages
        """
        if self.use_redis:
            key = f"conversation:{session_id}"
            data = self.redis.get(key)
            if data:
                return json.loads(data)
        else:
            # File-based storage
            session_file = self.storage_dir / f"{session_id}.json"
            if session_file.exists():
                with open(session_file, "r") as f:
                    return json.load(f)
        
        return []
    
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists.
        
        Args:
            session_id: Session ID
            
        Returns:
            Whether the session exists
        """
        if self.use_redis:
            key = f"conversation:{session_id}"
            return bool(self.redis.exists(key))
        else:
            # File-based storage
            session_file = self.storage_dir / f"{session_id}.json"
            return session_file.exists()
    
    def manage_context_window(self, messages: List[Dict[str, Any]], max_tokens: int = 4096) -> List[Dict[str, Any]]:
        """
        Optimize messages to fit within context window.
        
        Args:
            messages: List of messages
            max_tokens: Maximum token count
            
        Returns:
            Optimized list of messages
        """
        if not messages:
            return []
        
        # Estimate token count
        estimated_tokens = self._estimate_token_count(messages)
        
        # If under limit, return as is
        if estimated_tokens <= max_tokens:
            return messages
        
        # Keep system message if present
        result = []
        if messages[0].get("role") == "system":
            result.append(messages[0])
            messages = messages[1:]
        
        # Calculate tokens used by system message
        system_tokens = self._estimate_token_count(result)
        remaining_tokens = max_tokens - system_tokens
        
        # If very limited tokens, use summarization strategy
        if remaining_tokens < 1000:
            # Just keep the last few messages
            last_messages = []
            for msg in reversed(messages):
                msg_tokens = self._estimate_token_count([msg])
                if msg_tokens <= remaining_tokens:
                    last_messages.insert(0, msg)
                    remaining_tokens -= msg_tokens
                else:
                    break
            
            return result + last_messages
        
        # Otherwise, use a sliding window approach
        # First, identify tool usage sequences (keep these intact)
        sequences = self._identify_tool_sequences(messages)
        
        # Now, fit as many sequences as possible
        for sequence in reversed(sequences):
            seq_tokens = self._estimate_token_count(sequence)
            if seq_tokens <= remaining_tokens:
                result.extend(sequence)
                remaining_tokens -= seq_tokens
            else:
                # If sequence doesn't fit, try to fit the most recent message
                if sequence and remaining_tokens > 0:
                    last_msg = sequence[-1]
                    last_tokens = self._estimate_token_count([last_msg])
                    if last_tokens <= remaining_tokens:
                        result.append(last_msg)
        
        # Sort messages by their original order
        return sorted(result, key=lambda x: messages.index(x) if x in messages else 0)
    
    def _estimate_token_count(self, messages: List[Dict[str, Any]]) -> int:
        """
        Estimate token count for a list of messages.
        
        Args:
            messages: List of messages
            
        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 chars per token + overhead
        total = 0
        for msg in messages:
            # Role and metadata overhead (approximately 4 tokens per message)
            total += 4
            
            # Content tokens
            if "content" in msg and msg["content"]:
                content = msg["content"]
                if isinstance(content, str):
                    total += len(content) // 4
            
            # Tool calls tokens
            if "tool_calls" in msg and msg["tool_calls"]:
                tool_calls = msg["tool_calls"]
                # Each tool call has overhead
                total += len(tool_calls) * 5
                
                for call in tool_calls:
                    # Name and id
                    if "function" in call:
                        total += len(call["function"].get("name", "")) // 4
                        
                        # Arguments
                        args = call["function"].get("arguments", "{}")
                        if isinstance(args, str):
                            total += len(args) // 4
                        elif isinstance(args, dict):
                            total += len(json.dumps(args)) // 4
            
            # Tool response tokens
            if msg.get("role") == "tool" and "content" in msg:
                content = msg["content"]
                if isinstance(content, str):
                    total += len(content) // 4
        
        return total
    
    def _identify_tool_sequences(self, messages: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Identify sequences of tool calls and responses.
        
        Args:
            messages: List of messages
            
        Returns:
            List of sequences
        """
        sequences = []
        current_sequence = []
        in_tool_sequence = False
        
        for msg in messages:
            role = msg.get("role", "")
            
            # Start of a tool sequence
            if role == "assistant" and "tool_calls" in msg and msg["tool_calls"]:
                # If we were in a sequence, save it
                if current_sequence:
                    sequences.append(current_sequence)
                
                # Start new sequence
                current_sequence = [msg]
                in_tool_sequence = True
                continue
            
            # Tool response
            if role == "tool" and in_tool_sequence:
                current_sequence.append(msg)
                continue
            
            # End of tool sequence
            if in_tool_sequence and role != "tool":
                in_tool_sequence = False
                sequences.append(current_sequence)
                current_sequence = [msg]
                continue
            
            # Regular message
            if current_sequence:
                sequences.append(current_sequence)
                current_sequence = [msg]
            else:
                current_sequence = [msg]
        
        # Add final sequence
        if current_sequence:
            sequences.append(current_sequence)
        
        return sequences