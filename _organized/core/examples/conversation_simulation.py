#!/usr/bin/env python3
"""
Conversation Simulation Example for Llama-GPU

This example demonstrates GPU-accelerated multi-turn conversation simulation.
GPU acceleration provides significant benefits for:
- Long conversation threads (10+ turns)
- Multiple conversation scenarios
- Context maintenance across turns
- Batch conversation processing

Usage:
    python examples/conversation_simulation.py --model path/to/model --scenario "customer_support"
    python examples/conversation_simulation.py --model path/to/model --turns 15 --output-file chat.json
    python examples/conversation_simulation.py --model path/to/model --batch-size 3 --scenario "interview"
"""

import argparse
import json
import time
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llama_gpu import LlamaGPU
from utils.logging import setup_logger

logger = setup_logger(__name__)

class ConversationSimulator:
    """High-performance conversation simulation with GPU acceleration"""
    
    def __init__(self, model_path: str, prefer_gpu: bool = True):
        self.llama = LlamaGPU(model_path, prefer_gpu=prefer_gpu)
        self.backend_info = self.llama.get_backend_info()
        logger.info(f"Initialized ConversationSimulator with backend: {self.backend_info['backend_type']}")
        
    def simulate_conversation(self, scenario: str, turns: int = 10, context: str = "") -> Dict[str, Any]:
        """Simulate a multi-turn conversation"""
        start_time = time.time()
        
        # Get scenario-specific prompts
        scenario_config = self._get_scenario_config(scenario)
        conversation_history = []
        
        # Initialize conversation
        if context:
            conversation_history.append(f"Context: {context}")
        
        conversation_history.append(scenario_config["initial_prompt"])
        
        try:
            for turn in range(turns):
                # Build conversation context
                full_context = "\n".join(conversation_history)
                
                # Generate response
                response = self.llama.infer(
                    full_context, 
                    max_tokens=200, 
                    temperature=0.7
                )
                
                conversation_history.append(f"Assistant: {response}")
                
                # Generate user response based on scenario
                user_response = self._generate_user_response(scenario_config, turn, response)
                conversation_history.append(f"User: {user_response}")
                
                # Add scenario-specific guidance
                if turn < len(scenario_config.get("turn_guidance", [])):
                    guidance = scenario_config["turn_guidance"][turn]
                    conversation_history.append(f"Guidance: {guidance}")
            
            simulation_time = time.time() - start_time
            total_tokens = len(" ".join(conversation_history).split())
            
            return {
                "scenario": scenario,
                "turns": turns,
                "context": context,
                "conversation": conversation_history,
                "total_tokens": total_tokens,
                "simulation_time": simulation_time,
                "tokens_per_second": total_tokens / simulation_time if simulation_time > 0 else 0,
                "backend": self.backend_info['backend_type'],
                "gpu_used": self.backend_info['backend_type'] != 'cpu'
            }
            
        except Exception as e:
            logger.error(f"Conversation simulation failed: {e}")
            return {
                "scenario": scenario,
                "error": str(e),
                "simulation_time": time.time() - start_time
            }
    
    def batch_simulate(self, scenarios: List[str], turns: int = 10) -> List[Dict[str, Any]]:
        """Simulate multiple conversations in batch"""
        start_time = time.time()
        
        # Process in batches for optimal GPU utilization
        batch_size = 2 if self.backend_info['backend_type'] != 'cpu' else 1
        results = []
        
        for i in range(0, len(scenarios), batch_size):
            batch_scenarios = scenarios[i:i + batch_size]
            batch_results = []
            
            for scenario in batch_scenarios:
                result = self.simulate_conversation(scenario, turns)
                batch_results.append(result)
            
            results.extend(batch_results)
        
        total_time = time.time() - start_time
        total_tokens = sum(r.get('total_tokens', 0) for r in results)
        
        logger.info(f"Batch conversation simulation completed: {len(results)} conversations, {total_tokens} tokens, {total_time:.2f}s")
        logger.info(f"Average tokens per second: {total_tokens / total_time:.2f}")
        
        return results
    
    def _get_scenario_config(self, scenario: str) -> Dict[str, Any]:
        """Get configuration for different conversation scenarios"""
        scenarios = {
            "customer_support": {
                "initial_prompt": "You are a helpful customer support representative. A customer has contacted you with an issue.",
                "turn_guidance": [
                    "Ask clarifying questions about the customer's problem",
                    "Provide a solution or next steps",
                    "Confirm if the solution worked",
                    "Offer additional assistance if needed"
                ]
            },
            "interview": {
                "initial_prompt": "You are conducting a job interview. The candidate has applied for a software engineering position.",
                "turn_guidance": [
                    "Ask about their technical background and experience",
                    "Present a coding challenge or technical problem",
                    "Ask about their problem-solving approach",
                    "Discuss their career goals and motivation"
                ]
            },
            "therapy": {
                "initial_prompt": "You are a supportive therapist. A client has come to you seeking help with stress and anxiety.",
                "turn_guidance": [
                    "Listen empathetically and ask about their feelings",
                    "Explore the root causes of their stress",
                    "Suggest coping strategies and techniques",
                    "Help them develop an action plan"
                ]
            },
            "teaching": {
                "initial_prompt": "You are a patient teacher explaining a complex topic to a student who is struggling to understand.",
                "turn_guidance": [
                    "Break down the concept into simpler parts",
                    "Provide concrete examples and analogies",
                    "Ask questions to check understanding",
                    "Encourage questions and provide clarification"
                ]
            },
            "negotiation": {
                "initial_prompt": "You are negotiating a business deal. The other party has made an initial offer.",
                "turn_guidance": [
                    "Acknowledge their offer and ask for clarification",
                    "Present your counter-offer with justification",
                    "Address their concerns and find common ground",
                    "Work towards a mutually beneficial agreement"
                ]
            }
        }
        
        return scenarios.get(scenario, scenarios["customer_support"])
    
    def _generate_user_response(self, scenario_config: Dict[str, Any], turn: int, assistant_response: str) -> str:
        """Generate realistic user responses based on scenario"""
        # Simple template-based user responses
        user_templates = {
            "customer_support": [
                "My product stopped working after the latest update",
                "I tried that but it didn't work",
                "Thank you, that fixed the issue",
                "Is there anything else I should know?"
            ],
            "interview": [
                "I have 5 years of experience in Python and JavaScript",
                "I would approach this by first understanding the requirements",
                "I'm passionate about learning new technologies",
                "I'm looking for opportunities to grow and lead teams"
            ],
            "therapy": [
                "I've been feeling overwhelmed at work lately",
                "I try to exercise but it's hard to find time",
                "That makes sense, I never thought about it that way",
                "I'll try those techniques and let you know how it goes"
            ],
            "teaching": [
                "I'm still confused about the main concept",
                "Can you give me a real-world example?",
                "I think I understand now, but I have a question",
                "Thank you, that really helped clarify things"
            ],
            "negotiation": [
                "We're looking for a 20% discount on the bulk order",
                "That's more than our budget allows",
                "What if we commit to a longer-term contract?",
                "I think we can work with those terms"
            ]
        }
        
        templates = user_templates.get(scenario_config.get("scenario_type", "customer_support"), user_templates["customer_support"])
        return templates[turn % len(templates)]

