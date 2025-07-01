#!/usr/bin/env python3
"""
Named Entity Recognition (NER) Example using Llama-GPU

This example demonstrates high-speed entity extraction using Llama-GPU
for processing large volumes of text and identifying named entities
such as persons, organizations, locations, dates, and more.
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

class NERProcessor:
    """Named Entity Recognition processor using Llama-GPU."""
    
    def __init__(self, model_path: str, prefer_gpu: bool = True, auto_detect_aws: bool = True):
        """Initialize NER processor with Llama-GPU backend.
        
        Args:
            model_path: Path to the LLaMA model
            prefer_gpu: Whether to prefer GPU backends
            auto_detect_aws: Whether to auto-detect AWS GPU instances
        """
        self.llama = LlamaGPU(model_path, prefer_gpu=prefer_gpu, auto_detect_aws=auto_detect_aws)
        self.entity_types = [
            "PERSON", "ORGANIZATION", "LOCATION", "DATE", "TIME", 
            "MONEY", "PERCENT", "QUANTITY", "EVENT", "PRODUCT"
        ]
        
        # NER prompt templates
        self.ner_prompt = """Extract named entities from the following text. 
Return the results as a JSON array with each entity containing:
- "text": the entity text
- "type": the entity type (PERSON, ORGANIZATION, LOCATION, DATE, TIME, MONEY, PERCENT, QUANTITY, EVENT, PRODUCT)
- "start": starting position in text
- "end": ending position in text

Text: {text}

Entities:"""

    def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities from text.
        
        Args:
            text: Input text to process
            
        Returns:
            List of dictionaries containing entity information
        """
        try:
            # Create prompt for entity extraction
            prompt = self.ner_prompt.format(text=text)
            
            # Get model response
            response = self.llama.infer(prompt)
            
            # Parse JSON response
            entities = self._parse_entity_response(response, text)
            return entities
            
        except Exception as e:
            logging.error(f"Error extracting entities: {e}")
            return []

    def extract_entities_batch(self, texts: List[str], batch_size: Optional[int] = None) -> List[List[Dict]]:
        """Extract named entities from multiple texts in batch.
        
        Args:
            texts: List of input texts
            batch_size: Optional batch size for processing
            
        Returns:
            List of entity lists for each input text
        """
        try:
            # Create prompts for all texts
            prompts = [self.ner_prompt.format(text=text) for text in texts]
            
            # Process in batch
            responses = self.llama.batch_infer(prompts, batch_size)
            
            # Parse responses
            results = []
            for i, response in enumerate(responses):
                entities = self._parse_entity_response(response, texts[i])
                results.append(entities)
            
            return results
            
        except Exception as e:
            logging.error(f"Error in batch entity extraction: {e}")
            return [[] for _ in texts]

    def _parse_entity_response(self, response: str, original_text: str) -> List[Dict]:
        """Parse the model response to extract entity information.
        
        Args:
            response: Model response string
            original_text: Original input text for position calculation
            
        Returns:
            List of entity dictionaries
        """
        entities = []
        
        try:
            # Try to extract JSON from response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                entity_list = json.loads(json_str)
                
                for entity in entity_list:
                    if isinstance(entity, dict) and 'text' in entity and 'type' in entity:
                        # Validate entity type
                        if entity['type'] in self.entity_types:
                            # Calculate positions if not provided
                            if 'start' not in entity or 'end' not in entity:
                                start_pos = original_text.find(entity['text'])
                                if start_pos != -1:
                                    entity['start'] = start_pos
                                    entity['end'] = start_pos + len(entity['text'])
                            
                            entities.append(entity)
            
        except (json.JSONDecodeError, KeyError) as e:
            logging.warning(f"Failed to parse entity response: {e}")
            # Fallback: try to extract entities using simple pattern matching
            entities = self._fallback_entity_extraction(response, original_text)
        
        return entities

    def _fallback_entity_extraction(self, response: str, original_text: str) -> List[Dict]:
        """Fallback entity extraction using pattern matching.
        
        Args:
            response: Model response string
            original_text: Original input text
            
        Returns:
            List of entity dictionaries
        """
        entities = []
        
        # Simple pattern matching for common entity types
        import re
        
        # Person names (capitalized words)
        person_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        for match in re.finditer(person_pattern, original_text):
            entities.append({
                'text': match.group(),
                'type': 'PERSON',
                'start': match.start(),
                'end': match.end()
            })
        
        # Organizations (words ending with Inc, Corp, Ltd, etc.)
        org_pattern = r'\b[A-Z][a-zA-Z\s]+(?:Inc|Corp|Ltd|LLC|Company|Organization)\b'
        for match in re.finditer(org_pattern, original_text):
            entities.append({
                'text': match.group(),
                'type': 'ORGANIZATION',
                'start': match.start(),
                'end': match.end()
            })
        
        # Dates
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b'
        for match in re.finditer(date_pattern, original_text):
            entities.append({
                'text': match.group(),
                'type': 'DATE',
                'start': match.start(),
                'end': match.end()
            })
        
        return entities

    def get_entity_statistics(self, entities: List[Dict]) -> Dict:
        """Get statistics about extracted entities.
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Dictionary with entity statistics
        """
        stats = {
            'total_entities': len(entities),
            'by_type': {},
            'most_common': {}
        }
        
        # Count by type
        for entity in entities:
            entity_type = entity.get('type', 'UNKNOWN')
            stats['by_type'][entity_type] = stats['by_type'].get(entity_type, 0) + 1
        
        # Find most common entities
        entity_texts = [entity.get('text', '') for entity in entities]
        from collections import Counter
        text_counts = Counter(entity_texts)
        stats['most_common'] = dict(text_counts.most_common(5))
        
        return stats

