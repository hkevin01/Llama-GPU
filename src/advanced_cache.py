"""
Advanced Caching Module
Provides model and inference result caching interfaces.
"""

from typing import Any, Dict, Optional

_model_cache = {}
_inference_cache = {}


def cache_model(model: Any, config: Dict) -> Optional[Any]:
    """
    Cache a model with given configuration in memory.
    Logs output to logs/advanced_cache.log.
    """
    key = str(config)
    _model_cache[key] = model
    with open('logs/advanced_cache.log', 'a', encoding='utf-8') as log:
        log.write(f"Model cached with key={key}\n")
    return model


def cache_inference_result(result: Any, config: Dict) -> Optional[Any]:
    """
    Cache inference result with given configuration in memory.
    Logs output to logs/advanced_cache.log.
    """
    key = str(config)
    _inference_cache[key] = result
    with open('logs/advanced_cache.log', 'a', encoding='utf-8') as log:
        log.write(f"Inference result cached with key={key}\n")
    return result
