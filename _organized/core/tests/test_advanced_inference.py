"""
Tests for advanced inference features.

This module tests the advanced sampling strategies, guided generation,
and function calling capabilities.
"""

import json
import logging
import os
from unittest.mock import Mock, patch

import pytest

# Configure logging
LOG_DIR = os.environ.get("LLAMA_GPU_LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "test_advanced_inference.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("test_advanced_inference")

# Mock model and tokenizer for testing
class MockModel:
    def __init__(self):
        self.device = "cpu"
    
    def parameters(self):
        return iter([Mock(device=self.device)])
    
    def __call__(self, input_ids):
        # Mock logits output
        batch_size, seq_len = input_ids.shape
        vocab_size = 32000  # Typical LLaMA vocab size
        logits = Mock()
        logits.logits = Mock()
        logits.logits.shape = (batch_size, seq_len, vocab_size)
        return logits

class MockTokenizer:
    def __init__(self):
        self.eos_token_id = 2
        self.pad_token_id = 0
    
    def __call__(self, text, return_tensors="pt"):
        # Mock tokenization
        tokens = [1, 2, 3, 4, 5]  # Mock token IDs
        return {"input_ids": Mock(shape=(1, len(tokens)))}
    
    def decode(self, tokens, skip_special_tokens=True):
        return "Mock generated text"
    
    def encode(self, text):
        return [1, 2, 3, 4, 5]

@pytest.fixture
def mock_model():
    return MockModel()

@pytest.fixture
def mock_tokenizer():
    return MockTokenizer()

@pytest.fixture
def advanced_inference(mock_model, mock_tokenizer):
    from src.advanced_inference import AdvancedInference
    return AdvancedInference(mock_model, mock_tokenizer)

@pytest.fixture
def guided_generation(mock_model, mock_tokenizer):
    from src.advanced_inference import GuidedGeneration
    return GuidedGeneration(mock_model, mock_tokenizer)

@pytest.fixture
def function_calling(mock_model, mock_tokenizer):
    from src.advanced_inference import FunctionCalling
    return FunctionCalling(mock_model, mock_tokenizer)

def test_sampling_strategies_enum():
    """Test that all sampling strategies are defined."""
    from src.advanced_inference import SamplingStrategy
    
    strategies = [
        SamplingStrategy.GREEDY,
        SamplingStrategy.TEMPERATURE,
        SamplingStrategy.TOP_K,
        SamplingStrategy.TOP_P,
        SamplingStrategy.NUCLEUS,
        SamplingStrategy.TYPICAL,
        SamplingStrategy.BEAM_SEARCH
    ]
    
    assert len(strategies) == 7
    logger.info("All sampling strategies defined")

def test_sampling_config_defaults():
    """Test SamplingConfig default values."""
    from src.advanced_inference import SamplingConfig, SamplingStrategy
    
    config = SamplingConfig()
    
    assert config.strategy == SamplingStrategy.TEMPERATURE
    assert config.temperature == 0.7
    assert config.top_k == 50
    assert config.top_p == 0.9
    assert config.typical_p == 0.9
    assert config.beam_size == 4
    assert config.repetition_penalty == 1.1
    assert config.length_penalty == 1.0
    assert config.no_repeat_ngram_size == 3
    
    logger.info("SamplingConfig defaults verified")

@patch('torch.argmax')
@patch('torch.nn.functional.softmax')
@patch('torch.multinomial')
def test_greedy_sampling(mock_multinomial, mock_softmax, mock_argmax, advanced_inference):
    """Test greedy sampling strategy."""
    import torch

    from src.advanced_inference import SamplingConfig, SamplingStrategy

    # Mock tensor
    logits = Mock()
    logits.shape = (1, 32000)
    
    # Mock return values
    mock_argmax.return_value = torch.tensor([42])
    
    config = SamplingConfig(strategy=SamplingStrategy.GREEDY)
    result = advanced_inference.sample_with_strategy(logits, config)
    
    mock_argmax.assert_called_once_with(logits, dim=-1)
    logger.info("Greedy sampling test passed")

@patch('torch.nn.functional.softmax')
@patch('torch.multinomial')
def test_temperature_sampling(mock_multinomial, mock_softmax, advanced_inference):
    """Test temperature sampling strategy."""
    import torch

    from src.advanced_inference import SamplingConfig, SamplingStrategy

    # Mock tensor
    logits = Mock()
    logits.shape = (1, 32000)
    
    # Mock return values
    mock_softmax.return_value = torch.tensor([[0.1, 0.2, 0.7]])
    mock_multinomial.return_value = torch.tensor([[2]])
    
    config = SamplingConfig(strategy=SamplingStrategy.TEMPERATURE, temperature=0.8)
    result = advanced_inference.sample_with_strategy(logits, config)
    
    mock_softmax.assert_called()
    mock_multinomial.assert_called()
    logger.info("Temperature sampling test passed")

@patch('torch.topk')
@patch('torch.nn.functional.softmax')
@patch('torch.multinomial')
@patch('torch.gather')
def test_top_k_sampling(mock_gather, mock_multinomial, mock_softmax, mock_topk, advanced_inference):
    """Test top-k sampling strategy."""
    import torch

    from src.advanced_inference import SamplingConfig, SamplingStrategy

    # Mock tensor
    logits = Mock()
    logits.shape = (1, 32000)
    
    # Mock return values
    mock_topk.return_value = (torch.tensor([[0.9, 0.8, 0.7]]), torch.tensor([[42, 15, 23]]))
    mock_softmax.return_value = torch.tensor([[0.5, 0.3, 0.2]])
    mock_multinomial.return_value = torch.tensor([[0]])
    mock_gather.return_value = torch.tensor([[42]])
    
    config = SamplingConfig(strategy=SamplingStrategy.TOP_K, top_k=3)
    result = advanced_inference.sample_with_strategy(logits, config)
    
    mock_topk.assert_called_with(logits, 3, dim=-1)
    logger.info("Top-k sampling test passed")

def test_guided_generation_initialization(guided_generation):
    """Test GuidedGeneration initialization."""
    assert guided_generation.model is not None
    assert guided_generation.tokenizer is not None
    assert guided_generation.device == "cpu"
    logger.info("GuidedGeneration initialization test passed")

def test_create_schema_prompt(guided_generation):
    """Test schema prompt creation."""
    prompt = "Generate a user profile"
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name", "age"]
    }
    
    schema_prompt = guided_generation._create_schema_prompt(prompt, schema)
    
    assert prompt in schema_prompt
    assert "JSON" in schema_prompt
    assert "schema" in schema_prompt
    logger.info("Schema prompt creation test passed")

