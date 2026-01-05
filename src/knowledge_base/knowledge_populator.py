#!/usr/bin/env python3
"""
Knowledge Base Populator - Downloads and integrates software engineering knowledge
Works completely offline after initial setup
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
import logging

from rag_engine import RAGEngine


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgePopulator:
    """
    Populates the RAG engine with comprehensive software engineering knowledge.
    Designed to work completely locally after initial setup.
    """
    
    def __init__(self, rag_engine: RAGEngine, knowledge_dir: str = None):
        """
        Initialize knowledge populator.
        
        Args:
            rag_engine: RAG engine instance
            knowledge_dir: Directory containing knowledge files
        """
        self.rag = rag_engine
        
        if knowledge_dir is None:
            knowledge_dir = Path(__file__).parent.parent.parent / "knowledge-base"
        self.knowledge_dir = Path(knowledge_dir)
        self.knowledge_dir.mkdir(exist_ok=True)
    
    def populate_python_knowledge(self) -> None:
        """Populate Python programming knowledge"""
        logger.info("Populating Python knowledge...")
        
        python_docs = [
            # Core Python concepts
            {
                "content": """Python Data Types and Structures:
                
Basic types: int, float, str, bool, None
Collections: list, tuple, dict, set, frozenset

Lists: Mutable ordered sequences. Create with [] or list(). Methods: append(), extend(), insert(), remove(), pop(), sort()
Tuples: Immutable ordered sequences. Create with () or tuple()
Dictionaries: Key-value mappings. Create with {} or dict(). Methods: keys(), values(), items(), get(), pop()
Sets: Unordered collections of unique elements. Create with {} or set(). Operations: union(), intersection(), difference()

Example:
my_list = [1, 2, 3]
my_dict = {'key': 'value'}
my_set = {1, 2, 3}
""",
                "metadata": {"category": "python", "source": "python_core", "topic": "data_types"}
            },
            {
                "content": """Python Functions and Decorators:

Function definition:
def function_name(param1, param2, *args, **kwargs):
    '''Docstring'''
    return value

Lambda functions: lambda x: x * 2

Decorators: Functions that modify other functions
def decorator(func):
    def wrapper(*args, **kwargs):
        # Before function
        result = func(*args, **kwargs)
        # After function
        return result
    return wrapper

@decorator
def my_function():
    pass

Common decorators: @staticmethod, @classmethod, @property
""",
                "metadata": {"category": "python", "source": "python_core", "topic": "functions"}
            },
            {
                "content": """Python Object-Oriented Programming:

Class definition:
class MyClass:
    def __init__(self, param):
        self.attribute = param
    
    def method(self):
        return self.attribute

Inheritance:
class Child(Parent):
    def __init__(self, param):
        super().__init__(param)

Special methods (dunder methods):
__init__, __str__, __repr__, __len__, __getitem__, __setitem__
__enter__, __exit__ (context managers)
__call__ (callable objects)

Properties:
@property
def value(self):
    return self._value

@value.setter
def value(self, val):
    self._value = val
""",
                "metadata": {"category": "python", "source": "python_core", "topic": "oop"}
            },
            {
                "content": """Python Error Handling and Exceptions:

Try-except blocks:
try:
    risky_operation()
except SpecificError as e:
    handle_error(e)
except (Error1, Error2):
    handle_multiple()
except Exception as e:
    handle_any(e)
else:
    # Runs if no exception
    pass
finally:
    # Always runs
    cleanup()

Custom exceptions:
class CustomError(Exception):
    pass

raise CustomError("message")

Context managers:
with open('file.txt') as f:
    data = f.read()

Best practices:
- Catch specific exceptions
- Don't use bare except:
- Use finally for cleanup
- Log errors properly
""",
                "metadata": {"category": "python", "source": "python_core", "topic": "exceptions"}
            },
            {
                "content": """Python Async/Await and Concurrency:

Async functions:
async def async_function():
    await some_async_operation()
    return result

Running async code:
import asyncio
asyncio.run(async_function())

Creating tasks:
task = asyncio.create_task(async_function())
result = await task

