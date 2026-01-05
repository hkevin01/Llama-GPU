# RAG-Enhanced Knowledge System for Software Engineering

## Overview

The Llama-GPU project now includes a comprehensive **Retrieval-Augmented Generation (RAG)** system that transforms the local LLM into an expert software engineering assistant. This system works **completely offline** after initial setup and provides context-aware responses with deep knowledge of:

- **Python**: Core concepts, OOP, async/await, decorators, best practices
- **AI/ML**: Machine learning fundamentals, PyTorch, transformers, LLMs
- **Computer Science**: Data structures, algorithms, design patterns, complexity analysis
- **SDLC**: Agile, testing strategies, CI/CD, DevOps practices
- **Ubuntu/Linux**: System administration, command line tools, systemd

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Query                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              RAG Engine (rag_engine.py)                      │
│  ┌────────────────────────────────────────────────────┐     │
│  │  1. Query → Sentence Transformer Embedding          │     │
│  │  2. Vector Similarity Search in ChromaDB            │     │
│  │  3. Retrieve Top-K Relevant Knowledge Chunks        │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │  Retrieved Context    │
           │  (3-5 knowledge chunks)│
           └───────────┬───────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         RAG-Enhanced LLM (rag_llm_interface.py)              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  1. Build Prompt: System + Context + Query          │     │
│  │  2. Run Qwen/LLaMA Model Inference                  │     │
│  │  3. Generate Context-Aware Response                 │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │  Final Response │
              └────────────────┘
```

## Components

### 1. RAG Engine (`rag_engine.py`)

**Purpose**: Vector database management and semantic search

**Key Features**:
- Uses ChromaDB for persistent vector storage
- Sentence Transformers (all-MiniLM-L6-v2) for embeddings
- Automatic document chunking with overlap
- Category-based filtering (python, ai_ml, cs, sdlc, ubuntu)
- Supports add, query, and reset operations

**Usage**:
```python
from src.knowledge_base import RAGEngine

# Initialize
rag = RAGEngine()

# Add documents
rag.add_documents(
    documents=["Python is a high-level programming language..."],
    metadatas=[{"category": "python", "source": "manual"}]
)

# Query
results = rag.query("How do I use decorators?", n_results=3)

# Get formatted context
context = rag.get_context("Explain async/await", category="python")
```

### 2. Knowledge Populator (`knowledge_populator.py`)

**Purpose**: Populate vector database with comprehensive software engineering knowledge

**Knowledge Categories**:

#### Python (5 documents, ~20 chunks)
- Data types and structures
- Functions and decorators
- Object-oriented programming
- Error handling and exceptions
- Async/await and concurrency

#### AI/ML (3 documents, ~12 chunks)
- Machine learning fundamentals
- Deep learning with PyTorch
- Transformers and LLMs

#### Computer Science (3 documents, ~12 chunks)
- Data structures
- Algorithm complexity and Big O
- Design patterns

#### SDLC (3 documents, ~12 chunks)
- Software development lifecycle
- Testing strategies
- CI/CD and DevOps

#### Ubuntu/Linux (4 documents, ~16 chunks)
- System administration
- File system and permissions
- Command line tools
- Services and systemd

**Usage**:
```python
from src.knowledge_base import RAGEngine, KnowledgePopulator

rag = RAGEngine()
populator = KnowledgePopulator(rag)

# Populate all categories
populator.populate_all()

# Or populate specific categories
populator.populate_python_knowledge()
populator.populate_ai_ml_knowledge()
```

### 3. RAG-Enhanced LLM (`rag_llm_interface.py`)

**Purpose**: LLM interface with automatic RAG context injection

**Key Features**:
- Automatic context retrieval for every query
- GPU acceleration support (CUDA/CPU auto-detect)
- Customizable system prompts
- Category filtering
- Streaming support

**Usage**:
```python
from src.knowledge_base.rag_llm_interface import RAGEnhancedLLM