def test_extract_json(guided_generation):
    """Test JSON extraction from text."""
    # Test valid JSON extraction
    text_with_json = "Here is the response: {\"name\": \"John\", \"age\": 30}"
    result = guided_generation._extract_json(text_with_json)
    
    assert result == {"name": "John", "age": 30}
    
    # Test invalid JSON
    text_without_json = "No JSON here"
    result = guided_generation._extract_json(text_without_json)
    
    assert "error" in result
    logger.info("JSON extraction test passed")

def test_validate_schema(guided_generation):
    """Test schema validation."""
    # Test valid object
    data = {"name": "John", "age": 30}
    schema = {
        "type": "object",
        "required": ["name", "age"]
    }
    
    assert guided_generation._validate_schema(data, schema) == True
    
    # Test missing required field
    data_missing = {"name": "John"}
    assert guided_generation._validate_schema(data_missing, schema) == False
    
    logger.info("Schema validation test passed")

def test_function_calling_initialization(function_calling):
    """Test FunctionCalling initialization."""
    assert function_calling.model is not None
    assert function_calling.tokenizer is not None
    assert function_calling.available_functions == {}
    logger.info("FunctionCalling initialization test passed")

def test_register_function(function_calling):
    """Test function registration."""
    def mock_function(args):
        return f"Processed: {args}"
    
    function_calling.register_function("test_func", mock_function, "A test function")
    
    assert "test_func" in function_calling.available_functions
    assert function_calling.available_functions["test_func"]["function"] == mock_function
    assert function_calling.available_functions["test_func"]["description"] == "A test function"
    logger.info("Function registration test passed")

