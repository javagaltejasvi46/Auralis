# Design Document: Phi-3-Mini Summarization Migration

## Overview

This design document outlines the architecture for migrating the Auralis medical transcription system from Google Gemini API to a locally trained and deployed Phi-3-Mini model. The solution leverages fine-tuning with LoRA (Low-Rank Adaptation) for efficient training on the psychotherapy dataset, and uses llama.cpp/llama-cpp-python for optimized inference with quantized models.

### Model Selection Rationale: Phi-3-Mini

**Phi-3-Mini-4K-Instruct** is selected for the following reasons:

| Aspect | Details |
|--------|---------|
| **Size** | 3.8B parameters (~2.5GB quantized) |
| **Performance** | Outperforms models 2x its size on many benchmarks |
| **Efficiency** | Optimized for low-resource environments |
| **Training** | Trained on high-quality, curated data including medical/clinical content |
| **Context** | 4K context window (sufficient for therapy sessions) |
| **Support** | Microsoft-backed with excellent documentation |
| **Inference Speed** | ~10-15 seconds per summary on CPU |
| **RAM Requirements** | 4GB for inference, 12GB for training |

**Why Phi-3-Mini over larger models**:
- 40% smaller than Mistral-7B (2.5GB vs 4GB quantized)
- Faster inference times
- Lower memory requirements
- Specifically optimized for instruction-following
- Excellent performance on summarization tasks
- Better suited for deployment on standard hardware

### Key Design Decisions

1. **Model Selection**: **Phi-3-Mini-4K-Instruct** (3.8B parameters)
   - Microsoft's efficient small language model
   - Optimized for instruction-following and summarization
   - Excellent quality-to-size ratio
   - Strong performance on medical/clinical tasks
   - Well-documented and actively maintained
2. **Training Approach**: LoRA fine-tuning using the Hugging Face ecosystem (transformers, peft, trl) with 4-bit quantization during training
3. **Inference Engine**: llama-cpp-python for efficient CPU/GPU inference with GGUF quantized models (Q4_K_M quantization)
4. **Deployment Strategy**: Separate training pipeline (offline) and inference service (integrated into backend)
5. **Data Format**: Phi-3 instruction format optimized for clinical summarization task
6. **Optimization**: 4-bit quantization reduces model size from ~7.6GB to ~2.5GB with minimal quality loss

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Training Pipeline (Offline)              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Dataset    │───▶│  Fine-tuning │───▶│    Model     │  │
│  │   Loader     │    │   (LoRA)     │    │  Checkpoint  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  psychotherapy.csv    Training Logs        models/llama2/   │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ Model Export (GGUF)
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                  Production Backend (Runtime)                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Summarization Service                   │   │
│  │  ┌────────────────┐         ┌──────────────────┐    │   │
│  │  │  Model Loader  │────────▶│  Llama2 Inference│    │   │
│  │  │  (llama-cpp)   │         │     Engine       │    │   │
│  │  └────────────────┘         └──────────────────┘    │   │
│  │         │                            │               │   │
│  │         ▼                            ▼               │   │
│  │  GGUF Model File              Generated Summary     │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              FastAPI Endpoints                       │   │
│  │  /summarize-sessions  │  /summarize-text            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
                  React Native Frontend
```

### Component Interaction Flow

1. **Training Phase** (Offline, one-time or periodic):
   - Load psychotherapy_transcriptions.csv
   - Preprocess and format data for instruction tuning
   - Fine-tune Llama2-7B-Chat with LoRA adapters
   - Merge LoRA weights and export to GGUF format
   - Save quantized model to models/ directory

2. **Inference Phase** (Runtime):
   
   **Per-Session Note Generation**:
   - User completes a therapy session recording
   - Frontend calls POST /sessions/{session_id}/generate-notes
   - Backend retrieves session transcription from database
   - Summarization Service formats single-session prompt
   - Llama2 Inference Engine generates clinical notes
   - Notes saved to session.notes field with AI-generated metadata
   - Frontend displays notes in editable text field
   - User reviews, edits if needed, and saves
   - Backend updates notes and metadata (edited_from_ai=true if modified)
   
   **Multi-Session Summary** (Existing functionality):
   - Frontend sends summarization request to /summarize-sessions
   - Summarization Service formats prompt with all session data
   - Llama2 Inference Engine generates comprehensive summary
   - Response formatted and returned to frontend

## Components and Interfaces

### 1. Training Pipeline Components

#### DatasetLoader
**Purpose**: Load, validate, and preprocess the psychotherapy dataset

**Interface**:
```python
class DatasetLoader:
    def load_csv(self, file_path: str) -> pd.DataFrame
    def validate_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]
    def split_dataset(self, df: pd.DataFrame, train_ratio: float, val_ratio: float) -> Dict[str, pd.DataFrame]
    def format_for_training(self, df: pd.DataFrame) -> datasets.Dataset
