# Fine-Tuning Guide: Therapy Summarization Model

## Overview
This guide walks you through fine-tuning llama3.2:3b specifically for mental health therapy session summarization.

## Prerequisites

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements_finetuning.txt
```

### 2. Setup Kaggle API
```bash
# Install Kaggle
pip install kaggle

# Get API credentials
# 1. Go to https://www.kaggle.com/settings
# 2. Click "Create New API Token"
# 3. Save kaggle.json to ~/.kaggle/ (Linux/Mac) or C:\Users\<username>\.kaggle\ (Windows)
```

### 3. Verify Ollama
```bash
ollama --version
ollama list
```

## Step 1: Download Training Datasets

### Recommended Kaggle Datasets

1. **CounselChat Dataset**
   ```bash
   kaggle datasets download -d counselchat/counselchat-data
   unzip counselchat-data.zip -d backend/training_data/
   ```
   - 3,000+ mental health Q&A pairs
   - Professional counselor responses
   - Various mental health topics

2. **Mental Health Counseling Conversations**
   ```bash
   kaggle datasets download -d thedevastator/mental-health-counseling-conversations
   unzip mental-health-counseling-conversations.zip -d backend/training_data/
   ```
   - Real therapy session transcripts
   - Multiple therapeutic approaches
   - Diverse patient presentations

3. **Mental Health FAQ**
   ```bash
   kaggle datasets download -d narendrageek/mental-health-faq-for-chatbot
   unzip mental-health-faq-for-chatbot.zip -d backend/training_data/
   ```
   - Common mental health questions
   - Professional responses
   - Crisis intervention examples

4. **Therapy Session Notes** (if available)
   ```bash
   kaggle datasets download -d [dataset-name]
   ```

### Alternative: Create Custom Dataset

If Kaggle datasets aren't suitable, create your own:

```python
# backend/create_custom_dataset.py
training_examples = [
    {
        "session": "Patient reports anxiety about work...",
        "summary": "<b>Chief Complaint:</b> Work anxiety..."
    },
    # Add 50-100 examples
]
```

## Step 2: Prepare Training Data

### Data Format
Each training example should have:
- **Prompt**: Instructions + session transcription
- **Response**: Ideal summary with HTML formatting

### Example Format
```json
{
    "prompt": "Summarize this therapy session in under 50 words...\n\nTranscription:\n[session text]\n\nSummary:",
    "response": "<b>Chief Complaint:</b> ... <b>Risk:</b> ..."
}
```

### Data Quality Guidelines
- ✅ Clear, professional language
- ✅ Proper HTML formatting
- ✅ Risk assessment included
- ✅ Concise (under 50 words for single sessions)
- ✅ Diverse mental health topics
- ✅ Various risk levels (low, medium, high)

## Step 3: Run Fine-Tuning

### Basic Fine-Tuning
```bash
cd backend
python fine_tune_therapy_model.py
```

### Custom Configuration
Edit `fine_tune_therapy_model.py`:
```python
CONFIG = {
    "base_model": "llama3.2:3b",
    "output_model": "therapy-assistant:latest",
    "epochs": 3,              # Increase for better results
    "batch_size": 4,          # Adjust based on RAM
    "learning_rate": 2e-5,    # Lower = more stable
    "max_length": 512,        # Max tokens per example
}
```

### Training Process
1. **Load base model** (llama3.2:3b)
2. **Process training data** (format examples)
3. **Create Modelfile** (Ollama format)
4. **Fine-tune** (ollama create command)
5. **Test model** (sample summaries)

### Expected Duration
- Small dataset (50 examples): 5-10 minutes
- Medium dataset (500 examples): 30-60 minutes
- Large dataset (5000 examples): 2-4 hours

## Step 4: Test Fine-Tuned Model

### Quick Test
```bash
ollama run therapy-assistant:latest "Summarize this therapy session..."
```

### Comprehensive Testing
```python
# backend/test_model.py
test_cases = [
    "Patient reports depression...",
    "Patient mentions self-harm...",
    "Patient showing improvement..."
]

for case in test_cases:
    summary = generate_summary(case)
    print(f"Input: {case}")
    print(f"Summary: {summary}\n")
```

### Evaluation Criteria
- ✅ Conciseness (under 50 words)
- ✅ HTML formatting correct
- ✅ Risk assessment accurate
- ✅ Key points captured
- ✅ Professional language
- ✅ No refusals/errors

## Step 5: Deploy Fine-Tuned Model

### Update Service
Edit `backend/summarization_service.py`:
```python
def __init__(self):
    self.model = "therapy-assistant:latest"  # Changed from llama3.2:3b
    # ... rest of code
