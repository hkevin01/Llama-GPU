import importlib.util
import os

def test_monitor_resources_script_exists():
    script_path = os.path.join(os.path.dirname(__file__), '../scripts/monitor_resources.py')
    assert os.path.exists(script_path)

def test_monitor_resources_importable():
    script_path = os.path.join(os.path.dirname(__file__), '../scripts/monitor_resources.py')
    spec = importlib.util.spec_from_file_location('monitor_resources', script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert hasattr(module, 'log_resources')
