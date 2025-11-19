"""
Metadata Vision Agent System Backend

A LangChain v1 + LangGraph agentic system for autonomous product metadata extraction.
"""

from .metadata_agent import (
    ProductMetadata,
    MetadataExtractionAgent,
    extract_metadata,
)

__all__ = [
    "ProductMetadata",
    "MetadataExtractionAgent",
    "extract_metadata",
]
