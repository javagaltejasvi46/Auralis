# Implementation Plan: Phi-3-Mini Summarization Migration

## Overview
This implementation plan guides the migration from Google Gemini API to a locally trained Phi-3-Mini model for therapy session summarization. Tasks are organized to build incrementally, with testing integrated throughout.

---

## Phase 1: Training Infrastructure Setup

- [x] 1. Setup training environment and dependencies



  - Install Python dependencies: transformers, peft, trl, bitsandbytes, datasets, accelerate
  - Download Phi-3-Mini-4K-Instruct base model from Hugging Face
  - Verify 4-bit quantization support (bitsandbytes)
  - Setup GPU environment if available, otherwise configure for CPU training
  - Create models/ directory structure
  - _Requirements: 2.1, 2.2_



- [ ] 2. Implement dataset loading and preprocessing
- [ ] 2.1 Create DatasetLoader class



  - Implement CSV loading with encoding handling
  - Add data validation (check for required columns)
  - Implement train/val/test splitting (80/10/10)
  - Add error handling for malformed data
  - _Requirements: 2.1, 2.2, 3.1_



- [ ]* 2.2 Write property test for dataset splitting
  - **Property 2: Dataset Split Proportions and Disjointness**
  - **Validates: Requirements 2.2**

- [ ] 2.3 Implement text preprocessing
  - Create whitespace normalization function
  - Implement token counting and truncation (2048 limit)
  - Preserve {{RED:text}} markers in summaries
  - Add input validation
  - _Requirements: 3.2, 3.3, 3.5_

- [ ]* 2.4 Write property test for whitespace normalization
  - **Property 4: Whitespace Normalization**


  - **Validates: Requirements 3.2**

- [ ]* 2.5 Write property test for marker preservation
  - **Property 6: Clinical Marker Preservation**
  - **Validates: Requirements 3.5**

- [ ] 2.6 Implement Phi-3 prompt formatting
  - Create PromptFormatter class with Phi-3 chat template
  - Implement format_single_session method


  - Implement format_multiple_sessions method
  - Add system instruction formatting
  - _Requirements: 3.4_

- [ ]* 2.7 Write property test for prompt template consistency
  - **Property 5: Prompt Template Consistency**



  - **Validates: Requirements 3.4**

- [ ] 3. Checkpoint - Verify data pipeline
  - Ensure all tests pass, ask the user if questions arise.

---

## Phase 2: Model Training

- [ ] 4. Implement FineTuner class
- [ ] 4.1 Create model and tokenizer loading
  - Load Phi-3-Mini with 4-bit quantization
  - Configure trust_remote_code=True
  - Setup tokenizer with padding and special tokens
  - Add error handling for model loading failures
  - _Requirements: 2.3, 7.1_

- [ ] 4.2 Configure LoRA for Phi-3
  - Setup LoRA config with rank=8, alpha=16
  - Configure Phi-3 specific target modules (qkv_proj, o_proj, gate_up_proj, down_proj)
  - Enable gradient checkpointing
  - Add flash attention if available
  - _Requirements: 2.3_

- [ ] 4.3 Implement training loop
  - Setup SFTTrainer with training arguments
  - Configure batch size, learning rate, epochs
  - Add validation during training
  - Implement checkpoint saving
  - Add progress logging
  - _Requirements: 2.3, 2.4_

- [ ] 4.4 Add training error handling
  - Handle OOM errors with helpful messages
  - Skip invalid dataset entries with logging
  - Implement graceful failure on disk space issues
  - _Requirements: 2.5_

- [ ] 5. Execute model training
- [ ] 5.1 Prepare training dataset
  - Load and preprocess psychotherapy_transcriptions.csv
  - Format data with Phi-3 prompt template
  - Split into train/val/test sets
  - Save processed datasets
  - _Requirements: 2.1, 2.2, 3.4_

- [ ] 5.2 Run fine-tuning
  - Execute training script
  - Monitor training metrics (loss, perplexity)
  - Save checkpoints every 100 steps
  - Validate on validation set
  - _Requirements: 2.3, 2.4_

- [ ] 5.3 Merge LoRA weights
  - Merge LoRA adapters into base model
  - Save full fine-tuned model
  - Verify model integrity
  - _Requirements: 2.4_

- [ ] 6. Checkpoint - Verify training completion
  - Ensure all tests pass, ask the user if questions arise.

