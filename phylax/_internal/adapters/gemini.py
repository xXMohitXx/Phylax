"""
Gemini Adapter

Provides integration with Google's Gemini API using the new unified google-genai SDK.
Supports gemini-2.5-flash, gemini-2.5-pro, and other models.
"""

import os
from typing import Any, Optional

from phylax._internal.capture import CaptureLayer, get_capture_layer
from phylax._internal.schema import Trace


class GeminiAdapter:
    """
    Adapter for Google Gemini API (using new google-genai SDK).
    
    Usage:
        adapter = GeminiAdapter()
        response, trace = adapter.chat_completion(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        capture_layer: Optional[CaptureLayer] = None,
    ):
        """
        Initialize the Gemini adapter.
        
        Args:
            api_key: Optional API key (uses GOOGLE_API_KEY env var if not provided)
            capture_layer: Optional custom capture layer
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.capture_layer = capture_layer or get_capture_layer()
        self._client = None
    
    @property
    def client(self):
        """Lazy-load the Gemini client."""
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "google-genai package not installed. "
                    "Install with: pip install google-genai"
                )
        return self._client
    
    def chat_completion(
        self,
        model: str = "gemini-2.5-flash",
        messages: list[dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
        **kwargs,
    ) -> tuple[Any, Trace]:
        """
        Create a chat completion with automatic tracing.
        
        Args:
            model: The model to use (e.g., "gemini-2.5-flash", "gemini-2.5-pro")
            messages: List of messages with role and content
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (Gemini response, Trace)
        """
        messages = messages or []
        parameters = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }
        
        def make_call():
            from google.genai import types
            
            # Convert messages to Gemini format
            contents = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                # Map roles to Gemini format
                if role == "system":
                    contents.append(types.Content(
                        role="user",
                        parts=[types.Part(text=content)]
                    ))
                elif role == "assistant":
                    contents.append(types.Content(
                        role="model",
                        parts=[types.Part(text=content)]
                    ))
                else:
                    contents.append(types.Content(
                        role="user",
                        parts=[types.Part(text=content)]
                    ))
            
            # Create generation config
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            # Make the call using the new SDK
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            
            return response
        
        response, trace = self.capture_layer.capture(
            provider="gemini",
            model=model,
            messages=messages,
            parameters=parameters,
            call_fn=make_call,
        )
        
        return response, trace
    
    def generate(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 256,
        **kwargs,
    ) -> tuple[Any, Trace]:
        """
        Simple text generation with a prompt.
        
        Args:
            prompt: The prompt text
            model: The model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            
        Returns:
            Tuple of (response, Trace)
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
