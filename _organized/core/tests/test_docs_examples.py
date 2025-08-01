import os

def test_usage_doc_exists():
    assert os.path.exists(os.path.join(os.path.dirname(__file__), '../docs/usage.md'))

def test_api_doc_exists():
    assert os.path.exists(os.path.join(os.path.dirname(__file__), '../docs/api.md'))

def test_example_script_exists():
    assert os.path.exists(os.path.join(os.path.dirname(__file__), '../examples/inference_example.py'))
