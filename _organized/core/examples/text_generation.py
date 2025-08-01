#!/usr/bin/env python3
"""
Text Generation Example for Llama-GPU

This example demonstrates GPU-accelerated text generation with various styles
and lengths. GPU acceleration provides significant benefits for:
- Long-form content generation (1000+ tokens)
- Multiple generation attempts
- Complex prompt processing
- Batch generation of different styles

Usage:
    python examples/text_generation.py --model path/to/model --prompt "Write a story about"
    python examples/text_generation.py --model path/to/model --style creative --length long
    python examples/text_generation.py --model path/to/model --batch-size 4 --output-file stories.json
"""

import argparse
import json
import time
import sys
from pathlib import Path
from typing import List, Dict, Any
import random

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llama_gpu import LlamaGPU
from utils.logging import setup_logger

logger = setup_logger(__name__)

class TextGenerator:
    """High-performance text generation with GPU acceleration"""
    
    def __init__(self, model_path: str, prefer_gpu: bool = True):
        self.llama = LlamaGPU(model_path, prefer_gpu=prefer_gpu)
        self.backend_info = self.llama.get_backend_info()
        logger.info(f"Initialized TextGenerator with backend: {self.backend_info['backend_type']}")
        
    def generate_text(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate text with performance tracking"""
        start_time = time.time()
        
        # Add generation parameters to prompt
        enhanced_prompt = f"{prompt}\n\nGenerate a detailed response:"
        
        try:
            # Use streaming for better performance on long generations
            if max_tokens > 200:
                tokens = []
                for token in self.llama.stream_infer(enhanced_prompt, max_tokens=max_tokens, temperature=temperature):
                    tokens.append(token)
                result = "".join(tokens)
            else:
                result = self.llama.infer(enhanced_prompt, max_tokens=max_tokens, temperature=temperature)
            
            generation_time = time.time() - start_time
            token_count = len(result.split())
            
            return {
                "prompt": prompt,
                "generated_text": result,
                "token_count": token_count,
                "generation_time": generation_time,
                "tokens_per_second": token_count / generation_time if generation_time > 0 else 0,
                "backend": self.backend_info['backend_type'],
                "gpu_used": self.backend_info['backend_type'] != 'cpu'
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {
                "prompt": prompt,
                "error": str(e),
                "generation_time": time.time() - start_time
            }
    
    def batch_generate(self, prompts: List[str], max_tokens: int = 500, temperature: float = 0.7) -> List[Dict[str, Any]]:
        """Generate multiple texts in batch for better GPU utilization"""
        start_time = time.time()
        
        # Process in batches for optimal GPU utilization
        batch_size = 4 if self.backend_info['backend_type'] != 'cpu' else 1
        results = []
        
        for i in range(0, len(prompts), batch_size):
            batch_prompts = prompts[i:i + batch_size]
            batch_results = self.llama.batch_infer(
                batch_prompts, 
                max_tokens=max_tokens, 
                temperature=temperature,
                batch_size=batch_size
            )
            
            for j, result in enumerate(batch_results):
                prompt = batch_prompts[j]
                token_count = len(result.split())
                results.append({
                    "prompt": prompt,
                    "generated_text": result,
                    "token_count": token_count,
                    "batch_index": i // batch_size,
                    "backend": self.backend_info['backend_type'],
                    "gpu_used": self.backend_info['backend_type'] != 'cpu'
                })
        
        total_time = time.time() - start_time
        total_tokens = sum(r['token_count'] for r in results)
        
        logger.info(f"Batch generation completed: {len(results)} texts, {total_tokens} tokens, {total_time:.2f}s")
        logger.info(f"Average tokens per second: {total_tokens / total_time:.2f}")
        
        return results

def get_style_prompts() -> Dict[str, List[str]]:
    """Get predefined prompts for different writing styles"""
    return {
        "creative": [
            "Write a fantasy story about a magical forest",
            "Create a science fiction tale about time travel",
            "Compose a poem about the ocean",
            "Write a creative story about a robot learning emotions"
        ],
        "technical": [
            "Explain how neural networks work in detail",
            "Describe the process of machine learning model training",
            "Write a technical guide for implementing GPU acceleration",
            "Explain the differences between CPU and GPU computing"
        ],
        "business": [
            "Write a business proposal for a new AI startup",
            "Create a marketing strategy for a tech product",
            "Write an executive summary for a quarterly report",
            "Compose a professional email for client communication"
        ],
        "academic": [
            "Write an academic introduction for a research paper on AI",
            "Create a literature review section on machine learning",
            "Write a methodology section for a computer science study",
            "Compose an abstract for a conference paper"
        ]
    }

def get_length_configs() -> Dict[str, Dict[str, int]]:
    """Get token configurations for different lengths"""
    return {
        "short": {"max_tokens": 100, "description": "Short responses (~100 tokens)"},
        "medium": {"max_tokens": 300, "description": "Medium responses (~300 tokens)"},
        "long": {"max_tokens": 800, "description": "Long responses (~800 tokens)"},
        "extended": {"max_tokens": 1500, "description": "Extended responses (~1500 tokens)"}
    }

def benchmark_gpu_vs_cpu(generator: TextGenerator, prompt: str, max_tokens: int = 500):
    """Benchmark GPU vs CPU performance"""
    logger.info("Running GPU vs CPU benchmark...")
    
    # Test GPU (if available)
    gpu_result = generator.generate_text(prompt, max_tokens)
    
    # Test CPU
    cpu_generator = TextGenerator(generator.llama.model_path, prefer_gpu=False)
    cpu_result = cpu_generator.generate_text(prompt, max_tokens)
    
    # Calculate speedup
    if cpu_result.get('generation_time', 0) > 0 and gpu_result.get('generation_time', 0) > 0:
        speedup = cpu_result['generation_time'] / gpu_result['generation_time']
        logger.info(f"GPU Speedup: {speedup:.2f}x faster than CPU")
        logger.info(f"GPU: {gpu_result.get('tokens_per_second', 0):.2f} tokens/sec")
        logger.info(f"CPU: {cpu_result.get('tokens_per_second', 0):.2f} tokens/sec")
    
    return gpu_result, cpu_result

def main():
    parser = argparse.ArgumentParser(description="GPU-accelerated text generation example")
    parser.add_argument("--model", required=True, help="Path to the LLaMA model")
    parser.add_argument("--prompt", help="Custom prompt for generation")
    parser.add_argument("--style", choices=["creative", "technical", "business", "academic"], 
                       help="Writing style for predefined prompts")
    parser.add_argument("--length", choices=["short", "medium", "long", "extended"], 
                       default="medium", help="Length of generated text")
    parser.add_argument("--max-tokens", type=int, help="Maximum tokens to generate")
    parser.add_argument("--temperature", type=float, default=0.7, help="Generation temperature")
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size for multiple generations")
    parser.add_argument("--output-file", help="Output file for results (JSON)")
    parser.add_argument("--benchmark", action="store_true", help="Run GPU vs CPU benchmark")
    parser.add_argument("--prefer-gpu", action="store_true", default=True, help="Prefer GPU acceleration")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = TextGenerator(args.model, prefer_gpu=args.prefer_gpu)
    
    # Get length configuration
    length_configs = get_length_configs()
    max_tokens = args.max_tokens or length_configs[args.length]["max_tokens"]
    
    results = []
    
    if args.benchmark:
        # Run benchmark with a standard prompt
        benchmark_prompt = "Write a detailed explanation of artificial intelligence and its applications in modern technology."
        gpu_result, cpu_result = benchmark_gpu_vs_cpu(generator, benchmark_prompt, max_tokens)
        results.extend([gpu_result, cpu_result])
    
    elif args.prompt:
        # Single custom prompt
        result = generator.generate_text(args.prompt, max_tokens, args.temperature)
        results.append(result)
        print(f"\nGenerated Text:\n{result['generated_text']}")
        
    elif args.style:
        # Multiple prompts in selected style
        style_prompts = get_style_prompts()[args.style]
        if args.batch_size > 1:
            results = generator.batch_generate(style_prompts, max_tokens, args.temperature)
        else:
            for prompt in style_prompts:
                result = generator.generate_text(prompt, max_tokens, args.temperature)
                results.append(result)
                print(f"\nPrompt: {prompt}")
                print(f"Generated: {result['generated_text'][:200]}...")
    
    else:
        # Default: generate creative content
        default_prompts = get_style_prompts()["creative"][:2]
        for prompt in default_prompts:
            result = generator.generate_text(prompt, max_tokens, args.temperature)
            results.append(result)
            print(f"\nPrompt: {prompt}")
            print(f"Generated: {result['generated_text'][:200]}...")
    
    # Print performance summary
    if results:
        print(f"\n{'='*60}")
        print("PERFORMANCE SUMMARY")
        print(f"{'='*60}")
        
        total_tokens = sum(r.get('token_count', 0) for r in results)
        total_time = sum(r.get('generation_time', 0) for r in results)
        gpu_results = [r for r in results if r.get('gpu_used', False)]
        cpu_results = [r for r in results if not r.get('gpu_used', False)]
        
        print(f"Total generations: {len(results)}")
        print(f"Total tokens: {total_tokens}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average tokens per second: {total_tokens / total_time:.2f}" if total_time > 0 else "N/A")
        print(f"GPU generations: {len(gpu_results)}")
        print(f"CPU generations: {len(cpu_results)}")
        
        if gpu_results and cpu_results:
            gpu_avg = sum(r.get('tokens_per_second', 0) for r in gpu_results) / len(gpu_results)
            cpu_avg = sum(r.get('tokens_per_second', 0) for r in cpu_results) / len(cpu_results)
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