"""
Medical Session Summarization Service using Google Gemini API
"""
import os
import google.generativeai as genai

class SummarizationService:
    def __init__(self):
        self.api_key = 'AIzaSyBtuKJvuQNANjdlMKluFVS0PmP9x2MsDyc'
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        print("✅ Gemini API initialized")
        print("🤖 Using gemini-2.5-flash")
        
        self.system_instruction = """You are a therapy session summarizer.

Create concise summaries using this format:
**Chief Complaint:** [main issue]
**Emotional State:** [mood]
**Risk:** [safety concerns - use {{RED:text}} for urgent]
**Intervention:** [what was done]
**Plan:** [next steps]

Highlight urgent keywords with {{RED:keyword}}:
- suicide, self-harm, kill, hurt myself
- violence, abuse, overdose

Keep under 50 words."""

    def summarize_text(self, text, max_length=250, min_length=100):
        if not text or len(text.strip()) < 50:
            return "Text too short."
        
        print(f"🤖 Generating summary...")
        
        try:
            prompt = f"{self.system_instruction}\n\nSummarize:\n{text[:2000]}\n\nSummary:"
            response = self.model.generate_content(prompt)
            summary = response.text.strip()
            
            if summary:
                print(f"✅ Summary generated ({len(summary)} chars)")
                return summary
            else:
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
        
        combined = ""
        for i, s in enumerate(sessions, 1):
            trans = s.get('original_transcription', '')
            notes = s.get('notes', '')
            if trans:
                combined += f"Session {i}: {trans}"
                if notes:
                    combined += f" Notes: {notes}"
                combined += "\n\n"
        
        if not combined.strip():
            return {"summary": "No data.", "session_count": len(sessions), "key_points": []}
        
        print(f"📊 Summarizing {len(sessions)} sessions...")
        
        try:
            prompt = f"{self.system_instruction}\n\nSummarize these {len(sessions)} sessions (200-300 words):\n\n{combined[:3000]}\n\nSummary:"
            response = self.model.generate_content(prompt)
            summary = response.text.strip()
            
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
            else:
                return {"summary": self._fallback(combined, 300), "session_count": len(sessions), "key_points": []}
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"summary": self._fallback(combined, 300), "session_count": len(sessions), "key_points": []}

summarization_service = SummarizationService()
