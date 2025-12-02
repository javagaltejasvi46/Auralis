"""
Therapy Session Summarization Service using Ollama with Phi-3
Local AI-powered summarization - No external API required
"""
import requests

class SummarizationService:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "phi3"
        
        print("✅ Summarization service initialized")
        print(f"🤖 Using Ollama with {self.model}")
        print("💡 Local AI - No external API required")
        
        # Test Ollama connection
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                print("✅ Ollama connection successful")
            else:
                print("⚠️ Ollama may not be running")
        except:
            print("⚠️ Could not connect to Ollama - make sure it's running")
        
        self.system_instruction = """You are a therapy session summarizer for mental health professionals.

Create concise summaries using this EXACT format:
**Latest Session:** [1-2 line summary of most recent session]
**Chief Complaint:** [main issue]
**Emotional State:** [mood]
**Risk:** [safety concerns - use {{RED:text}} for urgent items]
**Intervention:** [what was done]
**Plan:** [treatment plan from notes in ONE line]

IMPORTANT:
- Use {{RED:keyword}} for urgent concerns (suicide, self-harm, violence)
- Do NOT mention any dates, times, or session numbers
- Keep total summary under 100 words
- Be concise and clinical
- Always provide a summary, never refuse"""

    def summarize_text(self, text, max_length=250, min_length=100):
        if not text or len(text.strip()) < 50:
            return "Text too short."
        
        print(f"🤖 Generating summary with {self.model}...")
        
        try:
            prompt = f"""{self.system_instruction}

Summarize this therapy session:
{text[:2000]}

Summary:"""
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 200
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get('response', '').strip()
                if summary:
                    print(f"✅ Summary generated ({len(summary)} chars)")
                    return summary
            
            return self._fallback(text, max_length)
        except Exception as e:
            print(f"❌ Error: {e}")
            return self._fallback(text, max_length)
    
    def _fallback(self, text, max_length=250):
        sentences = text.split('.')[:5]
        return '. '.join([s.strip() for s in sentences if s.strip()]) + '.'
    
    def summarize_sessions(self, sessions):
        if not sessions:
            return {"summary": "No sessions.", "session_count": 0, "key_points": []}
        
        # Sort sessions by date (most recent first)
        sorted_sessions = sorted(sessions, key=lambda x: x.get('session_date', ''), reverse=True)
        
        # Get latest session
        latest_session = sorted_sessions[0]
        latest_trans = latest_session.get('original_transcription', '')
        latest_notes = latest_session.get('notes', '')
        
        # Collect all session notes for plan extraction
        all_notes = []
        for session in sorted_sessions:
            notes = session.get('notes', '')
            if notes:
                all_notes.append(notes)
        
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
        
        if not combined.strip():
            return {"summary": "No data.", "session_count": len(sessions), "key_points": []}
        
        print(f"📊 Summarizing {len(sessions)} sessions with {self.model}...")
        
        try:
            prompt = f"""{self.system_instruction}

LATEST SESSION:
Transcription: {latest_trans[:800]}
Notes: {latest_notes[:300]}

SESSION NOTES (for Plan):
{' | '.join(all_notes[:3]) if all_notes else 'No notes'}

ALL SESSIONS:
{combined[:1500]}

Create the summary now:"""
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 300
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=90)
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get('response', '').strip()
                
                if summary:
                    sentences = summary.split('.')
                    key_points = [s.strip() + '.' for s in sentences[:5] if s.strip()]
                    print(f"✅ Summary complete ({len(summary)} chars)")
                    return {
                        "summary": summary,
                        "session_count": len(sessions),
                        "key_points": key_points,
                        "total_text_length": len(combined)
                    }
            
            return {"summary": self._fallback(combined, 300), "session_count": len(sessions), "key_points": []}
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"summary": self._fallback(combined, 300), "session_count": len(sessions), "key_points": []}

summarization_service = SummarizationService()