```

**Responsibilities**:
- Read CSV file and handle encoding issues
- Validate required columns (session_transcription, session_summary)
- Remove or flag invalid entries
- Split into train/val/test sets
- Format as Hugging Face Dataset with instruction template

#### FineTuner
**Purpose**: Fine-tune Llama2 model using LoRA on the psychotherapy dataset

**Interface**:
```python
class FineTuner:
    def __init__(self, model_name: str, output_dir: str, config: TrainingConfig)
    def setup_model_and_tokenizer(self) -> Tuple[AutoModelForCausalLM, AutoTokenizer]
    def setup_lora_config(self) -> LoraConfig
    def train(self, train_dataset: Dataset, eval_dataset: Dataset) -> TrainingResults
    def save_checkpoint(self, checkpoint_dir: str)
    def merge_and_export(self, output_path: str, quantize: bool = True)
```

**Responsibilities**:
- Load base Llama2-7B-Chat model
- Configure LoRA parameters (rank, alpha, dropout)
- Set up training arguments (batch size, learning rate, epochs)
- Execute training loop with validation
- Save checkpoints and merge LoRA weights
- Export to GGUF format for inference

#### ModelEvaluator
**Purpose**: Evaluate model quality on test set

**Interface**:
```python
class ModelEvaluator:
    def compute_rouge_scores(self, predictions: List[str], references: List[str]) -> Dict[str, float]
    def compute_bleu_scores(self, predictions: List[str], references: List[str]) -> float
    def evaluate_clinical_accuracy(self, predictions: List[str], references: List[str]) -> Dict[str, float]
    def generate_evaluation_report(self, test_dataset: Dataset) -> EvaluationReport
```

**Responsibilities**:
- Generate summaries for test set
- Compute ROUGE-L, BLEU scores
- Check for required sections (Chief Complaint, Risk, etc.)
- Validate risk keyword formatting
- Generate comprehensive evaluation report

### 2. Inference Service Components

#### LlamaInferenceEngine
**Purpose**: Load and run the fine-tuned model (Mistral/Phi-3/TinyLlama) for inference

**Interface**:
```python
class LlamaInferenceEngine:
    def __init__(self, model_path: str, config: InferenceConfig)
    def load_model(self) -> Llama
    def generate(self, prompt: str, max_tokens: int, temperature: float, top_p: float) -> str
    def generate_with_timeout(self, prompt: str, timeout: int = 60) -> str
    def unload_model(self)
```

**Responsibilities**:
- Load GGUF model using llama-cpp-python
- Configure inference parameters (context size, threads, GPU layers)
- Generate text with specified parameters
- Handle timeouts and errors gracefully
- Manage model lifecycle (load/unload)

#### SummarizationService (Refactored)
**Purpose**: High-level service for generating therapy session summaries

**Interface**:
```python
class SummarizationService:
    def __init__(self, model_path: str, config: ServiceConfig)
    def summarize_single_session(self, transcription: str, notes: str = "") -> str
    def summarize_text(self, text: str, max_length: int = 250, min_length: int = 100) -> str
    def summarize_sessions(self, sessions: List[Dict]) -> Dict[str, Any]
    def auto_generate_session_notes(self, session_id: int, transcription: str) -> str
    def _format_prompt(self, text: str, session_type: str = "single") -> str
    def _parse_summary(self, raw_output: str) -> str
    def _fallback(self, text: str, max_length: int) -> str
```

**Responsibilities**:
- Initialize LlamaInferenceEngine
- Format prompts using clinical instruction template
- Generate summaries for individual sessions (auto-populate notes field)
- Generate comprehensive summaries across multiple sessions
- Parse and validate model output
- Provide fallback summaries on errors
- Maintain backward compatibility with existing API

#### PromptFormatter
**Purpose**: Create consistent prompts for the model

**Interface**:
```python
class PromptFormatter:
    @staticmethod
    def format_single_session(transcription: str, notes: str = "") -> str
    @staticmethod
    def format_multiple_sessions(sessions: List[Dict]) -> str
    @staticmethod
    def format_with_system_instruction() -> str
