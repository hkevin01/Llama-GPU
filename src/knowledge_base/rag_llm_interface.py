#!/usr/bin/env python3
"""
RAG-Enhanced LLM Interface
Integrates RAG knowledge retrieval with LLM inference for context-aware responses
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

from rag_engine import RAGEngine


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEnhancedLLM:
    """
    LLM interface enhanced with RAG for software engineering knowledge.
    Provides context-aware responses using vector database retrieval.
    """
    
    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-3B-Instruct",
        rag_engine: Optional[RAGEngine] = None,
        device: str = None,
        max_context_chunks: int = 3
    ):
        """
        Initialize RAG-enhanced LLM.
        
        Args:
            model_name: Hugging Face model name
            rag_engine: RAG engine instance (creates new if None)
            device: Device to run on ('cuda', 'cpu', or None for auto)
            max_context_chunks: Max knowledge chunks to retrieve
        """
        # Initialize RAG engine
        if rag_engine is None:
            logger.info("Initializing RAG engine...")
            self.rag = RAGEngine()
        else:
            self.rag = rag_engine
        
        # Set device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        logger.info(f"Using device: {self.device}")
        
        # Initialize LLM
        logger.info(f"Loading model: {model_name}")
        self.model_name = model_name
        self.max_context_chunks = max_context_chunks
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            # Create text generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.info("Falling back to simple generation without pipeline")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.model = self.model.to(self.device)
            self.generator = None
    
    def _build_rag_prompt(
        self,
        query: str,
        category: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Build prompt with RAG context.
        
        Args:
            query: User query
            category: Knowledge category filter
            system_prompt: System prompt (uses default if None)
        
        Returns:
            Complete prompt with context
        """
        # Get relevant context from RAG
        context = self.rag.get_context(
            query=query,
            max_chunks=self.max_context_chunks,
            category=category
        )
        
        # Build system prompt
        if system_prompt is None:
            system_prompt = """You are an expert software engineering assistant with deep knowledge of:
- Python programming and best practices
- AI/ML concepts, frameworks (PyTorch, TensorFlow), and deep learning
- Computer Science fundamentals (data structures, algorithms, design patterns)
- Software Development Life Cycle (Agile, testing, CI/CD, DevOps)
- Ubuntu/Linux system administration and command line

Provide accurate, concise, and practical answers. Include code examples when relevant."""
        
        # Build complete prompt
        if context:
            prompt = f"""{system_prompt}

# Relevant Knowledge:
{context}

# User Query:
{query}

# Response:
"""
        else:
            prompt = f"""{system_prompt}

# User Query:
{query}

# Response:
"""
        
        return prompt
    
    def generate(
        self,
        query: str,
        category: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        do_sample: bool = True
    ) -> Dict[str, Any]:
        """
        Generate response with RAG context.
        
        Args:
            query: User query
            category: Knowledge category filter
            system_prompt: Custom system prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            do_sample: Whether to use sampling
        
        Returns:
            Dictionary with response and metadata
        """
        # Build prompt with RAG context
        full_prompt = self._build_rag_prompt(query, category, system_prompt)
        
        try:
            if self.generator:
                # Use pipeline
                outputs = self.generator(
                    full_prompt,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=do_sample,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                response_text = outputs[0]['generated_text'][len(full_prompt):]
            else:
                # Manual generation
                inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.device)
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=max_new_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        do_sample=do_sample,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                response_text = self.tokenizer.decode(
                    outputs[0][inputs['input_ids'].shape[1]:],
                    skip_special_tokens=True
                )
            
            return {
                'response': response_text.strip(),
                'query': query,
                'category': category,
                'model': self.model_name,
                'rag_enabled': True
            }
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return {
                'response': f"Error generating response: {str(e)}",
                'query': query,
                'error': str(e)
            }
    
    def chat(
        self,
        query: str,
        category: Optional[str] = None,
        verbose: bool = False
    ) -> str:
        """
        Simple chat interface.
        
        Args:
            query: User query
            category: Knowledge category filter
            verbose: Print additional info
        
        Returns:
            Response text
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            if category:
                print(f"Category: {category}")
            print(f"{'='*60}\n")
        
        result = self.generate(query, category=category)
        
        if verbose:
            print(f"Model: {result.get('model', 'unknown')}")
            print(f"RAG Enabled: {result.get('rag_enabled', False)}")
            print(f"{'-'*60}\n")
        
        return result['response']


def main():
    """Test the RAG-enhanced LLM"""
    print("Initializing RAG-Enhanced LLM...")
    print("This may take a minute on first run...\n")
    
    llm = RAGEnhancedLLM()
    
    # Test queries
    test_queries = [
        ("How do I use Python decorators?", "python"),
        ("Explain binary search complexity", "cs"),
        ("What is Agile development?", "sdlc"),
        ("How do I check disk space in Ubuntu?", "ubuntu"),
        ("How do I train a neural network with PyTorch?", "ai_ml")
    ]
    
    print("\n" + "="*60)
    print("TESTING RAG-ENHANCED LLM")
    print("="*60)
    
    for query, category in test_queries:
        response = llm.chat(query, category=category, verbose=True)
        print(f"Response:\n{response}\n")
        print("="*60 + "\n")


if __name__ == "__main__":
    main()
