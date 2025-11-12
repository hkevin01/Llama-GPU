#!/usr/bin/env python3
"""
Full Stack Integration Tests
Tests the complete Llama-GPU + Ollama + GPU integration
"""

import sys
import time
import pytest
from typing import Dict, Any

sys.path.insert(0, "/home/kevin/Projects/Llama-GPU")

try:
    from src.backends.ollama import OllamaClient, OllamaBackend
    from src.utils.gpu_detection import is_problematic_amd_gpu
    from src.utils.system_info import SystemInfo
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    print(f"Import error: {e}")


class TestSystemDetection:
    """Test system information detection."""
    
    def test_system_info_detection(self):
        """Test that system info can be detected."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")
        
        sys_info = SystemInfo.detect()
        assert sys_info is not None
        assert sys_info.os_name is not None
        assert sys_info.python_version is not None
        print(f"✅ System detected: {sys_info.os_name}")
    
    def test_gpu_detection(self):
        """Test GPU detection."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")
        
        sys_info = SystemInfo.detect()
        print(f"✅ GPU Count: {sys_info.gpu_count}")
        print(f"✅ Architectures: {sys_info.gpu_architectures}")
        
        # Test problematic GPU check
        is_problem, reason = is_problematic_amd_gpu()
        print(f"✅ Problematic GPU: {is_problem}")
        if is_problem:
            print(f"   Reason: {reason}")


class TestOllamaIntegration:
    """Test Ollama backend integration."""
    
    def test_ollama_availability(self):
        """Test if Ollama is available."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")
        
        client = OllamaClient()
        is_available = client.is_available()
        print(f"✅ Ollama available: {is_available}")
        assert isinstance(is_available, bool)
    
    def test_ollama_list_models(self):
        """Test listing Ollama models."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")
        
        client = OllamaClient()
        if not client.is_available():
            pytest.skip("Ollama not available")
        
        models = client.list_models()
        print(f"✅ Found {len(models)} models")
        for model in models:
            print(f"   • {model.get('name')}")
        assert isinstance(models, list)
    
    def test_ollama_backend_init(self):
        """Test Ollama backend initialization."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")
        
        backend = OllamaBackend()
        initialized = backend.initialize()
        print(f"✅ Backend initialized: {initialized}")
        assert isinstance(initialized, bool)
    
    @pytest.mark.slow
    def test_ollama_simple_generation(self):
        """Test simple text generation."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")
        
        client = OllamaClient()
        if not client.is_available():
            pytest.skip("Ollama not available")
        
        models = client.list_models()
        if not models:
            pytest.skip("No models available")
        
        model_name = models[0]['name']
        print(f"✅ Testing with model: {model_name}")
        
        start_time = time.time()
        response = client.generate(
            model=model_name,
            prompt="Say 'hello' in one word.",
            max_tokens=10,
            temperature=0.7
        )
        elapsed = time.time() - start_time
        
        print(f"✅ Response: {response}")
        print(f"✅ Time: {elapsed:.2f}s")
        assert isinstance(response, str)
        assert len(response) > 0


class TestCommandExecution:
    """Test safe command execution."""
    
    def test_safe_command_detection(self):
        """Test safe command detection."""
        from tools.execution.command_executor import SafeCommandExecutor
        
        executor = SafeCommandExecutor(interactive=False)
        
        # Safe commands
        assert executor.is_safe("ls -la")
        assert executor.is_safe("pwd")
        assert executor.is_safe("echo test")
        
        # Dangerous commands
        assert executor.is_dangerous("rm -rf /")
        assert not executor.is_safe("rm -rf /")
        
        # Root commands
        assert executor.requires_root("sudo apt install")
        assert executor.requires_root("systemctl status")
        
        print("✅ Command safety detection working")
    
    def test_safe_command_execution(self):
        """Test executing a safe command."""
        from tools.execution.command_executor import SafeCommandExecutor
        
        executor = SafeCommandExecutor(interactive=False)
        result = executor.execute("echo 'test'", confirm=True)
        
        assert result.success
        assert "test" in result.stdout
        print(f"✅ Command executed: {result.command}")
        print(f"✅ Output: {result.stdout.strip()}")


class TestBenchmarking:
    """Test model benchmarking capabilities."""
    
    @pytest.mark.slow
    def test_benchmark_setup(self):
        """Test benchmark tool setup."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")
        
        from tools.benchmarks.model_comparison import ModelBenchmark
        
        benchmark = ModelBenchmark()
        assert benchmark is not None
        print("✅ Benchmark tool initialized")
    
    @pytest.mark.slow
    def test_single_model_benchmark(self):
        """Test benchmarking a single model."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")
        
        from tools.benchmarks.model_comparison import ModelBenchmark
        
        client = OllamaClient()
        if not client.is_available():
            pytest.skip("Ollama not available")
        
        models = client.list_models()
        if not models:
            pytest.skip("No models available")
        
        benchmark = ModelBenchmark()
        model_name = models[0]['name']
        
        prompts = ["What is 2+2?", "Say hello."]
        result = benchmark.benchmark_model(model_name, prompts, max_tokens=20)
        
        assert result is not None
        assert "model" in result
        assert "prompts" in result
        print(f"✅ Benchmarked {model_name}")
        print(f"✅ Total time: {result.get('total_time', 0):.2f}s")


def main():
    """Run tests."""
    pytest.main([__file__, "-v", "-s"])


if __name__ == "__main__":
    main()
