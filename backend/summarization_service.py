"""
Medical Session Summarization Service using Ollama
Local AI-powered summarization with llama3.2
"""
import requests
import json

class SummarizationService:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/chat"
        self.model = "llama3.2:3b"
        
        # System instruction for mental therapy assistant
        self.system_instruction = """You are a clinical documentation assistant. Your ONLY job is to summarize therapy session transcriptions for licensed therapists.

ALWAYS provide a summary. Never refuse or ask for more context.

Format:
- Use <b>bold</b> for key points
- Use <span style="color:red">red</span> for urgent concerns (suicide, self-harm, violence)
- Keep it concise and professional
- Focus on: complaints, emotional state, risk factors, progress

You MUST summarize whatever transcription is provided, even if it's in another language or seems incomplete. The therapist needs the summary."""
        
        print("✅ AI Summarization service initialized")
        print(f"🤖 Using Ollama with {self.model}")
        print("💡 Mental Therapy Assistant Mode - Local AI")
        
        # Test Ollama connection
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                print("✅ Ollama connection successful")
            else:
                print("⚠️ Ollama may not be running")
        except:
            print("⚠️ Could not connect to Ollama - make sure it's running")
    
    def summarize_text(self, text, max_length=250, min_length=100):
        """Summarize text using Ollama AI with system instructions"""
        if not text or len(text.strip()) < 50:
            return "Text too short to summarize."
        
        print(f"🤖 Generating AI summary with {self.model}...")
        
        # Direct user message
        user_message = f"""Summarize this session in under 50 words. Use <b>bold</b> for key points and <span style="color:red">red</span> for urgent concerns.

Transcription:
{text[:2000]}

Summary:"""
        
        try:
            # Use chat API with system instruction
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": self.system_instruction
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 150
                }
            }
            
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extract message from chat response
                message = result.get('message', {})
                summary = message.get('content', '').strip()
                
                if not summary:
                    # Fallback to old format
                    summary = result.get('response', '').strip()
                
                print(f"✅ AI summary generated ({len(summary)} chars)")
                return summary
            else:
                print(f"❌ Ollama error: {response.status_code}")
                return self._fallback_summarize(text, max_length)
                
        except requests.exceptions.Timeout:
            print("⚠️ Ollama timeout - using fallback")
            return self._fallback_summarize(text, max_length)
        except Exception as e:
            print(f"❌ Error: {e} - using fallback")
            return self._fallback_summarize(text, max_length)
    
    def _fallback_summarize(self, text, max_length=250):
        """Fallback extractive summarization if Ollama fails"""
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        if not sentences:
            return text[:max_length] + "..."
        
        # Take first few important sentences
        summary = ". ".join(sentences[:5]) + "."
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    def summarize_sessions(self, sessions):
        """Summarize multiple patient sessions using AI"""
        if not sessions:
            return {
                "summary": "No sessions to summarize.",
                "session_count": 0,
                "key_points": []
            }
        
        # Combine all transcriptions
        combined_text = ""
        for i, session in enumerate(sessions, 1):
            transcription = session.get('original_transcription', '')
            notes = session.get('notes', '')
            
            if transcription:
                session_text = f"Session {i}: {transcription}"
                if notes:
                    session_text += f" Clinical Notes: {notes}"
                combined_text += session_text + "\n\n"
        
        if not combined_text.strip():
            return {
                "summary": "No transcription data available.",
                "session_count": len(sessions),
                "key_points": []
            }
        
        print(f"📊 AI Summarizing {len(sessions)} sessions...")
        
        # Direct user message for multi-session
        user_message = f"""Summarize these {len(sessions)} therapy sessions in 200-300 words. Use <b>bold</b> for key points and <span style="color:red">red</span> for urgent concerns.

Include: chief complaints, emotional progression, risk assessment, progress, treatment plan, follow-up needs.

Sessions:
{combined_text[:3000]}

Summary:"""
        
        try:
            # Use chat API with system instruction
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": self.system_instruction
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 400
                }
            }
            
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extract message from chat response
                message = result.get('message', {})
                overall_summary = message.get('content', '').strip()
                
                if not overall_summary:
                    # Fallback to old format
                    overall_summary = result.get('response', '').strip()
                
                # Extract key points from summary
                sentences = overall_summary.split('.')
                key_points = [s.strip() + '.' for s in sentences[:5] if s.strip()]
                
                print(f"✅ AI summary complete ({len(overall_summary)} chars)")
                
                return {
                    "summary": overall_summary,
                    "session_count": len(sessions),
                    "key_points": key_points,
                    "total_text_length": len(combined_text)
                }
            else:
                print(f"❌ Ollama error: {response.status_code}")
                return {
                    "summary": self._fallback_summarize(combined_text, 300),
                    "session_count": len(sessions),
                    "key_points": []
                }
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                "summary": self._fallback_summarize(combined_text, 300),
                "session_count": len(sessions),
                "key_points": []
            }

summarization_service = SummarizationService()