```

**Responsibilities**:
- Apply instruction template matching training format
- Include system instructions for clinical summarization
- Format multiple sessions with context
- Ensure consistent prompt structure

### 3. API Endpoints (New/Modified)

#### POST /sessions/{session_id}/generate-notes
**Purpose**: Auto-generate clinical notes for a specific session

**Request**:
```python
{
    "session_id": int,
    "regenerate": bool  # Optional: force regeneration if notes exist
}
```

**Response**:
```python
{
    "success": bool,
    "session_id": int,
    "generated_notes": str,
    "can_edit": bool  # Always true - user can edit
}
```

**Behavior**:
- Retrieves session transcription from database
- Generates clinical summary using Llama2
- Populates the session's notes field (does not overwrite if notes exist unless regenerate=true)
- Returns generated notes for immediate display/editing

#### PUT /sessions/{session_id}/notes
**Purpose**: Update session notes (user-edited or confirmed AI-generated)

**Request**:
```python
{
    "notes": str,
    "is_ai_generated": bool,  # Track if notes are AI-generated or user-written
    "edited_from_ai": bool    # Track if AI notes were edited by user
}
```

**Response**:
```python
{
    "success": bool,
    "session_id": int,
    "notes": str,
    "updated_at": str
}
```

#### GET /sessions/{session_id}
**Purpose**: Retrieve session with notes

**Response** (Enhanced):
```python
{
    "id": int,
    "patient_id": int,
    "session_number": int,
    "session_date": str,
    "original_transcription": str,
    "notes": str,
    "notes_metadata": {
        "is_ai_generated": bool,
        "edited_from_ai": bool,
        "generated_at": str,
        "last_edited_at": str
    },
    // ... other fields
}
```

### 3. Configuration Components

#### TrainingConfig
```python
@dataclass
class TrainingConfig:
    # Phi-3-Mini model
    model_name: str = "microsoft/Phi-3-mini-4k-instruct"
    output_dir: str = "models/phi3-therapy-finetuned"
    dataset_path: str = "psychotherapy_transcriptions.csv"
    
    # LoRA parameters (optimized for Phi-3-Mini)
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: [
        "qkv_proj",  # Phi-3 uses combined QKV projection
        "o_proj",
        "gate_up_proj",  # Phi-3 specific
        "down_proj"
    ])
    
    # Training parameters (optimized for Phi-3-Mini)
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    max_seq_length: int = 2048  # Phi-3-Mini supports 4K, but 2K is sufficient
    warmup_steps: int = 100
    
    # Optimization
    use_4bit: bool = True  # 4-bit quantization during training
    use_gradient_checkpointing: bool = True
    use_flash_attention: bool = True  # Phi-3 supports flash attention
    
    # Phi-3 specific
    trust_remote_code: bool = True  # Required for Phi-3
```

#### InferenceConfig
```python
@dataclass
class InferenceConfig:
    # Phi-3-Mini model path
    model_path: str = "models/phi3-therapy-q4_k_m.gguf"  # ~2.5GB
    
    # Model parameters
    n_ctx: int = 2048  # Context window (Phi-3 supports up to 4K)
    n_threads: int = 4  # CPU threads (adjust based on your CPU cores)
    n_gpu_layers: int = 0  # GPU layers (0 for CPU-only, 32 for full GPU offload)
    
    # Generation parameters (tuned for clinical summarization)
    max_tokens: int = 150
    temperature: float = 0.7  # Balanced creativity/consistency
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    
    # Performance
    timeout: int = 45  # Reduced from 60 due to faster Phi-3 inference
    use_mlock: bool = True  # Lock model in RAM for faster inference
    use_mmap: bool = True  # Memory-map model file
    
    # Resource limits
    max_memory_gb: float = 4.0  # Phi-3-Mini requires less RAM
```

## Data Models

### Database Schema Updates

The Session model needs to be extended to support notes metadata:

```python
class Session(Base):
    """Therapy session with transcription"""
    __tablename__ = "sessions"
    
    # ... existing fields ...
    
    # Enhanced notes fields
    notes = Column(Text)
    notes_is_ai_generated = Column(Boolean, default=False)
    notes_edited_from_ai = Column(Boolean, default=False)
    notes_generated_at = Column(DateTime, nullable=True)
    notes_last_edited_at = Column(DateTime, nullable=True)
    
    # ... rest of fields ...
```

**Migration Required**: Add new columns to existing sessions table:
- `notes_is_ai_generated` (BOOLEAN, default FALSE)
- `notes_edited_from_ai` (BOOLEAN, default FALSE)
- `notes_generated_at` (DATETIME, nullable)
- `notes_last_edited_at` (DATETIME, nullable)

### Training Data Format

**Input Format** (Instruction Tuning):
```python
{
    "instruction": "You are a therapy session summarizer. Create a concise clinical summary...",
    "input": "<session transcription text>",
    "output": "<expected summary with formatting>"
}
```

**Prompt Template** (Phi-3 format):
```
<|system|>
You are a therapy session summarizer. Create concise clinical summaries using this format:
**Chief Complaint:** [main issue]
**Emotional State:** [mood]
**Risk:** [safety concerns - use {{RED:text}} for urgent]
**Intervention:** [what was done]
**Plan:** [next steps]

