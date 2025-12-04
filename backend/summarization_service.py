"""
Therapy Session Summarization Service using Ollama with Phi-3
Local AI-powered summarization - No external API required
Follows psychotherapy report template format
"""
import requests
from datetime import datetime

class SummarizationService:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "phi3:mini"  # Use the correct model name with tag
        
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

Create comprehensive summaries using this format:
**Latest Session:** [detailed summary of most recent session including key discussion points]
**Chief Complaint:** [main issue with context]
**Emotional State:** [mood and emotional observations]
**Risk:** [safety concerns - use {{RED:text}} for urgent items]
**Intervention:** [therapeutic techniques and interventions used]
**Progress:** [observed changes and improvements]
**Plan:** [treatment plan and next steps]

IMPORTANT:
- Use {{RED:keyword}} for urgent concerns (suicide, self-harm, violence)
- Provide detailed and comprehensive summaries
- Include all relevant clinical information
- Be thorough and clinical
- Always provide a complete summary, never refuse"""

        self.session_template_instruction = """You are a therapy session summarizer for mental health professionals.

Create a detailed structured session summary using this format:

SESSION RECORDING FORM
Session #: {session_number} | Date: {session_date}
Topics Discussed: [comprehensive list of all topics covered in the session]
Interventions Used: [all therapeutic techniques and approaches applied]
Client Progress: [detailed observations of progress, changes, and responses]
Homework Assigned: [specific tasks given to client with details, or "None" if not applicable]
Therapist Observations: [thorough clinical observations about client's presentation, behavior, and responses]
Plan for Next Session: [detailed goals and focus areas for upcoming session]

IMPORTANT:
- Provide comprehensive and detailed information for each section
- Use {{RED:keyword}} for urgent concerns (suicide, self-harm, violence)
- Always provide a complete summary, never refuse
- Include all relevant clinical details"""

    def summarize_text(self, text, max_length=1000, min_length=100):
        if not text or len(text.strip()) < 50:
            return "Text too short."
        
        print(f"🤖 Generating summary with {self.model}...")
        
        try:
            prompt = f"""{self.system_instruction}

Summarize this therapy session:
{text}

Summary:"""
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 1000
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

    def generate_session_summary(self, session_data: dict, therapist_name: str = ""):
        """Generate a structured session summary following the template format"""
        session_number = session_data.get('session_number', 1)
        session_date = session_data.get('session_date', datetime.now().isoformat())
        transcription = session_data.get('original_transcription', '')
        notes = session_data.get('notes', '')
        
        if isinstance(session_date, str):
            try:
                session_date = datetime.fromisoformat(session_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')
            except:
                session_date = datetime.now().strftime('%Y-%m-%d')
        
        if not transcription and not notes:
            return self._create_empty_session_summary(session_number, session_date, therapist_name)
        
        print(f"🤖 Generating structured session summary for Session #{session_number}...")
        
        try:
            prompt = f"""{self.session_template_instruction.format(session_number=session_number, session_date=session_date)}

Session Transcription:
{transcription if transcription else 'No transcription available'}

Session Notes:
{notes if notes else 'No notes available'}

Generate the structured session summary now:"""
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 1500
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=90)
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get('response', '').strip()
                if summary:
                    # Append therapist info
                    if therapist_name:
                        summary += f"\n\nTherapist Name: {therapist_name}\nDate: {session_date}"
                    print(f"✅ Session summary generated ({len(summary)} chars)")
                    return {
                        "session_number": session_number,
                        "session_date": session_date,
                        "summary": summary,
                        "therapist_name": therapist_name
                    }
            
            return self._create_empty_session_summary(session_number, session_date, therapist_name)
        except Exception as e:
            print(f"❌ Error generating session summary: {e}")
            return self._create_empty_session_summary(session_number, session_date, therapist_name)

    def _create_empty_session_summary(self, session_number, session_date, therapist_name):
        """Create an empty session summary template"""
        return {
            "session_number": session_number,
            "session_date": session_date,
            "summary": f"""SESSION RECORDING FORM
Session #: {session_number} | Date: {session_date}
Topics Discussed: No data available
Interventions Used: No data available
Client Progress: No data available
Homework Assigned: None
Therapist Observations: No data available
Plan for Next Session: To be determined

Therapist Name: {therapist_name}
Date: {session_date}""",
            "therapist_name": therapist_name
        }
    
    def _fallback(self, text, max_length=2000):
        """Fallback summary when AI is unavailable - returns full text"""
        sentences = text.split('.')
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
Transcription: {latest_trans}
Notes: {latest_notes}

SESSION NOTES (for Plan):
{' | '.join(all_notes) if all_notes else 'No notes'}

ALL SESSIONS:
{combined}

Create a comprehensive summary now:"""
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 2000
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

    def generate_overall_summary(self, patient_data: dict, sessions: list, therapist_name: str = ""):
        """Generate a comprehensive overall summary following the psychotherapy report template with concise answers"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📊 Generating overall summary for patient: {patient_data.get('full_name', 'Unknown')}")
        print(f"📊 Number of sessions: {len(sessions) if sessions else 0}")
        
        # Sort sessions chronologically
        sorted_sessions = sorted(sessions, key=lambda x: x.get('session_date', '')) if sessions else []
        
        # Combine all session data for AI analysis
        combined_transcriptions = ""
        combined_notes = ""
        for i, session in enumerate(sorted_sessions, 1):
            trans = session.get('original_transcription', '')
            notes = session.get('notes', '')
            print(f"  Session {i}: transcription={len(trans) if trans else 0} chars, notes={len(notes) if notes else 0} chars")
            if trans:
                combined_transcriptions += f"Session {i}: {trans}\n\n"
            if notes:
                combined_notes += f"Session {i} Notes: {notes}\n\n"
        
        print(f"📊 Combined data: transcriptions={len(combined_transcriptions)} chars, notes={len(combined_notes)} chars")
        
        # Generate AI-based concise summary fields from sessions
        ai_summary = self._generate_ai_summary_fields(combined_transcriptions, combined_notes)
        print(f"📊 AI Summary result: {ai_summary}")
        
        # Helper function to get value with fallback chain
        def get_value(ai_key, patient_key, default):
            """Get value from AI summary, then patient data, then default"""
            val = ai_summary.get(ai_key)
            if val and val not in ['N/A', 'None', '', None]:
                return val
            val = patient_data.get(patient_key)
            if val and val not in ['N/A', 'None', '', None]:
                return val
            return default
        
        # Generate individual session summaries
        session_summaries = []
        for session in sorted_sessions:
            session_summary = self.generate_session_summary(session, therapist_name)
            session_summaries.append(session_summary)
        
        # Build overall summary with template format
        overall_summary = {
            # Patient Information (from patient data)
            "patient_information": {
                "name": patient_data.get('full_name', 'N/A'),
                "age": str(patient_data.get('age', 'N/A')),
                "gender": patient_data.get('gender', 'N/A'),
                "date_of_birth": patient_data.get('date_of_birth', 'N/A'),
                "residence": patient_data.get('residence', 'N/A'),
                "education": patient_data.get('education', 'N/A'),
                "occupation": patient_data.get('occupation', 'N/A'),
                "marital_status": patient_data.get('marital_status', 'N/A'),
                "date_of_assessment": patient_data.get('date_of_assessment', current_date)
            },
            # Medical History (from patient data)
            "medical_history": {
                "current_medical_conditions": patient_data.get('current_medical_conditions', 'None'),
                "past_medical_conditions": patient_data.get('past_medical_conditions', 'None'),
                "current_medications": patient_data.get('current_medications', 'None'),
                "allergies": patient_data.get('allergies', 'None'),
                "hospitalizations": patient_data.get('hospitalizations', 'None')
            },
            # Psychiatric History (from patient data)
            "psychiatric_history": {
                "previous_diagnoses": patient_data.get('previous_psychiatric_diagnoses', 'None'),
                "previous_treatment": patient_data.get('previous_psychiatric_treatment', 'None'),
                "previous_hospitalizations": patient_data.get('previous_psychiatric_hospitalizations', 'None'),
                "suicide_self_harm_history": patient_data.get('suicide_self_harm_history', 'None'),
                "substance_use_history": patient_data.get('substance_use_history', 'None')
            },
            # Family History (from patient data)
            "family_history": {
                "psychiatric_illness": patient_data.get('psychiatric_illness_family', 'None'),
                "medical_illness": patient_data.get('medical_illness_family', 'None'),
                "family_dynamics": patient_data.get('family_dynamics', 'N/A'),
                "significant_events": patient_data.get('significant_family_events', 'None')
            },
            # Social History (from patient data)
            "social_history": {
                "childhood_developmental": patient_data.get('childhood_developmental_history', 'N/A'),
                "educational": patient_data.get('educational_history', 'N/A'),
                "occupational": patient_data.get('occupational_history', 'N/A'),
                "relationship": patient_data.get('relationship_history', 'N/A'),
                "social_support": patient_data.get('social_support_system', 'N/A'),
                "living_situation": patient_data.get('living_situation', 'N/A'),
                "cultural_religious": patient_data.get('cultural_religious_background', 'N/A')
            },
            # Chief Complaints (AI-generated from sessions, fallback to patient data, then defaults)
            "chief_complaints": {
                "primary": get_value('chief_complaint', 'chief_complaint', 'Under assessment'),
                "description": get_value('chief_complaint_description', 'chief_complaint_description', 'Initial assessment in progress')
            },
            # Course of Illness (AI-generated from sessions)
            "course_of_illness": {
                "onset": get_value('onset', 'illness_onset', 'Gradual'),
                "progression": get_value('progression', 'illness_progression', 'Stable'),
                "previous_episodes": get_value('previous_episodes', 'previous_episodes', 'None reported'),
                "triggers": get_value('triggers', 'triggers', 'Under evaluation'),
                "impact_on_functioning": get_value('impact', 'impact_on_functioning', 'Moderate')
            },
            # Baseline Assessment - MSE (AI-generated from sessions or patient data)
            "baseline_assessment": {
                "appearance": get_value('appearance', 'mse_appearance', 'Appropriate'),
                "behavior": get_value('behavior', 'mse_behavior', 'Cooperative'),
                "speech": get_value('speech', 'mse_speech', 'Normal'),
                "mood": get_value('mood', 'mse_mood', 'Euthymic'),
                "affect": get_value('affect', 'mse_affect', 'Appropriate'),
                "thought_process": get_value('thought_process', 'mse_thought_process', 'Linear'),
                "thought_content": get_value('thought_content', 'mse_thought_content', 'Normal'),
                "perception": get_value('perception', 'mse_perception', 'Intact'),
                "cognition": get_value('cognition', 'mse_cognition', 'Intact'),
                "insight": get_value('insight', 'mse_insight', 'Fair'),
                "judgment": get_value('judgment', 'mse_judgment', 'Fair')
            },
            # Session Summaries
            "session_summaries": session_summaries,
            # Metadata
            "generated_date": current_date,
            "therapist_name": therapist_name,
            "session_count": len(sessions) if sessions else 0
        }
        
        # Debug: Print the clinical fields being returned
        print(f"📊 Final chief_complaints: {overall_summary['chief_complaints']}")
        print(f"📊 Final course_of_illness: {overall_summary['course_of_illness']}")
        print(f"📊 Final baseline_assessment: {overall_summary['baseline_assessment']}")
        
        return overall_summary

    def _generate_ai_summary_fields(self, transcriptions: str, notes: str):
        """Generate concise 1-2 word answers for template fields using AI with JSON output"""
        import json
        
        if not transcriptions and not notes:
            print("⚠️ No transcriptions or notes to analyze")
            return self._get_default_clinical_fields()
        
        print("🤖 Generating clinical assessment fields using AI...")
        print(f"📝 Transcription length: {len(transcriptions)} chars, Notes length: {len(notes)} chars")
        
        # First, try to extract from existing notes if they have the format
        extracted = self._extract_from_formatted_notes(notes)
        if extracted and len(extracted) >= 5:
            print(f"✅ Extracted {len(extracted)} fields from formatted notes")
            defaults = self._get_default_clinical_fields()
            defaults.update(extracted)
            return defaults
        
        try:
            # Use JSON format for more reliable parsing
            prompt = f"""You are a clinical psychologist analyzing therapy session data. Based on the session information below, provide a clinical assessment.

SESSION TRANSCRIPTION:
{transcriptions[:3000] if transcriptions else 'No transcription available'}

SESSION NOTES:
{notes[:2000] if notes else 'No notes available'}

Analyze the above and respond with ONLY a valid JSON object (no other text). Each field should have a 1-3 word clinical answer:

{{"chief_complaint": "main problem in 1-3 words",
"chief_complaint_description": "brief one sentence description",
"onset": "Gradual or Sudden or Childhood or Recent",
"progression": "Worsening or Stable or Improving or Fluctuating",
"previous_episodes": "None or Single or Multiple or Chronic",
"triggers": "main trigger 1-2 words",
"impact": "Mild or Moderate or Severe",
"appearance": "Appropriate or Neat or Disheveled or Unkempt",
"behavior": "Cooperative or Guarded or Agitated or Withdrawn",
"speech": "Normal or Pressured or Slow or Soft",
"mood": "Depressed or Anxious or Euthymic or Irritable",
"affect": "Appropriate or Constricted or Flat or Labile",
"thought_process": "Linear or Tangential or Circumstantial or Disorganized",
"thought_content": "Normal or Preoccupied or Ruminating",
"perception": "Intact or Impaired",
"cognition": "Intact or Impaired",
"insight": "Good or Fair or Poor",
"judgment": "Good or Fair or Poor"}}

Respond with ONLY the JSON object, no explanation:"""
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "num_predict": 800
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '').strip()
                print(f"📄 AI Response:\n{ai_response}")
                
                # Try to parse JSON from response
                summary_fields = self._parse_json_response(ai_response)
                
                if summary_fields:
                    print(f"✅ Parsed {len(summary_fields)} fields from JSON")
                    # Merge with defaults
                    defaults = self._get_default_clinical_fields()
                    defaults.update(summary_fields)
                    print(f"✅ Final clinical assessment: {defaults}")
                    return defaults
                else:
                    print("⚠️ Could not parse JSON, trying line-by-line parsing...")
                    # Fallback to line-by-line parsing
                    return self._parse_line_response(ai_response)
            else:
                print(f"❌ Ollama returned status {response.status_code}")
            
            return self._get_default_clinical_fields()
        except Exception as e:
            print(f"❌ Error generating summary fields: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_clinical_fields()
    
    def _parse_json_response(self, response: str) -> dict:
        """Parse JSON from AI response, handling various formats"""
        import json
        import re
        
        if not response:
            return {}
        
        # Try direct JSON parse first
        try:
            return json.loads(response)
        except:
            pass
        
        # Try to find JSON object in response
        json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        # Try to fix common JSON issues
        try:
            # Remove markdown code blocks
            cleaned = re.sub(r'```json?\s*', '', response)
            cleaned = re.sub(r'```\s*', '', cleaned)
            cleaned = cleaned.strip()
            
            # Find the JSON object
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = cleaned[start:end]
                return json.loads(json_str)
        except:
            pass
        
        return {}
    
    def _parse_line_response(self, response: str) -> dict:
        """Fallback parser for line-by-line format"""
        summary_fields = {}
        
        for line in response.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#') and not line.startswith('*') and not line.startswith('{'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower().replace(' ', '_').replace('-', '_').replace('"', '')
                    key = key.lstrip('0123456789.-) ')
                    value = parts[1].strip().strip('[]",').strip()
                    
                    # Clean up value
                    for prefix in ['the ', 'a ', 'an ']:
                        if value.lower().startswith(prefix):
                            value = value[len(prefix):]
                    value = value.rstrip('.,;')
                    
                    if value and len(value) > 0 and value.lower() not in ['n/a', 'not specified', 'unknown', '']:
                        summary_fields[key] = value.capitalize() if len(value) < 50 else value
        
        # Merge with defaults
        defaults = self._get_default_clinical_fields()
        defaults.update(summary_fields)
        return defaults
    
    def _get_default_clinical_fields(self):
        """Return default clinical field values"""
        return {
            'chief_complaint': 'Under assessment',
            'chief_complaint_description': 'Initial assessment in progress',
            'onset': 'Gradual',
            'progression': 'Stable',
            'previous_episodes': 'None reported',
            'triggers': 'Under evaluation',
            'impact': 'Moderate',
            'appearance': 'Appropriate',
            'behavior': 'Cooperative',
            'speech': 'Normal',
            'mood': 'Euthymic',
            'affect': 'Appropriate',
            'thought_process': 'Linear',
            'thought_content': 'Normal',
            'perception': 'Intact',
            'cognition': 'Intact',
            'insight': 'Fair',
            'judgment': 'Fair'
        }

    def _extract_from_formatted_notes(self, notes: str) -> dict:
        """Extract clinical fields from already formatted session notes"""
        import re
        extracted = {}
        
        if not notes:
            return extracted
        
        # Look for patterns like **Chief Complaint:** text or "Chief Complaint:" text
        patterns = {
            'chief_complaint': [
                r'\*\*Chief Complaint[s]?:\*\*\s*([^\n*]+)', 
                r'Chief Complaint[s]?:\s*([^\n]+)',
                r'\*\*Primary Complaint:\*\*\s*([^\n*]+)'
            ],
            'chief_complaint_description': [
                r'\*\*Description:\*\*\s*([^\n*]+)',
                r'Description:\s*([^\n]+)'
            ],
            'mood': [
                r'\*\*(?:Mood|Emotional State):\*\*\s*([^\n*]+)', 
                r'(?:Mood|Emotional State):\s*([^\n]+)',
                r'mood[:\s]+([a-zA-Z]+)'
            ],
            'affect': [r'\*\*Affect:\*\*\s*([^\n*]+)', r'Affect:\s*([^\n]+)'],
            'appearance': [r'\*\*Appearance:\*\*\s*([^\n*]+)', r'Appearance:\s*([^\n]+)'],
            'behavior': [r'\*\*Behavior:\*\*\s*([^\n*]+)', r'Behavior:\s*([^\n]+)'],
            'speech': [r'\*\*Speech:\*\*\s*([^\n*]+)', r'Speech:\s*([^\n]+)'],
            'thought_process': [r'\*\*Thought Process:\*\*\s*([^\n*]+)', r'Thought Process:\s*([^\n]+)'],
            'thought_content': [r'\*\*Thought Content:\*\*\s*([^\n*]+)', r'Thought Content:\s*([^\n]+)'],
            'insight': [r'\*\*Insight:\*\*\s*([^\n*]+)', r'Insight:\s*([^\n]+)'],
            'judgment': [r'\*\*Judgment:\*\*\s*([^\n*]+)', r'Judgment:\s*([^\n]+)'],
            'perception': [r'\*\*Perception:\*\*\s*([^\n*]+)', r'Perception:\s*([^\n]+)'],
            'cognition': [r'\*\*Cognition:\*\*\s*([^\n*]+)', r'Cognition:\s*([^\n]+)'],
            'onset': [r'\*\*Onset:\*\*\s*([^\n*]+)', r'Onset:\s*([^\n]+)'],
            'progression': [
                r'\*\*Progression:\*\*\s*([^\n*]+)', 
                r'Progression:\s*([^\n]+)',
                r'\*\*Progress:\*\*\s*([^\n*]+)'
            ],
            'triggers': [r'\*\*Triggers?:\*\*\s*([^\n*]+)', r'Triggers?:\s*([^\n]+)'],
            'impact': [
                r'\*\*Impact[^:]*:\*\*\s*([^\n*]+)', 
                r'Impact[^:]*:\s*([^\n]+)',
                r'\*\*Risk:\*\*\s*([^\n*]+)'
            ],
        }
        
        for field, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, notes, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    # Get first few words as concise answer (more for descriptions)
                    max_words = 15 if 'description' in field else 5
                    words = value.split()[:max_words]
                    concise_value = ' '.join(words)
                    if concise_value and concise_value.lower() not in ['n/a', 'none', 'not specified', 'not assessed']:
                        extracted[field] = concise_value
                    break
        
        print(f"📋 Extracted from notes: {extracted}")
        return extracted

    def _create_empty_overall_summary(self, patient_data: dict, therapist_name: str):
        """Create an empty overall summary template"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        return {
            "patient": patient_data,
            "chief_complaints": {"primary": "Not specified", "description": "Not specified"},
            "course_of_illness": {
                "onset": "Not specified",
                "progression": "Not specified",
                "previous_episodes": "Not specified",
                "triggers": "Not specified",
                "impact_on_functioning": "Not specified"
            },
            "baseline_assessment": {
                "appearance": "Not assessed",
                "behavior": "Not assessed",
                "speech": "Not assessed",
                "mood": "Not assessed",
                "affect": "Not assessed",
                "thought_process": "Not assessed",
                "thought_content": "Not assessed",
                "perception": "Not assessed",
                "cognition": "Not assessed",
                "insight": "Not assessed",
                "judgment": "Not assessed"
            },
            "session_summaries": [],
            "generated_date": current_date,
            "therapist_name": therapist_name,
            "session_count": 0
        }

summarization_service = SummarizationService()