Gathering multiple tasks:
results = await asyncio.gather(
    async_func1(),
    async_func2(),
    async_func3()
)

Threading:
from threading import Thread
thread = Thread(target=function, args=(arg1,))
thread.start()
thread.join()

Multiprocessing:
from multiprocessing import Process, Pool
process = Process(target=function, args=(arg1,))
with Pool(4) as pool:
    results = pool.map(function, items)
""",
                "metadata": {"category": "python", "source": "python_core", "topic": "async"}
            }
        ]
        
        documents = [doc["content"] for doc in python_docs]
        metadatas = [doc["metadata"] for doc in python_docs]
        
        self.rag.add_documents(documents, metadatas)
        logger.info(f"Added {len(documents)} Python knowledge documents")
    
    def populate_ai_ml_knowledge(self) -> None:
        """Populate AI/ML knowledge"""
        logger.info("Populating AI/ML knowledge...")
        
        ai_ml_docs = [
            {
                "content": """Machine Learning Fundamentals:

Types of ML:
1. Supervised Learning: Labeled data (classification, regression)
2. Unsupervised Learning: Unlabeled data (clustering, dimensionality reduction)
3. Reinforcement Learning: Agent learning through rewards

Common algorithms:
- Linear Regression: Predicting continuous values
- Logistic Regression: Binary/multiclass classification
- Decision Trees: Tree-based decisions
- Random Forest: Ensemble of decision trees
- SVM: Support Vector Machines for classification
- K-Means: Clustering algorithm
- Neural Networks: Deep learning models

Model evaluation:
- Train/Test split
- Cross-validation
- Metrics: Accuracy, Precision, Recall, F1-Score, AUC-ROC
- Confusion matrix
- Overfitting vs Underfitting
""",
                "metadata": {"category": "ai_ml", "source": "ml_fundamentals", "topic": "basics"}
            },
            {
                "content": """Deep Learning with PyTorch:

Basic PyTorch operations:
import torch
tensor = torch.tensor([1, 2, 3])
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
tensor = tensor.to(device)

Neural network definition:
import torch.nn as nn

class NeuralNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(784, 128)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = self.layer1(x)
        x = self.relu(x)
        x = self.layer2(x)
        return x

Training loop:
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

for epoch in range(num_epochs):
    for batch_data, batch_labels in dataloader:
        optimizer.zero_grad()
        outputs = model(batch_data)
        loss = criterion(outputs, batch_labels)
        loss.backward()
        optimizer.step()
""",
                "metadata": {"category": "ai_ml", "source": "pytorch", "topic": "deep_learning"}
            },
            {
                "content": """Transformers and LLMs:

Transformer architecture:
- Self-attention mechanism
- Multi-head attention
- Position encodings
- Feed-forward networks
- Layer normalization

Using transformers with Hugging Face:
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("model-name")
model = AutoModel.from_pretrained("model-name")

inputs = tokenizer("Hello world", return_tensors="pt")
outputs = model(**inputs)

Text generation:
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")
result = generator("Once upon a time", max_length=50)

Fine-tuning:
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    learning_rate=2e-5
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset
)
trainer.train()
""",
                "metadata": {"category": "ai_ml", "source": "transformers", "topic": "llms"}
            }
        ]
        
        documents = [doc["content"] for doc in ai_ml_docs]
        metadatas = [doc["metadata"] for doc in ai_ml_docs]
        
        self.rag.add_documents(documents, metadatas)
        logger.info(f"Added {len(documents)} AI/ML knowledge documents")
    
    def populate_cs_concepts(self) -> None:
        """Populate computer science concepts"""
        logger.info("Populating CS concepts...")
        
        cs_docs = [
            {
                "content": """Data Structures:

Arrays/Lists: O(1) access, O(n) search, O(n) insertion
Linked Lists: O(n) access, O(n) search, O(1) insertion at head
Stacks: LIFO - push(), pop(), peek() - O(1) all operations
Queues: FIFO - enqueue(), dequeue() - O(1) all operations
Hash Tables/Dictionaries: O(1) average for insert, delete, search
Trees: Hierarchical structure
  - Binary Tree: Each node has max 2 children
  - BST: Left < Parent < Right - O(log n) average operations
  - AVL Tree: Self-balancing BST
  - Heap: Complete binary tree, min-heap or max-heap
Graphs: Nodes and edges - Adjacency list/matrix representation

Python implementations:
Stack: list with append() and pop()
Queue: collections.deque with append() and popleft()
Heap: heapq module
Graph: dict of adjacency lists
""",
                "metadata": {"category": "cs", "source": "data_structures", "topic": "core_structures"}
            },
            {
                "content": """Algorithm Complexity and Big O:

Time Complexity:
O(1) - Constant: Array access, hash table operations
O(log n) - Logarithmic: Binary search, balanced tree operations
O(n) - Linear: Array traversal, linear search
O(n log n) - Linearithmic: Merge sort, heap sort
O(n²) - Quadratic: Bubble sort, nested loops
O(2ⁿ) - Exponential: Recursive fibonacci
O(n!) - Factorial: Permutations

Space Complexity:
Memory used by algorithm
In-place algorithms: O(1) extra space
Recursive algorithms: O(n) stack space

Common algorithms:
- Binary Search: O(log n) on sorted array
- Merge Sort: O(n log n) time, O(n) space
- Quick Sort: O(n log n) average, O(n²) worst
- DFS: O(V + E) time, O(V) space
- BFS: O(V + E) time, O(V) space
- Dijkstra: O((V + E) log V) with heap
""",
                "metadata": {"category": "cs", "source": "algorithms", "topic": "complexity"}
            },
            {
                "content": """Design Patterns:

Creational Patterns:
1. Singleton: Ensure only one instance
2. Factory: Create objects without specifying exact class
3. Builder: Construct complex objects step by step

Structural Patterns:
1. Adapter: Make incompatible interfaces work together
2. Decorator: Add behavior to objects dynamically
3. Facade: Simplify complex subsystems

Behavioral Patterns:
1. Observer: Notify dependents of state changes
2. Strategy: Define family of algorithms, make them interchangeable
3. Command: Encapsulate request as object

Python examples:
Singleton:
class Singleton:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

Decorator pattern using Python decorators
Observer using callbacks
Strategy using classes with common interface
""",
                "metadata": {"category": "cs", "source": "design_patterns", "topic": "patterns"}
            }
        ]
        
        documents = [doc["content"] for doc in cs_docs]
        metadatas = [doc["metadata"] for doc in cs_docs]
        
        self.rag.add_documents(documents, metadatas)
        logger.info(f"Added {len(documents)} CS concept documents")
    
    def populate_sdlc_knowledge(self) -> None:
        """Populate SDLC and DevOps knowledge"""
        logger.info("Populating SDLC knowledge...")
        
        sdlc_docs = [
            {
                "content": """Software Development Life Cycle (SDLC):

Phases:
1. Planning: Define scope, requirements, feasibility
2. Analysis: Detailed requirements gathering
3. Design: Architecture, system design, UI/UX
4. Implementation: Code development
5. Testing: Unit, integration, system, UAT
6. Deployment: Release to production
7. Maintenance: Bug fixes, updates, enhancements

Agile Methodology:
- Iterative development in sprints (1-4 weeks)
- Daily standups
- Sprint planning and retrospectives
- User stories and backlog management
- Continuous feedback and adaptation

Scrum roles:
- Product Owner: Manages backlog, priorities
- Scrum Master: Facilitates process, removes blockers
- Development Team: Self-organizing, cross-functional

Kanban:
- Visualize workflow on board
- Limit work in progress (WIP)
- Focus on flow efficiency
- Continuous delivery
""",
                "metadata": {"category": "sdlc", "source": "methodology", "topic": "agile"}
            },
            {
                "content": """Testing Strategies:

Test Types:
1. Unit Tests: Test individual functions/methods
2. Integration Tests: Test component interactions
3. System Tests: Test complete system
4. Acceptance Tests: Verify requirements met
5. Performance Tests: Load, stress, spike testing
6. Security Tests: Penetration, vulnerability testing