Highlight urgent keywords with {{RED:keyword}}: suicide, self-harm, kill, hurt myself, violence, abuse, overdose

Keep under 50 words.<|end|>
<|user|>
Summarize the following therapy session:

{transcription}<|end|>
<|assistant|>
```

**Note**: Phi-3 uses a specific chat template with `<|system|>`, `<|user|>`, and `<|assistant|>` tags. This format is crucial for optimal performance.

### Runtime Data Models

**GenerateNotesRequest**:
```python
class GenerateNotesRequest(BaseModel):
    session_id: int
    regenerate: bool = False
```

**GenerateNotesResponse**:
```python
class GenerateNotesResponse(BaseModel):
    success: bool
    session_id: int
    generated_notes: str
    can_edit: bool = True
    inference_time: Optional[float]
```

**UpdateNotesRequest**:
```python
class UpdateNotesRequest(BaseModel):
    notes: str
    is_ai_generated: bool = False
    edited_from_ai: bool = False
```

**SummarizationRequest**:
```python
class SummarizationRequest(BaseModel):
    patient_id: int
```

**SummarizationResponse**:
```python
class SummarizationResponse(BaseModel):
    success: bool
    summary: str
    session_count: int
    key_points: List[str]
    total_text_length: Optional[int]
    inference_time: Optional[float]
```

**SessionData**:
```python
class SessionData(TypedDict):
    original_transcription: str
    notes: str
    session_date: str
```

**NotesMetadata**:
```python
class NotesMetadata(TypedDict):
    is_ai_generated: bool
    edited_from_ai: bool
    generated_at: Optional[datetime]
    last_edited_at: Optional[datetime]
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: No External API Calls During Summarization
*For any* summarization request, the system should process it using only local resources without making external network calls to third-party APIs.
**Validates: Requirements 1.2**

### Property 2: Dataset Split Proportions and Disjointness
*For any* dataset loaded for training, the train/validation/test splits should have the correct proportions (80%/10%/10%) and contain no overlapping records.
**Validates: Requirements 2.2**

### Property 3: Required Fields Validation
*For any* record in the loaded dataset, if it is considered valid, it must contain both session_transcription and session_summary fields with non-empty values.
**Validates: Requirements 3.1**

### Property 4: Whitespace Normalization
*For any* input text passed through preprocessing, the output should have normalized whitespace (no multiple consecutive spaces, no leading/trailing whitespace).
**Validates: Requirements 3.2**

### Property 5: Prompt Template Consistency
*For any* training example generated, the prompt format should match the inference template structure (instruction, input, output format).
**Validates: Requirements 3.4**

### Property 6: Clinical Marker Preservation
*For any* summary text containing {{RED:text}} markers during preprocessing, those markers should be preserved in the output.
**Validates: Requirements 3.5**

### Property 7: Local Model Parameter Usage
*For any* call to summarize_text or summarize_sessions, the inference should use the local Llama2 model with the configured temperature and token limit parameters.
**Validates: Requirements 4.2**

### Property 8: Multi-Session Formatting
*For any* list of sessions passed to summarize_sessions, the method should format all sessions into a single prompt and generate a comprehensive summary.
**Validates: Requirements 4.3**

### Property 9: Required Summary Sections
*For any* generated summary, it should contain all required sections: Chief Complaint, Emotional State, Risk Assessment, Intervention, and Plan (or indicate their absence).
**Validates: Requirements 5.1**

### Property 10: Risk Keyword Formatting
*For any* generated summary containing risk-related keywords (suicide, self-harm, violence, abuse), those keywords should be formatted with {{RED:keyword}} markers.
**Validates: Requirements 5.2**

### Property 11: Summary Word Count Bounds
*For any* generated summary, the word count should be between 30 and 70 words, unless the session content explicitly requires more detail (in which case it should not exceed 150 words).
**Validates: Requirements 5.5**

### Property 12: Inference Logging
*For any* inference operation performed, the system should create log entries containing input length, output length, and processing time.
**Validates: Requirements 8.2**

### Property 13: API Response Format Compatibility
*For any* request to /summarize-sessions, the response should include the fields: summary, session_count, and key_points in the same structure as the previous Gemini-based implementation.
**Validates: Requirements 9.1, 9.4**

### Property 14: Session Processing Equivalence
*For any* session data submitted to the new system, the processing steps (formatting, validation, summarization) should produce results equivalent to the Gemini-based implementation.
**Validates: Requirements 9.3**

