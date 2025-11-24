# Hugging Face API Token Setup (Free)

## Why You Need This

The free public API has limitations. Getting a free API token gives you:
- ✅ Higher rate limits
- ✅ Reliable access
- ✅ Better performance
- ✅ Still 100% FREE!

## How to Get Your Free API Token (2 minutes)

### Step 1: Create Account
1. Go to https://huggingface.co/join
2. Sign up with email (free)
3. Verify your email

### Step 2: Generate Token
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name it: "AURALIS-Summarization"
4. Type: "Read"
5. Click "Generate"
6. Copy the token (starts with `hf_...`)

### Step 3: Add to Code
1. Open `backend/summarization_service.py`
2. Find line 11:
   ```python
   # self.headers = {"Authorization": "Bearer hf_YOUR_TOKEN_HERE"}
   ```
3. Uncomment and replace with your token:
   ```python
   self.headers = {"Authorization": "Bearer hf_abcdefghijklmnop1234567890"}
   ```
4. Save the file
5. Restart backend: `python main.py`

## Example

```python
class SummarizationService:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
        
        # Add your token here:
        self.headers = {"Authorization": "Bearer hf_YourActualTokenHere"}
```

## Alternative: Use Different Free API

If you don't want to create an account, you can use other free APIs:

### Option 1: Cohere (Free Tier)
```python
import cohere
co = cohere.Client('YOUR_COHERE_API_KEY')  # Free at cohere.com
response = co.summarize(text=text)
```

### Option 2: OpenAI (Paid but cheap)
```python
import openai
openai.api_key = 'YOUR_KEY'
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": f"Summarize: {text}"}]
)
```

### Option 3: Local Ollama (Already Installed!)
```python
import requests
response = requests.post('http://localhost:11434/api/generate', json={
    'model': 'mistral:7b',
    'prompt': f"Summarize this medical session:\n\n{text}\n\nSummary:",
    'stream': False
})
```

## Recommended: Hugging Face (Easiest)

Just get the free token - takes 2 minutes and works perfectly!

## Testing

After adding your token, test it:

```bash
curl -X POST http://localhost:8002/summarize-sessions \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1}'
```

You should see a summary instead of an error!