---

## Phase 3: Model Export and Optimization

- [ ] 7. Convert model to GGUF format
- [ ] 7.1 Setup llama.cpp conversion tools
  - Clone llama.cpp repository
  - Build conversion scripts
  - Install required dependencies
  - _Requirements: 1.4_

- [ ] 7.2 Convert to GGUF and quantize
  - Convert Phi-3 model to GGUF format
  - Create Q4_K_M quantization (~2.5GB)
  - Create Q5_K_M quantization (~3GB) as backup
  - Verify GGUF file integrity
  - _Requirements: 1.4, 6.1_

- [ ] 8. Implement ModelEvaluator
- [ ] 8.1 Create evaluation metrics
  - Implement ROUGE-L score computation
  - Implement BLEU score computation
  - Add section completeness checker
  - Add risk keyword formatting validator
  - _Requirements: 5.3_

- [ ] 8.2 Run model evaluation
  - Generate summaries for test set
  - Compute ROUGE-L, BLEU scores
  - Verify ROUGE-L >= 0.40 target
  - Check section completeness percentage
  - Generate evaluation report
  - _Requirements: 5.3, 12.3_

- [ ] 9. Checkpoint - Verify model quality
  - Ensure all tests pass, ask the user if questions arise.

---

## Phase 4: Inference Service Implementation

- [ ] 10. Implement LlamaInferenceEngine
- [ ] 10.1 Create model loading functionality
  - Implement GGUF model loading with llama-cpp-python
  - Configure context size, threads, GPU layers
  - Add model initialization logging
  - Handle model loading failures
  - _Requirements: 1.1, 1.3, 8.1_

- [ ]* 10.2 Write unit test for model loading
  - Test successful model load
  - Test missing model file error
  - Test configuration validation
  - _Requirements: 1.1, 1.3_

- [ ] 10.3 Implement text generation
  - Create generate() method with parameters
  - Add timeout handling (45 seconds)
  - Implement generation with temperature, top_p, top_k
  - Add error handling and logging
  - _Requirements: 4.2, 4.4, 8.2_

- [ ]* 10.4 Write property test for local model usage
  - **Property 1: No External API Calls During Summarization**
  - **Validates: Requirements 1.2**

- [ ]* 10.5 Write property test for inference logging
  - **Property 12: Inference Logging**
  - **Validates: Requirements 8.2**

- [ ] 11. Refactor SummarizationService
- [ ] 11.1 Replace Gemini with Phi-3 inference
  - Remove Gemini API configuration
  - Initialize LlamaInferenceEngine
  - Update summarize_text() to use local model
  - Update summarize_sessions() to use local model
  - Maintain API response format
  - _Requirements: 4.1, 4.5, 9.1_

- [ ] 11.2 Implement per-session note generation
  - Create summarize_single_session() method
  - Create auto_generate_session_notes() method
  - Format prompts for single sessions
  - Parse and validate output
  - _Requirements: 10.2_

- [ ]* 11.3 Write property test for per-session notes
  - **Property 16: Per-Session Note Generation**
  - **Validates: Requirements 10.2**

- [ ] 11.4 Add fallback logic
  - Implement _fallback() method for errors
  - Add timeout handling with fallback
  - Log fallback usage
  - _Requirements: 4.4, 8.4_

- [ ] 11.5 Implement output parsing and validation
  - Parse model output for required sections
  - Validate {{RED:text}} formatting
  - Check word count bounds (30-70 words)
  - _Requirements: 5.1, 5.2, 5.5_

- [ ]* 11.6 Write property test for summary sections
  - **Property 9: Required Summary Sections**
  - **Validates: Requirements 5.1**

- [ ]* 11.7 Write property test for risk keyword formatting
  - **Property 10: Risk Keyword Formatting**
  - **Validates: Requirements 5.2**

- [ ]* 11.8 Write property test for word count bounds
  - **Property 11: Summary Word Count Bounds**
  - **Validates: Requirements 5.5**

- [ ] 12. Checkpoint - Verify inference service
  - Ensure all tests pass, ask the user if questions arise.

---

## Phase 5: API Integration and Database Updates

- [ ] 13. Update database schema
- [ ] 13.1 Create database migration
  - Add notes_is_ai_generated column (BOOLEAN)
  - Add notes_edited_from_ai column (BOOLEAN)
  - Add notes_generated_at column (DATETIME)
  - Add notes_last_edited_at column (DATETIME)
  - Create migration script
  - _Requirements: 11.1, 11.2_

