"""
Groq Adapter

Provides integration with Groq's LPU-accelerated inference API.
Supports Llama, Mixtral, and other models.
"""

import os
from typing import Any, Optional

from phylax._internal.capture import CaptureLayer, get_capture_layer
from phylax._internal.schema import Trace


class GroqAdapter:
    """
    Adapter for Groq API.
    
    Usage:
        adapter = GroqAdapter()
        response, trace = adapter.chat_completion(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        capture_layer: Optional[CaptureLayer] = None,
    ):
        """
        Initialize the Groq adapter.
        
        Args:
            api_key: Optional API key (uses GROQ_API_KEY env var if not provided)
            capture_layer: Optional custom capture layer
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.capture_layer = capture_layer or get_capture_layer()
        self._client = None
    
    @property
    def client(self):
        """Lazy-load the Groq client."""
        if self._client is None:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "groq package not installed. "
                    "Install with: pip install groq"
                )
        return self._client
    
    def chat_completion(
        self,
        model: str = "llama3-70b-8192",
        messages: list[dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
        **kwargs,
    ) -> tuple[Any, Trace]:
        """
        Create a chat completion with automatic tracing.
        
        Args:
            model: Model to use (e.g., "llama3-70b-8192", "mixtral-8x7b-32768")
            messages: List of messages with role and content
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (Groq response, Trace)
        """
        messages = messages or []
        parameters = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }
        
        def make_call():
            return self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
        
        response, trace = self.capture_layer.capture(
            provider="groq",
            model=model,
            messages=messages,
            parameters=parameters,
            call_fn=make_call,
        )
        
        return response, trace
    
    def generate(
        self,
        prompt: str,
        model: str = "llama3-70b-8192",
        temperature: float = 0.7,
        max_tokens: int = 256,
        **kwargs,
    ) -> tuple[Any, Trace]:
        """Simple text generation with a prompt."""
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
