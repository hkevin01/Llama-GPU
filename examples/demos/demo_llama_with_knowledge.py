#!/usr/bin/env python3
"""
LLaMA-GPU with Knowledge Base Integration Demo
Shows how to integrate the Python knowledge base with your LLaMA model
"""

import sys
from pathlib import Path

# Add src directory to path to import our modules
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from knowledge_base_loader import KnowledgeBaseLoader
except ImportError:
    print("❌ Could not import knowledge_base_loader")
    sys.exit(1)


class LlamaWithKnowledge:
    """LLaMA model wrapper with integrated knowledge base"""

    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.kb_loader = KnowledgeBaseLoader()
        print("✅ LLaMA-GPU with Knowledge Base initialized!")

        # Load knowledge base stats
        stats = self.kb_loader.get_stats()
        print(f"📚 Available knowledge files: {stats['available_files']}")

    def chat_with_knowledge(self, user_prompt: str,
                            include_python: bool = True,
                            max_knowledge_entries: int = 3) -> str:
        """
        Enhanced chat that includes knowledge base context

        Args:
            user_prompt: The user's question/prompt
            include_python: Whether to include Python knowledge
            max_knowledge_entries: Number of knowledge entries to include

        Returns:
            Enhanced prompt ready for LLaMA model
        """

        # Get relevant knowledge context
        if include_python:
            python_context = self.kb_loader.get_python_context(
                user_prompt, max_knowledge_entries)
        else:
            python_context = ""

        # Build enhanced prompt
        enhanced_prompt = ""

        if python_context:
            enhanced_prompt += "=== PYTHON KNOWLEDGE REFERENCE ===\n"
            enhanced_prompt += python_context
            enhanced_prompt += "\n=== END KNOWLEDGE REFERENCE ===\n\n"

        enhanced_prompt += f"User: {user_prompt}\n\n"
        enhanced_prompt += ("Assistant: I'll help you with that. "
                            "Based on my Python knowledge, ")

        return enhanced_prompt

    def simulate_response(self, prompt: str) -> str:
        """
        Simulate a LLaMA response (replace this with actual model inference)
        """
        # This is where you would call your actual LLaMA model
        # For demo purposes, we'll return a simulated response

        if "function" in prompt.lower():
            return """here's how to create a function in Python:

```python
def my_function(parameter1, parameter2):
    \"\"\"Function description\"\"\"
    result = parameter1 + parameter2
    return result

# Call the function
output = my_function(5, 3)
print(output)  # 8
```

Functions in Python use the `def` keyword, followed by the function name
and parameters in parentheses. The function body is indented, and you can
return a value using the `return` statement."""

        elif "python" in prompt.lower():
            return """Python is a versatile, high-level programming language
known for its readability and simplicity. It's widely used for web
development, data science, artificial intelligence, automation, and more.
Python's syntax is clean and intuitive, making it an excellent choice for
beginners and experienced developers alike."""

        else:
            return ("I can help you with Python programming questions. "
                    "Feel free to ask about functions, variables, data types, "
                    "loops, or any other Python concepts!")


def main():
    """Demo the LLaMA with knowledge base integration"""
    print("🤖 LLaMA-GPU with Integrated Python Knowledge Base")
    print("=" * 60)

    # Initialize LLaMA with knowledge
    llama_kb = LlamaWithKnowledge()

    # Test questions
    test_questions = [
        "How do I create a function in Python?",
        "What are Python data types?",
        "How much Python do you know?",
        "Explain Python variables to me"
    ]

    print("\n🧪 Testing Knowledge Integration:")
    print("=" * 40)

    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        print("-" * 50)

        # Get enhanced prompt with knowledge
        enhanced_prompt = llama_kb.chat_with_knowledge(
            question,
            include_python=True,
            max_knowledge_entries=2
        )

        # Show the enhanced prompt structure
        print("🔍 Enhanced Prompt Structure:")
        lines = enhanced_prompt.split('\n')
        for line in lines[:5]:  # Show first 5 lines
            print(f"   {line}")
        print(f"   ... ({len(lines)} total lines)")

        # Simulate model response
        response = llama_kb.simulate_response(enhanced_prompt)
        print("\n🤖 Simulated Response:")
        print(f"   {response[:200]}...")

        if i < len(test_questions):
            print("\n" + "="*40)

    print("\n✅ Knowledge Base Integration Complete!")
    print("📊 Your LLaMA model now has access to Python knowledge!")

    # Show integration instructions
    print("\n📋 Integration Instructions:")
    print("1. Replace `simulate_response()` with your actual LLaMA inference")
    print("2. Adjust `max_knowledge_entries` based on your model's "
          "context limit")
    print("3. Add more knowledge bases as needed "
          "(web dev, data science, etc.)")
    print("4. Use `chat_with_knowledge()` for all user interactions")


if __name__ == "__main__":
    main()