- [ ] 13.2 Update Session model
  - Add new fields to Session class
  - Update to_dict() method to include metadata
  - Add notes metadata helper methods
  - _Requirements: 11.1, 11.2, 11.4_

- [ ] 14. Implement new API endpoints
- [ ] 14.1 Create POST /sessions/{session_id}/generate-notes
  - Implement endpoint handler
  - Retrieve session transcription from database
  - Call summarize_single_session()
  - Save notes with AI-generated metadata
  - Return generated notes
  - _Requirements: 10.1, 10.2, 11.1_

- [ ]* 14.2 Write property test for notes metadata tracking
  - **Property 17: Notes Metadata Tracking**
  - **Validates: Requirements 11.1, 11.2, 11.3**

- [ ]* 14.3 Write property test for notes overwrite protection
  - **Property 18: Notes Overwrite Protection**
  - **Validates: Requirements 11.5**

- [ ] 14.4 Create PUT /sessions/{session_id}/notes
  - Implement endpoint handler
  - Update notes in database
  - Update metadata (edited_from_ai if modified)
  - Return updated session
  - _Requirements: 11.2, 11.3_

- [ ] 14.5 Update GET /sessions/{session_id}
  - Include notes_metadata in response
  - Format response with new fields
  - Maintain backward compatibility
  - _Requirements: 11.4_

- [ ] 14.6 Update POST /summarize-sessions
  - Ensure compatibility with new service
  - Verify response format unchanged
  - Test with multiple sessions
  - _Requirements: 9.1, 9.3, 9.4_

- [ ]* 14.7 Write property test for API response format
  - **Property 13: API Response Format Compatibility**
  - **Validates: Requirements 9.1, 9.4**

- [ ]* 14.8 Write property test for session processing equivalence
  - **Property 14: Session Processing Equivalence**
  - **Validates: Requirements 9.3**

- [ ]* 14.9 Write property test for formatting convention support
  - **Property 15: Formatting Convention Support**
  - **Validates: Requirements 9.5**

- [ ] 15. Checkpoint - Verify API integration
  - Ensure all tests pass, ask the user if questions arise.

---

## Phase 6: Configuration and Deployment

- [ ] 16. Implement configuration management
- [ ] 16.1 Create InferenceConfig class
  - Define configuration dataclass
  - Add environment variable support
  - Implement config validation
  - Add safe defaults
  - _Requirements: 7.1, 7.2, 7.4_

- [ ] 16.2 Add model path configuration
  - Support PHI3_MODEL_PATH environment variable
  - Add model size detection
  - Support switching between quantization levels
  - _Requirements: 7.2, 7.3, 7.5_

- [ ] 16.3 Implement logging configuration
  - Setup structured logging
  - Add log levels (INFO, WARNING, ERROR)
  - Implement model load logging
  - Implement inference logging
  - Add error logging with context
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 17. Update Docker configuration
- [ ] 17.1 Update Dockerfile.backend
  - Add llama-cpp-python to requirements
  - Install system dependencies for llama.cpp
  - Configure model volume mount
  - Optimize image size
  - _Requirements: 6.1, 6.5_

- [ ] 17.2 Update docker-compose.yml
  - Add model directory volume
  - Configure environment variables
  - Set memory limits (6GB)
  - Add GPU support configuration
  - _Requirements: 6.2, 6.3, 6.4_

- [ ] 17.3 Create model download script
  - Script to download Phi-3-Mini base model
  - Script to place fine-tuned model
  - Add model verification
  - _Requirements: 7.3_

- [ ] 18. Add monitoring and health checks
- [ ] 18.1 Implement metrics collection
  - Track inference time
  - Track success rate
  - Track fallback usage
  - Track memory usage
  - _Requirements: 8.5_

- [ ] 18.2 Update /health endpoint
  - Add model_loaded status
  - Add model_name and size
  - Add inference statistics
  - Add average inference time
  - _Requirements: 8.5_

- [ ] 19. Checkpoint - Verify deployment configuration
  - Ensure all tests pass, ask the user if questions arise.

---

## Phase 7: Integration Testing and Documentation

- [ ] 20. Write integration tests
- [ ]* 20.1 Test complete training pipeline
  - Load dataset → Preprocess → Format → Validate
  - Verify checkpoint creation
  - _Requirements: 12.1, 12.5_