### Property 15: Formatting Convention Support
*For any* summary generated by the system, if it contains risk-related content, the {{RED:text}} formatting convention should be maintained for backward compatibility.
**Validates: Requirements 9.5**

### Property 16: Per-Session Note Generation
*For any* session with a valid transcription, calling the generate-notes endpoint should produce clinical notes containing the required sections within the timeout period.
**Validates: Requirements 10.2**

### Property 17: Notes Metadata Tracking
*For any* session with notes, the system should maintain accurate metadata indicating whether notes are AI-generated, user-written, or AI-assisted with user edits.
**Validates: Requirements 11.1, 11.2, 11.3**

### Property 18: Notes Overwrite Protection
*For any* session with existing notes, attempting to generate new notes should not overwrite them unless the regenerate flag is explicitly set to true.
**Validates: Requirements 11.5**

## Error Handling

### Training Pipeline Errors

1. **Dataset Loading Failures**
   - **Error**: CSV file not found or corrupted
   - **Handling**: Log error with file path, exit with clear message
   - **Recovery**: Provide instructions for dataset location

2. **Invalid Data Records**
   - **Error**: Missing required fields or malformed data
   - **Handling**: Skip invalid records, log warnings with row numbers
   - **Recovery**: Continue training with valid records, report skipped count

3. **Out of Memory During Training**
   - **Error**: GPU/CPU memory exhausted
   - **Handling**: Catch OOM exception, log memory usage
   - **Recovery**: Suggest reducing batch size or using gradient checkpointing

4. **Model Save Failures**
   - **Error**: Insufficient disk space or permission issues
   - **Handling**: Log error with disk space info, attempt backup location
   - **Recovery**: Provide alternative save paths

### Inference Service Errors

1. **Model Loading Failures**
   - **Error**: Model file not found or corrupted
   - **Handling**: Log error, prevent service startup
   - **Recovery**: Provide clear instructions for model placement

2. **Inference Timeout**
   - **Error**: Generation exceeds 60-second timeout
   - **Handling**: Cancel generation, log timeout event
   - **Recovery**: Return fallback summary, increment timeout counter

3. **Invalid Input**
   - **Error**: Empty or malformed session data
   - **Handling**: Validate input, return 400 error with details
   - **Recovery**: Provide input format examples in error message

4. **Memory Exhaustion**
   - **Error**: Model inference exhausts available memory
   - **Handling**: Catch exception, log memory state
   - **Recovery**: Return fallback summary, suggest model quantization

5. **Malformed Model Output**
   - **Error**: Model generates invalid or incomplete summary
   - **Handling**: Parse output, detect missing sections
   - **Recovery**: Return partial summary with warning, log for review

### Deployment Errors

1. **Missing Dependencies**
   - **Error**: Required packages not installed
   - **Handling**: Check dependencies on startup, log missing packages
   - **Recovery**: Provide installation commands

2. **GPU Not Available**
   - **Error**: CUDA/GPU requested but not available
   - **Handling**: Detect GPU availability, log warning
   - **Recovery**: Fall back to CPU inference with quantized model

3. **Configuration Errors**
   - **Error**: Invalid or missing configuration values
   - **Handling**: Validate config on startup, log issues
   - **Recovery**: Use safe defaults, warn about performance impact

## Testing Strategy

### Unit Testing

**Scope**: Individual components and functions

**Key Test Areas**:
1. **DatasetLoader**
   - Test CSV loading with valid and invalid files
   - Test data validation logic
   - Test train/val/test splitting
   - Test prompt formatting

2. **PromptFormatter**
   - Test single session formatting
   - Test multiple session formatting
   - Test system instruction inclusion
   - Test special character handling

3. **LlamaInferenceEngine**
   - Test model loading (mocked)
   - Test generation parameter passing
   - Test timeout handling
   - Test error handling

4. **SummarizationService**
   - Test summarize_text with various inputs
   - Test summarize_sessions with multiple sessions
   - Test summarize_single_session for individual sessions
   - Test auto_generate_session_notes with database integration
   - Test fallback logic
   - Test output parsing

5. **Notes Management**
   - Test generate-notes endpoint
   - Test notes update endpoint
   - Test metadata tracking
   - Test overwrite protection

**Tools**: pytest, unittest.mock

### Property-Based Testing

**Scope**: Universal properties that should hold across all inputs

**Framework**: Hypothesis (Python property-based testing library)

**Key Properties**:
1. **Dataset Split Disjointness** (Property 2)
   - Generate random datasets
   - Verify splits have no overlap
   - Verify proportions are correct

