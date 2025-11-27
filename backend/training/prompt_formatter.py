"""
Prompt formatter for Phi-3-Mini fine-tuning.
Formats therapy transcriptions and summaries using Phi-3 chat template.
"""

import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptFormatter:
    """Formats prompts for Phi-3-Mini using the official chat template."""
    
    # Phi-3 uses special tokens for chat formatting
    SYSTEM_TOKEN = "<|system|>"
    USER_TOKEN = "<|user|>"
    ASSISTANT_TOKEN = "<|assistant|>"
    END_TOKEN = "<|end|>"
    
    def __init__(self):
        """Initialize the prompt formatter."""
        self.system_instruction = self._get_system_instruction()
    
    def _get_system_instruction(self) -> str:
        """
        Get the system instruction for therapy session summarization.
        
        Returns:
            System instruction text
        """
        return """You are an expert clinical psychologist assistant specializing in therapy session documentation. Your task is to create concise, professional summaries of therapy sessions.

Guidelines:
1. Summarize the key themes, interventions, and patient responses
2. Use clinical terminology appropriately
3. Mark any risk-related content (suicidal ideation, self-harm, violence) with {{RED:text}} format
4. Keep summaries between 30-70 words per section
5. Maintain professional, objective tone
6. Include relevant clinical observations and treatment progress"""
    
    def format_single_session(self, transcription: str, summary: str = None) -> str:
        """
        Format a single therapy session for training.
        
        Args:
            transcription: The therapy session transcription
            summary: The expected summary (optional, for training)
            
        Returns:
            Formatted prompt string
        """
        # Build the prompt using Phi-3 chat template
        prompt = f"{self.SYSTEM_TOKEN}\n{self.system_instruction}{self.END_TOKEN}\n"
        prompt += f"{self.USER_TOKEN}\n"
        prompt += f"Please summarize the following therapy session:\n\n{transcription}{self.END_TOKEN}\n"
        
        if summary:
            # Training format: include the expected output
            prompt += f"{self.ASSISTANT_TOKEN}\n{summary}{self.END_TOKEN}"
        else:
            # Inference format: just the prompt
            prompt += f"{self.ASSISTANT_TOKEN}\n"
        
        return prompt
    
    def format_multiple_sessions(self, sessions: List[Dict[str, str]]) -> List[str]:
        """
        Format multiple therapy sessions for batch training.
        
        Args:
            sessions: List of dicts with 'transcription' and 'summary' keys
            
        Returns:
            List of formatted prompt strings
        """
        formatted_prompts = []
        
        for i, session in enumerate(sessions):
            transcription = session.get('transcription', '')
            summary = session.get('summary', '')
            
            if not transcription:
                logger.warning(f"Session {i} has empty transcription, skipping")
                continue
            
            prompt = self.format_single_session(transcription, summary)
            formatted_prompts.append(prompt)
        
        logger.info(f"Formatted {len(formatted_prompts)} sessions")
        return formatted_prompts
    
    def format_for_inference(self, transcription: str) -> str:
        """
        Format a transcription for inference (no expected summary).
        
        Args:
            transcription: The therapy session transcription
            
        Returns:
            Formatted prompt string for inference
        """
        return self.format_single_session(transcription, summary=None)
    
    def extract_response(self, generated_text: str) -> str:
        """
        Extract the assistant's response from generated text.
        
        Args:
            generated_text: Full generated text including prompt
            
        Returns:
            Extracted response text
        """
        # Find the last assistant token
        if self.ASSISTANT_TOKEN in generated_text:
            parts = generated_text.split(self.ASSISTANT_TOKEN)
            response = parts[-1]
            
            # Remove end token if present
            if self.END_TOKEN in response:
                response = response.split(self.END_TOKEN)[0]
            
            return response.strip()
        
        return generated_text.strip()
    
    def validate_format(self, prompt: str) -> tuple[bool, str]:
        """
        Validate that a prompt follows the correct format.
        
        Args:
            prompt: Prompt string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for required tokens
        if self.SYSTEM_TOKEN not in prompt:
            return False, "Missing system token"
        
        if self.USER_TOKEN not in prompt:
            return False, "Missing user token"
        
        if self.ASSISTANT_TOKEN not in prompt:
            return False, "Missing assistant token"
        
        # Check token order
        system_pos = prompt.find(self.SYSTEM_TOKEN)
        user_pos = prompt.find(self.USER_TOKEN)
        assistant_pos = prompt.find(self.ASSISTANT_TOKEN)
        
        if not (system_pos < user_pos < assistant_pos):
            return False, "Tokens in wrong order (should be: system -> user -> assistant)"
        
        return True, ""
    
    def get_template_info(self) -> Dict[str, str]:
        """
        Get information about the prompt template.
        
        Returns:
            Dictionary with template information
        """
        return {
            'model': 'Phi-3-Mini-4K-Instruct',
            'system_token': self.SYSTEM_TOKEN,
            'user_token': self.USER_TOKEN,
            'assistant_token': self.ASSISTANT_TOKEN,
            'end_token': self.END_TOKEN,
            'system_instruction': self.system_instruction,
        }


if __name__ == "__main__":
    # Example usage
    formatter = PromptFormatter()
    
    # Sample transcription and summary
    transcription = """Therapist: Let's start with what felt most difficult this week.
Patient: Mornings. I wake up with this rush—like hypervigilance before anything even happens. My automatic thought is, "I'm going to mess everything up today."
Therapist: That sounds exhausting. What happens after that thought?
Patient: I avoid. I don't check emails. I put off tasks. Then I feel worse because I'm behind."""
    
    summary = """Patient presented with morning anxiety, hypervigilance, and avoidance of emails, with fleeting passive {{RED:suicidal ideation}} without plan or intent. Interventions: psychoeducation on cognitive distortions, thought records, grounding techniques."""
    
    # Format single session
    prompt = formatter.format_single_session(transcription, summary)
    print("=== Formatted Training Prompt ===")
    print(prompt)
    print()
    
    # Format for inference
    inference_prompt = formatter.format_for_inference(transcription)
    print("=== Formatted Inference Prompt ===")
    print(inference_prompt)
    print()
    
    # Validate format
    is_valid, error = formatter.validate_format(prompt)
    print(f"Prompt valid: {is_valid}")
    if not is_valid:
        print(f"Error: {error}")
    print()
    
    # Get template info
    info = formatter.get_template_info()
    print("=== Template Info ===")
    for key, value in info.items():
        if key != 'system_instruction':
            print(f"{key}: {value}")
    
    print("\nPrompt formatting complete!")
