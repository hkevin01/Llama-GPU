#!/usr/bin/env python3
"""
Code Generation Example for Llama-GPU

This example demonstrates GPU-accelerated code generation with various programming
languages and complexity levels. GPU acceleration provides significant benefits for:
- Complex code synthesis (100+ lines)
- Multiple language support
- Code completion and refactoring
- Batch code generation for different tasks

Usage:
    python examples/code_generation.py --model path/to/model --task "Create a Python function"
    python examples/code_generation.py --model path/to/model --language python --complexity high
    python examples/code_generation.py --model path/to/model --batch-size 4 --output-file code.json
"""

import argparse
import json
import time
import sys
from pathlib import Path
from typing import List, Dict, Any, Union

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llama_gpu import LlamaGPU
from utils.logging import setup_logger

logger = setup_logger(__name__)

class CodeGenerator:
    """High-performance code generation with GPU acceleration"""
    
    def __init__(self, model_path: str, prefer_gpu: bool = True):
        self.llama = LlamaGPU(model_path, prefer_gpu=prefer_gpu)
        self.backend_info = self.llama.get_backend_info()
        logger.info(f"Initialized CodeGenerator with backend: {self.backend_info['backend_type']}")
        
    def generate_code(self, task: str, language: str = "python", complexity: str = "medium") -> Dict[str, Any]:
        """Generate code with performance tracking"""
        start_time = time.time()
        
        # Create language-specific prompt
        prompt = self._create_code_prompt(task, language, complexity)
        
        try:
            # Use streaming for complex code generation
            max_tokens = self._get_complexity_tokens(complexity)
            tokens = []
            for token in self.llama.stream_infer(prompt, max_tokens=max_tokens, temperature=0.3):
                tokens.append(token)
            result = "".join(tokens)
            
            generation_time = time.time() - start_time
            line_count = len([line for line in result.split('\n') if line.strip()])
            
            return {
                "task": task,
                "language": language,
                "complexity": complexity,
                "generated_code": result,
                "line_count": line_count,
                "generation_time": generation_time,
                "lines_per_second": line_count / generation_time if generation_time > 0 else 0,
                "backend": self.backend_info['backend_type'],
                "gpu_used": self.backend_info['backend_type'] != 'cpu'
            }
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return {
                "task": task,
                "language": language,
                "error": str(e),
                "generation_time": time.time() - start_time
            }
    
    def batch_generate(self, tasks: List[str], language: str = "python", complexity: str = "medium") -> List[Dict[str, Any]]:
        """Generate multiple code snippets in batch"""
        start_time = time.time()
        
        # Process in batches for optimal GPU utilization
        batch_size = 3 if self.backend_info['backend_type'] != 'cpu' else 1
        results = []
        
        for i in range(0, len(tasks), batch_size):
            batch_tasks = tasks[i:i + batch_size]
            batch_prompts = [self._create_code_prompt(task, language, complexity) for task in batch_tasks]
            
            max_tokens = self._get_complexity_tokens(complexity)
            batch_results = self.llama.batch_infer(
                batch_prompts, 
                max_tokens=max_tokens, 
                temperature=0.3,
                batch_size=batch_size
            )
            
            for j, (task, result) in enumerate(zip(batch_tasks, batch_results)):
                line_count = len([line for line in result.split('\n') if line.strip()])
                results.append({
                    "task": task,
                    "language": language,
                    "complexity": complexity,
                    "generated_code": result,
                    "line_count": line_count,
                    "batch_index": i // batch_size,
                    "backend": self.backend_info['backend_type'],
                    "gpu_used": self.backend_info['backend_type'] != 'cpu'
                })
        
        total_time = time.time() - start_time
        total_lines = sum(r['line_count'] for r in results)
        
        logger.info(f"Batch code generation completed: {len(results)} snippets, {total_lines} lines, {total_time:.2f}s")
        logger.info(f"Average lines per second: {total_lines / total_time:.2f}")
        
        return results
    
    def _create_code_prompt(self, task: str, language: str, complexity: str) -> str:
        """Create a language-specific code generation prompt"""
        complexity_desc = {
            "simple": "simple and concise",
            "medium": "well-structured with error handling",
            "high": "comprehensive with documentation and tests"
        }
        
        language_specifics = {
            "python": "Use Python best practices, type hints, and docstrings.",
            "javascript": "Use modern JavaScript (ES6+), proper error handling, and JSDoc comments.",
            "java": "Use Java conventions, proper exception handling, and JavaDoc comments.",
            "cpp": "Use modern C++ (C++17), RAII principles, and comprehensive error handling.",
            "rust": "Use Rust idioms, proper error handling with Result types, and documentation comments."
        }
        
        return f"""Generate {complexity_desc[complexity]} {language} code for the following task:

Task: {task}

Requirements:
- {language_specifics.get(language, "Use best practices and proper documentation.")}
- Make the code production-ready and well-documented
- Include appropriate error handling
- Follow language-specific conventions

Generate the complete code:"""
    
    def _get_complexity_tokens(self, complexity: str) -> int:
        """Get token limit based on complexity"""
        return {
            "simple": 300,
            "medium": 600,
            "high": 1200
        }[complexity]

