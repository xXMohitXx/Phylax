"""
Mistral Adapter

Provides integration with Mistral AI API.
Supports mistral-large, mistral-small, codestral, and other models.
"""

import os
from typing import Any, Optional

from phylax._internal.capture import CaptureLayer, get_capture_layer
from phylax._internal.schema import Trace


class MistralAdapter:
    """
    Adapter for Mistral AI API.
    
    Usage:
        adapter = MistralAdapter()
        response, trace = adapter.chat_completion(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        capture_layer: Optional[CaptureLayer] = None,
    ):
        """
        Initialize the Mistral adapter.
        
        Args:
            api_key: Optional API key (uses MISTRAL_API_KEY env var if not provided)
            capture_layer: Optional custom capture layer
        """
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        self.capture_layer = capture_layer or get_capture_layer()
        self._client = None
    
    @property
    def client(self):
        """Lazy-load the Mistral client."""
        if self._client is None:
            try:
                from mistralai import Mistral
                self._client = Mistral(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "mistralai package not installed. "
                    "Install with: pip install mistralai"
                )
        return self._client
    
    def chat_completion(
        self,
        model: str = "mistral-large-latest",
        messages: list[dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
        **kwargs,
    ) -> tuple[Any, Trace]:
        """
        Create a chat completion with automatic tracing.
        
        Args:
            model: Model to use (e.g., "mistral-large-latest", "codestral-latest")
            messages: List of messages with role and content
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (Mistral response, Trace)
        """
        messages = messages or []
        parameters = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }
        
        def make_call():
            return self.client.chat.complete(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
        
        response, trace = self.capture_layer.capture(
            provider="mistral",
            model=model,
            messages=messages,
            parameters=parameters,
            call_fn=make_call,
        )
        
        return response, trace
    
    def generate(
        self,
        prompt: str,
        model: str = "mistral-large-latest",
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
