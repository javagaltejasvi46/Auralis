import os
import google.generativeai as genai

class SummarizationService:
    def __init__(self):
        self.api_key = 'AIzaSyB-MT1GiGSE_piSwBt864kPVkX1dOk54YI'
        
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
-> keep it concise and humanly format with less words
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
        
        print(f"📊 Summarizing {len(sessions)} sessions with latest session focus...")
        
        try:
            # Enhanced prompt with latest session and plan extraction
            prompt = f"""Create a professional therapy summary with these sections:

**Latest Session:** (Summarize the most recent session in 1-2 lines)

**Chief Complaint:** (main issues across all sessions)

**Emotional State:** (patient's mood and affect)

**Risk Assessment:** (use {{{{RED:text}}}} for urgent concerns like suicide, self-harm, violence)

**Intervention:** (therapeutic techniques used)

**Plan:** (Extract the treatment plan from session notes and summarize in ONE line)

LATEST SESSION:
Transcription: {latest_trans[:1000]}
Notes: {latest_notes[:500]}

ALL SESSION NOTES (for Plan):
{' | '.join(all_notes[:3]) if all_notes else 'No notes available'}

ALL SESSIONS DATA:
{combined[:2000]}

dont cross the words limit: 50 including all headings

Create the summary:"""
            
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