2. **Whitespace Normalization** (Property 4)
   - Generate random text with various whitespace patterns
   - Verify output has normalized whitespace

3. **Marker Preservation** (Property 6)
   - Generate summaries with {{RED:text}} markers
   - Verify markers are preserved after preprocessing

4. **Summary Section Presence** (Property 9)
   - Generate various session transcriptions
   - Verify all required sections appear in output

5. **API Response Format** (Property 13)
   - Generate random session data
   - Verify response structure matches expected format

6. **Per-Session Note Generation** (Property 16)
   - Generate random session transcriptions
   - Verify notes are generated successfully
   - Verify notes contain required sections

7. **Notes Metadata Tracking** (Property 17)
   - Generate sessions with different note types
   - Verify metadata is correctly set and updated

8. **Notes Overwrite Protection** (Property 18)
   - Generate sessions with existing notes
   - Verify notes are not overwritten without regenerate flag

**Configuration**: Each property test should run at least 100 iterations to ensure robustness.

### Integration Testing

**Scope**: End-to-end workflows

**Key Test Scenarios**:
1. **Complete Training Pipeline**
   - Load dataset → Preprocess → Train → Save model
   - Verify model checkpoint exists and is valid

2. **Complete Inference Pipeline**
   - Load model → Format prompt → Generate → Parse output
   - Verify summary meets quality criteria

3. **API Integration**
   - Start backend → Call /summarize-sessions → Verify response
   - Test with real session data from database

4. **Error Recovery**
   - Trigger various errors → Verify graceful handling
   - Test fallback mechanisms

### Model Quality Testing

**Scope**: Evaluate model performance on test set

**Metrics**:
1. **ROUGE-L Score**: Measure overlap with reference summaries (target: ≥ 0.40)
2. **BLEU Score**: Measure n-gram precision
3. **Section Completeness**: Percentage of summaries with all required sections
4. **Risk Keyword Accuracy**: Percentage of risk keywords correctly formatted
5. **Word Count Compliance**: Percentage of summaries within 30-70 word range

**Process**:
1. Generate summaries for entire test set
2. Compute all metrics
3. Generate evaluation report with examples
4. Compare against baseline (Gemini API results if available)

### Performance Testing

**Scope**: Measure inference speed and resource usage

**Key Metrics**:
1. **Model Load Time**: Time to load GGUF model (target: < 30 seconds)
2. **Inference Time**: Time to generate summary (target: < 30 seconds for < 2000 tokens)
3. **Memory Usage**: Peak RAM usage during inference
4. **Throughput**: Summaries per minute

**Tools**: time, memory_profiler, pytest-benchmark

### Test Tagging

All property-based tests must be tagged with comments explicitly referencing the correctness property:

```python
def test_dataset_split_disjointness():
    """
    **Feature: llama2-summarization-migration, Property 2: Dataset Split Proportions and Disjointness**
    """
    # Test implementation
```

## Implementation Plan

### Phase 1: Training Infrastructure (Week 1-2)

1. **Setup Development Environment**
   - Install Hugging Face transformers, peft, trl, bitsandbytes
   - Setup GPU environment (if available) or prepare for CPU training
   - Download Phi-3-Mini-4K-Instruct base model
   - Verify 4-bit quantization support
   - Install trust_remote_code dependencies

2. **Implement DatasetLoader**
   - CSV loading and validation
   - Data preprocessing
   - Train/val/test splitting
   - Prompt formatting (Phi-3 chat template format)

3. **Implement FineTuner**
   - Model and tokenizer loading with 4-bit quantization
   - LoRA configuration (rank=8, Phi-3 specific target modules)
   - Training loop with validation
   - Checkpoint saving
   - Handle Phi-3 specific requirements (trust_remote_code)

4. **Run Initial Training**
   - Fine-tune Phi-3-Mini on psychotherapy dataset
   - Monitor training metrics (loss, perplexity)
   - Evaluate on validation set
   - Expected training time: 2-4 hours on GPU, 8-12 hours on CPU

### Phase 2: Model Export and Optimization (Week 2)

1. **Merge LoRA Weights**
   - Merge adapters into Phi-3-Mini base model
   - Save full model (~7.6GB)

2. **Convert to GGUF Format**
   - Install llama.cpp conversion tools
   - Convert Phi-3 model to GGUF format (requires Phi-3 specific conversion)
   - Create quantized versions:
     - Q4_K_M (~2.5GB) - **recommended for production**
     - Q5_K_M (~3GB) - higher quality option
     - Q8_0 (~4.5GB) - near-original quality for evaluation

