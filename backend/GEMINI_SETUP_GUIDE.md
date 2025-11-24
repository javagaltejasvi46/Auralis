# Google Gemini API Setup Guide

## Overview
This guide helps you set up Google Gemini API for AI-powered therapy session summarization.

## Step 1: Get Gemini API Key

### Create Google AI Studio Account
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Get API Key"
4. Click "Create API Key"
5. Copy your API key (starts with `AIza...`)

**Note:** Gemini API is free for development use with generous limits.

## Step 2: Install Dependencies

```bash
cd backend
pip install -r requirements_gemini.txt
```

This installs:
- `google-generativeai` - Official Gemini Python SDK

## Step 3: Configure API Key

### Option 1: Environment Variable (Recommended)

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

**Windows (CMD):**
```cmd
set GEMINI_API_KEY=YOUR_API_KEY_HERE
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

### Option 2: Direct in Code (Quick Test)

Edit `backend/summarization_service.py` line 11:
```python
self.api_key = os.getenv('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')
```

### Option 3: .env File (Production)

Create `backend/.env`:
```
GEMINI_API_KEY=YOUR_API_KEY_HERE
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

Add to `summarization_service.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Step 4: Test the Setup

```bash
cd backend
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); model = genai.GenerativeModel('gemini-pro'); print(model.generate_content('Hello').text)"
```

Should output a response from Gemini.

## Step 5: Start Backend

```bash
cd backend
python main.py
```

You should see:
```
✅ Gemini API Summarization service initialized
🤖 Using Google Gemini Pro
💡 Professional therapy summarization with keyword highlighting
```

## Features

### 1. Professional Summarization
- Concise clinical summaries (under 50 words)
- Professional mental health terminology
- Structured format

### 2. Sensitive Keyword Highlighting
Automatically highlights in red:
- suicide, suicidal, kill myself
- self-harm, cut myself, hurt myself
- violence, hurt others
- abuse (sexual, physical)
- overdose, pills, weapon

### 3. Markdown Formatting
- **Bold** for important points
- {{RED:text}} for urgent concerns
- React Native renders these properly

### 4. Multi-Session Summaries
- Comprehensive 200-300 word summaries
- Tracks progression across sessions
- Identifies patterns and trends

## Summary Format

### Single Session (Under 50 words)
```
**Chief Complaint:** Work-related anxiety, sleep disturbances.
**Emotional State:** Distressed but engaged.
**Risk Assessment:** Low risk, no {{RED:suicidal ideation}}.
**Intervention:** Breathing exercises, time management.
**Plan:** Practice daily, follow-up next week.
```

### Multi-Session (200-300 words)
```
**Chief Complaints:** Patient presented with persistent anxiety...
**Emotional Progression:** Initial sessions showed high distress...
**Risk Assessment:** Session 3 revealed {{RED:self-harm thoughts}}...
**Therapeutic Progress:** Gradual improvement in coping skills...
**Treatment Plan:** Continued CBT, medication evaluation...
**Follow-up Needs:** Weekly sessions, crisis plan review...
```

## API Limits

### Free Tier (Gemini Pro)
- 60 requests per minute
- 1,500 requests per day
- 1 million tokens per day

**More than enough for therapy practice!**

### Paid Tier
- Higher limits available
- Pay-as-you-go pricing
- Enterprise support

## Troubleshooting

### Error: "API key not configured"
**Solution:** Set GEMINI_API_KEY environment variable

### Error: "Invalid API key"
**Solution:** 
1. Check key is correct (starts with `AIza`)
2. Ensure no extra spaces
3. Generate new key if needed

### Error: "Quota exceeded"
**Solution:**
1. Wait for quota reset (1 minute or 1 day)
2. Upgrade to paid tier
3. Use multiple API keys (rotate)

### Error: "Module not found: google.generativeai"
**Solution:**
```bash
pip install google-generativeai
```

### Summaries not showing in app
**Solution:**
1. Check backend logs for errors
2. Verify API key is set
3. Test API directly:
```bash
curl -X POST http://localhost:8002/summarize-sessions \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1}'
```

## Security Best Practices

### 1. Never Commit API Keys
Add to `.gitignore`:
```
.env
*.key
```

### 2. Use Environment Variables
Don't hardcode keys in source code

### 3. Rotate Keys Regularly
Generate new keys every 3-6 months

### 4. Monitor Usage
Check Google AI Studio dashboard for unusual activity

### 5. Restrict Key Permissions
Use API key restrictions in Google Cloud Console

## Performance Optimization

### 1. Caching
Cache summaries to avoid re-generating:
```python
# Store in database
session.summary = generated_summary
session.save()
```

### 2. Batch Processing
Summarize multiple sessions at once

### 3. Async Requests
Use async/await for faster responses

### 4. Timeout Handling
Set reasonable timeouts (30-60 seconds)

## Comparison: Gemini vs Ollama

| Feature | Gemini API | Ollama (Local) |
|---------|-----------|----------------|
| **Cost** | Free tier available | Completely free |
| **Speed** | Fast (cloud) | Slower (local CPU) |
| **Quality** | Excellent | Good |
| **Privacy** | Data sent to Google | 100% local |
| **Setup** | Easy (API key) | Complex (model download) |
| **Reliability** | High (Google infra) | Depends on hardware |
| **Offline** | No | Yes |

**Recommendation:** Use Gemini for production, Ollama for offline/privacy needs.

## Next Steps

1. ✅ Get API key from Google AI Studio
2. ✅ Install dependencies
3. ✅ Set environment variable
4. ✅ Start backend
5. ✅ Test in mobile app
6. ✅ Monitor usage
7. ✅ Collect feedback

## Support

- **Gemini Docs:** https://ai.google.dev/docs
- **API Reference:** https://ai.google.dev/api/python
- **Community:** https://discuss.ai.google.dev/

---

**Status:** Ready for Production
**API:** Google Gemini Pro
**Cost:** Free (with limits)
**Quality:** Excellent
