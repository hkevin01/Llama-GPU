#!/usr/bin/env python3
"""
Document Classification Example using Llama-GPU

This example demonstrates large-scale document categorization using Llama-GPU
for classifying documents into predefined categories such as news, technical,
legal, medical, financial, and more.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llama_gpu import LlamaGPU

class DocumentClassifier:
    """Document classifier using Llama-GPU."""
    
    def __init__(self, model_path: str, prefer_gpu: bool = True, auto_detect_aws: bool = True):
        """Initialize document classifier with Llama-GPU backend.
        
        Args:
            model_path: Path to the LLaMA model
            prefer_gpu: Whether to prefer GPU backends
            auto_detect_aws: Whether to auto-detect AWS GPU instances
        """
        self.llama = LlamaGPU(model_path, prefer_gpu=prefer_gpu, auto_detect_aws=auto_detect_aws)
        
        # Predefined document categories
        self.categories = [
            "NEWS", "TECHNICAL", "LEGAL", "MEDICAL", "FINANCIAL", 
            "ACADEMIC", "MARKETING", "PERSONAL", "GOVERNMENT", "ENTERTAINMENT"
        ]
        
        # Classification prompt template
        self.classification_prompt = """Classify the following document into one of these categories:
- NEWS: News articles, current events, journalism
- TECHNICAL: Technical documentation, manuals, specifications
- LEGAL: Legal documents, contracts, regulations
- MEDICAL: Medical reports, health information, clinical studies
- FINANCIAL: Financial reports, economic data, investment information
- ACADEMIC: Research papers, scholarly articles, educational content
- MARKETING: Advertisements, promotional materials, sales content
- PERSONAL: Personal correspondence, diaries, private communications
- GOVERNMENT: Government documents, official communications, policy papers
- ENTERTAINMENT: Entertainment content, reviews, creative writing

Document: {document}

Category:"""

    def classify_document(self, document: str) -> Dict:
        """Classify a single document.
        
        Args:
            document: Input document text
            
        Returns:
            Dictionary with classification results
        """
        try:
            # Create prompt for classification
            prompt = self.classification_prompt.format(document=document[:1000])  # Limit length
            
            # Get model response
            response = self.llama.infer(prompt)
            
            # Parse response
            category, confidence = self._parse_classification_response(response)
            
            return {
                'document': document[:200] + "..." if len(document) > 200 else document,
                'category': category,
                'confidence': confidence,
                'processing_time': None  # Will be set by caller
            }
            
        except Exception as e:
            logging.error(f"Error classifying document: {e}")
            return {
                'document': document[:200] + "..." if len(document) > 200 else document,
                'category': 'UNKNOWN',
                'confidence': 0.0,
                'error': str(e)
            }

    def classify_documents_batch(self, documents: List[str], batch_size: Optional[int] = None) -> List[Dict]:
        """Classify multiple documents in batch.
        
        Args:
            documents: List of document texts
            batch_size: Optional batch size for processing
            
        Returns:
            List of classification results
        """
        try:
            # Create prompts for all documents
            prompts = [self.classification_prompt.format(document=doc[:1000]) for doc in documents]
            
            # Process in batch
            responses = self.llama.batch_infer(prompts, batch_size)
            
            # Parse responses
            results = []
            for i, response in enumerate(responses):
                category, confidence = self._parse_classification_response(response)
                results.append({
                    'document': documents[i][:200] + "..." if len(documents[i]) > 200 else documents[i],
                    'category': category,
                    'confidence': confidence
                })
            
            return results
            
        except Exception as e:
            logging.error(f"Error in batch document classification: {e}")
            return [{'document': doc[:200] + "...", 'category': 'UNKNOWN', 'confidence': 0.0, 'error': str(e)} 
                   for doc in documents]

    def _parse_classification_response(self, response: str) -> Tuple[str, float]:
        """Parse the model response to extract category and confidence.
        
        Args:
            response: Model response string
            
        Returns:
            Tuple of (category, confidence)
        """
        try:
            # Clean response
            response = response.strip().upper()
            
            # Try to extract category from response
            for category in self.categories:
                if category in response:
                    # Simple confidence calculation based on response clarity
                    confidence = self._calculate_confidence(response, category)
                    return category, confidence
            
            # If no exact match, try partial matches
            for category in self.categories:
                if any(word in response for word in category.split()):
                    confidence = self._calculate_confidence(response, category)
                    return category, confidence
            
            # Default fallback
            return 'UNKNOWN', 0.0
            
        except Exception as e:
            logging.warning(f"Failed to parse classification response: {e}")
            return 'UNKNOWN', 0.0

    def _calculate_confidence(self, response: str, category: str) -> float:
        """Calculate confidence score for classification.
        
        Args:
            response: Model response
            category: Detected category
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Simple confidence calculation
        if category in response:
            # Higher confidence if category appears early in response
            position = response.find(category)
            if position < len(response) * 0.3:  # First 30% of response
                return 0.9
            elif position < len(response) * 0.7:  # First 70% of response
                return 0.7
            else:
                return 0.5
        
        return 0.3

    def get_classification_statistics(self, results: List[Dict]) -> Dict:
        """Get statistics about classification results.
        
        Args:
            results: List of classification results
            
        Returns:
            Dictionary with classification statistics
        """
        stats = {
            'total_documents': len(results),
            'by_category': {},
            'average_confidence': 0.0,
            'high_confidence_count': 0,
            'low_confidence_count': 0
        }
        
        total_confidence = 0.0
        
        for result in results:
            category = result.get('category', 'UNKNOWN')
            confidence = result.get('confidence', 0.0)
            
            # Count by category
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            # Track confidence
            total_confidence += confidence
            
            if confidence >= 0.7:
                stats['high_confidence_count'] += 1
            elif confidence < 0.3:
                stats['low_confidence_count'] += 1
        
        if results:
            stats['average_confidence'] = total_confidence / len(results)
        
        return stats

