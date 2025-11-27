# Requirements Document

## Introduction

This document outlines the requirements for migrating the Auralis medical transcription system from Google Gemini API to a locally trained Llama2 model for therapy session summarization. The migration aims to improve reliability, reduce external dependencies, enhance privacy, and leverage the existing psychotherapy dataset for domain-specific fine-tuning.

## Glossary

- **Auralis System**: The medical voice transcription and management system for mental health professionals
- **Summarization Service**: The component responsible for generating therapy session summaries
- **Llama2 Model**: Meta's open-source large language model used for text generation
- **Fine-tuning**: The process of training a pre-trained model on domain-specific data
- **Inference Engine**: The runtime system that executes the trained model for predictions
- **Training Dataset**: The psychotherapy_transcriptions.csv file containing session transcriptions and summaries
- **Backend API**: The FastAPI server running on port 8002
- **Model Checkpoint**: A saved state of the trained model
- **Quantization**: Technique to reduce model size and improve inference speed
- **GGUF Format**: GPT-Generated Unified Format for efficient model storage and inference

## Requirements

### Requirement 1: Local Model Infrastructure

**User Story:** As a system administrator, I want to run the summarization model locally, so that the system is independent of external APIs and maintains patient data privacy.

#### Acceptance Criteria

1. WHEN the Backend API starts, THEN the Summarization Service SHALL load the Llama2 model from local storage
2. WHEN a summarization request is received, THEN the Summarization Service SHALL process it using the local model without external API calls
3. WHEN the local model is unavailable, THEN the Summarization Service SHALL return a clear error message and log the failure
4. THE Summarization Service SHALL support model loading in GGUF format for efficient inference
5. THE Summarization Service SHALL initialize within 30 seconds of Backend API startup

### Requirement 2: Model Training Pipeline

**User Story:** As a developer, I want to fine-tune Llama2 on the psychotherapy dataset, so that the model generates domain-specific, clinically accurate summaries.

#### Acceptance Criteria

1. WHEN the training script is executed, THEN the system SHALL load and validate the psychotherapy_transcriptions.csv dataset
2. WHEN the dataset is loaded, THEN the system SHALL split it into training (80%), validation (10%), and test (10%) sets
3. WHEN fine-tuning begins, THEN the system SHALL use LoRA (Low-Rank Adaptation) for parameter-efficient training
4. WHEN training completes, THEN the system SHALL save model checkpoints with validation metrics
5. WHEN the training dataset contains invalid entries, THEN the system SHALL skip them and log warnings without halting training

### Requirement 3: Data Preprocessing and Validation

**User Story:** As a data scientist, I want to preprocess the psychotherapy dataset, so that the model receives clean, properly formatted training data.

#### Acceptance Criteria

1. WHEN the dataset is loaded, THEN the system SHALL validate that each record contains both session_transcription and session_summary fields
2. WHEN preprocessing text, THEN the system SHALL normalize whitespace and remove invalid characters
3. WHEN a transcription exceeds 2048 tokens, THEN the system SHALL truncate it and log a warning
4. WHEN formatting training examples, THEN the system SHALL use a consistent prompt template matching the inference format
5. THE system SHALL preserve the clinical terminology and formatting markers (e.g., {{RED:text}}) from the original summaries

### Requirement 4: Inference Service Integration

**User Story:** As a backend developer, I want to integrate the trained model into the existing API, so that summarization requests work seamlessly with the new model.

#### Acceptance Criteria

1. WHEN the summarization_service.py module initializes, THEN it SHALL load the fine-tuned Llama2 model instead of configuring Gemini API
2. WHEN the summarize_text method is called, THEN it SHALL generate summaries using the local model with appropriate temperature and token limits
3. WHEN the summarize_sessions method is called, THEN it SHALL format multiple sessions and generate a comprehensive summary
4. WHEN inference takes longer than 60 seconds, THEN the system SHALL timeout and return a fallback summary
5. THE Inference Service SHALL maintain the same API interface as the current Gemini-based service

### Requirement 5: Model Performance and Quality

**User Story:** As a therapist, I want the AI-generated summaries to be accurate and clinically relevant, so that I can trust them for patient documentation.

#### Acceptance Criteria

1. WHEN the model generates a summary, THEN it SHALL include all required sections: Chief Complaint, Emotional State, Risk Assessment, Intervention, and Plan
2. WHEN the summary contains risk keywords, THEN the system SHALL format them with {{RED:keyword}} markers
3. WHEN evaluated on the test set, THEN the model SHALL achieve a ROUGE-L score of at least 0.40
4. WHEN generating summaries, THEN the model SHALL complete inference within 30 seconds for sessions under 2000 tokens
5. THE model SHALL generate summaries between 30 and 70 words unless the session content requires more detail