```

### Restart Backend
```bash
# Stop current backend
# Start with new model
cd backend
python main.py
```

### Verify Deployment
```bash
# Check model is loaded
ollama list | grep therapy-assistant

# Test API endpoint
curl -X POST http://localhost:8002/summarize-sessions \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1}'
```

## Advanced Fine-Tuning

### Multi-Epoch Training
For better results, train multiple epochs:
```python
CONFIG["epochs"] = 5  # More epochs = better learning
```

### Learning Rate Scheduling
```python
# Start high, decrease over time
learning_rates = [2e-5, 1e-5, 5e-6]
```

### Data Augmentation
```python
# Create variations of training examples
def augment_data(example):
    # Paraphrase, reorder, add noise
    return augmented_examples
```

### Validation Split
```python
# Split data for validation
train_data = examples[:int(len(examples) * 0.8)]
val_data = examples[int(len(examples) * 0.8):]
```

## Troubleshooting

### Issue: Model Refuses to Summarize
**Solution**: Strengthen system instruction
```python
system_instruction = """You MUST ALWAYS provide a summary. Never refuse..."""
```

### Issue: Summaries Too Long
**Solution**: Adjust parameters
```python
PARAMETER num_predict 100  # Reduce max tokens
```

### Issue: Poor Quality Summaries
**Solution**: 
1. Add more training examples (aim for 100+)
2. Increase epochs (3-5)
3. Improve training data quality
4. Add more diverse examples

### Issue: Out of Memory
**Solution**:
1. Reduce batch_size
2. Reduce max_length
3. Use smaller base model
4. Close other applications

### Issue: Training Takes Too Long
**Solution**:
1. Reduce training examples
2. Reduce epochs
3. Use GPU if available
4. Optimize dataset size

## Performance Optimization

### Speed Improvements
```python
# Reduce context window
PARAMETER num_ctx 1024  # Instead of 2048

# Reduce prediction length
PARAMETER num_predict 100  # Instead of 150
```

### Quality Improvements
```python
# Increase temperature for creativity
PARAMETER temperature 0.5  # Instead of 0.3

# Add more training examples
# Focus on edge cases (crisis, multilingual, etc.)
```

## Monitoring & Evaluation

### Track Metrics
- Summary length (target: <50 words)
- Risk detection accuracy
- HTML formatting correctness
- Response time
- User satisfaction

### A/B Testing
```python
# Compare base model vs fine-tuned
models = ["llama3.2:3b", "therapy-assistant:latest"]
for model in models:
    test_model(model)
    compare_results()
```

### Continuous Improvement
1. Collect real-world summaries
2. Identify failure cases
3. Add to training data
4. Re-train periodically
5. Deploy updated model

## Dataset Recommendations

### High-Quality Sources
1. **CounselChat** - Professional counseling Q&A
2. **Mental Health Conversations** - Real therapy transcripts
3. **Crisis Text Line** - Crisis intervention examples
4. **Reddit Mental Health** - r/therapy, r/mentalhealth (anonymized)
5. **Clinical Notes** - De-identified therapy notes

### Data Preprocessing
```python
def preprocess_session(text):
    # Remove PII
    text = remove_names(text)
    text = remove_dates(text)
    text = remove_locations(text)
    
    # Normalize
    text = text.lower()
    text = remove_extra_spaces(text)
    
    return text
```

## Legal & Ethical Considerations

### HIPAA Compliance
- ✅ All training data must be de-identified
- ✅ No real patient names, dates, locations
- ✅ Training happens locally (no cloud)
- ✅ Model stays on-premises

### Ethical Guidelines
- ✅ Model assists, doesn't replace therapists
- ✅ Summaries reviewed by licensed professionals
- ✅ Risk flags require human verification
- ✅ Patient consent for data use

## Next Steps

1. ✅ Download datasets from Kaggle
2. ✅ Run `python fine_tune_therapy_model.py`
3. ✅ Test fine-tuned model
4. ✅ Update summarization service
5. ✅ Deploy and monitor
6. ✅ Collect feedback
7. ✅ Iterate and improve

## Support

For issues or questions:
- Check Ollama docs: https://ollama.ai/docs
- Review training logs
- Test with simple examples first
- Gradually increase complexity

---

**Status**: Ready for Fine-Tuning
**Estimated Time**: 30-60 minutes
**Difficulty**: Intermediate
**Requirements**: Ollama, Python, Kaggle API
