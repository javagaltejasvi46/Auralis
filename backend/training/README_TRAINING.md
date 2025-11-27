# Phi-3-Mini Training Guide

Complete guide for fine-tuning Phi-3-Mini on psychotherapy dataset.

## Prerequisites

### Hardware Requirements
- **Training**: 12GB RAM (with 4-bit quantization)
- **GPU** (Optional): CUDA 11.8+ with 8GB+ VRAM
- **Disk Space**: 15GB (base model + fine-tuned model + checkpoints)

### Software Requirements
- Python 3.10+
- CUDA 11.8+ (optional, for GPU training)

## Installation

### 1. Install Training Dependencies

```bash
cd backend/training
pip install -r requirements_training.txt
```

### 2. Verify Installation

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
```

## Dataset Preparation

### 1. Verify Dataset

Ensure `psychotherapy_transcriptions.csv` is in the project root with columns:
- `session_transcription`: Full therapy session text
- `session_summary`: Target summary with clinical formatting

### 2. Test Dataset Loading

```bash
python dataset_loader.py
```

Expected output:
```
✅ Loaded X records from psychotherapy_transcriptions.csv
✅ Validated X records (Y removed)
✅ Split: train=X, val=Y, test=Z
```

## Training Process

### 1. Configure Training

Edit `fine_tuner.py` to adjust parameters:

```python
config = TrainingConfig(
    num_epochs=3,           # Training epochs
    batch_size=4,           # Batch size (reduce if OOM)
    learning_rate=2e-4,     # Learning rate
    lora_rank=8,            # LoRA rank
    use_4bit=True           # 4-bit quantization
)
```

### 2. Run Training

```bash
python train.py
```

**Training Time Estimates:**
- GPU (RTX 3090): 2-4 hours
- CPU (16 cores): 8-12 hours

### 3. Monitor Training

Watch for:
- ✅ Model loading successful
- ✅ Training loss decreasing
- ✅ Validation loss stable
- ✅ Checkpoints saved every 100 steps

### 4. Training Output

```
models/
├── phi3-therapy-finetuned/        # LoRA adapters
│   ├── adapter_config.json
│   ├── adapter_model.safetensors
│   └── ...
├── phi3-therapy-finetuned_merged/ # Full merged model
│   ├── model.safetensors
│   ├── config.json
│   └── ...
└── training_logs/
    └── checkpoints/
```

## Model Export to GGUF

### 1. Install llama.cpp

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
```

### 2. Convert to GGUF

```bash
python llama.cpp/convert.py \
  models/phi3-therapy-finetuned_merged \
  --outfile models/phi3-therapy-f16.gguf \
  --outtype f16
```

### 3. Quantize Model

**Q4_K_M (Recommended for Production)**:
```bash
./llama.cpp/quantize \
  models/phi3-therapy-f16.gguf \
  models/phi3-therapy-q4_k_m.gguf \
  Q4_K_M
```

**Q5_K_M (Higher Quality)**:
```bash
./llama.cpp/quantize \
  models/phi3-therapy-f16.gguf \
  models/phi3-therapy-q5_k_m.gguf \
  Q5_K_M
```

### 4. Verify GGUF Model

```bash
ls -lh models/*.gguf
```

Expected sizes:
- `phi3-therapy-q4_k_m.gguf`: ~2.5GB
- `phi3-therapy-q5_k_m.gguf`: ~3.0GB

## Model Evaluation

### 1. Run Evaluation

```bash
python -c "
from model_evaluator import ModelEvaluator
from dataset_loader import DatasetLoader

# Load test set
loader = DatasetLoader('psychotherapy_transcriptions.csv')
loader.load_csv()
loader.validate_data()
splits = loader.split_dataset()

# TODO: Generate predictions with model
# predictions = [...]
# references = [...]

# evaluator = ModelEvaluator()
# report = evaluator.generate_evaluation_report(predictions, references)
"
```

### 2. Quality Metrics

Target metrics:
- **ROUGE-L**: ≥ 0.40
- **Section Completeness**: ≥ 90%
- **Risk Formatting**: ≥ 95%
- **Word Count Compliance**: ≥ 80%

## Troubleshooting

### Out of Memory (OOM)

**Symptoms**: Training crashes with CUDA OOM or system memory error

**Solutions**:
1. Reduce batch size: `batch_size=2` or `batch_size=1`
2. Enable gradient checkpointing: `use_gradient_checkpointing=True`
3. Reduce sequence length: `max_seq_length=1024`
4. Use CPU training (slower but more memory)

### Slow Training

**Symptoms**: Training takes > 24 hours

**Solutions**:
1. Use GPU if available
2. Increase batch size: `batch_size=8`
3. Reduce epochs: `num_epochs=2`
4. Use smaller dataset for testing

### Model Quality Issues

**Symptoms**: ROUGE-L < 0.40 or poor summaries

**Solutions**:
1. Increase training epochs: `num_epochs=5`
2. Adjust learning rate: `learning_rate=1e-4`
3. Increase LoRA rank: `lora_rank=16`
4. Check dataset quality
5. Try different quantization (Q5_K_M instead of Q4_K_M)

### Conversion Errors

**Symptoms**: GGUF conversion fails

**Solutions**:
1. Update llama.cpp: `git pull`
2. Check Phi-3 compatibility
3. Use official conversion script for Phi-3
4. Verify merged model integrity

## Next Steps

After successful training:

1. ✅ Copy GGUF model to `models/phi3-therapy-q4_k_m.gguf`
2. ✅ Test inference with `llama_inference_engine.py`
3. ✅ Run property-based tests
4. ✅ Deploy to production
5. ✅ Monitor performance

## References

- [Phi-3 Model Card](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [llama.cpp Documentation](https://github.com/ggerganov/llama.cpp)
- [GGUF Format Specification](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)
