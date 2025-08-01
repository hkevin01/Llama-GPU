import pytest
from src.edge_optimization import optimize_for_edge

def test_optimize_for_edge_logs():
    optimize_for_edge('test_model', {'edge': True})
    with open('logs/edge_optimization.log') as log:
        assert 'Edge optimization called' in log.read()
