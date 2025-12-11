"""
Summarization Service using Phi-3-Mini Local Model
Replaces Google Gemini API with local inference via Ollama
"""
import os
import logging
from typing import List, Dict, Any, Optional
import re

# Try Ollama first, fallback to llama-cpp
try:
    from ollama_inference_engine import OllamaInferenceEngine, OllamaConfig
    USE_OLLAMA = True
except ImportError:
    from llama_inference_engine import LlamaInferenceEngine, InferenceConfig
    USE_OLLAMA = False


class PromptFormatter:
    """Format prompts for Phi-3-Mini"""
    
    @staticmethod
    def format_single_session(transcription: str, notes: str = "") -> str:
        """Format prompt for single session summarization"""
        system_instruction = """You are a therapy session summarizer. Create comprehensive clinical summaries using this format:
**Chief Complaint:** [detailed main issue with context]
**Emotional State:** [mood and emotional observations]
**Risk:** [safety concerns - use {{RED:text}} for urgent items]
**Intervention:** [therapeutic techniques and interventions used]
**Progress:** [observed changes and client responses]
**Plan:** [detailed next steps and treatment plan]

Highlight urgent keywords with {{RED:keyword}}: suicide, self-harm, kill, hurt myself, violence, abuse, overdose

IMPORTANT: Provide detailed and comprehensive summaries. Include all relevant clinical information."""
        
        prompt = f"""<|system|>
{system_instruction}<|end|>
<|user|>
Summarize the following therapy session:

{transcription}<|end|>
<|assistant|>
"""
        return prompt
    
    @staticmethod
    def format_multiple_sessions(sessions: List[Dict]) -> str:
        """Format prompt for multiple session summarization"""
        system_instruction = """You are a therapy session summarizer. Create a comprehensive professional therapy summary with these sections:

**Latest Session:** (Detailed summary of the most recent session)
**Chief Complaint:** (comprehensive main issues across all sessions)
**Emotional State:** (detailed patient's mood, affect, and emotional patterns)
**Risk Assessment:** (use {{RED:text}} for urgent concerns like suicide, self-harm, violence)
**Intervention:** (all therapeutic techniques and approaches used)
**Progress:** (observed changes and improvements over sessions)
**Plan:** (detailed treatment plan and next steps)

IMPORTANT: Provide comprehensive and detailed summaries. Include all relevant clinical information."""
        
        # Sort sessions by date
        sorted_sessions = sorted(sessions, key=lambda x: x.get('session_date', ''), reverse=True)
        
        # Get latest session
        latest_session = sorted_sessions[0] if sorted_sessions else {}
        latest_trans = latest_session.get('original_transcription', '')
        latest_notes = latest_session.get('notes', '')
        
        # Collect all notes
        all_notes = [s.get('notes', '') for s in sorted_sessions if s.get('notes', '')]
        notes_summary = ' | '.join(all_notes)
        
        # Build combined text
        combined = ""
        for i, s in enumerate(sorted_sessions, 1):
            trans = s.get('original_transcription', '')
            notes = s.get('notes', '')
            if trans:
                combined += f"Session {i}: {trans}"
                if notes:
                    combined += f" | Notes: {notes}"
                combined += "\n\n"
        
        prompt = f"""<|system|>
{system_instruction}<|end|>
<|user|>
LATEST SESSION:
Transcription: {latest_trans}
Notes: {latest_notes}

ALL SESSION NOTES (for Plan):
{notes_summary if notes_summary else 'No notes available'}

ALL SESSIONS DATA:
{combined}

Create a comprehensive summary:<|end|>
<|assistant|>
"""
        return prompt


