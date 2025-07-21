import pytest
from src.distributed_inference import run_distributed_inference

def test_distributed_inference_logs():
    run_distributed_inference('test_model', ['input1'], {'nodes': 2})
    with open('logs/distributed_inference.log') as log:
        assert 'Distributed inference called' in log.read()
