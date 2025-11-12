#!/usr/bin/env python3
"""
Model Comparison and Benchmarking Tool
Compares performance across different models (Phi4-mini, DeepSeek-R1, etc.)
"""

import sys
import time
import json
from typing import Dict, List, Any
from datetime import datetime

sys.path.insert(0, "/home/kevin/Projects/Llama-GPU")
from src.backends.ollama import OllamaClient


class ModelBenchmark:
    """Benchmark and compare different models."""
    
    def __init__(self):
        self.client = OllamaClient()
        self.results = []
        
    def benchmark_model(
        self,
        model: str,
        prompts: List[str],
        max_tokens: int = 100
    ) -> Dict[str, Any]:
        """Benchmark a single model with multiple prompts."""
        print(f"\n🔍 Benchmarking {model}...")
        print("=" * 60)
        
        results = {
            "model": model,
            "prompts": [],
            "total_time": 0,
            "avg_time": 0,
            "tokens_per_second": 0
        }
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\nPrompt {i}/{len(prompts)}: {prompt[:50]}...")
            
            start_time = time.time()
            try:
                response = self.client.generate(
                    model=model,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                end_time = time.time()
                
                elapsed = end_time - start_time
                response_length = len(response.split())
                
                prompt_result = {
                    "prompt": prompt,
                    "response": response,
                    "time": elapsed,
                    "response_words": response_length,
                    "words_per_second": response_length / elapsed if elapsed > 0 else 0
                }
                
                results["prompts"].append(prompt_result)
                results["total_time"] += elapsed
                
                print(f"✅ Response time: {elapsed:.2f}s")
                print(f"📝 Response length: {response_length} words")
                print(f"⚡ Speed: {prompt_result['words_per_second']:.2f} words/sec")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                results["prompts"].append({
                    "prompt": prompt,
                    "error": str(e),
                    "time": 0
                })
        
        # Calculate averages
        successful_prompts = [p for p in results["prompts"] if "error" not in p]
        if successful_prompts:
            results["avg_time"] = results["total_time"] / len(successful_prompts)
            avg_words = sum(p["response_words"] for p in successful_prompts) / len(successful_prompts)
            results["avg_words"] = avg_words
            results["words_per_second"] = avg_words / results["avg_time"] if results["avg_time"] > 0 else 0
        
        return results
    
    def compare_models(
        self,
        models: List[str],
        prompts: List[str],
        max_tokens: int = 100
    ) -> Dict[str, Any]:
        """Compare multiple models on the same prompts."""
        print("\n🚀 Model Comparison Benchmark")
        print("=" * 60)
        print(f"Models: {', '.join(models)}")
        print(f"Prompts: {len(prompts)}")
        print(f"Max tokens: {max_tokens}")
        print()
        
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "models": models,
            "prompt_count": len(prompts),
            "max_tokens": max_tokens,
            "results": []
        }
        
        for model in models:
            result = self.benchmark_model(model, prompts, max_tokens)
            comparison["results"].append(result)
            self.results.append(result)
        
        return comparison
    
    def print_comparison_table(self, comparison: Dict[str, Any]):
        """Print formatted comparison table."""
        print("\n" + "=" * 80)
        print("📊 BENCHMARK RESULTS SUMMARY")
        print("=" * 80)
        print()
        
        # Header
        print(f"{'Model':<20} {'Avg Time (s)':<15} {'Avg Words':<12} {'Words/Sec':<12} {'Status':<10}")
        print("-" * 80)
        
        # Results
        for result in comparison["results"]:
            model = result["model"]
            avg_time = result.get("avg_time", 0)
            avg_words = result.get("avg_words", 0)
            words_per_sec = result.get("words_per_second", 0)
            
            successful = sum(1 for p in result["prompts"] if "error" not in p)
            total = len(result["prompts"])
            status = f"{successful}/{total}"
            
            print(f"{model:<20} {avg_time:<15.2f} {avg_words:<12.1f} {words_per_sec:<12.2f} {status:<10}")
        
        print()
        
        # Winner
        best_speed = max(comparison["results"], key=lambda r: r.get("words_per_second", 0))
        best_quality = min(
            [r for r in comparison["results"] if r.get("avg_time", float('inf')) > 0],
            key=lambda r: r.get("avg_time", float('inf')),
            default=None
        )
        
        print("🏆 WINNERS:")
        print(f"   Fastest: {best_speed['model']} ({best_speed.get('words_per_second', 0):.2f} words/sec)")
        if best_quality:
            print(f"   Quickest: {best_quality['model']} ({best_quality.get('avg_time', 0):.2f}s avg)")
        print()
    
    def save_results(self, comparison: Dict[str, Any], filename: str = None):
        """Save benchmark results to JSON file."""
        if filename is None:
            filename = f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = f"/home/kevin/Projects/Llama-GPU/tools/benchmarks/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        print(f"💾 Results saved to: {filepath}")


def main():
    """Main benchmark runner."""
    benchmark = ModelBenchmark()
    
    # Default benchmark prompts
    prompts = [
        "What is artificial intelligence?",
        "Explain quantum computing in simple terms.",
        "Write a Python function to sort a list.",
        "What are the benefits of machine learning?",
        "Describe the process of photosynthesis."
    ]
    
    # Get available models
    client = OllamaClient()
    if not client.is_available():
        print("❌ Ollama is not available. Please start Ollama first.")
        return
    
    available_models = client.list_models()
    model_names = [m["name"] for m in available_models]
    
    if not model_names:
        print("❌ No models found. Please install models first.")
        return
    
    print("\n📦 Available Models:")
    for i, name in enumerate(model_names, 1):
        print(f"   {i}. {name}")
    print()
    
    # Run comparison
    comparison = benchmark.compare_models(
        models=model_names,
        prompts=prompts,
        max_tokens=100
    )
    
    # Display results
    benchmark.print_comparison_table(comparison)
    
    # Save results
    benchmark.save_results(comparison)
    
    print("✅ Benchmark complete!")


if __name__ == "__main__":
    main()
