#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) Engine for Software Engineering Knowledge
Provides context-aware responses using vector database and embeddings
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Retrieval-Augmented Generation engine for local software engineering assistant.
    Manages vector database, embeddings, and knowledge retrieval.
    """
    
    def __init__(
        self,
        persist_directory: str = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        collection_name: str = "software_engineering_knowledge"
    ):
        """
        Initialize RAG engine with vector database and embedding model.
        
        Args:
            persist_directory: Directory to persist vector database
            embedding_model: Sentence transformer model for embeddings
            collection_name: Name of the chroma collection
        """
        if persist_directory is None:
            persist_directory = str(Path.home() / ".llama-gpu" / "vectordb")
        
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize sentence transformer for embeddings
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection_name = collection_name
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self._get_embedding_function()
            )
            logger.info(f"Loaded existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self._get_embedding_function(),
                metadata={"description": "Software engineering knowledge base"}
            )
            logger.info(f"Created new collection: {collection_name}")
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def _get_embedding_function(self):
        """Get custom embedding function for ChromaDB"""
        class CustomEmbeddingFunction:
            def __init__(self, model):
                self.model = model
            
            def __call__(self, input: List[str]) -> List[List[float]]:
                embeddings = self.model.encode(input, convert_to_numpy=True)
                return embeddings.tolist()
        
        return CustomEmbeddingFunction(self.embedding_model)
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of document texts
            metadatas: Optional metadata for each document
            ids: Optional unique IDs for each document
        """
        if not documents:
            logger.warning("No documents to add")
            return
        
        # Generate IDs if not provided
        if ids is None:
            existing_count = self.collection.count()
            ids = [f"doc_{existing_count + i}" for i in range(len(documents))]
        
        # Add metadata if not provided
        if metadatas is None:
            metadatas = [{"source": "manual"} for _ in documents]
        
        # Split documents into chunks
        all_chunks = []
        all_metadatas = []
        all_ids = []
        
        for doc, metadata, doc_id in zip(documents, metadatas, ids):
            chunks = self.text_splitter.split_text(doc)
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_id'] = i
                chunk_metadata['parent_doc_id'] = doc_id
                all_metadatas.append(chunk_metadata)
                all_ids.append(f"{doc_id}_chunk_{i}")
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch_chunks = all_chunks[i:i + batch_size]
            batch_metadatas = all_metadatas[i:i + batch_size]
            batch_ids = all_ids[i:i + batch_size]
            
            self.collection.add(
                documents=batch_chunks,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
        
        logger.info(f"Added {len(all_chunks)} chunks from {len(documents)} documents")
    
    def query(
        self,
        query_text: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector database for relevant documents.
        
        Args:
            query_text: Query string
            n_results: Number of results to return
            filter_metadata: Optional metadata filter
        
        Returns:
            Dictionary with documents, metadatas, and distances
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=filter_metadata
            )
            
            return {
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else [],
                'distances': results['distances'][0] if results['distances'] else []
            }
        except Exception as e:
            logger.error(f"Query error: {e}")
            return {'documents': [], 'metadatas': [], 'distances': []}
    
    def get_context(
        self,
        query: str,
        max_chunks: int = 3,
        category: Optional[str] = None
    ) -> str:
        """
        Get formatted context for a query.
        
        Args:
            query: User query
            max_chunks: Maximum number of chunks to return
            category: Optional category filter (python, ai_ml, cs, sdlc, ubuntu)
        
        Returns:
            Formatted context string
        """
        filter_dict = {"category": category} if category else None
        
        results = self.query(
            query_text=query,
            n_results=max_chunks,
            filter_metadata=filter_dict
        )
        
        if not results['documents']:
            return ""
        
        context_parts = []
        for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
            source = metadata.get('source', 'unknown')
            category = metadata.get('category', 'general')
            context_parts.append(
                f"[Reference {i+1} - {category.upper()}]:\n{doc}\n"
            )
        
        return "\n".join(context_parts)
    
    def reset_collection(self) -> None:
        """Delete and recreate the collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception:
            pass
        
        self.collection = self.client.create_collection(
            name=self.collection_name,
            embedding_function=self._get_embedding_function(),
            metadata={"description": "Software engineering knowledge base"}
        )
        logger.info(f"Created new collection: {self.collection_name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            'total_chunks': count,
            'collection_name': self.collection_name,
            'embedding_model': self.embedding_model.__class__.__name__,
            'persist_directory': self.persist_directory
        }


if __name__ == "__main__":
    # Test the RAG engine
    rag = RAGEngine()
    
    # Add sample documents
    sample_docs = [
        "Python is a high-level programming language. It supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
        "List comprehensions in Python provide a concise way to create lists. The syntax is [expression for item in iterable if condition].",
        "Docker is a platform for developing, shipping, and running applications in containers. Containers package software with dependencies.",
        "Git is a distributed version control system. Common commands include git add, git commit, git push, and git pull."
    ]
    
    sample_metadata = [
        {"category": "python", "source": "python_basics", "topic": "introduction"},
        {"category": "python", "source": "python_basics", "topic": "list_comprehensions"},
        {"category": "devops", "source": "docker_intro", "topic": "containers"},
        {"category": "devops", "source": "git_basics", "topic": "version_control"}
    ]
    
    rag.add_documents(sample_docs, sample_metadata)
    
    # Test query
    print("\n=== Testing RAG Engine ===\n")
    query = "How do I create lists in Python?"
    context = rag.get_context(query, max_chunks=2)
    print(f"Query: {query}\n")
    print(f"Context:\n{context}")
    
    # Get stats
    stats = rag.get_stats()
    print(f"\nCollection stats: {stats}")