# Initialize (loads Qwen model + RAG)
llm = RAGEnhancedLLM()

# Simple chat
response = llm.chat("How do I create a decorator in Python?")
print(response)

# With category filter
response = llm.chat(
    "Explain Docker containers",
    category="sdlc",
    verbose=True
)

# Advanced generation
result = llm.generate(
    query="What is cyclomatic complexity?",
    category="cs",
    max_new_tokens=300,
    temperature=0.7
)
print(result['response'])
```

### 4. Code Analyzer (`code_analyzer.py`)

**Purpose**: Static code analysis with complexity metrics

**Features**:
- Cyclomatic complexity analysis (Radon)
- Maintainability index calculation
- Halstead metrics
- Lines of code statistics
- AST-based structure analysis
- Actionable improvement suggestions

**Usage**:
```python
from src.knowledge_base.code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()

# Analyze file
analysis = analyzer.analyze_file("my_script.py")
summary = analyzer.get_analysis_summary(analysis)
print(summary)

# Analyze code string
code = '''
def complex_function(x, y):
    if x > 0:
        if y > 0:
            return x + y
    return 0
'''
analysis = analyzer.analyze_code(code)
```

## Setup Instructions

### Quick Setup

```bash
# Run the setup script
./scripts/setup_knowledge_base.sh
```

This will:
1. Create/activate virtual environment
2. Install all dependencies
3. Initialize ChromaDB vector database
4. Populate knowledge base with all categories
5. Download sentence transformer model (190MB)

### Manual Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize knowledge base
cd src/knowledge_base
python3 knowledge_populator.py
```

## Storage Requirements

- **Sentence Transformer Model**: ~190MB (`all-MiniLM-L6-v2`)
- **Vector Database**: ~50MB (with all knowledge populated)
- **LLM Model** (Qwen2.5-3B): ~2.5GB (downloaded on first use)

**Total**: ~2.74GB for complete local setup

## Working Completely Offline

Once the initial setup is complete, the system works **100% offline**:

1. **Vector Database**: Stored locally in `~/.llama-gpu/vectordb/`
2. **Embedding Model**: Cached in `~/.cache/huggingface/`
3. **LLM Model**: Cached in `~/.cache/huggingface/`
4. **Knowledge Base**: All embedded in vector database (no internet needed)

To ensure offline operation:
```bash
# Test with network disabled
sudo ifconfig wlan0 down  # Or your network interface
python3 src/knowledge_base/rag_llm_interface.py
```

## Example Queries

### Python
```python
llm.chat("How do I use Python decorators?", category="python")
llm.chat("Explain context managers", category="python")
llm.chat("What are lambda functions?", category="python")
```

### AI/ML
```python
llm.chat("How do I train a PyTorch model?", category="ai_ml")
llm.chat("Explain transformer architecture", category="ai_ml")
llm.chat("What is the difference between supervised and unsupervised learning?", category="ai_ml")
```

### Computer Science
```python
llm.chat("What is Big O notation?", category="cs")
llm.chat("Explain binary search tree", category="cs")
llm.chat("What is the Singleton pattern?", category="cs")
```

### SDLC
```python
llm.chat("Explain Agile methodology", category="sdlc")
llm.chat("How do I write unit tests with pytest?", category="sdlc")
llm.chat("What is CI/CD?", category="sdlc")
```

### Ubuntu
```python
llm.chat("How do I check disk space?", category="ubuntu")
llm.chat("Explain systemctl commands", category="ubuntu")
llm.chat("How do I change file permissions?", category="ubuntu")
```

## Performance

### Benchmarks (on typical workstation)

| Operation | Time | Notes |
|-----------|------|-------|
| RAG Query (3 chunks) | ~50ms | Vector similarity search |
| Embedding Generation | ~20ms | Sentence transformer |
| LLM Inference (CPU) | ~2-5s | Qwen-3B, 512 tokens |
| LLM Inference (GPU) | ~0.5-1s | With CUDA acceleration |
| Knowledge Population | ~30s | One-time setup |

