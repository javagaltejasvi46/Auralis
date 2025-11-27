"""
Text preprocessing utilities for therapy transcriptions.
Handles whitespace normalization, token counting, and marker preservation.
"""

import re
import logging
from typing import Optional
from transformers import AutoTokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextPreprocessor:
    """Preprocesses text for Phi-3-Mini fine-tuning."""
    
    def __init__(self, model_name: str = "microsoft/Phi-3-mini-4k-instruct", max_tokens: int = 2048):
        """
        Initialize the text preprocessor.
        
        Args:
            model_name: Name of the model for tokenizer (default: Phi-3-mini-4k-instruct)
            max_tokens: Maximum number of tokens allowed (default: 2048)
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.tokenizer = None
        
        # Pattern to match {{RED:text}} markers
        self.red_marker_pattern = re.compile(r'\{\{RED:[^}]+\}\}')
    
    def load_tokenizer(self):
        """Load the tokenizer for token counting."""
        if self.tokenizer is None:
            logger.info(f"Loading tokenizer: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            logger.info("Tokenizer loaded successfully")
    
    def normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace in text while preserving structure.
        
        - Converts multiple spaces to single space
        - Converts multiple newlines to single newline
        - Strips leading/trailing whitespace
        - Preserves {{RED:text}} markers
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with single newline
        text = re.sub(r'\n+', '\n', text)
        
        # Replace tabs with spaces
        text = text.replace('\t', ' ')
        
        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)
        
        # Final strip
        text = text.strip()
        
        return text
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in the text.
        
        Args:
            text: Input text
            
        Returns:
            Number of tokens
        """
        if self.tokenizer is None:
            self.load_tokenizer()
        
        tokens = self.tokenizer.encode(text, add_special_tokens=True)
        return len(tokens)
    
    def truncate_to_max_tokens(self, text: str, max_tokens: Optional[int] = None) -> str:
        """
        Truncate text to maximum number of tokens.
        
        Args:
            text: Input text
            max_tokens: Maximum tokens (uses self.max_tokens if None)
            
        Returns:
            Truncated text
        """
        if self.tokenizer is None:
            self.load_tokenizer()
        
        max_tokens = max_tokens or self.max_tokens
        
        # Encode text
        tokens = self.tokenizer.encode(text, add_special_tokens=True)
        
        # Check if truncation needed
        if len(tokens) <= max_tokens:
            return text
        
        # Truncate tokens
        truncated_tokens = tokens[:max_tokens]
        
        # Decode back to text
        truncated_text = self.tokenizer.decode(truncated_tokens, skip_special_tokens=True)
        
        logger.warning(f"Truncated text from {len(tokens)} to {max_tokens} tokens")
        
        return truncated_text
    
    def preserve_red_markers(self, text: str) -> bool:
        """
        Check if {{RED:text}} markers are preserved in the text.
        
        Args:
            text: Text to check
            
        Returns:
            True if markers are present and properly formatted
        """
        markers = self.red_marker_pattern.findall(text)
        return len(markers) > 0
    
    def extract_red_markers(self, text: str) -> list:
        """
        Extract all {{RED:text}} markers from text.
        
        Args:
            text: Text to extract markers from
            
        Returns:
            List of marker strings
        """
        return self.red_marker_pattern.findall(text)
    
    def validate_input(self, text: str) -> tuple[bool, str]:
        """
        Validate input text.
        
        Args:
            text: Text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text:
            return False, "Text is empty"
        
        if not isinstance(text, str):
            return False, f"Text must be string, got {type(text)}"
        
        if len(text.strip()) == 0:
            return False, "Text contains only whitespace"
        
        return True, ""
    
    def preprocess(self, text: str, preserve_markers: bool = True) -> str:
        """
        Full preprocessing pipeline.
        
        Args:
            text: Input text
            preserve_markers: Whether to check for marker preservation
            
        Returns:
            Preprocessed text
            
        Raises:
            ValueError: If input validation fails
        """
        # Validate input
        is_valid, error_msg = self.validate_input(text)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error_msg}")
        
        # Store original markers if needed
        original_markers = None
        if preserve_markers:
            original_markers = self.extract_red_markers(text)
        
        # Normalize whitespace
        text = self.normalize_whitespace(text)
        
        # Truncate if needed
        token_count = self.count_tokens(text)
        if token_count > self.max_tokens:
            text = self.truncate_to_max_tokens(text)
            
            # Verify markers still present after truncation
            if preserve_markers and original_markers:
                new_markers = self.extract_red_markers(text)
                if len(new_markers) < len(original_markers):
                    logger.warning(
                        f"Some {{{{RED:}}}} markers lost during truncation: "
                        f"{len(original_markers)} -> {len(new_markers)}"
                    )
        
        return text
    
    def preprocess_pair(self, transcription: str, summary: str) -> tuple[str, str]:
        """
        Preprocess a transcription-summary pair.
        
        Args:
            transcription: Session transcription
            summary: Session summary
            
        Returns:
            Tuple of (preprocessed_transcription, preprocessed_summary)
        """
        # Preprocess transcription (no markers expected)
        processed_transcription = self.preprocess(transcription, preserve_markers=False)
        
        # Preprocess summary (preserve {{RED:}} markers)
        processed_summary = self.preprocess(summary, preserve_markers=True)
        
        return processed_transcription, processed_summary


if __name__ == "__main__":
    # Example usage
    preprocessor = TextPreprocessor()
    
    # Test whitespace normalization
    text = "This  has   multiple    spaces\n\n\nand\n\n\nmultiple\nnewlines"
    normalized = preprocessor.normalize_whitespace(text)
    print("Original:", repr(text))
    print("Normalized:", repr(normalized))
    print()
    
    # Test marker preservation
    summary = "Patient showed {{RED:suicidal ideation}} but no plan. Discussed coping strategies."
    markers = preprocessor.extract_red_markers(summary)
    print("Summary:", summary)
    print("Markers found:", markers)
    print()
    
    # Test full preprocessing
    long_text = "This is a test. " * 500  # Create long text
    preprocessor.load_tokenizer()
    token_count = preprocessor.count_tokens(long_text)
    print(f"Original token count: {token_count}")
    
    if token_count > 2048:
        truncated = preprocessor.truncate_to_max_tokens(long_text)
        new_count = preprocessor.count_tokens(truncated)
        print(f"Truncated token count: {new_count}")
    
    print("\nPreprocessing complete!")
