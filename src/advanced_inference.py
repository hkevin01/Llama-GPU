"""
Advanced inference features for LLaMA GPU.

This module provides advanced sampling strategies, guided generation,
and function calling capabilities for enhanced model inference.
"""

import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import torch
import torch.nn.functional as F

# Configure logging
LOG_DIR = "logs"
logging.basicConfig(
    filename=f"{LOG_DIR}/advanced_inference.log",
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("advanced_inference")

class SamplingStrategy(Enum):
    """Available sampling strategies for text generation."""
    GREEDY = "greedy"
    TEMPERATURE = "temperature"
    TOP_K = "top_k"
    TOP_P = "top_p"
    NUCLEUS = "nucleus"
    TYPICAL = "typical"
    BEAM_SEARCH = "beam_search"

@dataclass
class SamplingConfig:
    """Configuration for text generation sampling."""
    strategy: SamplingStrategy = SamplingStrategy.TEMPERATURE
    temperature: float = 0.7
    top_k: int = 50
    top_p: float = 0.9
    typical_p: float = 0.9
    beam_size: int = 4
    repetition_penalty: float = 1.1
    length_penalty: float = 1.0
    no_repeat_ngram_size: int = 3

class AdvancedInference:
    """Advanced inference features for LLaMA models."""
    
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.device = next(model.parameters()).device
        logger.info(f"Advanced inference initialized on device: {self.device}")
    
    def sample_with_strategy(self, logits: torch.Tensor, config: SamplingConfig) -> torch.Tensor:
        """Apply the specified sampling strategy to logits."""
        if config.strategy == SamplingStrategy.GREEDY:
            return self._greedy_sampling(logits)
        elif config.strategy == SamplingStrategy.TEMPERATURE:
            return self._temperature_sampling(logits, config.temperature)
        elif config.strategy == SamplingStrategy.TOP_K:
            return self._top_k_sampling(logits, config.top_k)
        elif config.strategy == SamplingStrategy.TOP_P:
            return self._top_p_sampling(logits, config.top_p)
        elif config.strategy == SamplingStrategy.NUCLEUS:
            return self._nucleus_sampling(logits, config.top_p)
        elif config.strategy == SamplingStrategy.TYPICAL:
            return self._typical_sampling(logits, config.typical_p)
        else:
            logger.warning(f"Unknown sampling strategy: {config.strategy}, using temperature")
            return self._temperature_sampling(logits, config.temperature)
    
    def _greedy_sampling(self, logits: torch.Tensor) -> torch.Tensor:
        """Greedy sampling - always select the most likely token."""
        return torch.argmax(logits, dim=-1)
    
    def _temperature_sampling(self, logits: torch.Tensor, temperature: float) -> torch.Tensor:
        """Temperature sampling - adjust randomness with temperature parameter."""
        if temperature == 0:
            return self._greedy_sampling(logits)
        
        logits = logits / temperature
        probs = F.softmax(logits, dim=-1)
        return torch.multinomial(probs, 1).squeeze(-1)
    
    def _top_k_sampling(self, logits: torch.Tensor, k: int) -> torch.Tensor:
        """Top-k sampling - only consider the top k most likely tokens."""
        top_k_logits, top_k_indices = torch.topk(logits, k, dim=-1)
        probs = F.softmax(top_k_logits, dim=-1)
        selected_indices = torch.multinomial(probs, 1)
        return top_k_indices.gather(-1, selected_indices).squeeze(-1)
    
    def _top_p_sampling(self, logits: torch.Tensor, p: float) -> torch.Tensor:
        """Top-p (nucleus) sampling - consider tokens until cumulative probability reaches p."""
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
        
        # Remove tokens with cumulative probability above the threshold
        sorted_indices_to_remove = cumulative_probs > p
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0
        
        indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
        logits[indices_to_remove] = float('-inf')
        
        probs = F.softmax(logits, dim=-1)
        return torch.multinomial(probs, 1).squeeze(-1)
    
    def _nucleus_sampling(self, logits: torch.Tensor, p: float) -> torch.Tensor:
        """Nucleus sampling (same as top-p)."""
        return self._top_p_sampling(logits, p)
    
    def _typical_sampling(self, logits: torch.Tensor, p: float) -> torch.Tensor:
        """Typical sampling - select tokens with typical probability mass."""
        # Calculate entropy
        probs = F.softmax(logits, dim=-1)
        entropy = -torch.sum(probs * torch.log(probs + 1e-8), dim=-1, keepdim=True)
        
        # Calculate typicality
        log_probs = torch.log(probs + 1e-8)
        typicality = torch.abs(log_probs + entropy)
        
        # Sort by typicality
        sorted_typicality, sorted_indices = torch.sort(typicality, dim=-1)
        cumulative_probs = torch.cumsum(probs.gather(-1, sorted_indices), dim=-1)
        
        # Remove tokens with cumulative probability above the threshold
        sorted_indices_to_remove = cumulative_probs > p
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0
        
        indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
        logits[indices_to_remove] = float('-inf')
        
        probs = F.softmax(logits, dim=-1)
        return torch.multinomial(probs, 1).squeeze(-1)
    
    def generate_with_sampling(
        self, 
        prompt: str, 
        max_tokens: int = 100,
        config: Optional[SamplingConfig] = None
    ) -> str:
        """Generate text using the specified sampling strategy."""
        if config is None:
            config = SamplingConfig()
        
        logger.info(f"Generating with strategy: {config.strategy.value}")
        
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        input_ids = inputs["input_ids"]
        
        generated_tokens = []
        
        with torch.no_grad():
            for _ in range(max_tokens):
                # Get model outputs
                outputs = self.model(input_ids)
                next_token_logits = outputs.logits[:, -1, :]
                
                # Apply repetition penalty
                if config.repetition_penalty != 1.0:
                    for token_id in set(generated_tokens):
                        next_token_logits[0, token_id] /= config.repetition_penalty
                
                # Sample next token
                next_token = self.sample_with_strategy(next_token_logits, config)
                generated_tokens.append(next_token.item())
                
                # Append to input for next iteration
                input_ids = torch.cat([input_ids, next_token.unsqueeze(0).unsqueeze(0)], dim=1)
                
                # Check for end of sequence
                if next_token.item() == self.tokenizer.eos_token_id:
                    break
        
        # Decode generated tokens
        generated_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        logger.info(f"Generated {len(generated_tokens)} tokens")
        
        return generated_text

class GuidedGeneration:
    """Guided generation with JSON schema constraints."""
    
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.device = next(model.parameters()).device
        logger.info("Guided generation initialized")
    
    def generate_with_json_schema(
        self, 
        prompt: str, 
        schema: Dict[str, Any],
        max_tokens: int = 200
    ) -> Dict[str, Any]:
        """Generate JSON output conforming to the specified schema."""
        logger.info(f"Generating JSON with schema: {schema.get('type', 'unknown')}")
        
        # Create schema-aware prompt
        schema_prompt = self._create_schema_prompt(prompt, schema)
        
        # Generate text
        generated_text = self._generate_text(schema_prompt, max_tokens)
        
        # Extract and validate JSON
        json_output = self._extract_json(generated_text)
        
        # Validate against schema
        if self._validate_schema(json_output, schema):
            logger.info("Generated JSON validated against schema")
            return json_output
        else:
            logger.warning("Generated JSON failed schema validation")
            return {"error": "Failed to generate valid JSON", "raw_output": generated_text}
    
    def _create_schema_prompt(self, prompt: str, schema: Dict[str, Any]) -> str:
        """Create a prompt that includes JSON schema constraints."""
        schema_str = json.dumps(schema, indent=2)
        return f"""{prompt}

Please respond with valid JSON that conforms to this schema:

{schema_str}

JSON response:"""
    
    def _generate_text(self, prompt: str, max_tokens: int) -> str:
        """Generate text using the model."""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=inputs["input_ids"].shape[1] + max_tokens,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text[len(prompt):]  # Remove the prompt part
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from generated text."""
        # Look for JSON-like content
        json_pattern = r'\{.*\}'
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                logger.warning("Failed to parse extracted JSON")
                return {"error": "Invalid JSON format"}
        
        return {"error": "No JSON found in generated text"}
    
    def _validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Basic schema validation."""
        try:
            # This is a simplified validation - in production, use a proper JSON schema validator
            if schema.get("type") == "object":
                required_fields = schema.get("required", [])
                for field in required_fields:
                    if field not in data:
                        return False
            return True
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            return False

class FunctionCalling:
    """Function calling capabilities for LLaMA models."""
    
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.device = next(model.parameters()).device
        self.available_functions = {}
        logger.info("Function calling initialized")
    
    def register_function(self, name: str, func: Callable, description: str = ""):
        """Register a function that can be called by the model."""
        self.available_functions[name] = {
            "function": func,
            "description": description
        }
        logger.info(f"Registered function: {name}")
    
    def generate_with_function_calling(
        self, 
        prompt: str, 
        max_tokens: int = 100
    ) -> Dict[str, Any]:
        """Generate text with potential function calls."""
        logger.info("Generating with function calling capabilities")
        
        # Create function-aware prompt
        function_prompt = self._create_function_prompt(prompt)
        
        # Generate text
        generated_text = self._generate_text(function_prompt, max_tokens)
        
        # Parse function calls
        function_calls = self._parse_function_calls(generated_text)
        
        # Execute function calls
        results = []
        for call in function_calls:
            result = self._execute_function_call(call)
            results.append(result)
        
        return {
            "text": generated_text,
            "function_calls": function_calls,
            "results": results
        }
    
    def _create_function_prompt(self, prompt: str) -> str:
        """Create a prompt that includes available functions."""
        function_descriptions = []
        for name, info in self.available_functions.items():
            function_descriptions.append(f"- {name}: {info['description']}")
        
        functions_text = "\n".join(function_descriptions)
        
        return f"""{prompt}

Available functions:
{functions_text}

You can call functions using the format: CALL_FUNCTION(function_name, arguments)

Response:"""
    
    def _generate_text(self, prompt: str, max_tokens: int) -> str:
        """Generate text using the model."""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=inputs["input_ids"].shape[1] + max_tokens,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text[len(prompt):]
    
    def _parse_function_calls(self, text: str) -> List[Dict[str, Any]]:
        """Parse function calls from generated text."""
        function_calls = []
        
        # Look for CALL_FUNCTION patterns
        pattern = r'CALL_FUNCTION\(([^,]+),\s*([^)]+)\)'
        matches = re.findall(pattern, text)
        
        for match in matches:
            function_name = match[0].strip()
            arguments = match[1].strip()
            
            try:
                # Try to parse arguments as JSON
                args = json.loads(arguments)
            except json.JSONDecodeError:
                # If not JSON, treat as string
                args = arguments
            
            function_calls.append({
                "function": function_name,
                "arguments": args
            })
        
        return function_calls
    
    def _execute_function_call(self, call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function call."""
        function_name = call["function"]
        arguments = call["arguments"]
        
        if function_name not in self.available_functions:
            return {
                "error": f"Function '{function_name}' not found",
                "function": function_name,
                "arguments": arguments
            }
        
        try:
            func = self.available_functions[function_name]["function"]
            result = func(arguments)
            
            logger.info(f"Executed function {function_name} with result: {result}")
            
            return {
                "function": function_name,
                "arguments": arguments,
                "result": result,
                "success": True
            }
        except Exception as e:
            logger.error(f"Function execution error: {e}")
            return {
                "function": function_name,
                "arguments": arguments,
                "error": str(e),
                "success": False
            } 