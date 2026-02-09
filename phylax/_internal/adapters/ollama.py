"""
Ollama Adapter

Provides integration with Ollama for local model inference.
Supports llama3, mistral, codellama, and other local models.
"""

import os
from typing import Any, Optional

from phylax._internal.capture import CaptureLayer, get_capture_layer
from phylax._internal.schema import Trace


class OllamaAdapter:
    """
    Adapter for Ollama local inference.
    
    Usage:
        adapter = OllamaAdapter()
        response, trace = adapter.chat_completion(
            model="llama3",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        capture_layer: Optional[CaptureLayer] = None,
    ):
        """
        Initialize the Ollama adapter.
        
        Args:
            host: Optional Ollama host (uses OLLAMA_HOST env var, default: http://localhost:11434)
            capture_layer: Optional custom capture layer
        """
        self.host = host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.capture_layer = capture_layer or get_capture_layer()
        self._client = None
    
    @property
    def client(self):
        """Lazy-load the Ollama client."""
        if self._client is None:
            try:
                from ollama import Client
                self._client = Client(host=self.host)
            except ImportError:
                raise ImportError(
                    "ollama package not installed. "
                    "Install with: pip install ollama"
                )
        return self._client
    
    def chat_completion(
        self,
        model: str = "llama3",
        messages: list[dict[str, str]] = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> tuple[Any, Trace]:
        """
        Create a chat completion with automatic tracing.
        
        Args:
            model: Ollama model name (e.g., "llama3", "mistral", "codellama")
            messages: List of messages with role and content
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (Ollama response, Trace)
        """
        messages = messages or []
        parameters = {
            "temperature": temperature,
            **kwargs,
        }
        
        # Ollama uses options dict for parameters
        options = {
            "temperature": temperature,
        }
        
        def make_call():
            return self.client.chat(
                model=model,
                messages=messages,
                options=options,
                **kwargs,
            )
        
        response, trace = self.capture_layer.capture(
            provider="ollama",
            model=model,
            messages=messages,
            parameters=parameters,
            call_fn=make_call,
        )
        
        return response, trace
    
    def generate(
        self,
        prompt: str,
        model: str = "llama3",
        temperature: float = 0.7,
        **kwargs,
    ) -> tuple[Any, Trace]:
        """Simple text generation with a prompt."""
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(
            model=model,
            messages=messages,
            temperature=temperature,
            **kwargs,
        )
    
    def list_models(self) -> list[str]:
        """List available local models."""
        models = self.client.list()
        return [m["name"] for m in models.get("models", [])]
