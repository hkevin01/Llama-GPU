#!/usr/bin/env python3
"""
Question Answering Example using Llama-GPU

This example demonstrates neural question answering with attention mechanisms
using Llama-GPU for extracting answers from context with confidence scoring
and answer validation.
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

class QuestionAnswering:
    """Question answering system using Llama-GPU."""
    
    def __init__(self, model_path: str, prefer_gpu: bool = True, auto_detect_aws: bool = True):
        """Initialize question answering system with Llama-GPU backend.
        
        Args:
            model_path: Path to the LLaMA model
            prefer_gpu: Whether to prefer GPU backends
            auto_detect_aws: Whether to auto-detect AWS GPU instances
        """
        self.llama = LlamaGPU(model_path, prefer_gpu=prefer_gpu, auto_detect_aws=auto_detect_aws)
        
        # QA prompt template with attention mechanism guidance
        self.qa_prompt = """Answer the following question based on the given context. 
Use attention mechanisms to focus on the most relevant parts of the context.

Context: {context}

Question: {question}

Instructions:
1. Read the context carefully and identify the most relevant information
2. Focus your attention on the parts that directly answer the question
3. Provide a concise and accurate answer
4. If the answer is not in the context, say "I cannot find the answer in the provided context"
5. Include confidence level (high/medium/low) based on how clearly the context supports your answer

