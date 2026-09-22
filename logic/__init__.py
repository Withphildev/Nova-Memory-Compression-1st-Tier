"""HYDRANGEA Tier 1 compression package."""

from .compression_engine import (
    CompressionResult,
    TokenDecision,
    TokenizerUnavailableError,
    compress,
    compress_with_metadata,
    detect_mode,
)

__all__ = [
    "CompressionResult",
    "TokenDecision",
    "TokenizerUnavailableError",
    "compress",
    "compress_with_metadata",
    "detect_mode",
]
