import pytest
from src.fine_tuning import fine_tune_model

def test_fine_tune_model_logs():
    fine_tune_model('test_model', 'test_data', {'param': 1})
    with open('logs/fine_tuning.log') as log:
        assert 'Fine-tuning called' in log.read()
