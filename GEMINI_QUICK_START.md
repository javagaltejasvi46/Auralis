# 🚀 Gemini API Quick Start

## ✅ What's Been Set Up

1. **Gemini Integration** - Professional AI summarization
2. **Keyword Highlighting** - Sensitive words in red
3. **React Native Renderer** - Proper formatting in mobile app
4. **System Instructions** - Optimized for therapy sessions

## 📋 Quick Setup (3 Steps)

### Step 1: Get API Key
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

### Step 2: Set API Key

**Option A: Use the script (Easiest)**
```cmd
set_gemini_key.bat
```
Paste your API key when prompted.

**Option B: Manual**
```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

### Step 3: Start Backend
```bash
cd backend
python main.py
```

## ✨ Features

### Professional Summaries
```
**Chief Complaint:** Work anxiety, sleep issues (1 week)
**Emotional State:** Distressed but engaged
**Risk Assessment:** Low risk, no suicidal ideation
**Intervention:** Breathing exercises, time management
**Plan:** Practice daily, follow-up next week
```

### Sensitive Keyword Highlighting
These words appear in **RED** in the app:
- suicide, suicidal, kill myself
- self-harm, cut myself, hurt myself
- violence, hurt others
- abuse (sexual, physical)
- overdose, pills, weapon

### Format Examples

**Bold text:** `**important**` → **important**
**Red urgent:** `{{RED:suicide}}` → 🔴 suicide (red background)

## 🧪 Test It

1. Start backend
2. Open mobile app
3. Go to patient profile
4. Click "Summarize"
5. See professional AI summary with highlighting!

## 📊 API Limits (Free Tier)

- ✅ 60 requests/minute
- ✅ 1,500 requests/day
- ✅ 1M tokens/day

**Perfect for therapy practice!**

## 🔧 Troubleshooting

### "API key not configured"
Run `set_gemini_key.bat` or set environment variable

### "Module not found"
```bash
pip install google-generativeai
```

### Still not working?
Check `backend/GEMINI_SETUP_GUIDE.md` for detailed help

## 📚 Files Created

- `backend/summarization_service.py` - Gemini integration
- `frontend/src/components/SummaryRenderer.tsx` - Formatting component
- `backend/GEMINI_SETUP_GUIDE.md` - Detailed guide
- `set_gemini_key.bat` - Easy API key setup

## 🎯 System Instructions

The AI is configured to:
1. Create concise summaries (under 50 words)
2. Use professional clinical language
3. Highlight sensitive keywords in red
4. Format with markdown bold
5. Never refuse to summarize
6. Focus on: complaints, emotional state, risk, interventions, plan

## 💡 Tips

- **First time:** May take 10-20 seconds (model loading)
- **After that:** 2-5 seconds per summary
- **Quality:** Excellent - better than local models
- **Privacy:** Data sent to Google (encrypted)
- **Cost:** Free for development

## 🚀 Ready to Use!

Your API key: `[Paste here after getting it]`

1. Get key: https://makersuite.google.com/app/apikey
2. Run: `set_gemini_key.bat`
3. Start: `python backend/main.py`
4. Test in app!

---

**Status:** ✅ Ready
**API:** Google Gemini Pro
**Quality:** Excellent
**Cost:** Free
