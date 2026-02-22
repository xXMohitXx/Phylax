"""
Text Surface Adapter

Wraps existing text LLM responses into the generic Surface model.
This bridges Axis 1 text enforcement with the Axis 2 surface abstraction.

Design rules:
- Raw text is preserved without modification
- No normalization, no trimming, no encoding changes
"""

from typing import Any

from phylax._internal.surfaces.surface import Surface, SurfaceAdapter


class TextSurfaceAdapter(SurfaceAdapter):
    """
    Adapter for plain text LLM responses.

    Converts a text string into a Surface with type="text_output".
    The raw_payload is the original text string, preserved as-is.

    Usage:
        adapter = TextSurfaceAdapter()
        surface = adapter.adapt("Hello, world!")
        assert surface.type == "text_output"
        assert surface.raw_payload == "Hello, world!"
    """

    surface_type = "text_output"

    def adapt(self, raw_data: Any, **kwargs) -> Surface:
        """
        Convert text data into a Surface.

        Args:
            raw_data: Text string to wrap
            **kwargs: Optional metadata fields

        Returns:
            Surface with type="text_output" and raw_payload=raw_data
        """
        metadata = kwargs.get("metadata", {})
        return Surface(
            type="text_output",
            raw_payload=raw_data,
            metadata=metadata,
        )