3. **Benchmark Models**
   - Test inference speed for each quantization level
   - Measure quality degradation (ROUGE scores)
   - Test on different hardware (CPU-only, GPU)
   - Verify Q4_K_M meets performance targets (< 15s per summary)
   - Document resource requirements (RAM, CPU usage)

### Phase 3: Inference Service (Week 3)

1. **Implement LlamaInferenceEngine**
   - Model loading with llama-cpp-python
   - Generation with parameters
   - Timeout handling

2. **Refactor SummarizationService**
   - Replace Gemini API calls
   - Integrate LlamaInferenceEngine
   - Maintain API compatibility

3. **Implement PromptFormatter**
   - Single and multi-session formatting
   - System instruction templates

4. **Add Configuration Management**
   - Environment variables
   - Config file support
   - Default values

### Phase 4: Testing and Validation (Week 3-4)

1. **Write Unit Tests**
   - Test all components
   - Achieve > 80% code coverage

2. **Write Property-Based Tests**
   - Implement all 15 correctness properties
   - Run with 100+ iterations each

3. **Run Integration Tests**
   - Test complete pipelines
   - Verify API compatibility

4. **Evaluate Model Quality**
   - Compute ROUGE, BLEU scores
   - Validate section completeness
   - Compare with Gemini baseline

### Phase 5: Deployment (Week 4)

1. **Update Docker Configuration**
   - Add llama-cpp-python to requirements
   - Configure model volume mounts
   - Optimize image size

2. **Update Documentation**
   - Model training instructions
   - Deployment guide
   - Configuration reference

3. **Deploy to Production**
   - Build Docker images
   - Deploy containers
   - Monitor performance

4. **Cleanup**
   - Remove Gemini API dependencies
   - Archive old code
   - Update README

## Dependencies

### Training Dependencies
```
torch>=2.0.0
transformers>=4.35.0
peft>=0.6.0
trl>=0.7.0
datasets>=2.14.0
accelerate>=0.24.0
bitsandbytes>=0.41.0
scipy>=1.11.0
pandas>=2.0.0
```

### Inference Dependencies
```
llama-cpp-python>=0.2.0
fastapi>=0.104.1
uvicorn>=0.24.0
pydantic>=2.0.0
```

### Testing Dependencies
```
pytest>=7.4.0
hypothesis>=6.90.0
pytest-benchmark>=4.0.0
memory-profiler>=0.61.0
rouge-score>=0.1.2
nltk>=3.8.0
```

### System Dependencies
- Python 3.10+
- CUDA 11.8+ (optional, for GPU training and inference)

**Resource Requirements for Phi-3-Mini**:

| Aspect | Requirement |
|--------|-------------|
| **Training RAM** | 12GB (with 4-bit quantization) |
| **Inference RAM** | 4GB |
| **Disk Space** | 2.5GB (Q4_K_M quantized) |
| **Inference Speed (CPU)** | ~10-15 seconds per summary |
| **Inference Speed (GPU)** | ~3-5 seconds per summary |
| **Training Time** | ~2-4 hours on GPU, ~8-12 hours on CPU |

## Deployment Architecture

### Docker Compose Configuration

```yaml
services:
  backend-api:
    build:
      context: .
      dockerfile: Dockerfile.backend
    volumes:
      - ./backend:/app
      - ./models:/app/models  # Model directory
      - whisper-models:/root/.cache/huggingface
      - uploads:/app/uploads
      - database:/app
    environment:
      - PHI3_MODEL_PATH=/app/models/phi3-therapy-q4_k_m.gguf
      - PHI3_N_CTX=2048
      - PHI3_N_THREADS=4
      - PHI3_N_GPU_LAYERS=0  # Set to 32 for full GPU offload
    deploy:
      resources:
        limits:
          memory: 6G  # Reduced for Phi-3-Mini
        reservations:
          memory: 3G
```

### Model Storage Structure
```
models/
├── phi3-therapy-finetuned/        # Full fine-tuned model (~7.6GB)
│   ├── model.safetensors
│   ├── config.json
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   └── special_tokens_map.json
├── phi3-therapy-q4_k_m.gguf       # Quantized for production (~2.5GB) ⭐ PRODUCTION
├── phi3-therapy-q5_k_m.gguf       # Higher quality option (~3GB) - Optional
├── phi3-therapy-q8_0.gguf         # Near-original quality (~4.5GB) - Optional
└── training_logs/
    ├── training_metrics.json
    ├── evaluation_report.txt
    └── checkpoints/
        ├── checkpoint-100/
        ├── checkpoint-200/
        └── checkpoint-final/
```

**Quantization Levels for Phi-3-Mini**:
- **Q4_K_M**: 4-bit quantization (~2.5GB) - **Recommended for production**
- **Q5_K_M**: 5-bit quantization (~3GB) - Higher quality if RAM allows
- **Q8_0**: 8-bit quantization (~4.5GB) - Near-original quality for evaluation

