# Requirements Document - AI Notes Generation

## Introduction

The AI Notes Generation system provides automated clinical note generation from therapy session transcriptions using Phi-3-Mini language model. It creates structured, professional clinical summaries with risk keyword highlighting and supports editing after generation.

## Glossary

- **Clinical Notes**: Structured summary of therapy session following professional format
- **Phi-3-Mini**: Microsoft's 3.8B parameter language model for text generation
- **Ollama**: Local AI model serving platform
- **Risk Keywords**: Words indicating safety concerns (suicide, self-harm, violence, abuse)
- **Markdown Formatting**: Text formatting using **bold** and {{RED:text}} syntax
- **AI Generation Metadata**: Timestamps and flags tracking AI-generated content

## Requirements

### Requirement 1: AI Note Generation

**User Story:** As a therapist, I want to automatically generate clinical notes from transcriptions, so that I can save time on documentation.

#### Acceptance Criteria

1. WHEN a therapist requests note generation THEN the system SHALL use Phi-3-Mini model via Ollama
2. WHEN notes are generated THEN the system SHALL complete within 15 seconds
3. WHEN notes are generated THEN the system SHALL include Chief Complaint, Emotional State, Risk, Intervention, Progress, and Plan sections
4. WHEN notes are generated THEN the system SHALL format sections with **bold** headers
5. WHEN notes are generated THEN the system SHALL keep each section under 50 words

### Requirement 2: Risk Keyword Detection

**User Story:** As a therapist, I want risk-related keywords automatically highlighted, so that I can quickly identify safety concerns.

#### Acceptance Criteria

1. WHEN notes contain risk keywords THEN the system SHALL detect suicide, self-harm, kill, hurt myself, violence, abuse, overdose
2. WHEN risk keywords are detected THEN the system SHALL format them as {{RED:keyword}}
3. WHEN notes are displayed THEN the system SHALL render {{RED:text}} in red color
4. WHEN risk detection occurs THEN the system SHALL use case-insensitive matching
5. WHEN multiple risk keywords exist THEN the system SHALL highlight all occurrences

### Requirement 3: Note Editing

**User Story:** As a therapist, I want to review and edit AI-generated notes, so that I can ensure accuracy and add personal observations.

#### Acceptance Criteria

1. WHEN notes are generated THEN the system SHALL allow immediate editing
2. WHEN notes are edited THEN the system SHALL preserve markdown formatting
3. WHEN notes are edited THEN the system SHALL update edited_from_ai flag to true
4. WHEN notes are edited THEN the system SHALL record last edit timestamp
5. WHEN notes are saved THEN the system SHALL validate required fields

### Requirement 4: Regeneration Support

**User Story:** As a therapist, I want to regenerate notes if unsatisfied with initial output, so that I can get better summaries.

#### Acceptance Criteria

1. WHEN regenerate is requested THEN the system SHALL generate new notes from transcription
2. WHEN regenerate is requested THEN the system SHALL replace existing notes
3. WHEN regenerate is requested THEN the system SHALL reset edited_from_ai flag to false
4. WHEN regenerate is requested THEN the system SHALL update generation timestamp
5. WHEN regenerate fails THEN the system SHALL preserve existing notes

### Requirement 5: Metadata Tracking

**User Story:** As a therapist, I want to track which notes are AI-generated versus manually written, so that I can distinguish between automated and human input.

#### Acceptance Criteria

1. WHEN notes are AI-generated THEN the system SHALL set is_ai_generated flag to true
2. WHEN notes are manually written THEN the system SHALL set is_ai_generated flag to false
3. WHEN AI notes are edited THEN the system SHALL set edited_from_ai flag to true
4. WHEN notes are generated THEN the system SHALL record generation timestamp
5. WHEN notes are edited THEN the system SHALL record last edit timestamp

### Requirement 6: Prompt Engineering

**User Story:** As a system administrator, I want the AI to follow a consistent clinical format, so that notes are professional and standardized.

#### Acceptance Criteria

1. WHEN prompt is constructed THEN the system SHALL use Phi-3 chat template format
2. WHEN prompt is constructed THEN the system SHALL include section structure instructions
3. WHEN prompt is constructed THEN the system SHALL specify risk keyword highlighting rules
4. WHEN prompt is constructed THEN the system SHALL limit output to 50 words per section
5. WHEN prompt is constructed THEN the system SHALL include transcription context

### Requirement 7: Error Handling

**User Story:** As a therapist, I want graceful error handling when AI generation fails, so that I can still document sessions manually.

#### Acceptance Criteria

1. WHEN Ollama is unavailable THEN the system SHALL return clear error message
2. WHEN generation times out THEN the system SHALL return timeout error after 30 seconds
3. WHEN model fails THEN the system SHALL preserve existing notes
4. WHEN error occurs THEN the system SHALL log error details for debugging
5. WHEN generation fails THEN the system SHALL allow manual note entry

### Requirement 8: Performance Optimization

**User Story:** As a therapist, I want fast note generation, so that I can quickly complete documentation.

#### Acceptance Criteria

1. WHEN using CPU THEN the system SHALL generate notes within 15 seconds
2. WHEN using GPU THEN the system SHALL generate notes within 5 seconds
3. WHEN model is loaded THEN the system SHALL cache it for subsequent requests
4. WHEN multiple requests occur THEN the system SHALL queue them appropriately
5. WHEN generation completes THEN the system SHALL return inference time metric