class SummarizationService:
    """Summarization service using local Phi-3-Mini model via Ollama"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        if USE_OLLAMA:
            # Use Ollama (recommended)
            model_name = model_name or os.getenv('OLLAMA_MODEL', 'phi3:mini')
            
            self.config = OllamaConfig(
                base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
                model_name=model_name,
                max_tokens=2000,
                temperature=0.7,
                timeout=180
            )
            
            self.engine = OllamaInferenceEngine(self.config)
            
            try:
                self.engine.load_model()
                print("✅ Phi-3-Mini model initialized via Ollama")
                print(f"🤖 Using model: {model_name}")
            except Exception as e:
                self.logger.error(f"❌ Failed to load Ollama model: {e}")
                print(f"❌ Ollama model loading failed: {e}")
                print(f"💡 Make sure Ollama is running and model is pulled:")
                print(f"   ollama pull {model_name}")
                raise
        else:
            # Fallback to llama-cpp (GGUF)
            model_path = model_name or os.getenv('PHI3_MODEL_PATH', 'models/phi3-therapy-q4_k_m.gguf')
            
            self.config = InferenceConfig(
                model_path=model_path,
                n_ctx=int(os.getenv('PHI3_N_CTX', '4096')),
                n_threads=int(os.getenv('PHI3_N_THREADS', '4')),
                n_gpu_layers=int(os.getenv('PHI3_N_GPU_LAYERS', '0')),
                max_tokens=2000,
                temperature=0.7,
                timeout=180
            )
            
            self.engine = LlamaInferenceEngine(self.config)
            
            try:
                self.engine.load_model()
                print("✅ Phi-3-Mini model initialized via llama-cpp")
                print(f"🤖 Using model: {os.path.basename(model_path)}")
            except Exception as e:
                self.logger.error(f"❌ Failed to load model: {e}")
                print(f"❌ Model loading failed: {e}")
                raise
        
        self.formatter = PromptFormatter()
        
        # Statistics
        self.total_inferences = 0
        self.successful_inferences = 0
        self.fallback_count = 0
        self.total_inference_time = 0.0
    
    def summarize_text(self, text: str, max_length: int = 250, min_length: int = 100) -> str:
        """Summarize text using local model"""
        if not text or len(text.strip()) < 50:
            return "Text too short."
        
        print(f"🤖 Generating summary...")
        self.total_inferences += 1
        
        try:
            # Format prompt
            prompt = self.formatter.format_single_session(text)
            
            # Generate summary
            import time
            start_time = time.time()
            summary = self.engine.generate(prompt, max_tokens=2000)
            inference_time = time.time() - start_time
            
            self.total_inference_time += inference_time
            
            # Parse output
            summary = self._parse_summary(summary)
            
            if summary and len(summary.strip()) > 20:
                self.successful_inferences += 1
                print(f"✅ Summary generated ({len(summary)} chars, {inference_time:.2f}s)")
                return summary
            else:
                return self._fallback(text, max_length)
                
        except TimeoutError:
            self.logger.warning("⏱️  Inference timeout, using fallback")
            self.fallback_count += 1
            return self._fallback(text, max_length)
        except Exception as e:
            self.logger.error(f"❌ Inference error: {e}")
            self.fallback_count += 1
            return self._fallback(text, max_length)
    
    def summarize_single_session(self, transcription: str, notes: str = "") -> str:
        """Generate clinical notes for a single session"""
        if not transcription or len(transcription.strip()) < 50:
            return "Transcription too short for summarization."
        
        print(f"🤖 Generating session notes...")
        self.total_inferences += 1
        
        try:
            # Format prompt
            prompt = self.formatter.format_single_session(transcription, notes)
            
            # Generate
            import time
            start_time = time.time()
            summary = self.engine.generate_with_timeout(prompt, timeout=180, max_tokens=2000)
            inference_time = time.time() - start_time
            
            self.total_inference_time += inference_time
            
            # Parse
            summary = self._parse_summary(summary)
            
            if summary and len(summary.strip()) > 20:
                self.successful_inferences += 1
                print(f"✅ Session notes generated ({len(summary)} chars, {inference_time:.2f}s)")
                return summary
            else:
                return self._fallback(transcription, 250)
                
        except TimeoutError:
            self.logger.warning("⏱️  Session note generation timeout (180s)")
            self.fallback_count += 1
            return self._fallback(transcription, 250)
        except Exception as e:
            self.logger.error(f"❌ Session note generation error: {e}")
            self.fallback_count += 1
            return self._fallback(transcription, 250)
    
    def summarize_sessions(self, sessions: List[Dict]) -> Dict[str, Any]:
        """Summarize multiple sessions"""
        if not sessions:
            return {"summary": "No sessions.", "session_count": 0, "key_points": []}
        
        print(f"📊 Summarizing {len(sessions)} sessions...")
        self.total_inferences += 1
        
        try:
            # Format prompt
            prompt = self.formatter.format_multiple_sessions(sessions)
            
            # Generate
            import time
            start_time = time.time()
            summary = self.engine.generate_with_timeout(prompt, timeout=180, max_tokens=2000)
            inference_time = time.time() - start_time
            
            self.total_inference_time += inference_time
            
            # Parse
            summary = self._parse_summary(summary)
            
            if summary and len(summary.strip()) > 20:
                self.successful_inferences += 1
                
                # Extract key points
                sentences = summary.split('.')
                key_points = [s.strip() + '.' for s in sentences[:5] if s.strip()]
                
                print(f"✅ Summary complete ({len(summary)} chars, {inference_time:.2f}s)")
                
                return {
                    "summary": summary,
                    "session_count": len(sessions),
                    "key_points": key_points,
                    "inference_time": round(inference_time, 2)
                }
            else:
                # Fallback
                combined = self._build_combined_text(sessions)
                return {
                    "summary": self._fallback(combined, 300),
                    "session_count": len(sessions),
                    "key_points": []
                }
                
        except TimeoutError:
            self.logger.warning("⏱️  Multi-session summarization timeout (180s)")
            self.fallback_count += 1
            combined = self._build_combined_text(sessions)
            return {
                "summary": self._fallback(combined, 300),
                "session_count": len(sessions),
                "key_points": []
            }
        except Exception as e:
            self.logger.error(f"❌ Multi-session summarization error: {e}")
            self.fallback_count += 1
            combined = self._build_combined_text(sessions)
            return {
                "summary": self._fallback(combined, 300),
                "session_count": len(sessions),
                "key_points": []
            }
    
    def auto_generate_session_notes(self, session_id: int, transcription: str) -> str:
        """Auto-generate notes for a session (alias for summarize_single_session)"""
        return self.summarize_single_session(transcription)
    
    def _parse_summary(self, raw_output: str) -> str:
        """Parse and clean model output"""
        # Remove any remaining special tokens
        output = raw_output.replace('<|end|>', '').replace('<|endoftext|>', '')
        
        # Clean up whitespace
        output = re.sub(r'\s+', ' ', output).strip()
        
        # Normalize RED marker formats to {{RED:text}} format
        # Handle {{RED}}text{{/REDC}} or {{RED}}text{{/RED}} format
        output = re.sub(r'\{\{RED\}\}([^{]*)\{\{/REDC?\}\}', r'{{RED:\1}}', output, flags=re.IGNORECASE)
        
        # Handle {{red:text}} - normalize case
        output = re.sub(r'\{\{red:', '{{RED:', output, flags=re.IGNORECASE)
        
        # Handle any remaining malformed RED tags
        output = re.sub(r'\{\{/REDC?\}\}', '', output, flags=re.IGNORECASE)
        
        # Validate sections (basic check)
        if '**Chief Complaint:**' in output or '**Emotional State:**' in output:
            return output
        
        # If no proper formatting, return as-is
        return output
    
    def _fallback(self, text: str, max_length: int = 5000) -> str:
        """Fallback summary when model fails - returns full text"""
        self.fallback_count += 1
        sentences = text.split('.')
        fallback = '. '.join([s.strip() for s in sentences if s.strip()]) + '.'
        
        self.logger.info(f"⚠️  Using fallback summary")
        return fallback
    
    def _build_combined_text(self, sessions: List[Dict]) -> str:
        """Build combined text from sessions"""
        combined = ""
        for i, s in enumerate(sessions, 1):
            trans = s.get('original_transcription', '')
            notes = s.get('notes', '')
            if trans:
                combined += f"Session {i}: {trans}"
                if notes:
                    combined += f" | Notes: {notes}"
                combined += "\n\n"
        return combined
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get inference statistics"""
        success_rate = (self.successful_inferences / self.total_inferences * 100) if self.total_inferences > 0 else 0
        avg_time = (self.total_inference_time / self.successful_inferences) if self.successful_inferences > 0 else 0
        
        return {
            "total_inferences": self.total_inferences,
            "successful_inferences": self.successful_inferences,
            "fallback_count": self.fallback_count,
            "success_rate": round(success_rate, 2),
            "avg_inference_time": round(avg_time, 2),
            "model_info": self.engine.get_model_info()
        }


# Initialize service
try:
    summarization_service = SummarizationService()
except Exception as e:
    print(f"⚠️  Failed to initialize summarization service: {e}")
    print(f"⚠️  Service will not be available")
    summarization_service = None


if __name__ == "__main__":
    # Test service
    if summarization_service:
        test_text = "Patient reports feeling depressed for the past two weeks. Mentions thoughts of suicide. Discussed coping strategies and safety planning."
        
        summary = summarization_service.summarize_text(test_text)
        print(f"\n📝 Summary:\n{summary}")
        
        stats = summarization_service.get_statistics()
        print(f"\n📊 Statistics:\n{stats}")
