# Knowledge System Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (2 minutes)

```bash
cd /home/kevin/Projects/Llama-GPU
source venv/bin/activate
pip install chromadb sentence-transformers langchain langchain-community langchain-chroma radon
```

### Step 2: Initialize Knowledge Base (1 minute)

```bash
cd src/knowledge_base
python3 knowledge_populator.py
```

You'll see output like:
```
INFO:__main__:==================================================
INFO:__main__:Starting comprehensive knowledge population
INFO:__main__:==================================================
INFO:__main__:Populating Python knowledge...
INFO:__main__:Added 5 Python knowledge documents
INFO:__main__:Populating AI/ML knowledge...
INFO:__main__:Added 3 AI/ML knowledge documents
...
INFO:__main__:Total chunks in database: 72
```

### Step 3: Test the System (2 minutes)

```bash
# Test RAG engine
python3 rag_engine.py

# Test RAG-enhanced LLM
python3 rag_llm_interface.py

# Test code analyzer
python3 code_analyzer.py
```

## 💡 Example Usage

### Python Console

```python
from src.knowledge_base.rag_llm_interface import RAGEnhancedLLM

# Initialize (one-time, takes ~30 seconds)
llm = RAGEnhancedLLM()

# Ask questions!
print(llm.chat("How do I use Python decorators?"))
print(llm.chat("Explain binary search complexity", category="cs"))
print(llm.chat("How do I check disk space in Ubuntu?", category="ubuntu"))
```

### Command Line

Create a simple script `ask.py`:

```python
#!/usr/bin/env python3
import sys
from src.knowledge_base.rag_llm_interface import RAGEnhancedLLM

llm = RAGEnhancedLLM()
query = " ".join(sys.argv[1:])
print(llm.chat(query))
```

Then use it:
```bash
chmod +x ask.py
./ask.py "How do I create a Flask API?"
./ask.py "Explain Docker containers"
./ask.py "What is the difference between async and threading in Python?"
```

## 📚 Knowledge Categories

| Category | Examples |
|----------|----------|
| `python` | Decorators, OOP, async/await, exceptions |
| `ai_ml` | PyTorch, transformers, ML algorithms |
| `cs` | Data structures, Big O, design patterns |
| `sdlc` | Agile, testing, CI/CD, DevOps |
| `ubuntu` | System admin, CLI tools, systemd |

## 🎯 Common Tasks

### 1. Python Development Help

```python
llm.chat("How do I handle exceptions in Python?", category="python")
llm.chat("Explain context managers", category="python")
llm.chat("What are Python decorators?", category="python")
```

### 2. AI/ML Questions

```python
llm.chat("How do I train a neural network with PyTorch?", category="ai_ml")
llm.chat("Explain the transformer architecture", category="ai_ml")
llm.chat("What is overfitting?", category="ai_ml")
```

### 3. System Administration

```python
llm.chat("How do I restart a service with systemctl?", category="ubuntu")
llm.chat("Check disk usage commands", category="ubuntu")
llm.chat("Explain file permissions in Linux", category="ubuntu")
```

### 4. Code Analysis

```python
from src.knowledge_base.code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()

# Analyze your code
analysis = analyzer.analyze_file("my_script.py")
summary = analyzer.get_analysis_summary(analysis)
print(summary)
```

## 🔧 Customization

### Add Your Own Knowledge

```python
from src.knowledge_base import RAGEngine

rag = RAGEngine()

# Add custom documentation
docs = [
    "Our internal API uses FastAPI. To create an endpoint: @app.get('/path')",
    "Our deployment process: 1) Run tests 2) Build Docker 3) Push to registry"
]

metadata = [
    {"category": "internal", "source": "api_docs"},
    {"category": "internal", "source": "deployment"}
]

rag.add_documents(docs, metadata)
```

### Query Your Custom Knowledge

```python
llm = RAGEnhancedLLM()
response = llm.chat("How do I create an API endpoint?", category="internal")
```

## 📊 Performance Tuning

### For Faster Responses (Less Accurate)

```python
llm = RAGEnhancedLLM(
    max_context_chunks=1,  # Use only 1 chunk instead of 3
    device="cuda"  # Use GPU if available
)
```

### For Better Answers (Slower)

```python
llm = RAGEnhancedLLM(
    max_context_chunks=5,  # Use more context
    device="cuda"
)

response = llm.generate(
    query="Explain Python async/await in detail",
    max_new_tokens=1024,  # Longer response
    temperature=0.3  # More focused
)
```

## 🐛 Quick Troubleshooting

### Problem: "ChromaDB not installed"
```bash
pip install chromadb
```

### Problem: "Sentence transformer model download slow"
This is normal on first run (~190MB download). Subsequent runs are instant.

### Problem: "Out of memory"
```python
llm = RAGEnhancedLLM(device="cpu")  # Use CPU instead of GPU
```

### Problem: "No results from RAG"
```bash
# Reinitialize knowledge base
cd src/knowledge_base
python3 knowledge_populator.py
```

## 🎓 Next Steps

1. **Read Full Documentation**: `docs/RAG_KNOWLEDGE_SYSTEM.md`
2. **Integrate with AI Agent**: `tools/ai_agent.py`
3. **Add More Knowledge**: Edit `knowledge_populator.py`
4. **Build Custom Tools**: Use RAG engine in your scripts

## 📝 Complete Example Script

```python
#!/usr/bin/env python3
"""
Software Engineering Assistant
"""

from src.knowledge_base.rag_llm_interface import RAGEnhancedLLM
from src.knowledge_base.code_analyzer import CodeAnalyzer

class DevAssistant:
    def __init__(self):
        print("Initializing assistant...")
        self.llm = RAGEnhancedLLM()
        self.analyzer = CodeAnalyzer()
        print("Ready!")
    
    def ask(self, question: str, category: str = None):
        """Ask a software engineering question"""
        return self.llm.chat(question, category=category)
    
    def analyze_file(self, filepath: str):
        """Analyze a Python file"""
        analysis = self.analyzer.analyze_file(filepath)
        summary = self.analyzer.get_analysis_summary(analysis)
        
        # Get LLM explanation
        explanation = self.llm.chat(
            f"Explain this code analysis and suggest improvements:\n{summary}",
            category="python"
        )
        
        return {
            'summary': summary,
            'explanation': explanation
        }
    
    def interactive(self):
        """Interactive Q&A session"""
        print("\n=== Software Engineering Assistant ===")
        print("Ask me anything about Python, AI/ML, CS, SDLC, or Ubuntu!")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                question = input("You: ").strip()
                if question.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not question:
                    continue
                
                response = self.ask(question)
                print(f"\nAssistant: {response}\n")
            
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    assistant = DevAssistant()
    assistant.interactive()
```

Save as `dev_assistant.py` and run:
```bash
python3 dev_assistant.py
```

Enjoy your fully local, offline software engineering assistant! 🎉
