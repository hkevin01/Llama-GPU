#!/usr/bin/env python3
"""
Data Analysis Example for Llama-GPU

This example demonstrates GPU-accelerated data analysis and insights generation.
GPU acceleration provides significant benefits for:
- Large dataset analysis (1000+ data points)
- Complex analytical queries
- Multiple analysis types
- Batch processing of different datasets

Usage:
    python examples/data_analysis.py --model path/to/model --data "sales_data.csv"
    python examples/data_analysis.py --model path/to/model --analysis-type "trend" --output-file insights.json
    python examples/data_analysis.py --model path/to/model --batch-size 4 --data-dir "datasets/"
"""

import argparse
import json
import time
import sys
import csv
import random
from pathlib import Path
from typing import List, Dict, Any, Union
from collections import defaultdict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llama_gpu import LlamaGPU
from utils.logging import setup_logger

logger = setup_logger(__name__)

class DataAnalyzer:
    """High-performance data analysis with GPU acceleration"""
    
    def __init__(self, model_path: str, prefer_gpu: bool = True):
        self.llama = LlamaGPU(model_path, prefer_gpu=prefer_gpu)
        self.backend_info = self.llama.get_backend_info()
        logger.info(f"Initialized DataAnalyzer with backend: {self.backend_info['backend_type']}")
        
    def analyze_data(self, data: List[Dict[str, Any]], analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze data with performance tracking"""
        start_time = time.time()
        
        # Prepare data summary
        data_summary = self._prepare_data_summary(data)
        analysis_prompt = self._create_analysis_prompt(data_summary, analysis_type)
        
        try:
            # Generate analysis
            max_tokens = self._get_analysis_tokens(analysis_type)
            result = self.llama.infer(analysis_prompt, max_tokens=max_tokens, temperature=0.3)
            
            analysis_time = time.time() - start_time
            token_count = len(result.split())
            
            return {
                "analysis_type": analysis_type,
                "data_points": len(data),
                "data_summary": data_summary,
                "analysis_result": result,
                "token_count": token_count,
                "analysis_time": analysis_time,
                "tokens_per_second": token_count / analysis_time if analysis_time > 0 else 0,
                "backend": self.backend_info['backend_type'],
                "gpu_used": self.backend_info['backend_type'] != 'cpu'
            }
            
        except Exception as e:
            logger.error(f"Data analysis failed: {e}")
            return {
                "analysis_type": analysis_type,
                "error": str(e),
                "analysis_time": time.time() - start_time
            }
    
    def batch_analyze(self, datasets: List[List[Dict[str, Any]]], analysis_type: str = "comprehensive") -> List[Dict[str, Any]]:
        """Analyze multiple datasets in batch"""
        start_time = time.time()
        
        # Process in batches for optimal GPU utilization
        batch_size = 3 if self.backend_info['backend_type'] != 'cpu' else 1
        results = []
        
        for i in range(0, len(datasets), batch_size):
            batch_datasets = datasets[i:i + batch_size]
            batch_results = []
            
            for dataset in batch_datasets:
                result = self.analyze_data(dataset, analysis_type)
                batch_results.append(result)
            
            results.extend(batch_results)
        
        total_time = time.time() - start_time
        total_tokens = sum(r.get('token_count', 0) for r in results)
        
        logger.info(f"Batch data analysis completed: {len(results)} analyses, {total_tokens} tokens, {total_time:.2f}s")
        logger.info(f"Average tokens per second: {total_tokens / total_time:.2f}")
        
        return results
    
    def _prepare_data_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare a comprehensive summary of the data"""
        if not data:
            return {"error": "No data provided"}
        
        # Get all unique keys
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        summary = {
            "total_records": len(data),
            "fields": list(all_keys),
            "field_analysis": {}
        }
        
        # Analyze each field
        for field in all_keys:
            values = [item.get(field) for item in data if item.get(field) is not None]
            if not values:
                continue
                
            field_summary = {
                "count": len(values),
                "unique_count": len(set(str(v) for v in values)),
                "sample_values": list(set(str(v) for v in values[:5]))
            }
            
            # Try to determine data type and calculate statistics
            try:
                numeric_values = [float(v) for v in values if str(v).replace('.', '').replace('-', '').isdigit()]
                if numeric_values:
                    field_summary.update({
                        "type": "numeric",
                        "min": min(numeric_values),
                        "max": max(numeric_values),
                        "avg": sum(numeric_values) / len(numeric_values)
                    })
                else:
                    field_summary["type"] = "categorical"
            except (ValueError, TypeError):
                field_summary["type"] = "categorical"
            
            summary["field_analysis"][field] = field_summary
        
        return summary
    
    def _create_analysis_prompt(self, data_summary: Dict[str, Any], analysis_type: str) -> str:
        """Create analysis-specific prompts"""
        analysis_prompts = {
            "trend": """Analyze the following data for trends and patterns:

Data Summary:
{data_summary}

Focus on:
- Identifying trends over time
- Seasonal patterns
- Growth or decline patterns
- Anomalies or outliers

Provide a detailed trend analysis:""",
            
            "correlation": """Analyze the following data for correlations and relationships:

Data Summary:
{data_summary}

Focus on:
- Relationships between different fields
- Correlation strength and direction
- Potential causal relationships
- Statistical significance

Provide a detailed correlation analysis:""",
            
            "insights": """Generate business insights from the following data:

Data Summary:
{data_summary}

Focus on:
- Key business insights
- Actionable recommendations
- Risk factors and opportunities
- Performance indicators

Provide detailed business insights:""",
            
            "comprehensive": """Perform a comprehensive analysis of the following data:

Data Summary:
{data_summary}

Provide a complete analysis including:
- Data quality assessment
- Key patterns and trends
- Statistical insights
- Business implications
- Recommendations

Provide a comprehensive analysis:"""
        }
        
        prompt_template = analysis_prompts.get(analysis_type, analysis_prompts["comprehensive"])
        return prompt_template.format(data_summary=json.dumps(data_summary, indent=2))
    
    def _get_analysis_tokens(self, analysis_type: str) -> int:
        """Get token limit based on analysis type"""
        return {
            "trend": 400,
            "correlation": 500,
            "insights": 600,
            "comprehensive": 800
        }[analysis_type]

def generate_sample_data(data_type: str, size: int = 100) -> List[Dict[str, Any]]:
    """Generate sample data for testing"""
    if data_type == "sales":
        return [
            {
                "date": f"2024-{month:02d}-{day:02d}",
                "product": random.choice(["Laptop", "Phone", "Tablet", "Monitor"]),
                "sales_amount": round(random.uniform(100, 2000), 2),
                "quantity": random.randint(1, 10),
                "region": random.choice(["North", "South", "East", "West"]),
                "customer_type": random.choice(["Individual", "Business", "Government"])
            }
            for month in range(1, 13)
            for day in range(1, 29)
            for _ in range(size // 336)  # Approximate distribution
        ]
    
    elif data_type == "user_behavior":
        return [
            {
                "user_id": f"user_{i:04d}",
                "session_duration": random.randint(60, 3600),
                "pages_visited": random.randint(1, 20),
                "conversion": random.choice([True, False]),
                "device": random.choice(["Mobile", "Desktop", "Tablet"]),
                "time_of_day": random.choice(["Morning", "Afternoon", "Evening", "Night"])
            }
            for i in range(size)
        ]
    
    elif data_type == "financial":
        return [
            {
                "date": f"2024-{month:02d}-{day:02d}",
                "revenue": round(random.uniform(10000, 100000), 2),
                "expenses": round(random.uniform(5000, 80000), 2),
                "profit": 0,  # Will be calculated
                "department": random.choice(["Sales", "Marketing", "Engineering", "Support"]),
                "region": random.choice(["US", "Europe", "Asia", "Other"])
            }
            for month in range(1, 13)
            for day in range(1, 29)
            for _ in range(size // 336)
        ]
    
    else:  # generic
        return [
            {
                "id": i,
                "value": random.randint(1, 1000),
                "category": random.choice(["A", "B", "C", "D"]),
                "score": round(random.uniform(0, 100), 2),
                "active": random.choice([True, False])
            }
            for i in range(size)
        ]

def load_data_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Load data from CSV file"""
    data = []
    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
        return data
    except Exception as e:
        logger.error(f"Failed to load data from {file_path}: {e}")
        return []

def benchmark_gpu_vs_cpu(analyzer: DataAnalyzer, data: List[Dict[str, Any]], analysis_type: str = "comprehensive"):
    """Benchmark GPU vs CPU performance for data analysis"""
    logger.info("Running GPU vs CPU data analysis benchmark...")
    
    # Test GPU (if available)
    gpu_result = analyzer.analyze_data(data, analysis_type)
    
    # Test CPU
    cpu_analyzer = DataAnalyzer(analyzer.llama.model_path, prefer_gpu=False)
    cpu_result = cpu_analyzer.analyze_data(data, analysis_type)
    
    # Calculate speedup
    if cpu_result.get('analysis_time', 0) > 0 and gpu_result.get('analysis_time', 0) > 0:
        speedup = cpu_result['analysis_time'] / gpu_result['analysis_time']
        logger.info(f"GPU Speedup: {speedup:.2f}x faster than CPU")
        logger.info(f"GPU: {gpu_result.get('tokens_per_second', 0):.2f} tokens/sec")
        logger.info(f"CPU: {cpu_result.get('tokens_per_second', 0):.2f} tokens/sec")
    
    return gpu_result, cpu_result

def main():
    parser = argparse.ArgumentParser(description="GPU-accelerated data analysis example")
    parser.add_argument("--model", required=True, help="Path to the LLaMA model")
    parser.add_argument("--data", help="Path to CSV data file")
    parser.add_argument("--data-type", choices=["sales", "user_behavior", "financial", "generic"], 
                       default="sales", help="Type of sample data to generate")
    parser.add_argument("--data-size", type=int, default=100, help="Size of sample data to generate")
    parser.add_argument("--analysis-type", choices=["trend", "correlation", "insights", "comprehensive"], 
                       default="comprehensive", help="Type of analysis to perform")
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size for multiple datasets")
    parser.add_argument("--output-file", help="Output file for results (JSON)")
    parser.add_argument("--benchmark", action="store_true", help="Run GPU vs CPU benchmark")
    parser.add_argument("--prefer-gpu", action="store_true", default=True, help="Prefer GPU acceleration")
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = DataAnalyzer(args.model, prefer_gpu=args.prefer_gpu)
    
    # Load or generate data
    if args.data:
        data = load_data_from_file(args.data)
        if not data:
            logger.warning("Failed to load data from file, generating sample data")
            data = generate_sample_data(args.data_type, args.data_size)
    else:
        data = generate_sample_data(args.data_type, args.data_size)
    
    results = []
    
    if args.benchmark:
        # Run benchmark
        gpu_result, cpu_result = benchmark_gpu_vs_cpu(analyzer, data, args.analysis_type)
        results.extend([gpu_result, cpu_result])
    
    elif args.batch_size > 1:
        # Multiple datasets in batch
        datasets = [generate_sample_data(args.data_type, args.data_size) for _ in range(args.batch_size)]
        results = analyzer.batch_analyze(datasets, args.analysis_type)
        
    else:
        # Single dataset analysis
        result = analyzer.analyze_data(data, args.analysis_type)
        results.append(result)
        
        # Print analysis
        print(f"\n{'='*60}")
        print(f"DATA ANALYSIS: {args.analysis_type.upper()}")
        print(f"{'='*60}")
        print(f"Data points: {result['data_points']}")
        print(f"Analysis result:\n{result['analysis_result']}")
    
    # Print performance summary
    if results:
        print(f"\n{'='*60}")
        print("DATA ANALYSIS PERFORMANCE SUMMARY")
        print(f"{'='*60}")
        
        total_tokens = sum(r.get('token_count', 0) for r in results)
        total_time = sum(r.get('analysis_time', 0) for r in results)
        gpu_results = [r for r in results if r.get('gpu_used', False)]
        cpu_results = [r for r in results if not r.get('gpu_used', False)]
        
        print(f"Total analyses: {len(results)}")
        print(f"Total tokens: {total_tokens}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average tokens per second: {total_tokens / total_time:.2f}" if total_time > 0 else "N/A")
        print(f"GPU analyses: {len(gpu_results)}")
        print(f"CPU analyses: {len(cpu_results)}")
        
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