def main():
    """Main function for document classification example."""
    parser = argparse.ArgumentParser(description="Document Classification with Llama-GPU")
    parser.add_argument("--model", required=True, help="Path to the LLaMA model")
    parser.add_argument("--input", help="Input document for classification")
    parser.add_argument("--input-file", help="File containing documents (one per line)")
    parser.add_argument("--output-file", help="File to save results")
    parser.add_argument("--batch-size", type=int, help="Batch size for processing")
    parser.add_argument("--prefer-gpu", action="store_true", default=True, help="Prefer GPU backends")
    parser.add_argument("--auto-detect-aws", action="store_true", default=True, help="Auto-detect AWS")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=getattr(logging, args.log_level.upper()))
    logger = logging.getLogger(__name__)
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    try:
        # Initialize document classifier
        logger.info(f"Initializing document classifier with model: {args.model}")
        classifier = DocumentClassifier(
            model_path=args.model,
            prefer_gpu=args.prefer_gpu,
            auto_detect_aws=args.auto_detect_aws
        )
        
        # Load input documents
        documents = []
        if args.input:
            documents = [args.input]
        elif args.input_file:
            with open(args.input_file, 'r') as f:
                documents = [line.strip() for line in f if line.strip()]
        else:
            # Default example documents
            documents = [
                "Apple Inc. today announced record quarterly revenue of $119.6 billion, up 2 percent year over year. The company's iPhone sales reached new heights with strong demand across all markets.",
                "The implementation of neural networks requires careful consideration of hyperparameters including learning rate, batch size, and network architecture. This technical specification outlines the requirements for the machine learning pipeline.",
                "This agreement is made and entered into as of January 1, 2024, by and between Company A, a corporation organized under the laws of Delaware, and Company B, a corporation organized under the laws of California.",
                "Patient presents with symptoms of chest pain and shortness of breath. EKG shows ST-segment elevation. Recommend immediate cardiac catheterization and potential stent placement.",
                "Q4 2024 financial results show revenue growth of 15% year-over-year, with net income reaching $2.3 billion. The company's stock price increased by 8% following the earnings announcement."
            ]
        
        if not documents:
            logger.error("No input documents provided")
            return 1
        
        logger.info(f"Processing {len(documents)} document(s) for classification")
        
        # Process documents
        start_time = time.time()
        
        if len(documents) == 1:
            # Single document processing
            result = classifier.classify_document(documents[0])
            result['processing_time'] = time.time() - start_time
            results = [result]
        else:
            # Batch processing
            results = classifier.classify_documents_batch(documents, args.batch_size)
            for result in results:
                result['processing_time'] = (time.time() - start_time) / len(documents)
        
        end_time = time.time()
        
        # Display results
        print(f"\n=== Document Classification Results ===")
        print(f"Total processing time: {end_time - start_time:.2f} seconds")
        print(f"Average time per document: {(end_time - start_time) / len(documents):.2f} seconds")
        
        for i, result in enumerate(results):
            print(f"\n--- Document {i+1} ---")
            print(f"Document: {result['document']}")
            print(f"Category: {result['category']}")
            print(f"Confidence: {result['confidence']:.2f}")
            if 'processing_time' in result:
                print(f"Processing time: {result['processing_time']:.2f} seconds")
        
        # Show overall statistics
        stats = classifier.get_classification_statistics(results)
        print(f"\n=== Classification Statistics ===")
        print(f"Total documents: {stats['total_documents']}")
        print(f"Average confidence: {stats['average_confidence']:.2f}")
        print(f"High confidence (≥0.7): {stats['high_confidence_count']}")
        print(f"Low confidence (<0.3): {stats['low_confidence_count']}")
        print(f"Categories found:")
        for category, count in stats['by_category'].items():
            print(f"  - {category}: {count}")
        
        # Save results if output file specified
        if args.output_file:
            output_data = {
                'total_processing_time': end_time - start_time,
                'documents_processed': len(documents),
                'statistics': stats,
                'results': results
            }
            
            with open(args.output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            logger.info(f"Results saved to {args.output_file}")
        
        logger.info("Document classification completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during document classification: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 