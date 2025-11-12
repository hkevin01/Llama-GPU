#!/usr/bin/env python3
"""
Unified CLI tool for Llama-GPU with Ollama integration.
Provides easy access to local AI models via command line.
"""

import sys
import argparse
import requests
import json
from typing import Optional, List, Dict

# Try importing Ollama client
try:
    sys.path.insert(0, "/home/kevin/Projects/Llama-GPU")
    from src.backends.ollama import OllamaClient
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class LLMCLi:
    """CLI interface for local LLM interactions."""
    
    def __init__(self, backend: str = "ollama", api_url: Optional[str] = None):
        """Initialize CLI.
        
        Args:
            backend: Backend to use ('ollama' or 'llama-gpu')
            api_url: Custom API URL
        """
        self.backend = backend
        self.api_url = api_url or "http://localhost:8000"
        
        if backend == "ollama" and OLLAMA_AVAILABLE:
            self.ollama = OllamaClient()
        else:
            self.ollama = None
    
    def chat(self, prompt: str, model: Optional[str] = None, stream: bool = True):
        """Interactive chat with the model."""
        if self.backend == "ollama" and self.ollama:
            model = model or "phi4-mini:3.8b"
            
            print(f"🤖 Using {model} via Ollama")
            print(f"💬 You: {prompt}")
            print("🤖 AI: ", end="", flush=True)
            
            if stream:
                for chunk in self.ollama.generate(
                    model=model,
                    prompt=prompt,
                    stream=True
                ):
                    print(chunk, end="", flush=True)
                print()  # Newline at end
            else:
                response = self.ollama.generate(model=model, prompt=prompt)
                print(response)
        else:
            # Use unified API
            self._api_chat(prompt, model)
    
    def _api_chat(self, prompt: str, model: Optional[str] = None):
        """Chat via unified API."""
        try:
            response = requests.post(
                f"{self.api_url}/v1/completions",
                json={
                    "prompt": prompt,
                    "model": model,
                    "max_tokens": 512,
                    "temperature": 0.7
                },
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            if "choices" in data and data["choices"]:
                text = data["choices"][0]["text"]
                print(f"🤖 AI: {text}")
            else:
                print("❌ No response received")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def list_models(self):
        """List available models."""
        if self.backend == "ollama" and self.ollama:
            models = self.ollama.list_models()
            print("\n📦 Available Ollama Models:")
            print("=" * 50)
            for model in models:
                name = model.get("name", "unknown")
                size = model.get("size", 0) / (1024**3)  # Convert to GB
                print(f"  • {name:30} ({size:.2f} GB)")
            print()
        else:
            try:
                response = requests.get(f"{self.api_url}/v1/models", timeout=5)
                response.raise_for_status()
                data = response.json()
                
                print("\n📦 Available Models:")
                print("=" * 50)
                for model in data.get("data", []):
                    name = model.get("id", "unknown")
                    backend = model.get("backend", "unknown")
                    print(f"  • {name:30} ({backend})")
                print()
            except Exception as e:
                print(f"❌ Error listing models: {e}")
    
    def status(self):
        """Show system status."""
        print("\n🔍 System Status")
        print("=" * 50)
        
        # Check Ollama
        if OLLAMA_AVAILABLE:
            ollama_client = OllamaClient()
            if ollama_client.is_available():
                print("✅ Ollama: Running")
                models = ollama_client.list_models()
                print(f"   Models: {len(models)}")
            else:
                print("❌ Ollama: Not available")
        else:
            print("⚠️  Ollama: Client not installed")
        
        # Check unified API
        try:
            response = requests.get(f"{self.api_url}/healthz", timeout=2)
            if response.status_code == 200:
                print(f"✅ Unified API: Running ({self.api_url})")
            else:
                print(f"⚠️  Unified API: Responding but unhealthy")
        except:
            print(f"❌ Unified API: Not available ({self.api_url})")
        
        # Check Open WebUI
        try:
            response = requests.get("http://localhost:8080/health", timeout=2)
            if response.status_code == 200:
                print("✅ Open WebUI: Running (http://localhost:8080)")
            else:
                print("⚠️  Open WebUI: Responding but unhealthy")
        except:
            print("❌ Open WebUI: Not available")
        
        print()
    
    def interactive(self):
        """Start interactive chat session."""
        print("\n🤖 Interactive LLM Chat")
        print("=" * 50)
        print("Commands:")
        print("  /help    - Show this help")
        print("  /models  - List available models")
        print("  /status  - Show system status")
        print("  /quit    - Exit")
        print("=" * 50)
        print()
        
        while True:
            try:
                prompt = input("You: ").strip()
                
                if not prompt:
                    continue
                
                if prompt.startswith("/"):
                    if prompt == "/quit":
                        print("👋 Goodbye!")
                        break
                    elif prompt == "/models":
                        self.list_models()
                    elif prompt == "/status":
                        self.status()
                    elif prompt == "/help":
                        print("\nAvailable commands:")
                        print("  /help    - Show this help")
                        print("  /models  - List available models")
                        print("  /status  - Show system status")
                        print("  /quit    - Exit\n")
                    else:
                        print(f"❌ Unknown command: {prompt}")
                    continue
                
                self.chat(prompt)
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Unified CLI for Llama-GPU with Ollama"
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Prompt to send to the model"
    )
    parser.add_argument(
        "-m", "--model",
        help="Model to use (default: phi4-mini:3.8b)"
    )
    parser.add_argument(
        "-b", "--backend",
        choices=["ollama", "llama-gpu", "api"],
        default="ollama",
        help="Backend to use"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive chat session"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List available models"
    )
    parser.add_argument(
        "-s", "--status",
        action="store_true",
        help="Show system status"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="API URL for unified backend"
    )
    
    args = parser.parse_args()
    
    cli = LLMCLi(backend=args.backend, api_url=args.api_url)
    
    if args.status:
        cli.status()
    elif args.list:
        cli.list_models()
    elif args.interactive:
        cli.interactive()
    elif args.prompt:
        prompt = " ".join(args.prompt)
        cli.chat(prompt, model=args.model)
    else:
        # No arguments, start interactive mode
        cli.interactive()


if __name__ == "__main__":
    main()
