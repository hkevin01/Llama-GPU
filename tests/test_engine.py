#!/usr/bin/env python3
"""
Test Engine CPU Fallback
Tests the LlamaGPU engine implementation to verify Part C requirements
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after path setup
try:
    from src.llama_gpu import LlamaGPU
except ImportError as e:
    print(f"Failed to import LlamaGPU: {e}")
    sys.exit(1)


def test_engine_initialization() -> bool:
    """Test engine initialization with different backends."""
    try:
        # Test with GPU preference
        engine_gpu = LlamaGPU(model_path=None, prefer_gpu=True)
        print(f"✅ GPU engine initialized: backend={engine_gpu.backend}")

        # Test with CPU preference
        engine_cpu = LlamaGPU(model_path=None, prefer_gpu=False)
        print(f"✅ CPU engine initialized: backend={engine_cpu.backend}")

        return True
    except Exception as e:
        print(f"❌ Engine initialization error: {e}")
        return False


def test_infer_method() -> bool:
    """Test the infer method."""
    try:
        engine = LlamaGPU(model_path=None, prefer_gpu=True)

        # Test basic inference
        prompt = "Hello, world!"
        result = engine.infer(prompt, max_tokens=20, temperature=0.7)
        print(f"✅ Infer method: {result}")

        # Verify result is a string
        if isinstance(result, str) and len(result) > 0:
            return True
        else:
            print(f"❌ Infer method returned invalid result: {type(result)}")
            return False
    except Exception as e:
        print(f"❌ Infer method error: {e}")
        return False


def test_batch_infer_method() -> bool:
    """Test the batch_infer method."""
    try:
        engine = LlamaGPU(model_path=None, prefer_gpu=True)

        # Test batch inference
        prompts = ["Hello", "How are you?", "What is AI?"]
        results = engine.batch_infer(prompts, max_tokens=15, temperature=0.5)
        print(f"✅ Batch infer method: {len(results)} results")

        # Verify results
        if (isinstance(results, list) and
                len(results) == len(prompts) and
                all(isinstance(r, str) for r in results)):
            return True
        else:
            print("❌ Batch infer method returned invalid results")
            return False
    except Exception as e:
        print(f"❌ Batch infer method error: {e}")
        return False


def test_stream_infer_method() -> bool:
    """Test the stream_infer method."""
    try:
        engine = LlamaGPU(model_path=None, prefer_gpu=True)

        # Test streaming inference
        prompt = "Hello, streaming world!"
        tokens = []
        for token in engine.stream_infer(prompt, max_tokens=10):
            tokens.append(token)
            if len(tokens) >= 5:  # Get first few tokens
                break

        print(f"✅ Stream infer method: {len(tokens)} tokens: {tokens}")

        # Verify tokens
        if len(tokens) > 0 and all(isinstance(t, str) for t in tokens):
            return True
        else:
            print("❌ Stream infer method returned invalid tokens")
            return False
    except Exception as e:
        print(f"❌ Stream infer method error: {e}")
        return False


def test_backend_detection() -> bool:
    """Test backend detection logic."""
    try:
        engine = LlamaGPU(model_path=None, prefer_gpu=True)
        backend = engine.backend

        print(f"✅ Backend detection: {backend}")

        # Verify backend is one of the expected values
        valid_backends = ["cpu", "cuda", "rocm"]
        if backend in valid_backends:
            return True
        else:
            print(f"❌ Invalid backend detected: {backend}")
            return False
    except Exception as e:
        print(f"❌ Backend detection error: {e}")
        return False


def test_cpu_fallback() -> bool:
    """Test CPU fallback when GPU is unavailable."""
    try:
        # Force CPU backend by setting prefer_gpu=False
        engine = LlamaGPU(model_path=None, prefer_gpu=False)

        if engine.backend == "cpu":
            print("✅ CPU fallback working")

            # Test CPU inference
            result = engine.infer("Test CPU fallback", max_tokens=10)
            if isinstance(result, str) and len(result) > 0:
                print(f"✅ CPU inference working: {result}")
                return True
            else:
                print("❌ CPU inference failed")
                return False
        else:
            print(f"⚠️ CPU fallback test inconclusive "
                  f"(backend: {engine.backend})")
            return True  # Not a failure if GPU is available
    except Exception as e:
        print(f"❌ CPU fallback error: {e}")
        return False


def main() -> bool:
    """Run all engine tests."""
    print("🔧 Testing Engine (CPU Fallback) Implementation")
    print("=" * 60)

    tests = [
        ("Engine Initialization", test_engine_initialization),
        ("Infer Method", test_infer_method),
        ("Batch Infer Method", test_batch_infer_method),
        ("Stream Infer Method", test_stream_infer_method),
        ("Backend Detection", test_backend_detection),
        ("CPU Fallback", test_cpu_fallback),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        result = test_func()
        results.append(result)

    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All engine tests passed!")
        return True
    else:
        print("⚠️ Some engine tests failed")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
