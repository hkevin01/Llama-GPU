"""
Knowledge Base Module for Llama-GPU
Provides RAG-based knowledge retrieval for software engineering assistant
"""

from .rag_engine import RAGEngine
from .knowledge_populator import KnowledgePopulator

__all__ = ['RAGEngine', 'KnowledgePopulator']
