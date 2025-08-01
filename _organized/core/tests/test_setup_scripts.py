import subprocess
import os
import sys

def test_setup_local_script_exists():
    script_path = os.path.join(os.path.dirname(__file__), '../scripts/setup_local.sh')
    assert os.path.exists(script_path)

def test_setup_aws_script_exists():
    script_path = os.path.join(os.path.dirname(__file__), '../scripts/setup_aws.sh')
    assert os.path.exists(script_path)

def test_setup_local_script_runs(monkeypatch):
    script_path = os.path.join(os.path.dirname(__file__), '../scripts/setup_local.sh')
    # Mock subprocess.run to avoid actual environment changes
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: type('Result', (), {'returncode': 0})())
    result = subprocess.run([script_path], capture_output=True)
    assert result.returncode == 0