def get_code_tasks() -> Dict[str, List[str]]:
    """Get predefined code generation tasks"""
    return {
        "python": [
            "Create a function to calculate fibonacci numbers with memoization",
            "Implement a binary search tree with insert, delete, and search methods",
            "Write a decorator for function timing and logging",
            "Create a context manager for database connections"
        ],
        "javascript": [
            "Create a Promise-based HTTP client with retry logic",
            "Implement a debounce function for search input",
            "Write a class for managing local storage with encryption",
            "Create a utility for deep object cloning"
        ],
        "java": [
            "Create a thread-safe singleton pattern implementation",
            "Implement a custom exception hierarchy for a banking system",
            "Write a utility class for JSON serialization/deserialization",
            "Create a generic cache implementation with LRU eviction"
        ],
        "cpp": [
            "Create a smart pointer implementation with reference counting",
            "Implement a thread pool with work queue",
            "Write a template class for matrix operations",
            "Create a RAII wrapper for file operations"
        ],
        "rust": [
            "Create a custom iterator for a binary tree",
            "Implement a thread-safe channel with multiple producers",
            "Write a macro for generating builder patterns",
            "Create a custom error type with proper error handling"
        ]
    }

def benchmark_gpu_vs_cpu(generator: CodeGenerator, task: str, language: str = "python", complexity: str = "medium"):
    """Benchmark GPU vs CPU performance for code generation"""
    logger.info("Running GPU vs CPU code generation benchmark...")
    
    # Test GPU (if available)
    gpu_result = generator.generate_code(task, language, complexity)
    
    # Test CPU
    cpu_generator = CodeGenerator(generator.llama.model_path, prefer_gpu=False)
    cpu_result = cpu_generator.generate_code(task, language, complexity)
    
    # Calculate speedup
    if cpu_result.get('generation_time', 0) > 0 and gpu_result.get('generation_time', 0) > 0:
        speedup = cpu_result['generation_time'] / gpu_result['generation_time']
        logger.info(f"GPU Speedup: {speedup:.2f}x faster than CPU")
        logger.info(f"GPU: {gpu_result.get('lines_per_second', 0):.2f} lines/sec")
        logger.info(f"CPU: {cpu_result.get('lines_per_second', 0):.2f} lines/sec")
    
    return gpu_result, cpu_result

def main():
    parser = argparse.ArgumentParser(description="GPU-accelerated code generation example")
    parser.add_argument("--model", required=True, help="Path to the LLaMA model")
    parser.add_argument("--task", help="Custom code generation task")
    parser.add_argument("--language", choices=["python", "javascript", "java", "cpp", "rust"], 
                       default="python", help="Programming language")
    parser.add_argument("--complexity", choices=["simple", "medium", "high"], 
                       default="medium", help="Code complexity level")
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size for multiple generations")
    parser.add_argument("--output-file", help="Output file for results (JSON)")
    parser.add_argument("--benchmark", action="store_true", help="Run GPU vs CPU benchmark")
    parser.add_argument("--prefer-gpu", action="store_true", default=True, help="Prefer GPU acceleration")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = CodeGenerator(args.model, prefer_gpu=args.prefer_gpu)
    
    results = []
    
    if args.benchmark:
        # Run benchmark with a standard task
        benchmark_task = "Create a function to sort a list of integers using quicksort algorithm"
        gpu_result, cpu_result = benchmark_gpu_vs_cpu(generator, benchmark_task, args.language, args.complexity)
        results.extend([gpu_result, cpu_result])
    
    elif args.task:
        # Single custom task
        result = generator.generate_code(args.task, args.language, args.complexity)
        results.append(result)
        print(f"\nGenerated Code:\n{result['generated_code']}")
        
    else:
        # Multiple tasks in selected language
        language_tasks = get_code_tasks()[args.language]
        if args.batch_size > 1:
            results = generator.batch_generate(language_tasks, args.language, args.complexity)
        else:
            for task in language_tasks:
                result = generator.generate_code(task, args.language, args.complexity)
                results.append(result)
                print(f"\nTask: {task}")
                print(f"Generated Code:\n{result['generated_code'][:300]}...")
    
    # Print performance summary
    if results:
        print(f"\n{'='*60}")
        print("CODE GENERATION PERFORMANCE SUMMARY")
        print(f"{'='*60}")
        
        total_lines = sum(r.get('line_count', 0) for r in results)
        total_time = sum(r.get('generation_time', 0) for r in results)
        gpu_results = [r for r in results if r.get('gpu_used', False)]
        cpu_results = [r for r in results if not r.get('gpu_used', False)]
        
        print(f"Total generations: {len(results)}")
        print(f"Total lines of code: {total_lines}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average lines per second: {total_lines / total_time:.2f}" if total_time > 0 else "N/A")
        print(f"GPU generations: {len(gpu_results)}")
        print(f"CPU generations: {len(cpu_results)}")
        
        if gpu_results and cpu_results:
            gpu_avg = sum(r.get('lines_per_second', 0) for r in gpu_results) / len(gpu_results)
            cpu_avg = sum(r.get('lines_per_second', 0) for r in cpu_results) / len(cpu_results)
            if cpu_avg > 0:
                speedup = gpu_avg / cpu_avg
                print(f"GPU vs CPU speedup: {speedup:.2f}x")
    
    # Save results
    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output_file}")

if __name__ == "__main__":
    main() 