def main():
    """Main function for NER example."""
    parser = argparse.ArgumentParser(description="Named Entity Recognition with Llama-GPU")
    parser.add_argument("--model", required=True, help="Path to the LLaMA model")
    parser.add_argument("--input", help="Input text for entity extraction")
    parser.add_argument("--input-file", help="File containing input texts (one per line)")
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
        # Initialize NER processor
        logger.info(f"Initializing NER processor with model: {args.model}")
        ner_processor = NERProcessor(
            model_path=args.model,
            prefer_gpu=args.prefer_gpu,
            auto_detect_aws=args.auto_detect_aws
        )
        
        # Load input texts
        texts = []
        if args.input:
            texts = [args.input]
        elif args.input_file:
            with open(args.input_file, 'r') as f:
                texts = [line.strip() for line in f if line.strip()]
        else:
            # Default example texts
            texts = [
                "Apple Inc. CEO Tim Cook announced new products at the WWDC event in San Francisco on June 10, 2024.",
                "Microsoft Corporation reported $50 billion in revenue for Q3 2024, with Satya Nadella leading the company.",
                "The United Nations meeting in New York City on March 15, 2024 discussed climate change policies.",
                "Tesla Motors CEO Elon Musk unveiled the new Model S at the factory in Fremont, California."
            ]
        
        if not texts:
            logger.error("No input texts provided")
            return 1
        
        logger.info(f"Processing {len(texts)} text(s) for entity extraction")
        
        # Process texts
        start_time = time.time()
        
        if len(texts) == 1:
            # Single text processing
            entities = ner_processor.extract_entities(texts[0])
            results = [entities]
        else:
            # Batch processing
            results = ner_processor.extract_entities_batch(texts, args.batch_size)
        
        end_time = time.time()
        
        # Display results
        print(f"\n=== Named Entity Recognition Results ===")
        print(f"Processing time: {end_time - start_time:.2f} seconds")
        print(f"Average time per text: {(end_time - start_time) / len(texts):.2f} seconds")
        
        for i, (text, entities) in enumerate(zip(texts, results)):
            print(f"\n--- Text {i+1} ---")
            print(f"Input: {text}")
            print(f"Entities found: {len(entities)}")
            
            if entities:
                print("Extracted entities:")
                for entity in entities:
                    print(f"  - {entity['text']} ({entity['type']}) at position {entity.get('start', 'N/A')}-{entity.get('end', 'N/A')}")
                
                # Show statistics
                stats = ner_processor.get_entity_statistics(entities)
                print(f"\nStatistics:")
                print(f"  Total entities: {stats['total_entities']}")
                print(f"  By type: {stats['by_type']}")
                print(f"  Most common: {stats['most_common']}")
            else:
                print("No entities found")
        
        # Save results if output file specified
        if args.output_file:
            output_data = {
                'processing_time': end_time - start_time,
                'texts_processed': len(texts),
                'results': []
            }
            
            for i, (text, entities) in enumerate(zip(texts, results)):
                output_data['results'].append({
                    'text_id': i + 1,
                    'input_text': text,
                    'entities': entities,
                    'statistics': ner_processor.get_entity_statistics(entities)
                })
            
            with open(args.output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            logger.info(f"Results saved to {args.output_file}")
        
        logger.info("NER processing completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during NER processing: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 