#!/usr/bin/env python3
"""
Comprehensive inference example for Llama-GPU.

This script demonstrates various usage patterns including:
- Single inference
- Batch inference
- Streaming inference
- AWS detection
- Performance benchmarking
- Error handling
"""

import argparse
import sys
import time
import logging
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llama_gpu import LlamaGPU
from utils.aws_detection import is_aws_gpu_instance, get_aws_gpu_info

def setup_logging(level: str = "INFO"):
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/inference_example.log'),
            logging.StreamHandler()
        ]
    )

def single_inference_example(llama: LlamaGPU, input_text: str):
    """Demonstrate single inference."""
    print(f"\n=== Single Inference ===")
    print(f"Input: {input_text}")
    
    start_time = time.time()
    result = llama.infer(input_text)
    end_time = time.time()
    
    print(f"Output: {result}")
    print(f"Time: {end_time - start_time:.2f} seconds")
    return result

def batch_inference_example(llama: LlamaGPU, inputs: List[str], batch_size: Optional[int] = None):
    """Demonstrate batch inference."""
    print(f"\n=== Batch Inference ===")
    print(f"Inputs: {inputs}")
    print(f"Batch size: {batch_size or 'auto'}")
    
    start_time = time.time()
    results = llama.batch_infer(inputs, batch_size)
    end_time = time.time()
    
    print(f"Results:")
    for i, (input_text, result) in enumerate(zip(inputs, results)):
        print(f"  {i+1}. Input: {input_text}")
        print(f"     Output: {result}")
    
    print(f"Total time: {end_time - start_time:.2f} seconds")
    print(f"Average time per input: {(end_time - start_time) / len(inputs):.2f} seconds")
    return results

def streaming_inference_example(llama: LlamaGPU, input_text: str, max_tokens: Optional[int] = None):
    """Demonstrate streaming inference."""
    print(f"\n=== Streaming Inference ===")
    print(f"Input: {input_text}")
    if max_tokens:
        print(f"Max tokens: {max_tokens}")
    
    print("Output: ", end="", flush=True)
    start_time = time.time()
    
    token_count = 0
    for token in llama.stream_infer(input_text, max_tokens):
        print(token, end="", flush=True)
        token_count += 1
    
    end_time = time.time()
    print()  # New line
    print(f"Generated {token_count} tokens in {end_time - start_time:.2f} seconds")
    print(f"Tokens per second: {token_count / (end_time - start_time):.2f}")

def aws_detection_example():
    """Demonstrate AWS detection capabilities."""
    print(f"\n=== AWS Detection ===")
    
    is_aws = is_aws_gpu_instance()
    print(f"Running on AWS GPU instance: {is_aws}")
    
    if is_aws:
        gpu_info = get_aws_gpu_info()
        print(f"AWS GPU information: {gpu_info}")
    else:
        print("Not running on AWS or not a GPU instance")

def backend_info_example(llama: LlamaGPU):
    """Display backend information."""
    print(f"\n=== Backend Information ===")
    
    info = llama.get_backend_info()
    for key, value in info.items():
        print(f"{key}: {value}")

def performance_benchmark(llama: LlamaGPU, test_inputs: List[str], iterations: int = 3):
    """Run performance benchmark."""
    print(f"\n=== Performance Benchmark ===")
    print(f"Running {iterations} iterations with {len(test_inputs)} inputs")
    
    # Single inference benchmark
    single_times = []
    for _ in range(iterations):
        start_time = time.time()
        llama.infer(test_inputs[0])
        end_time = time.time()
        single_times.append(end_time - start_time)
    
    avg_single = sum(single_times) / len(single_times)
    print(f"Single inference average: {avg_single:.3f} seconds")
    
    # Batch inference benchmark
    batch_times = []
    for _ in range(iterations):
        start_time = time.time()
        llama.batch_infer(test_inputs)
        end_time = time.time()
        batch_times.append(end_time - start_time)
    
    avg_batch = sum(batch_times) / len(batch_times)
    print(f"Batch inference average: {avg_batch:.3f} seconds")
    print(f"Batch efficiency: {avg_single * len(test_inputs) / avg_batch:.2f}x speedup")

def error_handling_example(llama: LlamaGPU):
    """Demonstrate error handling."""
    print(f"\n=== Error Handling ===")
    
    # Test with empty input
    try:
        result = llama.infer("")
        print(f"Empty input result: {result}")
    except Exception as e:
        print(f"Empty input error: {e}")
    
    # Test with very long input
    long_input = "This is a very long input " * 1000
    try:
        result = llama.infer(long_input)
        print(f"Long input processed successfully (length: {len(result)})")
    except Exception as e:
        print(f"Long input error: {e}")

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Llama-GPU Inference Example")
    parser.add_argument("--model", required=True, help="Path to the model")
    parser.add_argument("--input", help="Single input text for inference")
    parser.add_argument("--input-file", help="File containing input texts (one per line)")
    parser.add_argument("--output-file", help="File to save results")
    parser.add_argument("--batch-size", type=int, help="Batch size for processing")
    parser.add_argument("--max-tokens", type=int, help="Maximum tokens for streaming")
    parser.add_argument("--prefer-gpu", action="store_true", default=True, help="Prefer GPU backends")
    parser.add_argument("--auto-detect-aws", action="store_true", default=True, help="Auto-detect AWS")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--benchmark", action="store_true", help="Run performance benchmark")
    parser.add_argument("--iterations", type=int, default=3, help="Number of benchmark iterations")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    try:
        # Initialize LlamaGPU
        logger.info(f"Initializing LlamaGPU with model: {args.model}")
        llama = LlamaGPU(
            model_path=args.model,
            prefer_gpu=args.prefer_gpu,
            auto_detect_aws=args.auto_detect_aws
        )
        
        # Show backend information
        backend_info_example(llama)
        
        # Show AWS detection
        aws_detection_example()
        
        # Load inputs
        inputs = []
        if args.input:
            inputs = [args.input]
        elif args.input_file:
            with open(args.input_file, 'r') as f:
                inputs = [line.strip() for line in f if line.strip()]
        else:
            # Default test inputs
            inputs = [
                "Hello, how are you?",
                "What is machine learning?",
                "Tell me a short story about a robot",
                "Explain quantum computing in simple terms"
            ]
        
        if not inputs:
            logger.error("No inputs provided")
            return 1
        
        results = []
        
        # Run inference based on input type
        if len(inputs) == 1:
            # Single inference
            result = single_inference_example(llama, inputs[0])
            results = [result]
            
            # Streaming example
            streaming_inference_example(llama, inputs[0], args.max_tokens)
        else:
            # Batch inference
            results = batch_inference_example(llama, inputs, args.batch_size)
        
        # Run benchmark if requested
        if args.benchmark:
            performance_benchmark(llama, inputs, args.iterations)
        
        # Error handling example
        error_handling_example(llama)
        
        # Save results if output file specified
        if args.output_file:
            with open(args.output_file, 'w') as f:
                for i, (input_text, result) in enumerate(zip(inputs, results)):
                    f.write(f"Input {i+1}: {input_text}\n")
                    f.write(f"Output {i+1}: {result}\n\n")
            logger.info(f"Results saved to {args.output_file}")
        
        logger.info("Inference example completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during inference: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