## Monitoring and Observability

### Logging Strategy

**Log Levels**:
- **INFO**: Model loading, inference requests, successful operations
- **WARNING**: Fallback usage, timeout events, invalid inputs
- **ERROR**: Model failures, inference errors, system errors

**Log Format**:
```python
{
    "timestamp": "2025-11-27T10:30:00Z",
    "level": "INFO",
    "component": "LlamaInferenceEngine",
    "event": "inference_complete",
    "data": {
        "input_length": 1024,
        "output_length": 150,
        "inference_time": 12.5,
        "model": "llama2-therapy-q4"
    }
}
```

### Metrics Collection

**Key Metrics**:
1. **inference_time_seconds**: Histogram of inference durations
2. **inference_success_rate**: Percentage of successful inferences
3. **fallback_usage_count**: Counter of fallback summary usage
4. **model_load_time_seconds**: Time to load model on startup
5. **memory_usage_bytes**: Current memory usage
6. **timeout_count**: Number of inference timeouts

**Metrics Endpoint**: `/metrics` (Prometheus format)

### Health Checks

**Endpoint**: `/health`

**Response**:
```json
{
    "status": "healthy",
    "model_loaded": true,
    "model_name": "phi3-therapy-q4_k_m.gguf",
    "model_size_mb": 2560,
    "uptime_seconds": 3600,
    "total_inferences": 150,
    "success_rate": 0.98,
    "avg_inference_time_seconds": 12.3
}
```

## Security Considerations

1. **Model File Integrity**
   - Verify model file checksums on load
   - Prevent unauthorized model replacement

2. **Input Validation**
   - Sanitize all input text
   - Limit input length to prevent DoS
   - Validate session data structure

3. **Output Sanitization**
   - Validate generated summaries
   - Remove any potential injection attempts
   - Ensure formatting markers are safe

4. **Resource Limits**
   - Set memory limits in Docker
   - Implement request rate limiting
   - Timeout long-running inferences

5. **Data Privacy**
   - Keep all processing local (no external calls)
   - Log only metadata, not patient data
   - Secure model files with appropriate permissions

## Performance Optimization

### Model Optimization
1. **Quantization**: Use Q4 or Q5 GGUF for 4x smaller size and faster inference
2. **Context Window**: Limit to 2048 tokens for optimal speed
3. **Batch Processing**: Process multiple summaries in parallel when possible

### Inference Optimization
1. **Model Caching**: Keep model in memory (use_mlock=True)
2. **Thread Configuration**: Optimize n_threads based on CPU cores
3. **GPU Acceleration**: Use n_gpu_layers for GPU offloading when available

### System Optimization
1. **Docker**: Use multi-stage builds to reduce image size
2. **Memory**: Allocate sufficient RAM to avoid swapping
3. **Storage**: Use SSD for model files for faster loading

## Rollback Plan

If issues arise with the local model implementation:

1. **Immediate Rollback**
   - Revert summarization_service.py to Gemini version
   - Restore Gemini API key in configuration
   - Restart backend services

2. **Gradual Migration**
   - Run both systems in parallel
   - Compare outputs for quality
   - Gradually shift traffic to local model

3. **Fallback Strategy**
   - Keep Gemini as backup in code (optional)
   - Auto-fallback on Phi-3 model failures
   - Monitor fallback usage rate
   - Phi-3-Mini should handle all standard hardware configurations

## Success Criteria

The migration will be considered successful when:

1. ✅ Model achieves ROUGE-L ≥ 0.40 on test set
2. ✅ Inference time < 30 seconds for 95% of requests
3. ✅ Zero external API calls during summarization
4. ✅ All 15 correctness properties pass with 100+ test iterations
5. ✅ API compatibility maintained (frontend works without changes)
6. ✅ Docker deployment successful with < 10GB image size
7. ✅ System runs reliably for 7 days without critical errors
8. ✅ Memory usage stays under 8GB during normal operation

## Future Enhancements

1. **Model Improvements**
   - Fine-tune on additional therapy datasets
   - Experiment with Phi-3-Medium (14B) for better quality if resources allow
   - Implement continuous learning from user feedback
   - Try domain-specific medical models when available

2. **Performance**
   - Implement model caching strategies
   - Add batch inference support
   - Optimize for edge deployment

3. **Features**
   - Add summary customization options
   - Support multiple summary styles
   - Implement confidence scores

4. **Monitoring**
   - Add detailed performance dashboards
   - Implement A/B testing framework
   - Track summary quality over time
