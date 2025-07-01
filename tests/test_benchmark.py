import subprocess
import sys
import os

def test_benchmark_script_runs():
    script_path = os.path.join(os.path.dirname(__file__), '../scripts/benchmark.py')
    # Use --help or dummy args to check script runs (not actual benchmark)
    result = subprocess.run([sys.executable, script_path, '--help'], capture_output=True, text=True)
    assert result.returncode == 0 or 'Usage' in result.stdout