### Optimization Tips

1. **Use GPU**: 4-10x faster inference
   ```python
   llm = RAGEnhancedLLM(device="cuda")
   ```

2. **Reduce Context**: Faster but less accurate
   ```python
   llm = RAGEnhancedLLM(max_context_chunks=2)
   ```

3. **Smaller Model**: Use distilled models
   ```python
   llm = RAGEnhancedLLM(model_name="TinyLlama/TinyLlama-1.1B")
   ```

## Advanced Usage

### Custom Knowledge Addition

```python
from src.knowledge_base import RAGEngine

rag = RAGEngine()

# Add your own documentation
docs = [
    "Custom framework guide: XYZ is a tool for...",
    "Internal API documentation: The service exposes..."
]

metadata = [
    {"category": "custom", "source": "internal_docs"},
    {"category": "custom", "source": "api_docs"}
]

rag.add_documents(docs, metadata)
```

### Integrating with Existing Code

```python
# In your AI agent or chatbot
from src.knowledge_base.rag_llm_interface import RAGEnhancedLLM

class MyAIAgent:
    def __init__(self):
        self.llm = RAGEnhancedLLM()
    
    def answer_question(self, question: str) -> str:
        # Automatic RAG context injection
        return self.llm.chat(question)
    
    def analyze_code(self, code: str) -> str:
        from src.knowledge_base.code_analyzer import CodeAnalyzer
        
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_code(code)
        
        # Use LLM to explain analysis
        prompt = f"Explain this code analysis:\n{analysis}"
        return self.llm.chat(prompt, category="python")
```

## Troubleshooting

### Issue: "No module named 'chromadb'"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "Sentence transformer model not found"
**Solution**: First run downloads model automatically, or manually:
```bash
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Issue: "Out of memory on GPU"
**Solution**: Use CPU or smaller model
```python
llm = RAGEnhancedLLM(device="cpu")
# or
llm = RAGEnhancedLLM(model_name="TinyLlama/TinyLlama-1.1B")
```

### Issue: "Vector database is empty"
**Solution**: Run knowledge populator
```bash
cd src/knowledge_base
python3 knowledge_populator.py
```

## Extending the System

### Adding New Knowledge Categories

1. Edit `knowledge_populator.py`:
```python
def populate_docker_knowledge(self) -> None:
    """Populate Docker knowledge"""
    docs = [
        {
            "content": "Docker containers are...",
            "metadata": {"category": "docker", "source": "manual"}
        }
    ]
    self.rag.add_documents([d["content"] for d in docs],
                          [d["metadata"] for d in docs])
```

2. Call in `populate_all()`:
```python
def populate_all(self):
    self.populate_python_knowledge()
    self.populate_docker_knowledge()  # Add your new category
    # ...
```

### Custom Embedding Models

```python
# Use a different sentence transformer
rag = RAGEngine(embedding_model="sentence-transformers/all-mpnet-base-v2")
```

### Advanced Retrieval

```python
# Hybrid search (coming soon)
# Combine semantic + keyword search
results = rag.hybrid_query(
    query="Python decorators",
    keyword_weight=0.3,
    semantic_weight=0.7
)
```

## API Reference

See inline documentation in:
- `src/knowledge_base/rag_engine.py`
- `src/knowledge_base/knowledge_populator.py`
- `src/knowledge_base/rag_llm_interface.py`
- `src/knowledge_base/code_analyzer.py`

## Contributing

To add new knowledge:
1. Fork the repo
2. Add knowledge to appropriate populate method in `knowledge_populator.py`
3. Submit PR with descriptive commit message

## License

MIT License - Same as main Llama-GPU project

## Support

For issues or questions:
- Open GitHub issue
- Check docs/TROUBLESHOOTING.md
- Review example code in `src/knowledge_base/`
