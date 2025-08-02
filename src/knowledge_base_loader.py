#!/usr/bin/env python3
"""
Knowledge Base Integration for LLaMA-GPU
Loads and integrates Python knowledge base with LLaMA models
"""

import json
from typing import List, Dict, Any
from pathlib import Path


class KnowledgeBaseLoader:
    """Load and manage knowledge bases for LLaMA models"""

    def __init__(self, knowledge_base_dir: str = None):
        if knowledge_base_dir is None:
            # Default to knowledge-base directory in project root
            self.kb_dir = Path(__file__).parent.parent / "knowledge-base"
        else:
            self.kb_dir = Path(knowledge_base_dir)

        self.loaded_knowledge = {}

    def load_alpaca_format(self, filename: str) -> List[Dict[str, str]]:
        """Load knowledge base in Alpaca format (instruction-input-output)"""
        file_path = self.kb_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Knowledge base file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            knowledge_data = json.load(f)

        print(f"✅ Loaded {len(knowledge_data)} knowledge entries "
              f"from {filename}")
        return knowledge_data

    def format_for_prompt(self, knowledge_entries: List[Dict[str, str]],
                          max_entries: int = 5) -> str:
        """Format knowledge entries for model prompt context"""

        # Select most relevant entries (for now, just take first few)
        selected_entries = knowledge_entries[:max_entries]

        formatted_context = "## Python Knowledge Reference:\n\n"

        for i, entry in enumerate(selected_entries, 1):
            instruction = entry.get('instruction', '')
            output = entry.get('output', '')

            formatted_context += f"**Q{i}: {instruction}**\n"
            formatted_context += f"{output}\n\n"

        return formatted_context

    def get_python_context(self, user_query: str = None,
                           max_entries: int = 3) -> str:
        """Get Python knowledge context for model prompting"""

        # Load Python knowledge if not already loaded
        if 'python' not in self.loaded_knowledge:
            try:
                self.loaded_knowledge['python'] = self.load_alpaca_format(
                    'python_knowledge_alpaca.json')
            except FileNotFoundError:
                return "# No Python knowledge base found\n"

        # For now, return general Python context
        # In a more advanced system, this would filter based on user_query
        return self.format_for_prompt(self.loaded_knowledge['python'],
                                      max_entries)

    def enhance_prompt(self, user_prompt: str,
                       include_python: bool = True) -> str:
        """Enhance user prompt with relevant knowledge base context"""

        enhanced_prompt = ""

        if include_python:
            python_context = self.get_python_context(user_prompt)
            enhanced_prompt += python_context
            enhanced_prompt += "---\n\n"

        enhanced_prompt += f"**User Question:** {user_prompt}\n\n"
        enhanced_prompt += ("**Assistant:** Based on the Python knowledge "
                            "above, ")

        return enhanced_prompt

    def list_available_knowledge_bases(self) -> List[str]:
        """List all available knowledge base files"""
        if not self.kb_dir.exists():
            return []

        kb_files = []
        for file_path in self.kb_dir.glob("*.json"):
            kb_files.append(file_path.name)

        return kb_files

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded knowledge bases"""
        total_entries = sum(
            len(entries) for entries in self.loaded_knowledge.values())

        stats = {
            'knowledge_base_dir': str(self.kb_dir),
            'available_files': self.list_available_knowledge_bases(),
            'loaded_knowledge_bases': list(self.loaded_knowledge.keys()),
            'total_entries': total_entries
        }

        return stats


def main():
    """Demo and test the knowledge base loader"""
    print("🧠 LLaMA-GPU Knowledge Base Loader")
    print("=" * 50)

    # Initialize loader
    kb_loader = KnowledgeBaseLoader()

    # Show stats
    stats = kb_loader.get_stats()
    print(f"📁 Knowledge Base Directory: {stats['knowledge_base_dir']}")
    print(f"📄 Available Files: {stats['available_files']}")

    # Test loading Python knowledge
    try:
        print("\n🐍 Loading Python Knowledge Base...")
        python_context = kb_loader.get_python_context(max_entries=2)
        print("✅ Successfully loaded Python knowledge!")
        print(f"📊 Total entries loaded: {stats['total_entries']}")

        print("\n📝 Sample Context Preview:")
        print("=" * 30)
        preview = (python_context[:500] + "..."
                   if len(python_context) > 500 else python_context)
        print(preview)

        # Test prompt enhancement
        print("\n🚀 Testing Prompt Enhancement:")
        print("=" * 30)
        test_prompt = "How do I create a function in Python?"
        enhanced = kb_loader.enhance_prompt(test_prompt)
        print(f"Original: {test_prompt}")
        print(f"Enhanced length: {len(enhanced)} characters")

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
