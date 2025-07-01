# Llama-GPU Examples Documentation

This document provides comprehensive documentation for all examples included with Llama-GPU, showcasing both advanced NLP capabilities and GPU-accelerated LLM performance.

## Table of Contents

1. [Advanced NLP Examples](#advanced-nlp-examples)
2. [LLM Performance Examples](#llm-performance-examples)
3. [Performance Benchmarks](#performance-benchmarks)
4. [GPU Benefits Analysis](#gpu-benefits-analysis)
5. [Example Integration](#example-integration)

## Advanced NLP Examples

These examples demonstrate sophisticated natural language processing capabilities with GPU acceleration.

### Named Entity Recognition (NER)

**File:** `examples/named_entity_recognition.py`

High-speed entity extraction from text with support for 10 entity types.

#### Usage Examples

```bash
# Extract entities from single text
python examples/named_entity_recognition.py \
  --model path/to/model \
  --input "Apple CEO Tim Cook announced new products at WWDC in San Francisco"

# Batch processing from file
python examples/named_entity_recognition.py \
  --model path/to/model \
  --input-file texts.txt \
  --batch-size 4 \
  --output-file entities.json

# Extract with specific entity types
python examples/named_entity_recognition.py \
  --model path/to/model \
  --input "Microsoft and Google compete in AI research" \
  --entity-types PERSON,ORG,LOC
```

#### Features

- **Entity Types**: PERSON, ORG, LOC, DATE, TIME, MONEY, PERCENT, FACILITY, GPE, PRODUCT
- **Batch Processing**: Process multiple texts efficiently
- **Position Tracking**: Extract entity positions in text
- **Fallback Matching**: Pattern-based extraction for robustness
- **Statistics**: Entity frequency and distribution analysis

#### Output Format

```json
{
  "entities": [
    {
      "text": "Apple",
      "type": "ORG",
      "start": 0,
      "end": 5,
      "confidence": 0.95
    }
  ],
  "statistics": {
    "total_entities": 4,
    "entity_types": {"ORG": 2, "PERSON": 1, "LOC": 1}
  },
  "processing_time": 0.15,
  "backend": "cuda"
}
```

### Document Classification

**File:** `examples/document_classification.py`

Large-scale document categorization into 10 predefined categories.

#### Usage Examples

```bash
# Classify single document
python examples/document_classification.py \
  --model path/to/model \
  --input "Technical documentation for neural networks and deep learning"

# Batch classification
python examples/document_classification.py \
  --model path/to/model \
  --input-file documents.txt \
  --output-file classifications.json

# Classify with confidence threshold
python examples/document_classification.py \
  --model path/to/model \
  --input "Legal contract terms and conditions" \
  --confidence-threshold 0.8
```

#### Categories

- **NEWS**: News articles, reports, current events
- **TECHNICAL**: Technical documentation, manuals, specifications
- **LEGAL**: Legal documents, contracts, regulations
- **MEDICAL**: Medical reports, research papers, clinical notes
- **FINANCIAL**: Financial reports, statements, market analysis
- **ACADEMIC**: Academic papers, research, scholarly articles
- **MARKETING**: Marketing materials, advertisements, promotional content
- **PERSONAL**: Personal correspondence, diaries, blogs
- **GOVERNMENT**: Government documents, policies, official communications
- **ENTERTAINMENT**: Entertainment content, reviews, creative writing

### Language Detection

**File:** `examples/language_detection.py`

Multi-language processing with 20+ supported languages.

#### Usage Examples

```bash
# Detect language of text
python examples/language_detection.py \
  --model path/to/model \
  --input "Bonjour, comment allez-vous aujourd'hui?"

# Batch language detection
python examples/language_detection.py \
  --model path/to/model \
  --input-file multilingual.txt \
  --output-file languages.json

# Detect with language families
python examples/language_detection.py \
  --model path/to/model \
  --input "Hola, ¿cómo estás?" \
  --include-families
```

#### Supported Languages

**Romance Languages**: French, Spanish, Italian, Portuguese, Romanian
**Germanic Languages**: English, German, Dutch, Swedish, Norwegian
**Slavic Languages**: Russian, Polish, Czech, Ukrainian, Bulgarian
**Asian Languages**: Chinese, Japanese, Korean, Thai, Vietnamese
**Other Languages**: Arabic, Hindi, Turkish, Greek, Hebrew

### Question Answering

**File:** `examples/question_answering.py`

Neural QA with attention mechanisms and answer validation.

#### Usage Examples

```bash
# Answer question from context
python examples/question_answering.py \
  --model path/to/model \
  --context "Python was created by Guido van Rossum and first released in 1991" \
  --question "Who created Python?"

# Batch QA processing
python examples/question_answering.py \
  --model path/to/model \
  --input-file qa_pairs.json \
  --output-file answers.json

# QA with validation
python examples/question_answering.py \
  --model path/to/model \
  --context "The Earth orbits the Sun" \
  --question "What does the Earth orbit?" \
  --validate-answer
```

## LLM Performance Examples

These examples demonstrate significant GPU acceleration benefits for complex LLM tasks.

### Text Generation

**File:** `examples/text_generation.py`

High-performance text generation with various styles and lengths.

#### Usage Examples

```bash
# Generate creative text
python examples/text_generation.py \
  --model path/to/model \
  --style creative \
  --length long

# Custom prompt generation
python examples/text_generation.py \
  --model path/to/model \
  --prompt "Write a science fiction story about time travel" \
  --max-tokens 1000

# Batch generation with multiple styles
python examples/text_generation.py \
  --model path/to/model \
  --batch-size 4 \
  --output-file stories.json

# Benchmark GPU vs CPU performance
python examples/text_generation.py \
  --model path/to/model \
  --benchmark
```

#### Writing Styles

- **Creative**: Fantasy, science fiction, poetry, creative stories
- **Technical**: Technical documentation, explanations, guides
- **Business**: Proposals, strategies, reports, communications
- **Academic**: Research papers, literature reviews, methodologies

#### Length Configurations

- **Short**: ~100 tokens (quick responses)
- **Medium**: ~300 tokens (detailed responses)
- **Long**: ~800 tokens (comprehensive content)
- **Extended**: ~1500 tokens (in-depth analysis)

### Code Generation

**File:** `examples/code_generation.py`

GPU-accelerated code synthesis across multiple programming languages.

#### Usage Examples

```bash
# Generate Python code
python examples/code_generation.py \
  --model path/to/model \
  --language python \
  --complexity high \
  --task "Create a function to sort a list using quicksort"

# Generate JavaScript code
python examples/code_generation.py \
  --model path/to/model \
  --language javascript \
  --task "Create a Promise-based HTTP client with retry logic"

# Batch code generation
python examples/code_generation.py \
  --model path/to/model \
  --batch-size 3 \
  --language python \
  --output-file code_snippets.json

# Benchmark performance
python examples/code_generation.py \
  --model path/to/model \
  --benchmark
```

#### Supported Languages

- **Python**: Type hints, docstrings, best practices
- **JavaScript**: ES6+, JSDoc, error handling
- **Java**: Conventions, exception handling, JavaDoc
- **C++**: Modern C++17, RAII, comprehensive error handling
- **Rust**: Idioms, Result types, documentation comments

#### Complexity Levels

- **Simple**: Basic functionality, minimal error handling
- **Medium**: Well-structured with error handling
- **High**: Comprehensive with documentation and tests

### Conversation Simulation

**File:** `examples/conversation_simulation.py`

Multi-turn dialogue simulation with realistic scenarios.

#### Usage Examples

```bash
# Simulate customer support conversation
python examples/conversation_simulation.py \
  --model path/to/model \
  --scenario customer_support \
  --turns 15

# Run multiple scenarios in batch
python examples/conversation_simulation.py \
  --model path/to/model \
  --batch-size 3 \
  --scenario interview

# Custom conversation context
python examples/conversation_simulation.py \
  --model path/to/model \
  --scenario therapy \
  --context "Client is dealing with work-related stress" \
  --turns 10

# Benchmark conversation performance
python examples/conversation_simulation.py \
  --model path/to/model \
  --benchmark
```

#### Available Scenarios

- **Customer Support**: Technical support, troubleshooting, assistance
- **Interview**: Job interviews, technical assessments, behavioral questions
- **Therapy**: Counseling sessions, stress management, emotional support
- **Teaching**: Educational interactions, concept explanations, tutoring
- **Negotiation**: Business deals, contract discussions, conflict resolution

### Data Analysis

**File:** `examples/data_analysis.py`

Intelligent data analysis and insights generation.

#### Usage Examples

```bash
# Analyze sales data
python examples/data_analysis.py \
  --model path/to/model \
  --data sales_data.csv \
  --analysis-type trend

# Generate business insights
python examples/data_analysis.py \
  --model path/to/model \
  --data-type financial \
  --analysis-type insights \
  --data-size 500

# Batch analysis of multiple datasets
python examples/data_analysis.py \
  --model path/to/model \
  --batch-size 4 \
  --data-type user_behavior

# Custom analysis with specific focus
python examples/data_analysis.py \
  --model path/to/model \
  --data customer_data.csv \
  --analysis-type correlation
```

#### Analysis Types

- **Trend**: Time-based patterns, seasonal variations, growth trends
- **Correlation**: Relationships between variables, statistical significance
- **Insights**: Business implications, actionable recommendations
- **Comprehensive**: Complete analysis with all aspects covered

#### Data Types

- **Sales**: Product sales, revenue, customer data
- **User Behavior**: Session data, engagement metrics, conversions
- **Financial**: Revenue, expenses, profit analysis
- **Generic**: Custom datasets with flexible structure

## Performance Benchmarks

All examples include built-in GPU vs CPU benchmarking capabilities.

### Running Benchmarks

```bash
# Text generation benchmark
python examples/text_generation.py --model path/to/model --benchmark

# Code generation benchmark
python examples/code_generation.py --model path/to/model --benchmark

# Conversation simulation benchmark
python examples/conversation_simulation.py --model path/to/model --benchmark

# Data analysis benchmark
python examples/data_analysis.py --model path/to/model --benchmark
```

### Benchmark Output

```json
{
  "gpu_result": {
    "generation_time": 2.45,
    "tokens_per_second": 156.8,
    "backend": "cuda"
  },
  "cpu_result": {
    "generation_time": 12.34,
    "tokens_per_second": 31.2,
    "backend": "cpu"
  },
  "speedup": 5.03,
  "performance_improvement": "503% faster with GPU"
}
```

## GPU Benefits Analysis

### Performance Improvements

| Example Type | GPU Speedup | Use Case |
|--------------|-------------|----------|
| Text Generation | 3-5x | Long-form content, batch processing |
| Code Generation | 4-6x | Complex synthesis, multi-language |
| Conversation Simulation | 5-8x | Long dialogues, context maintenance |
| Data Analysis | 4-7x | Large datasets, complex queries |
| NER | 2-3x | Batch processing, real-time extraction |
| Document Classification | 2-4x | Large document sets |
| Language Detection | 2-3x | Multi-language processing |
| Question Answering | 3-4x | Complex reasoning, validation |

### Memory Efficiency

- **GPU Memory**: Optimized batch sizes for different GPU types
- **CPU Fallback**: Automatic fallback when GPU memory is insufficient
- **Memory Monitoring**: Real-time memory usage tracking

### Scalability

- **Batch Processing**: Optimal batch sizes for maximum throughput
- **Parallel Processing**: Multiple tasks processed simultaneously
- **Resource Utilization**: Efficient use of available GPU resources

## Example Integration

### Programmatic Usage

```python
from examples.text_generation import TextGenerator
from examples.code_generation import CodeGenerator

# Initialize generators
text_gen = TextGenerator("path/to/model", prefer_gpu=True)
code_gen = CodeGenerator("path/to/model", prefer_gpu=True)

# Generate content
story = text_gen.generate_text("Write a fantasy story", max_tokens=500)
code = code_gen.generate_code("Create a sorting function", language="python")

# Batch processing
stories = text_gen.batch_generate(["Prompt 1", "Prompt 2", "Prompt 3"])
code_snippets = code_gen.batch_generate(["Task 1", "Task 2"], language="javascript")
```

### Customization

```python
# Custom text generation with specific parameters
class CustomTextGenerator(TextGenerator):
    def generate_poetry(self, theme: str, style: str) -> Dict[str, Any]:
        prompt = f"Write a {style} poem about {theme}"
        return self.generate_text(prompt, max_tokens=200, temperature=0.8)

# Custom code generation for specific domains
class DomainCodeGenerator(CodeGenerator):
    def generate_api_code(self, endpoint: str, method: str) -> Dict[str, Any]:
        task = f"Create a REST API endpoint for {method} {endpoint}"
        return self.generate_code(task, language="python", complexity="high")
```

### Error Handling

```python
try:
    result = generator.generate_text(prompt)
    if result.get('error'):
        logger.error(f"Generation failed: {result['error']}")
        # Fallback to simpler generation
        result = generator.generate_text(prompt, max_tokens=100)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle gracefully
```

## Best Practices

### Performance Optimization

1. **Batch Sizes**: Use optimal batch sizes for your GPU memory
2. **Token Limits**: Set appropriate max_tokens for your use case
3. **Temperature**: Lower temperature (0.1-0.3) for consistent results
4. **Streaming**: Use streaming for long generations to reduce memory usage

### Resource Management

1. **Memory Monitoring**: Monitor GPU memory usage during execution
2. **Batch Processing**: Process multiple items together for better efficiency
3. **Error Recovery**: Implement fallback mechanisms for failed generations
4. **Resource Cleanup**: Properly clean up resources after processing

### Output Handling

1. **JSON Output**: Use JSON format for structured data processing
2. **Error Logging**: Log errors and performance metrics for debugging
3. **Validation**: Validate outputs before using them in production
4. **Caching**: Cache results for repeated queries when appropriate

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the src directory is in your Python path
2. **GPU Memory**: Reduce batch size if you encounter memory errors
3. **Model Loading**: Verify model path and format are correct
4. **Performance**: Check GPU drivers and CUDA/ROCm installation

### Debugging

```bash
# Enable verbose logging
export LLAMA_GPU_LOG_LEVEL=DEBUG

# Run with detailed output
python examples/text_generation.py --model path/to/model --prompt "test" --verbose

# Check GPU status
nvidia-smi  # For NVIDIA GPUs
rocm-smi    # For AMD GPUs
```

### Performance Tuning

1. **Batch Size**: Experiment with different batch sizes for optimal performance
2. **Model Size**: Use smaller models for faster inference
3. **Precision**: Consider using mixed precision for better performance
4. **Parallelism**: Use multiple GPUs if available

This comprehensive examples documentation provides everything needed to effectively use Llama-GPU's advanced capabilities and achieve maximum performance benefits from GPU acceleration. 