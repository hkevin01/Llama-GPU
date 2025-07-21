"""
Data Preprocessing Utilities
Provides functions for cleaning and transforming input data.
"""

from typing import Any
import re

def clean_text(text: str) -> str:
    """Remove special characters and extra spaces."""
    text = re.sub(r'[^A-Za-z0-9 ]+', '', text)
    return ' '.join(text.split())

def to_lower(text: str) -> str:
    """Convert text to lowercase."""
    return text.lower()

def preprocess_input(data: Any) -> str:
    """Full preprocessing pipeline for input data."""
    if not isinstance(data, str):
        data = str(data)
    data = to_lower(data)
    data = clean_text(data)
    return data

def preprocess_input(input_data: Any) -> Any:
    """
    Preprocess input data for model inference.
    Args:
        input_data: Raw input data
    Returns:
        Preprocessed input
    """
    # Example: strip and lowercase if string
    if isinstance(input_data, str):
        return input_data.strip().lower()
    return input_data
