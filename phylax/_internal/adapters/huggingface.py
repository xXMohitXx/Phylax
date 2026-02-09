"""
HuggingFace Adapter

Provides integration with HuggingFace Inference API.
Supports text generation models via the serverless API.
"""

import os
from typing import Any, Optional

from phylax._internal.capture import CaptureLayer, get_capture_layer
from phylax._internal.schema import Trace


class HuggingFaceAdapter:
    """
    Adapter for HuggingFace Inference API.
    
    Usage:
        adapter = HuggingFaceAdapter()
        response, trace = adapter.generate(
            model="meta-llama/Llama-3.1-8B-Instruct",
            prompt="Hello!"
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        capture_layer: Optional[CaptureLayer] = None,
    ):
        """
        Initialize the HuggingFace adapter.
        
        Args:
            api_key: Optional API key (uses HF_TOKEN env var if not provided)
            capture_layer: Optional custom capture layer
        """
        self.api_key = api_key or os.environ.get("HF_TOKEN")
        self.capture_layer = capture_layer or get_capture_layer()
        self._client = None
    
    @property
    def client(self):
        """Lazy-load the HuggingFace client."""
        if self._client is None:
            try:
                from huggingface_hub import InferenceClient
                self._client = InferenceClient(token=self.api_key)
            except ImportError:
                raise ImportError(
                    "huggingface_hub package not installed. "
                    "Install with: pip install huggingface_hub"
                )
        return self._client
    
    def chat_completion(
        self,
        model: str = "meta-llama/Llama-3.1-8B-Instruct",
        messages: list[dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
        **kwargs,
    ) -> tuple[Any, Trace]:
        """
        Create a chat completion with automatic tracing.
        
        Args:
            model: HuggingFace model ID
            messages: List of messages with role and content
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (HuggingFace response, Trace)
        """
        messages = messages or []
        parameters = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }
        
        def make_call():
            return self.client.chat_completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
        
        response, trace = self.capture_layer.capture(
            provider="huggingface",
            model=model,
            messages=messages,
            parameters=parameters,
            call_fn=make_call,
        )
        
        return response, trace
    
    def generate(
        self,
        prompt: str,
        model: str = "meta-llama/Llama-3.1-8B-Instruct",
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