Answer:"""

    def answer_question(self, context: str, question: str) -> Dict:
        """Answer a single question based on context.
        
        Args:
            context: Context text to search for answers
            question: Question to answer
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Create prompt for question answering
            prompt = self.qa_prompt.format(
                context=context[:1500],  # Limit context length
                question=question
            )
            
            # Get model response
            response = self.llama.infer(prompt)
            
            # Parse response
            answer, confidence = self._parse_qa_response(response)
            
            return {
                'context': context[:200] + "..." if len(context) > 200 else context,
                'question': question,
                'answer': answer,
                'confidence': confidence,
                'processing_time': None  # Will be set by caller
            }
            
        except Exception as e:
            logging.error(f"Error answering question: {e}")
            return {
                'context': context[:200] + "..." if len(context) > 200 else context,
                'question': question,
                'answer': "Error processing question",
                'confidence': 0.0,
                'error': str(e)
            }

    def answer_questions_batch(self, qa_pairs: List[Tuple[str, str]], batch_size: Optional[int] = None) -> List[Dict]:
        """Answer multiple questions in batch.
        
        Args:
            qa_pairs: List of (context, question) tuples
            batch_size: Optional batch size for processing
            
        Returns:
            List of answer results
        """
        try:
            # Create prompts for all QA pairs
            prompts = [self.qa_prompt.format(context=context[:1500], question=question) 
                      for context, question in qa_pairs]
            
            # Process in batch
            responses = self.llama.batch_infer(prompts, batch_size)
            
            # Parse responses
            results = []
            for i, response in enumerate(responses):
                context, question = qa_pairs[i]
                answer, confidence = self._parse_qa_response(response)
                results.append({
                    'context': context[:200] + "..." if len(context) > 200 else context,
                    'question': question,
                    'answer': answer,
                    'confidence': confidence
                })
            
            return results
            
        except Exception as e:
            logging.error(f"Error in batch question answering: {e}")
            return [{'context': context[:200] + "...", 'question': question, 'answer': "Error processing question", 'confidence': 0.0, 'error': str(e)} 
                   for context, question in qa_pairs]

    def _parse_qa_response(self, response: str) -> Tuple[str, float]:
        """Parse the model response to extract answer and confidence.
        
        Args:
            response: Model response string
            
        Returns:
            Tuple of (answer, confidence)
        """
        try:
            # Clean response
            response = response.strip()
            
            # Extract confidence level
            confidence = self._extract_confidence(response)
            
            # Extract answer (remove confidence indicators)
            answer = self._extract_answer(response)
            
            return answer, confidence
            
        except Exception as e:
            logging.warning(f"Failed to parse QA response: {e}")
            return "Unable to parse answer", 0.0

    def _extract_confidence(self, response: str) -> float:
        """Extract confidence level from response.
        
        Args:
            response: Model response string
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        response_lower = response.lower()
        
        if 'high confidence' in response_lower or 'confidence: high' in response_lower:
            return 0.9
        elif 'medium confidence' in response_lower or 'confidence: medium' in response_lower:
            return 0.6
        elif 'low confidence' in response_lower or 'confidence: low' in response_lower:
            return 0.3
        elif 'cannot find' in response_lower or 'not in the context' in response_lower:
            return 0.1
        else:
            # Default confidence based on response length and clarity
            if len(response) > 50 and not response.startswith("I cannot"):
                return 0.7
            else:
                return 0.4

    def _extract_answer(self, response: str) -> str:
        """Extract the answer from the response.
        
        Args:
            response: Model response string
            
        Returns:
            Cleaned answer text
        """
        # Remove confidence indicators
        answer = response
        confidence_indicators = [
            'confidence: high', 'confidence: medium', 'confidence: low',
            'high confidence', 'medium confidence', 'low confidence'
        ]
        
        for indicator in confidence_indicators:
            answer = answer.replace(indicator, '').replace(indicator.title(), '')
        
        # Clean up extra whitespace
        answer = ' '.join(answer.split())
        
        return answer

    def validate_answer(self, context: str, question: str, answer: str) -> Dict:
        """Validate an answer against the context.
        
        Args:
            context: Original context
            question: Original question
            answer: Generated answer
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'answer_in_context': False,
            'context_support': 0.0,
            'answer_length': len(answer),
            'validation_score': 0.0
        }
        
        try:
            # Check if answer appears in context
            context_lower = context.lower()
            answer_lower = answer.lower()
            
            if answer_lower in context_lower:
                validation['answer_in_context'] = True
                validation['context_support'] = 0.8
            else:
                # Check for partial matches
                answer_words = answer_lower.split()
                context_words = context_lower.split()
                
                matches = sum(1 for word in answer_words if word in context_words)
                if matches > 0:
                    validation['context_support'] = matches / len(answer_words)
            
            # Calculate validation score
            validation['validation_score'] = (
                validation['context_support'] * 0.6 +
                (1.0 if validation['answer_in_context'] else 0.0) * 0.4
            )
            
        except Exception as e:
            logging.warning(f"Error validating answer: {e}")
        
        return validation

    def get_qa_statistics(self, results: List[Dict]) -> Dict:
        """Get statistics about question answering results.
        
        Args:
            results: List of QA results
            
        Returns:
            Dictionary with QA statistics
        """
        stats = {
            'total_questions': len(results),
            'average_confidence': 0.0,
            'high_confidence_count': 0,
            'low_confidence_count': 0,
            'average_answer_length': 0.0,
            'validation_scores': []
        }
        
        total_confidence = 0.0
        total_length = 0.0
        
        for result in results:
            confidence = result.get('confidence', 0.0)
            answer_length = len(result.get('answer', ''))
            
            total_confidence += confidence
            total_length += answer_length
            
            if confidence >= 0.7:
                stats['high_confidence_count'] += 1
            elif confidence < 0.3:
                stats['low_confidence_count'] += 1
        
        if results:
            stats['average_confidence'] = total_confidence / len(results)
            stats['average_answer_length'] = total_length / len(results)
        
        return stats