def test_create_function_prompt(function_calling):
    """Test function prompt creation."""
    # Register a test function
    def mock_function(args):
        return f"Processed: {args}"
    
    function_calling.register_function("test_func", mock_function, "A test function")
    
    prompt = "What is the weather?"
    function_prompt = function_calling._create_function_prompt(prompt)
    
    assert prompt in function_prompt
    assert "Available functions" in function_prompt
    assert "test_func" in function_prompt
    assert "A test function" in function_prompt
    logger.info("Function prompt creation test passed")

def test_parse_function_calls(function_calling):
    """Test function call parsing."""
    text = "I need to check the weather. CALL_FUNCTION(weather_check, {\"location\": \"New York\"})"
    
    calls = function_calling._parse_function_calls(text)
    
    assert len(calls) == 1
    assert calls[0]["function"] == "weather_check"
    assert calls[0]["arguments"] == {"location": "New York"}
    
    # Test multiple calls
    text_multiple = "CALL_FUNCTION(func1, \"arg1\") CALL_FUNCTION(func2, {\"key\": \"value\"})"
    calls = function_calling._parse_function_calls(text_multiple)
    
    assert len(calls) == 2
    assert calls[0]["function"] == "func1"
    assert calls[0]["arguments"] == "arg1"
    assert calls[1]["function"] == "func2"
    assert calls[1]["arguments"] == {"key": "value"}
    
    logger.info("Function call parsing test passed")

def test_execute_function_call(function_calling):
    """Test function execution."""
    # Register a test function
    def mock_function(args):
        return f"Processed: {args}"
    
    function_calling.register_function("test_func", mock_function, "A test function")
    
    # Test successful execution
    call = {"function": "test_func", "arguments": "test_args"}
    result = function_calling._execute_function_call(call)
    
    assert result["success"] == True
    assert result["function"] == "test_func"
    assert result["arguments"] == "test_args"
    assert result["result"] == "Processed: test_args"
    
    # Test non-existent function
    call_invalid = {"function": "non_existent", "arguments": "test"}
    result = function_calling._execute_function_call(call_invalid)
    
    assert result["success"] == False
    assert "error" in result
    
    logger.info("Function execution test passed")

def test_generate_with_sampling_integration(advanced_inference):
    """Test integration of sampling with generation."""
    from src.advanced_inference import SamplingConfig, SamplingStrategy

    # Mock the model's generate method
    with patch.object(advanced_inference.model, 'generate') as mock_generate:
        mock_generate.return_value = Mock()
        
        config = SamplingConfig(strategy=SamplingStrategy.TEMPERATURE, temperature=0.8)
        result = advanced_inference.generate_with_sampling("Test prompt", max_tokens=10, config=config)
        
        assert isinstance(result, str)
        logger.info("Generate with sampling integration test passed")

def test_guided_generation_integration(guided_generation):
    """Test integration of guided generation."""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name", "age"]
    }
    
    # Mock the model's generate method
    with patch.object(guided_generation.model, 'generate') as mock_generate:
        mock_generate.return_value = Mock()
        
        result = guided_generation.generate_with_json_schema("Generate a user profile", schema)
        
        assert isinstance(result, dict)
        logger.info("Guided generation integration test passed")

def test_function_calling_integration(function_calling):
    """Test integration of function calling."""
    # Register a test function
    def mock_function(args):
        return f"Processed: {args}"
    
    function_calling.register_function("test_func", mock_function, "A test function")
    
    # Mock the model's generate method
    with patch.object(function_calling.model, 'generate') as mock_generate:
        mock_generate.return_value = Mock()
        
        result = function_calling.generate_with_function_calling("Call the test function")
        
        assert isinstance(result, dict)
        assert "text" in result
        assert "function_calls" in result
        assert "results" in result
        logger.info("Function calling integration test passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 