- [ ]* 20.2 Test complete inference pipeline
  - Load model → Generate summary → Parse output
  - Verify summary quality
  - _Requirements: 12.2, 12.5_

- [ ]* 20.3 Test API integration
  - Start backend → Call endpoints → Verify responses
  - Test with real session data
  - _Requirements: 12.5_

- [ ]* 20.4 Test error recovery
  - Trigger various errors → Verify graceful handling
  - Test fallback mechanisms
  - _Requirements: 12.4_

- [ ] 21. Update documentation
- [ ] 21.1 Create training guide
  - Document training setup
  - Document dataset preparation
  - Document training execution
  - Document model export process
  - _Requirements: 2.1, 2.3_

- [ ] 21.2 Create deployment guide
  - Document Docker setup
  - Document model placement
  - Document configuration options
  - Document GPU vs CPU deployment
  - _Requirements: 6.1, 6.2, 7.1_

- [ ] 21.3 Update API documentation
  - Document new endpoints
  - Document request/response formats
  - Document notes metadata
  - Add usage examples
  - _Requirements: 10.1, 11.1_

- [ ] 21.4 Create troubleshooting guide
  - Document common errors
  - Document performance tuning
  - Document model quality issues
  - Add FAQ section
  - _Requirements: 8.1, 8.3_

- [ ] 22. Final checkpoint - Complete system verification
  - Ensure all tests pass, ask the user if questions arise.

---

## Phase 8: Production Deployment and Cleanup

- [ ] 23. Deploy to production
- [ ] 23.1 Build Docker images
  - Build backend image with Phi-3 support
  - Verify image size < 10GB
  - Test image startup
  - _Requirements: 6.5_

- [ ] 23.2 Deploy containers
  - Start backend-api container
  - Start backend-ws container
  - Verify model loading
  - Verify health checks
  - _Requirements: 6.1, 6.2_

- [ ] 23.3 Run smoke tests
  - Test single session summarization
  - Test multi-session summarization
  - Test note generation
  - Test note editing
  - Verify performance targets
  - _Requirements: 5.4, 10.2_

- [ ] 24. Monitor and validate
- [ ] 24.1 Monitor system performance
  - Check inference times (< 15s target)
  - Check memory usage (< 6GB)
  - Check success rate (> 95%)
  - Monitor error logs
  - _Requirements: 5.4, 8.2, 8.5_

- [ ] 24.2 Validate model quality
  - Review generated summaries
  - Check section completeness
  - Verify risk keyword formatting
  - Compare with Gemini baseline if available
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 25. Cleanup and finalization
- [ ] 25.1 Remove Gemini dependencies
  - Remove google-generativeai from requirements
  - Remove Gemini API key references
  - Archive old summarization_service.py
  - _Requirements: 1.2, 4.1_

- [ ] 25.2 Update README
  - Update feature list (local model)
  - Remove Gemini API setup instructions
  - Add Phi-3 model information
  - Update system requirements
  - _Requirements: 7.1_

- [ ] 25.3 Create release notes
  - Document migration changes
  - Document new features (per-session notes)
  - Document breaking changes (if any)
  - Document performance improvements
  - _Requirements: 9.1, 10.1_

- [ ] 26. Final verification
  - Ensure all tests pass, ask the user if questions arise.

---

## Success Criteria

The implementation will be considered complete when:

- ✅ Phi-3-Mini model fine-tuned on psychotherapy dataset
- ✅ Model achieves ROUGE-L ≥ 0.40 on test set
- ✅ Inference time < 15 seconds for 95% of requests
- ✅ Zero external API calls during summarization
- ✅ All 18 correctness properties pass with 100+ test iterations
- ✅ Per-session note generation working with user editing
- ✅ Notes metadata tracked correctly
- ✅ API compatibility maintained (frontend works without changes)
- ✅ Docker deployment successful with < 10GB image size
- ✅ System runs reliably for 7 days without critical errors
- ✅ Memory usage stays under 6GB during normal operation

---

## Notes

- Tasks marked with `*` are optional testing tasks that can be skipped for faster MVP
- Each checkpoint ensures tests pass before proceeding
- Property-based tests should run 100+ iterations
- Training can be done offline and model deployed separately
- GPU is optional but recommended for training (2-4 hours vs 8-12 hours on CPU)
