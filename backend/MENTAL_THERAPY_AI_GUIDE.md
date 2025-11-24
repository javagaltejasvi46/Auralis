# Mental Therapy AI Assistant - Configuration Guide

## Overview
The summarization service is now configured as a **Mental Therapy Assistant** using Ollama with llama3.2:3b model.

## System Instructions

The AI is configured with the following role:
- **Primary Role**: AI assistant for mental health therapists
- **Purpose**: Create concise, professional summaries of therapy session transcriptions
- **Mode**: Mental Therapy Assistant (not a therapist itself)

## Key Features

### 1. Clinical Summarization
- Summarizes therapy sessions in clear, clinical language
- Uses professional mental health terminology
- Maintains patient confidentiality

### 2. Risk Assessment
- Identifies and highlights critical mental health concerns
- Flags urgent safety concerns automatically
- Sensitive keywords monitored:
  - "suicide"
  - "self-harm"
  - "kill"
  - "end my life"
  - "hurt myself"
  - "no reason to live"

### 3. Therapeutic Insights
- Notes patient's emotional state and behavioral patterns
- Extracts key therapeutic insights
- Tracks progress indicators across sessions

### 4. HTML Formatting
- **Bold text** (`<b>`) for important points
- **Red text** (`<span style="color:red">`) for urgent safety concerns
- Structured, readable output

## Summary Guidelines

### Single Session Summary (Under 50 words)
Focuses on:
- Chief complaints and emotional state
- Risk assessment
- Key therapeutic insights
- Progress indicators

### Multi-Session Summary (200-300 words)
Includes:
1. **Chief Complaints**: Main issues across all sessions
2. **Emotional Progression**: Changes in patient's mental state
3. **Risk Assessment**: Any safety concerns (highlighted in red)
4. **Therapeutic Progress**: Improvements or setbacks
5. **Treatment Plan**: Interventions used and recommendations
6. **Follow-up Needs**: Suggested next steps

## Technical Configuration

### Model Settings
- **Model**: llama3.2:3b (local)
- **Temperature**: 0.3 (focused, consistent responses)
- **Top P**: 0.9 (balanced creativity)
- **Max Tokens**: 150 (single), 400 (multi-session)

### API Endpoint
- **URL**: http://localhost:11434/api/chat
- **Format**: Chat API with system instructions
- **Timeout**: 60s (single), 90s (multi-session)

## Usage

### From Mobile App
1. Navigate to Patient Profile
2. Click "Summarize" button
3. AI generates summary with:
   - Clinical observations
   - Risk flags (if any)
   - Therapeutic insights
   - HTML formatting

### Example Output
```html
<b>Chief Complaint:</b> Patient reports persistent anxiety and sleep disturbances. 
<b>Emotional State:</b> Appears distressed but engaged in session. 
<b>Risk Assessment:</b> <span style="color:red">Patient mentioned thoughts of self-harm</span> - requires immediate follow-up. 
<b>Progress:</b> Showing improvement in coping strategies. 
<b>Plan:</b> Continue CBT, schedule safety planning session.
```

## Safety Features

### Automatic Risk Flagging
- Scans for suicide/self-harm indicators
- Highlights in red for immediate attention
- Maintains clinical documentation standards

### Fallback Protection
- If Ollama fails, uses extractive summarization
- Ensures summaries are always generated
- No data loss

## Future Enhancements

### Potential Improvements
1. **Fine-tuning**: Train model on mental health datasets
2. **Layer Optimization**: Remove/adjust layers for better performance
3. **Custom Prompts**: Therapist-specific summary templates
4. **Risk Scoring**: Quantitative risk assessment
5. **Progress Tracking**: Longitudinal analysis across sessions

## Model Training (If Needed)

If the current model needs improvement:

### Option 1: Fine-tune llama3.2
```bash
# Prepare mental health dataset
# Fine-tune with therapy-specific examples
ollama create mental-therapy-assistant -f Modelfile
```

### Option 2: Layer Optimization
- Remove unnecessary layers
- Focus on summarization capabilities
- Reduce model size for faster inference

### Option 3: Prompt Engineering
- Refine system instructions
- Add more specific examples
- Adjust temperature/parameters

## Monitoring

### Check AI Performance
- Review generated summaries for accuracy
- Verify risk flagging works correctly
- Monitor response times
- Collect therapist feedback

### Logs
- AI summary generation logged in backend
- Character counts tracked
- Error handling with fallbacks

## Compliance

### HIPAA Considerations
- All processing is local (no external APIs)
- Data never leaves your machine
- Ollama runs entirely offline
- Patient confidentiality maintained

### Professional Standards
- Summaries are for therapist use only
- AI assists, does not replace clinical judgment
- Therapists review all AI-generated content
- Maintains professional documentation standards

---

**Status**: ✅ Active and Running
**Model**: llama3.2:3b (Local)
**Mode**: Mental Therapy Assistant
**Last Updated**: November 2025
