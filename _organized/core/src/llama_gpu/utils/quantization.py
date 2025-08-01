"""Quantization utilities for LLaMA GPU inference."""

import torch


def apply_quantization(model: torch.nn.Module, quant_type: str = "int8") -> torch.nn.Module:
    """
    Apply quantization to the given model.

    Args:
        model: PyTorch model to quantize
        quant_type: Type of quantization ('int8', 'float16', etc.)

    Returns:
        Quantized model
    """
    if quant_type == "int8":
        # Use PyTorch built-in quantization for linear layers
        model = torch.quantization.quantize_dynamic(
            model,
            {torch.nn.Linear},
            dtype=torch.qint8
        )
    elif quant_type == "float16":
        model = model.half()
    # Extend with more quantization types as needed
    return model