Python testing with pytest:
import pytest

def test_function():
    assert function_to_test() == expected_result

def test_with_fixture(sample_data):
    result = process(sample_data)
    assert result.is_valid()

@pytest.fixture
def sample_data():
    return {"key": "value"}

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6)
])
def test_multiple_cases(input, expected):
    assert multiply_by_two(input) == expected

Test coverage:
pytest --cov=myproject tests/

TDD (Test-Driven Development):
1. Write failing test
2. Write minimum code to pass
3. Refactor
4. Repeat
""",
                "metadata": {"category": "sdlc", "source": "testing", "topic": "strategies"}
            },
            {
                "content": """CI/CD and DevOps:

Continuous Integration:
- Automated builds on code commit
- Run tests automatically
- Fast feedback on code quality
- Catch integration issues early

Continuous Deployment:
- Automate release process
- Deploy to staging/production automatically
- Rollback capabilities
- Blue-green or canary deployments

GitHub Actions example:
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest

Docker for deployment:
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]

Kubernetes:
- Container orchestration
- Auto-scaling
- Self-healing
- Rolling updates
""",
                "metadata": {"category": "sdlc", "source": "cicd", "topic": "devops"}
            }
        ]
        
        documents = [doc["content"] for doc in sdlc_docs]
        metadatas = [doc["metadata"] for doc in sdlc_docs]
        
        self.rag.add_documents(documents, metadatas)
        logger.info(f"Added {len(documents)} SDLC knowledge documents")
    
    def populate_ubuntu_knowledge(self) -> None:
        """Populate Ubuntu/Linux system knowledge"""
        logger.info("Populating Ubuntu knowledge...")
        
        ubuntu_docs = [
            {
                "content": """Ubuntu System Administration:

Package Management (APT):
sudo apt update              # Update package lists
sudo apt upgrade             # Upgrade installed packages
sudo apt install package     # Install package
sudo apt remove package      # Remove package
sudo apt autoremove          # Remove unused dependencies
sudo apt search keyword      # Search for packages
apt list --installed         # List installed packages

System Information:
uname -a                     # System information
lsb_release -a              # Ubuntu version
df -h                       # Disk space usage
free -h                     # Memory usage
top / htop                  # Process monitoring
ps aux                      # List all processes
systemctl status service    # Service status

User Management:
sudo adduser username       # Add new user
sudo usermod -aG group user # Add user to group
sudo deluser username       # Delete user
groups username             # Show user's groups
sudo passwd username        # Change password
""",
                "metadata": {"category": "ubuntu", "source": "admin", "topic": "system_admin"}
            },
            {
                "content": """Linux File System and Permissions:

File System Structure:
/bin     - Essential binaries
/boot    - Boot loader files
/etc     - System configuration
/home    - User home directories
/lib     - System libraries
/opt     - Optional software
/tmp     - Temporary files
/usr     - User programs
/var     - Variable data (logs, etc.)

File Operations:
ls -la              # List files with details
cd /path            # Change directory
pwd                 # Print working directory
cp source dest      # Copy
mv source dest      # Move/rename
rm file             # Remove file
mkdir dir           # Create directory
rmdir dir           # Remove empty directory
rm -rf dir          # Remove directory recursively

Permissions:
chmod 755 file      # rwxr-xr-x
chmod u+x file      # Add execute for user
chown user:group    # Change ownership
chmod -R 644 dir    # Recursive permission change

Permission numbers:
4 = read (r)
2 = write (w)
1 = execute (x)
755 = rwxr-xr-x (owner: all, group/others: read+execute)
644 = rw-r--r-- (owner: read+write, others: read)
""",
                "metadata": {"category": "ubuntu", "source": "filesystem", "topic": "permissions"}
            },
            {
                "content": """Linux Command Line Tools:

Text Processing:
cat file                    # Display file
less file                   # Page through file
head -n 10 file            # First 10 lines
tail -n 10 file            # Last 10 lines
tail -f file               # Follow file updates
grep pattern file          # Search in file
grep -r pattern dir        # Recursive search
sed 's/old/new/g' file     # Replace text
awk '{print $1}' file      # Process columns

File Search:
find /path -name "*.py"    # Find Python files
find /path -type f -size +100M  # Files > 100MB
locate filename            # Quick file search (updatedb first)
which command              # Find command location
whereis command            # Find binary, source, manual

Network:
ping host                  # Test connectivity
curl url                   # HTTP request
wget url                   # Download file
netstat -tuln             # Show open ports
ss -tuln                  # Socket statistics
ip addr                   # Show IP addresses
traceroute host           # Trace route to host

Process Management:
kill PID                  # Send SIGTERM
kill -9 PID              # Force kill (SIGKILL)
killall processname      # Kill by name
pkill pattern            # Kill by pattern
bg / fg                  # Background/foreground jobs
nohup command &          # Run command detached
""",
                "metadata": {"category": "ubuntu", "source": "cli_tools", "topic": "commands"}
            },
            {
                "content": """Ubuntu Services and Systemd:

Systemd Service Management:
systemctl start service          # Start service
systemctl stop service           # Stop service
systemctl restart service        # Restart service
systemctl reload service         # Reload config
systemctl enable service         # Enable at boot
systemctl disable service        # Disable at boot
systemctl status service         # Check status
systemctl list-units --type=service  # List services

Service Logs:
journalctl -u service           # View service logs
journalctl -f                   # Follow all logs
journalctl --since "1 hour ago" # Recent logs
journalctl --vacuum-time=2d     # Clean old logs

Create Custom Service:
Create /etc/systemd/system/myservice.service:

[Unit]
Description=My Service
After=network.target

[Service]
Type=simple
User=username
WorkingDirectory=/app
ExecStart=/usr/bin/python3 /app/main.py
Restart=always

[Install]
WantedBy=multi-user.target

Then:
sudo systemctl daemon-reload
sudo systemctl enable myservice
sudo systemctl start myservice

Cron Jobs (Scheduled Tasks):
crontab -e              # Edit cron jobs
# Format: minute hour day month dayofweek command
0 2 * * * /path/to/backup.sh      # Daily at 2am
*/15 * * * * /path/to/script.sh   # Every 15 minutes
0 0 * * 0 /path/to/weekly.sh      # Weekly on Sunday
""",
                "metadata": {"category": "ubuntu", "source": "services", "topic": "systemd"}
            }
        ]
        
        documents = [doc["content"] for doc in ubuntu_docs]
        metadatas = [doc["metadata"] for doc in ubuntu_docs]
        
        self.rag.add_documents(documents, metadatas)
        logger.info(f"Added {len(documents)} Ubuntu knowledge documents")
    
    def populate_all(self) -> None:
        """Populate all knowledge categories"""
        logger.info("=" * 50)
        logger.info("Starting comprehensive knowledge population")
        logger.info("=" * 50)
        
        self.populate_python_knowledge()
        self.populate_ai_ml_knowledge()
        self.populate_cs_concepts()
        self.populate_sdlc_knowledge()
        self.populate_ubuntu_knowledge()
        
        stats = self.rag.get_stats()
        logger.info("=" * 50)
        logger.info("Knowledge population complete!")
        logger.info(f"Total chunks in database: {stats['total_chunks']}")
        logger.info("=" * 50)


if __name__ == "__main__":
    # Initialize and populate knowledge base
    rag = RAGEngine()
    populator = KnowledgePopulator(rag)
    
    # Populate all knowledge
    populator.populate_all()
    
    # Test queries
    print("\n" + "=" * 60)
    print("Testing Knowledge Retrieval")
    print("=" * 60)
    
    test_queries = [
        "How do I use decorators in Python?",
        "What is the Big O complexity of binary search?",
        "Explain Agile methodology",
        "How do I manage services with systemctl?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        context = rag.get_context(query, max_chunks=2)
        print(context[:500] + "..." if len(context) > 500 else context)
