#!/usr/bin/env python3
"""
Interactive CLI chat mode for Llama-GPU

Usage:
    python scripts/cli_chat.py --model path/to/model
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llama_gpu import LlamaGPU


def main():
    parser = argparse.ArgumentParser(description="Interactive chat with Llama-GPU")
    parser.add_argument("--model", required=True, help="Path to the LLaMA model")
    args = parser.parse_args()

    llama = LlamaGPU(args.model)
    print("Welcome to Llama-GPU Interactive Chat! Type 'exit' to quit.")
    while True:
        prompt = input("You: ").strip()
        if prompt.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        response = llama.infer(prompt)
        print(f"Llama: {response}")

if __name__ == "__main__":
    main() 