### Requirement 6: Deployment and Containerization

**User Story:** As a DevOps engineer, I want the model and dependencies packaged in Docker containers, so that deployment is consistent and reliable across environments.

#### Acceptance Criteria

1. WHEN the Docker container builds, THEN it SHALL include all required dependencies for Llama2 inference
2. WHEN the container starts, THEN it SHALL mount the model directory as a volume for easy model updates
3. WHEN GPU is available, THEN the system SHALL utilize it for faster inference
4. WHEN GPU is unavailable, THEN the system SHALL fall back to CPU inference with quantized models
5. THE Docker image SHALL be optimized to remain under 10GB in size

### Requirement 7: Configuration and Model Management

**User Story:** As a system administrator, I want to configure model parameters without code changes, so that I can optimize performance for different deployment environments.

#### Acceptance Criteria

1. WHEN the system starts, THEN it SHALL read model configuration from environment variables or a config file
2. THE configuration SHALL include model_path, max_tokens, temperature, top_p, and device settings
3. WHEN a new model checkpoint is available, THEN the administrator SHALL be able to update it by replacing files in the model directory
4. WHEN configuration is invalid, THEN the system SHALL use safe defaults and log warnings
5. THE system SHALL support switching between different model sizes (7B, 13B) via configuration

### Requirement 8: Monitoring and Logging

**User Story:** As a system administrator, I want detailed logging of model operations, so that I can troubleshoot issues and monitor performance.

#### Acceptance Criteria

1. WHEN the model loads, THEN the system SHALL log the model name, size, and load time
2. WHEN inference is performed, THEN the system SHALL log the input length, output length, and processing time
3. WHEN errors occur during inference, THEN the system SHALL log the full error with context
4. WHEN the system uses fallback summaries, THEN it SHALL log the reason and frequency
5. THE system SHALL expose metrics for average inference time, success rate, and error counts

### Requirement 9: Backward Compatibility

**User Story:** As a frontend developer, I want the API interface to remain unchanged, so that the mobile app continues to work without modifications.

#### Acceptance Criteria

1. WHEN the frontend calls /summarize-sessions, THEN it SHALL receive responses in the same format as before
2. WHEN the frontend calls /translate, THEN it SHALL continue to work with the existing translation service
3. WHEN session data is submitted, THEN the system SHALL process it identically to the Gemini-based implementation
4. THE response structure SHALL include summary, session_count, and key_points fields
5. THE system SHALL maintain support for the {{RED:text}} formatting convention

### Requirement 10: Per-Session Note Generation

**User Story:** As a therapist, I want AI-generated clinical notes for each individual session that I can review and edit, so that I can quickly document sessions while maintaining control over the final content.

#### Acceptance Criteria

1. WHEN a session recording is completed, THEN the system SHALL offer to auto-generate clinical notes for that session
2. WHEN the therapist requests note generation, THEN the system SHALL generate a summary based on the session transcription within 30 seconds
3. WHEN AI-generated notes are displayed, THEN the therapist SHALL be able to edit them before saving
4. WHEN the therapist edits AI-generated notes, THEN the system SHALL track that the notes were AI-assisted but user-modified
5. WHEN viewing a session, THEN the system SHALL indicate whether notes are AI-generated, user-written, or AI-assisted

### Requirement 11: Notes Management and Persistence

**User Story:** As a therapist, I want my session notes to be saved reliably with metadata about their origin, so that I can maintain accurate records and understand the source of documentation.

#### Acceptance Criteria

1. WHEN AI-generated notes are saved, THEN the system SHALL store metadata indicating they are AI-generated with a timestamp
2. WHEN a user edits AI-generated notes, THEN the system SHALL update metadata to reflect user modification
3. WHEN notes are manually written by the user, THEN the system SHALL mark them as user-written
4. WHEN retrieving a session, THEN the system SHALL include notes metadata in the response
5. THE system SHALL prevent accidental overwriting of existing notes unless explicitly requested by the user

### Requirement 12: Testing and Validation

**User Story:** As a quality assurance engineer, I want comprehensive tests for the new model integration, so that I can verify correctness before production deployment.

#### Acceptance Criteria

1. WHEN the test suite runs, THEN it SHALL validate model loading and initialization
2. WHEN testing inference, THEN the system SHALL verify output format and content structure
3. WHEN testing with the validation dataset, THEN the system SHALL compute and report quality metrics
4. WHEN testing error handling, THEN the system SHALL verify graceful degradation and fallback behavior
5. THE test suite SHALL include integration tests for the complete summarization pipeline