def get_available_scenarios() -> List[str]:
    """Get list of available conversation scenarios"""
    return ["customer_support", "interview", "therapy", "teaching", "negotiation"]

def benchmark_gpu_vs_cpu(simulator: ConversationSimulator, scenario: str, turns: int = 10):
    """Benchmark GPU vs CPU performance for conversation simulation"""
    logger.info("Running GPU vs CPU conversation simulation benchmark...")
    
    # Test GPU (if available)
    gpu_result = simulator.simulate_conversation(scenario, turns)
    
    # Test CPU
    cpu_simulator = ConversationSimulator(simulator.llama.model_path, prefer_gpu=False)
    cpu_result = cpu_simulator.simulate_conversation(scenario, turns)
    
    # Calculate speedup
    if cpu_result.get('simulation_time', 0) > 0 and gpu_result.get('simulation_time', 0) > 0:
        speedup = cpu_result['simulation_time'] / gpu_result['simulation_time']
        logger.info(f"GPU Speedup: {speedup:.2f}x faster than CPU")
        logger.info(f"GPU: {gpu_result.get('tokens_per_second', 0):.2f} tokens/sec")
        logger.info(f"CPU: {cpu_result.get('tokens_per_second', 0):.2f} tokens/sec")
    
    return gpu_result, cpu_result

def main():
    parser = argparse.ArgumentParser(description="GPU-accelerated conversation simulation example")
    parser.add_argument("--model", required=True, help="Path to the LLaMA model")
    parser.add_argument("--scenario", choices=get_available_scenarios(), 
                       default="customer_support", help="Conversation scenario")
    parser.add_argument("--turns", type=int, default=10, help="Number of conversation turns")
    parser.add_argument("--context", help="Additional context for the conversation")
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size for multiple scenarios")
    parser.add_argument("--output-file", help="Output file for results (JSON)")
    parser.add_argument("--benchmark", action="store_true", help="Run GPU vs CPU benchmark")
    parser.add_argument("--prefer-gpu", action="store_true", default=True, help="Prefer GPU acceleration")
    
    args = parser.parse_args()
    
    # Initialize simulator
    simulator = ConversationSimulator(args.model, prefer_gpu=args.prefer_gpu)
    
    results = []
    
    if args.benchmark:
        # Run benchmark with a standard scenario
        gpu_result, cpu_result = benchmark_gpu_vs_cpu(simulator, args.scenario, args.turns)
        results.extend([gpu_result, cpu_result])
    
    elif args.batch_size > 1:
        # Multiple scenarios in batch
        scenarios = get_available_scenarios()[:args.batch_size]
        results = simulator.batch_simulate(scenarios, args.turns)
        
    else:
        # Single scenario
        result = simulator.simulate_conversation(args.scenario, args.turns, args.context)
        results.append(result)
        
        # Print conversation
        print(f"\n{'='*60}")
        print(f"CONVERSATION SIMULATION: {args.scenario.upper()}")
        print(f"{'='*60}")
        for i, message in enumerate(result['conversation']):
            print(f"{i+1:2d}. {message}")
    
    # Print performance summary
    if results:
        print(f"\n{'='*60}")
        print("CONVERSATION SIMULATION PERFORMANCE SUMMARY")
        print(f"{'='*60}")
        
        total_tokens = sum(r.get('total_tokens', 0) for r in results)
        total_time = sum(r.get('simulation_time', 0) for r in results)
        gpu_results = [r for r in results if r.get('gpu_used', False)]
        cpu_results = [r for r in results if not r.get('gpu_used', False)]
        
        print(f"Total conversations: {len(results)}")
        print(f"Total tokens: {total_tokens}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average tokens per second: {total_tokens / total_time:.2f}" if total_time > 0 else "N/A")
        print(f"GPU simulations: {len(gpu_results)}")
        print(f"CPU simulations: {len(cpu_results)}")
        
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