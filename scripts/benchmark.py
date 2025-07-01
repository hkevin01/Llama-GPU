#!/usr/bin/env python3
"""Benchmark script for Llama-GPU performance testing."""

import time
import csv
import json
import argparse
import statistics
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from llama_gpu import LlamaGPU
from utils.aws_detection import is_aws_gpu_instance, get_aws_gpu_info
from utils.error_handling import get_system_info

class BenchmarkRunner:
    """Benchmark runner for Llama-GPU performance testing."""
    
    def __init__(self, model_path: str, output_dir: str = "benchmarks"):
        """Initialize benchmark runner.
        
        Args:
            model_path: Path to the model
            output_dir: Directory to save benchmark results
        """
        self.model_path = model_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize LlamaGPU instances for different backends
        self.backends = {}
        self._initialize_backends()
    
    def _initialize_backends(self):
        """Initialize different backend configurations."""
        backend_configs = [
            ("CPU", {"prefer_gpu": False, "auto_detect_aws": False}),
            ("GPU", {"prefer_gpu": True, "auto_detect_aws": False}),
            ("AWS_Optimized", {"prefer_gpu": True, "auto_detect_aws": True}),
        ]
        
        for name, config in backend_configs:
            try:
                llama = LlamaGPU(model_path=self.model_path, **config)
                self.backends[name] = llama
                print(f"✓ Initialized {name} backend: {llama.backend.__class__.__name__}")
            except Exception as e:
                print(f"✗ Failed to initialize {name} backend: {e}")
    
    def benchmark_single_inference(self, input_text: str, num_runs: int = 10) -> Dict[str, Any]:
        """Benchmark single inference performance.
        
        Args:
            input_text: Input text for inference
            num_runs: Number of benchmark runs
            
        Returns:
            Dictionary with benchmark results
        """
        results = {}
        
        for backend_name, llama in self.backends.items():
            print(f"\nBenchmarking {backend_name} backend...")
            times = []
            
            # Warmup run
            try:
                _ = llama.infer(input_text)
            except Exception as e:
                print(f"  ✗ Warmup failed: {e}")
                continue
            
            # Benchmark runs
            for i in range(num_runs):
                try:
                    start_time = time.time()
                    output = llama.infer(input_text)
                    end_time = time.time()
                    
                    inference_time = end_time - start_time
                    times.append(inference_time)
                    
                    if i == 0:  # Save first output for verification
                        results[f"{backend_name}_first_output"] = output
                        
                except Exception as e:
                    print(f"  ✗ Run {i+1} failed: {e}")
                    continue
            
            if times:
                results[backend_name] = {
                    'times': times,
                    'mean': statistics.mean(times),
                    'median': statistics.median(times),
                    'std': statistics.stdev(times) if len(times) > 1 else 0,
                    'min': min(times),
                    'max': max(times),
                    'successful_runs': len(times)
                }
                print(f"  ✓ Completed {len(times)} runs")
                print(f"    Mean: {results[backend_name]['mean']:.4f}s")
                print(f"    Median: {results[backend_name]['median']:.4f}s")
        
        return results
    
    def benchmark_batch_inference(self, input_texts: List[str], batch_size: int = 4, num_runs: int = 5) -> Dict[str, Any]:
        """Benchmark batch inference performance.
        
        Args:
            input_texts: List of input texts
            batch_size: Batch size for processing
            num_runs: Number of benchmark runs
            
        Returns:
            Dictionary with benchmark results
        """
        results = {}
        
        for backend_name, llama in self.backends.items():
            print(f"\nBenchmarking {backend_name} batch inference...")
            times = []
            
            # Warmup run
            try:
                _ = llama.batch_infer(input_texts[:batch_size], batch_size=batch_size)
            except Exception as e:
                print(f"  ✗ Warmup failed: {e}")
                continue
            
            # Benchmark runs
            for i in range(num_runs):
                try:
                    start_time = time.time()
                    outputs = llama.batch_infer(input_texts, batch_size=batch_size)
                    end_time = time.time()
                    
                    inference_time = end_time - start_time
                    times.append(inference_time)
                    
                    if i == 0:  # Save first output for verification
                        results[f"{backend_name}_first_batch_output"] = outputs[:2]
                        
                except Exception as e:
                    print(f"  ✗ Run {i+1} failed: {e}")
                    continue
            
            if times:
                results[f"{backend_name}_batch"] = {
                    'times': times,
                    'mean': statistics.mean(times),
                    'median': statistics.median(times),
                    'std': statistics.stdev(times) if len(times) > 1 else 0,
                    'min': min(times),
                    'max': max(times),
                    'successful_runs': len(times),
                    'batch_size': batch_size,
                    'total_inputs': len(input_texts)
                }
                print(f"  ✓ Completed {len(times)} runs")
                print(f"    Mean: {results[f'{backend_name}_batch']['mean']:.4f}s")
                print(f"    Throughput: {len(input_texts) / results[f'{backend_name}_batch']['mean']:.2f} inputs/s")
        
        return results
    
    def save_results(self, results: Dict[str, Any], test_name: str):
        """Save benchmark results to files.
        
        Args:
            results: Benchmark results
            test_name: Name of the test
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Save human-readable results
        human_readable_file = self.output_dir / f"{test_name}_{timestamp}.txt"
        with open(human_readable_file, 'w') as f:
            f.write(f"Llama-GPU Benchmark Results\n")
            f.write(f"Test: {test_name}\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: {self.model_path}\n\n")
            
            # System information
            system_info = get_system_info()
            f.write("System Information:\n")
            for key, value in system_info.items():
                f.write(f"  {key}: {value}\n")
            
            # AWS information
            if is_aws_gpu_instance():
                aws_info = get_aws_gpu_info()
                f.write(f"\nAWS GPU Information:\n")
                for key, value in aws_info.items():
                    f.write(f"  {key}: {value}\n")
            
            f.write("\n" + "="*50 + "\n\n")
            
            # Backend information
            for backend_name, llama in self.backends.items():
                f.write(f"{backend_name} Backend:\n")
                backend_info = llama.get_backend_info()
                for key, value in backend_info.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")
            
            # Results
            for key, value in results.items():
                if isinstance(value, dict) and 'times' in value:
                    f.write(f"{key} Results:\n")
                    f.write(f"  Mean: {value['mean']:.4f}s\n")
                    f.write(f"  Median: {value['median']:.4f}s\n")
                    f.write(f"  Std Dev: {value['std']:.4f}s\n")
                    f.write(f"  Min: {value['min']:.4f}s\n")
                    f.write(f"  Max: {value['max']:.4f}s\n")
                    f.write(f"  Successful Runs: {value['successful_runs']}\n")
                    if 'batch_size' in value:
                        f.write(f"  Batch Size: {value['batch_size']}\n")
                        f.write(f"  Total Inputs: {value['total_inputs']}\n")
                        f.write(f"  Throughput: {value['total_inputs'] / value['mean']:.2f} inputs/s\n")
                    f.write("\n")
        
        # Save CSV results
        csv_file = self.output_dir / f"{test_name}_{timestamp}.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Backend', 'Test', 'Mean (s)', 'Median (s)', 'Std Dev (s)', 'Min (s)', 'Max (s)', 'Successful Runs'])
            
            for key, value in results.items():
                if isinstance(value, dict) and 'times' in value:
                    writer.writerow([
                        key,
                        test_name,
                        f"{value['mean']:.4f}",
                        f"{value['median']:.4f}",
                        f"{value['std']:.4f}",
                        f"{value['min']:.4f}",
                        f"{value['max']:.4f}",
                        value['successful_runs']
                    ])
        
        # Save JSON results
        json_file = self.output_dir / f"{test_name}_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump({
                'test_name': test_name,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'model_path': self.model_path,
                'system_info': system_info,
                'aws_info': get_aws_gpu_info() if is_aws_gpu_instance() else None,
                'results': results
            }, f, indent=2)
        
        print(f"\nResults saved to:")
        print(f"  Human-readable: {human_readable_file}")
        print(f"  CSV: {csv_file}")
        print(f"  JSON: {json_file}")

def main():
    """Main benchmark function."""
    parser = argparse.ArgumentParser(description="Benchmark Llama-GPU performance")
    parser.add_argument("model_path", help="Path to the model")
    parser.add_argument("--input-text", default="Hello, how are you today?", help="Input text for inference")
    parser.add_argument("--num-runs", type=int, default=10, help="Number of benchmark runs")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size for batch inference")
    parser.add_argument("--output-dir", default="benchmarks", help="Output directory for results")
    parser.add_argument("--test-type", choices=["single", "batch", "both"], default="both", 
                       help="Type of benchmark to run")
    
    args = parser.parse_args()
    
    # Create benchmark runner
    runner = BenchmarkRunner(args.model_path, args.output_dir)
    
    if not runner.backends:
        print("No backends available for benchmarking!")
        return 1
    
    # Run single inference benchmark
    if args.test_type in ["single", "both"]:
        print("Running single inference benchmark...")
        single_results = runner.benchmark_single_inference(args.input_text, args.num_runs)
        runner.save_results(single_results, "single_inference")
    
    # Run batch inference benchmark
    if args.test_type in ["batch", "both"]:
        print("Running batch inference benchmark...")
        batch_inputs = [args.input_text] * (args.batch_size * 2)  # Create multiple inputs
        batch_results = runner.benchmark_batch_inference(batch_inputs, args.batch_size, args.num_runs // 2)
        runner.save_results(batch_results, "batch_inference")
    
    return 0

if __name__ == "__main__":
    exit(main())