def main():
    """Main function for question answering example."""
    parser = argparse.ArgumentParser(description="Question Answering with Llama-GPU")
    parser.add_argument("--model", required=True, help="Path to the LLaMA model")
    parser.add_argument("--context", help="Context text for answering questions")
    parser.add_argument("--question", help="Question to answer")
    parser.add_argument("--input-file", help="JSON file with context-question pairs")
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
        # Initialize question answering system
        logger.info(f"Initializing QA system with model: {args.model}")
        qa_system = QuestionAnswering(
            model_path=args.model,
            prefer_gpu=args.prefer_gpu,
            auto_detect_aws=args.auto_detect_aws
        )
        
        # Load input data
        qa_pairs = []
        if args.context and args.question:
            qa_pairs = [(args.context, args.question)]
        elif args.input_file:
            with open(args.input_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    qa_pairs = [(item['context'], item['question']) for item in data]
                else:
                    qa_pairs = [(data['context'], data['question'])]
        else:
            # Default example QA pairs
            qa_pairs = [
                ("The Python programming language was created by Guido van Rossum and was first released in 1991. Python is known for its simplicity and readability, making it popular for beginners and experts alike. It supports multiple programming paradigms including procedural, object-oriented, and functional programming.", 
                 "Who created the Python programming language?"),
                
                ("Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models that enable computers to improve their performance on a specific task through experience. Deep learning, a subset of machine learning, uses neural networks with multiple layers to model complex patterns in data.", 
                 "What is the relationship between machine learning and deep learning?"),
                
                ("The Great Wall of China is one of the most impressive architectural feats in human history. Construction began in the 7th century BC and continued for over 2,000 years. The wall stretches for approximately 13,171 miles (21,196 kilometers) across northern China.", 
                 "How long is the Great Wall of China?"),
                
                ("Climate change refers to long-term shifts in global weather patterns and average temperatures. The primary cause of recent climate change is the increase in greenhouse gas emissions from human activities, particularly the burning of fossil fuels. This leads to global warming and various environmental impacts.", 
                 "What is the main cause of climate change?")
            ]
        
        if not qa_pairs:
            logger.error("No input data provided")
            return 1
        
        logger.info(f"Processing {len(qa_pairs)} question(s)")
        
        # Process questions
        start_time = time.time()
        
        if len(qa_pairs) == 1:
            # Single question processing
            context, question = qa_pairs[0]
            result = qa_system.answer_question(context, question)
            result['processing_time'] = time.time() - start_time
            results = [result]
        else:
            # Batch processing
            results = qa_system.answer_questions_batch(qa_pairs, args.batch_size)
            for result in results:
                result['processing_time'] = (time.time() - start_time) / len(qa_pairs)
        
        end_time = time.time()
        
        # Display results
        print(f"\n=== Question Answering Results ===")
        print(f"Total processing time: {end_time - start_time:.2f} seconds")
        print(f"Average time per question: {(end_time - start_time) / len(qa_pairs):.2f} seconds")
        
        for i, result in enumerate(results):
            print(f"\n--- Question {i+1} ---")
            print(f"Context: {result['context']}")
            print(f"Question: {result['question']}")
            print(f"Answer: {result['answer']}")
            print(f"Confidence: {result['confidence']:.2f}")
            if 'processing_time' in result:
                print(f"Processing time: {result['processing_time']:.2f} seconds")
            
            # Validate answer if context is available
            if i < len(qa_pairs):
                context, _ = qa_pairs[i]
                validation = qa_system.validate_answer(context, result['question'], result['answer'])
                print(f"Validation: Context support {validation['context_support']:.2f}, Score {validation['validation_score']:.2f}")
        
        # Show overall statistics
        stats = qa_system.get_qa_statistics(results)
        print(f"\n=== QA Statistics ===")
        print(f"Total questions: {stats['total_questions']}")
        print(f"Average confidence: {stats['average_confidence']:.2f}")
        print(f"High confidence (≥0.7): {stats['high_confidence_count']}")
        print(f"Low confidence (<0.3): {stats['low_confidence_count']}")
        print(f"Average answer length: {stats['average_answer_length']:.1f} characters")
        
        # Save results if output file specified
        if args.output_file:
            output_data = {
                'total_processing_time': end_time - start_time,
                'questions_processed': len(qa_pairs),
                'statistics': stats,
                'results': results
            }
            
            with open(args.output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            logger.info(f"Results saved to {args.output_file}")
        
        logger.info("Question answering completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during question answering: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 