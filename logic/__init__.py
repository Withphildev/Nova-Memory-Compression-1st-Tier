"""HYDRANGEA Tier 1 compression package."""

from .compression_engine import CompressionResult, compress, compress_with_metadata, detect_mode

__all__ = ["CompressionResult", "compress", "compress_with_metadata", "detect_mode"]
