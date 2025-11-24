# BART Fine-Tuning Guide for Medical Summarization

## Model Information

**Model**: `facebook/bart-large-cnn`
- **Size**: 1.6 GB (406M parameters)
- **Current Use**: Pre-trained on CNN/DailyMail news articles
- **Target**: Fine-tune for medical/clinical session summarization

## Why Fine-Tune?

1. **Domain Adaptation**: Medical terminology and context differ from news articles
2. **Better Accuracy**: Learns medical conversation patterns
3. **Specialized Output**: Generates clinically relevant summaries

## Fine-Tuning Process

### 1. Prepare Training Data

Create a dataset of medical session transcriptions with human-written summaries:

```python
# Example format
training_data = [
    {
        "transcription": "Patient reports chest pain for 3 days...",
        "summary": "Patient presents with chest pain, duration 3 days..."
    },
    # Need 500-1000+ examples for good results
]
```

### 2. Install Requirements

```bash
pip install transformers datasets accelerate
```

### 3. Fine-Tuning Script

```python
from transformers import BartForConditionalGeneration, BartTokenizer, Trainer, TrainingArguments
from datasets import Dataset

# Load pre-trained model
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')

# Prepare dataset
def preprocess_function(examples):
    inputs = tokenizer(examples['transcription'], max_length=1024, truncation=True)
    targets = tokenizer(examples['summary'], max_length=256, truncation=True)
    inputs['labels'] = targets['input_ids']
    return inputs

dataset = Dataset.from_dict(training_data)
tokenized_dataset = dataset.map(preprocess_function, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir='./bart-medical-finetuned',
    num_train_epochs=3,
    per_device_train_batch_size=4,
    save_steps=500,
    save_total_limit=2,
    learning_rate=5e-5,
    weight_decay=0.01,
    logging_steps=100,
)

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

trainer.train()
model.save_pretrained('./bart-medical-finetuned')
```

### 4. Use Fine-Tuned Model

Update `summarization_service.py`:

```python
# Change from:
self.model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

# To:
self.model = BartForConditionalGeneration.from_pretrained('./bart-medical-finetuned')
```

## Alternative: Use Ollama

Since you have Ollama installed, you can use local LLMs:

### Ollama Models for Summarization:

1. **Llama 2 7B** (3.8 GB)
   ```bash
   ollama pull llama2:7b
   ```

2. **Mistral 7B** (4.1 GB) - Better for summarization
   ```bash
   ollama pull mistral:7b
   ```

3. **Phi-2** (1.7 GB) - Smaller, faster
   ```bash
   ollama pull phi:2.7b
   ```

### Ollama Integration:

```python
import requests

def summarize_with_ollama(text: str) -> str:
    response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'mistral:7b',
        'prompt': f"Summarize this medical session:\n\n{text}\n\nSummary:",
        'stream': False
    })
    return response.json()['response']
```

## Comparison

| Method | Size | Speed | Accuracy | Setup |
|--------|------|-------|----------|-------|
| BART (pre-trained) | 1.6 GB | Medium | Good | Easy |
| BART (fine-tuned) | 1.6 GB | Medium | Excellent | Complex |
| Ollama Mistral | 4.1 GB | Fast | Very Good | Easy |
| Ollama Llama2 | 3.8 GB | Fast | Good | Easy |

## Recommendation

**For Production**:
1. Start with pre-trained BART (already implemented)
2. Collect 500-1000 session summaries
3. Fine-tune BART on your data
4. Or use Ollama Mistral for easier setup

**Quick Start with Ollama**:
- Faster setup
- No training needed
- Good results out-of-the-box
- Easier to customize prompts

## Installation Steps

### Option 1: Use Current BART (Recommended to start)

```bash
cd backend
pip install -r requirements_summarization.txt
python main.py
```

### Option 2: Switch to Ollama

```bash
# Install Ollama (already done)
ollama pull mistral:7b

# Update summarization_service.py to use Ollama
```

## Testing

```bash
# Test summarization endpoint
curl -X POST http://localhost:8002/summarize-sessions \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1}'
```
