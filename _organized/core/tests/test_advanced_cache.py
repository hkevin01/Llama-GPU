import pytest
from src.advanced_cache import cache_model, cache_inference_result

def test_cache_model_logs():
    cache_model('test_model', {'cache': True})
    with open('logs/advanced_cache.log') as log:
        assert 'Model caching called' in log.read()

def test_cache_inference_result_logs():
    cache_inference_result('test_result', {'cache': True})
    with open('logs/advanced_cache.log') as log:
        assert 'Inference result caching called' in log.read()
