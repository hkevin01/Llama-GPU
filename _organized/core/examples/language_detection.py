#!/usr/bin/env python3
"""
Language Detection Example using Llama-GPU

This example demonstrates multi-language processing using Llama-GPU
for detecting and classifying text in different languages with
confidence scores and language family identification.
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

class LanguageDetector:
    """Language detector using Llama-GPU."""
    
    def __init__(self, model_path: str, prefer_gpu: bool = True, auto_detect_aws: bool = True):
        """Initialize language detector with Llama-GPU backend.
        
        Args:
            model_path: Path to the LLaMA model
            prefer_gpu: Whether to prefer GPU backends
            auto_detect_aws: Whether to auto-detect AWS GPU instances
        """
        self.llama = LlamaGPU(model_path, prefer_gpu=prefer_gpu, auto_detect_aws=auto_detect_aws)
        
        # Supported languages with ISO codes
        self.languages = {
            "ENGLISH": "en",
            "SPANISH": "es", 
            "FRENCH": "fr",
            "GERMAN": "de",
            "ITALIAN": "it",
            "PORTUGUESE": "pt",
            "RUSSIAN": "ru",
            "CHINESE": "zh",
            "JAPANESE": "ja",
            "KOREAN": "ko",
            "ARABIC": "ar",
            "HINDI": "hi",
            "DUTCH": "nl",
            "SWEDISH": "sv",
            "NORWEGIAN": "no",
            "DANISH": "da",
            "FINNISH": "fi",
            "POLISH": "pl",
            "TURKISH": "tr",
            "GREEK": "el"
        }
        
        # Language families
        self.language_families = {
            "GERMANIC": ["ENGLISH", "GERMAN", "DUTCH", "SWEDISH", "NORWEGIAN", "DANISH"],
            "ROMANCE": ["SPANISH", "FRENCH", "ITALIAN", "PORTUGUESE"],
            "SLAVIC": ["RUSSIAN", "POLISH"],
            "SINO-TIBETAN": ["CHINESE"],
            "JAPONIC": ["JAPANESE"],
            "KOREANIC": ["KOREAN"],
            "SEMITIC": ["ARABIC"],
            "INDO-ARYAN": ["HINDI"],
            "URALIC": ["FINNISH"],
            "TURKIC": ["TURKISH"],
            "HELLENIC": ["GREEK"]
        }
        
        # Language detection prompt template
        self.detection_prompt = """Detect the language of the following text. 
Return the result as a JSON object with:
- "language": the detected language name
- "iso_code": the ISO 639-1 language code
- "confidence": confidence score (0.0 to 1.0)
- "family": the language family

Supported languages: English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, Korean, Arabic, Hindi, Dutch, Swedish, Norwegian, Danish, Finnish, Polish, Turkish, Greek

Text: {text}

Result:"""

    def detect_language(self, text: str) -> Dict:
        """Detect language of a single text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with language detection results
        """
        try:
            # Create prompt for language detection
            prompt = self.detection_prompt.format(text=text[:500])  # Limit length
            
            # Get model response
            response = self.llama.infer(prompt)
            
            # Parse response
            result = self._parse_language_response(response)
            
            return {
                'text': text[:100] + "..." if len(text) > 100 else text,
                'language': result.get('language', 'UNKNOWN'),
                'iso_code': result.get('iso_code', ''),
                'confidence': result.get('confidence', 0.0),
                'family': result.get('family', 'UNKNOWN'),
                'processing_time': None  # Will be set by caller
            }
            
        except Exception as e:
            logging.error(f"Error detecting language: {e}")
            return {
                'text': text[:100] + "..." if len(text) > 100 else text,
                'language': 'UNKNOWN',
                'iso_code': '',
                'confidence': 0.0,
                'family': 'UNKNOWN',
                'error': str(e)
            }

    def detect_languages_batch(self, texts: List[str], batch_size: Optional[int] = None) -> List[Dict]:
        """Detect languages of multiple texts in batch.
        
        Args:
            texts: List of input texts
            batch_size: Optional batch size for processing
            
        Returns:
            List of language detection results
        """
        try:
            # Create prompts for all texts
            prompts = [self.detection_prompt.format(text=text[:500]) for text in texts]
            
            # Process in batch
            responses = self.llama.batch_infer(prompts, batch_size)
            
            # Parse responses
            results = []
            for i, response in enumerate(responses):
                result = self._parse_language_response(response)
                results.append({
                    'text': texts[i][:100] + "..." if len(texts[i]) > 100 else texts[i],
                    'language': result.get('language', 'UNKNOWN'),
                    'iso_code': result.get('iso_code', ''),
                    'confidence': result.get('confidence', 0.0),
                    'family': result.get('family', 'UNKNOWN')
                })
            
            return results
            
        except Exception as e:
            logging.error(f"Error in batch language detection: {e}")
            return [{'text': text[:100] + "...", 'language': 'UNKNOWN', 'iso_code': '', 'confidence': 0.0, 'family': 'UNKNOWN', 'error': str(e)} 
                   for text in texts]

    def _parse_language_response(self, response: str) -> Dict:
        """Parse the model response to extract language information.
        
        Args:
            response: Model response string
            
        Returns:
            Dictionary with language detection results
        """
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                # Validate and clean result
                language = result.get('language', 'UNKNOWN').upper()
                iso_code = result.get('iso_code', '')
                confidence = float(result.get('confidence', 0.0))
                family = result.get('family', 'UNKNOWN').upper()
                
                # Validate language
                if language not in self.languages:
                    language = 'UNKNOWN'
                    iso_code = ''
                
                # Get language family if not provided
                if family == 'UNKNOWN':
                    family = self._get_language_family(language)
                
                return {
                    'language': language,
                    'iso_code': iso_code,
                    'confidence': max(0.0, min(1.0, confidence)),
                    'family': family
                }
            
            # Fallback: try to extract language name from response
            return self._fallback_language_extraction(response)
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logging.warning(f"Failed to parse language response: {e}")
            return self._fallback_language_extraction(response)

    def _fallback_language_extraction(self, response: str) -> Dict:
        """Fallback language extraction using pattern matching.
        
        Args:
            response: Model response string
            
        Returns:
            Dictionary with language detection results
        """
        response_upper = response.upper()
        
        # Try to find language names in response
        for language in self.languages.keys():
            if language in response_upper:
                family = self._get_language_family(language)
                return {
                    'language': language,
                    'iso_code': self.languages[language],
                    'confidence': 0.7,  # Medium confidence for fallback
                    'family': family
                }
        
        # Default fallback
        return {
            'language': 'UNKNOWN',
            'iso_code': '',
            'confidence': 0.0,
            'family': 'UNKNOWN'
        }

    def _get_language_family(self, language: str) -> str:
        """Get the language family for a given language.
        
        Args:
            language: Language name
            
        Returns:
            Language family name
        """
        for family, languages in self.language_families.items():
            if language in languages:
                return family
        return 'UNKNOWN'

    def get_detection_statistics(self, results: List[Dict]) -> Dict:
        """Get statistics about language detection results.
        
        Args:
            results: List of language detection results
            
        Returns:
            Dictionary with detection statistics
        """
        stats = {
            'total_texts': len(results),
            'by_language': {},
            'by_family': {},
            'average_confidence': 0.0,
            'high_confidence_count': 0,
            'low_confidence_count': 0,
            'detected_languages': set()
        }
        
        total_confidence = 0.0
        
        for result in results:
            language = result.get('language', 'UNKNOWN')
            family = result.get('family', 'UNKNOWN')
            confidence = result.get('confidence', 0.0)
            
            # Count by language
            stats['by_language'][language] = stats['by_language'].get(language, 0) + 1
            
            # Count by family
            stats['by_family'][family] = stats['by_family'].get(family, 0) + 1
            
            # Track confidence
            total_confidence += confidence
            
            if confidence >= 0.7:
                stats['high_confidence_count'] += 1
            elif confidence < 0.3:
                stats['low_confidence_count'] += 1
            
            # Track unique languages
            if language != 'UNKNOWN':
                stats['detected_languages'].add(language)
        
        if results:
            stats['average_confidence'] = total_confidence / len(results)
        
        # Convert set to list for JSON serialization
        stats['detected_languages'] = list(stats['detected_languages'])
        
        return stats

def main():
    """Main function for language detection example."""
    parser = argparse.ArgumentParser(description="Language Detection with Llama-GPU")
    parser.add_argument("--model", required=True, help="Path to the LLaMA model")
    parser.add_argument("--input", help="Input text for language detection")
    parser.add_argument("--input-file", help="File containing texts (one per line)")
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
        # Initialize language detector
        logger.info(f"Initializing language detector with model: {args.model}")
        detector = LanguageDetector(
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
            # Default example texts in different languages
            texts = [
                "Hello, how are you today? This is an example of English text.",
                "Hola, ¿cómo estás hoy? Este es un ejemplo de texto en español.",
                "Bonjour, comment allez-vous aujourd'hui? Ceci est un exemple de texte français.",
                "Hallo, wie geht es dir heute? Dies ist ein Beispiel für deutschen Text.",
                "Ciao, come stai oggi? Questo è un esempio di testo italiano.",
                "Привет, как дела сегодня? Это пример русского текста.",
                "こんにちは、今日はどうですか？これは日本語のテキストの例です。",
                "안녕하세요, 오늘 어떠세요? 이것은 한국어 텍스트의 예입니다."
            ]
        
        if not texts:
            logger.error("No input texts provided")
            return 1
        
        logger.info(f"Processing {len(texts)} text(s) for language detection")
        
        # Process texts
        start_time = time.time()
        
        if len(texts) == 1:
            # Single text processing
            result = detector.detect_language(texts[0])
            result['processing_time'] = time.time() - start_time
            results = [result]
        else:
            # Batch processing
            results = detector.detect_languages_batch(texts, args.batch_size)
            for result in results:
                result['processing_time'] = (time.time() - start_time) / len(texts)
        
        end_time = time.time()
        
        # Display results
        print(f"\n=== Language Detection Results ===")
        print(f"Total processing time: {end_time - start_time:.2f} seconds")
        print(f"Average time per text: {(end_time - start_time) / len(texts):.2f} seconds")
        
        for i, result in enumerate(results):
            print(f"\n--- Text {i+1} ---")
            print(f"Text: {result['text']}")
            print(f"Language: {result['language']} ({result['iso_code']})")
            print(f"Family: {result['family']}")
            print(f"Confidence: {result['confidence']:.2f}")
            if 'processing_time' in result:
                print(f"Processing time: {result['processing_time']:.2f} seconds")
        
        # Show overall statistics
        stats = detector.get_detection_statistics(results)
        print(f"\n=== Detection Statistics ===")
        print(f"Total texts: {stats['total_texts']}")
        print(f"Average confidence: {stats['average_confidence']:.2f}")
        print(f"High confidence (≥0.7): {stats['high_confidence_count']}")
        print(f"Low confidence (<0.3): {stats['low_confidence_count']}")
        print(f"Languages detected: {stats['detected_languages']}")
        print(f"Languages found:")
        for language, count in stats['by_language'].items():
            print(f"  - {language}: {count}")
        print(f"Language families:")
        for family, count in stats['by_family'].items():
            print(f"  - {family}: {count}")
        
        # Save results if output file specified
        if args.output_file:
            output_data = {
                'total_processing_time': end_time - start_time,
                'texts_processed': len(texts),
                'statistics': stats,
                'results': results
            }
            
            with open(args.output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            logger.info(f"Results saved to {args.output_file}")
        
        logger.info("Language detection completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during language detection: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 