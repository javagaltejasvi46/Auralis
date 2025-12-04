# Requirements Document - Session Management

## Introduction

The Session Management system provides comprehensive therapy session recording, storage, and management capabilities. It handles session creation, audio file uploads, transcription storage, and session metadata tracking.

## Glossary

- **Session**: A single therapy appointment with transcription and clinical notes
- **Transcription**: Text representation of spoken audio from therapy session
- **Audio File**: Recorded audio of therapy session (WAV, M4A, MP3)
- **Session Number**: Auto-incrementing identifier for patient sessions
- **Clinical Notes**: Therapist observations and AI-generated summaries
- **Session Metadata**: Information about AI generation and edit history

## Requirements

### Requirement 1: Session Creation

**User Story:** As a therapist, I want to create a session record for each patient visit, so that I can maintain chronological session history.

#### Acceptance Criteria

1. WHEN a therapist creates a session THEN the system SHALL auto-increment session number for that patient
2. WHEN a session is created THEN the system SHALL record date, time, and duration
3. WHEN a session is created THEN the system SHALL link it to the patient profile
4. WHEN transcription is provided THEN the system SHALL store original and translated text
5. WHEN session is created THEN the system SHALL initialize completion status as false

### Requirement 2: Session Retrieval

**User Story:** As a therapist, I want to view all sessions for a patient, so that I can review treatment progress over time.

#### Acceptance Criteria

1. WHEN a therapist requests patient sessions THEN the system SHALL return all sessions for that patient
2. WHEN sessions are returned THEN the system SHALL order them by date descending
3. WHEN sessions are returned THEN the system SHALL include session number, date, duration, and language
4. WHEN a therapist requests specific session THEN the system SHALL return complete session details
5. WHEN session is not found THEN the system SHALL return 404 Not Found error

### Requirement 3: Session Updates

**User Story:** As a therapist, I want to edit session transcriptions and notes, so that I can correct errors and add observations.

#### Acceptance Criteria

1. WHEN a therapist updates session THEN the system SHALL allow editing transcription text
2. WHEN a therapist updates session THEN the system SHALL allow editing clinical notes
3. WHEN a therapist updates session THEN the system SHALL allow updating diagnosis and treatment plan
4. WHEN a therapist updates session THEN the system SHALL allow marking session as completed
5. WHEN session is updated THEN the system SHALL record update timestamp

### Requirement 4: Audio File Management

**User Story:** As a therapist, I want to upload audio files for sessions, so that I can store recordings for future reference.

#### Acceptance Criteria

1. WHEN a therapist uploads audio THEN the system SHALL accept WAV, M4A, and MP3 formats
2. WHEN audio is uploaded THEN the system SHALL store file in session-specific directory
3. WHEN audio is uploaded THEN the system SHALL record file path and size
4. WHEN audio file exists THEN the system SHALL replace it with new upload
5. WHEN audio is uploaded THEN the system SHALL validate file size and format

### Requirement 5: Session Deletion

**User Story:** As a therapist, I want to delete sessions if needed, so that I can remove incorrect or duplicate entries.

#### Acceptance Criteria

1. WHEN a therapist deletes session THEN the system SHALL permanently remove session record
2. WHEN session is deleted THEN the system SHALL delete associated audio file
3. WHEN session is deleted THEN the system SHALL verify therapist owns the patient
4. WHEN session is deleted THEN the system SHALL return success confirmation
5. WHEN session deletion fails THEN the system SHALL return appropriate error message

### Requirement 6: Transcription Storage

**User Story:** As a therapist, I want to store both original and translated transcriptions, so that I can reference either version.

#### Acceptance Criteria

1. WHEN transcription is stored THEN the system SHALL save original language text
2. WHEN translation is available THEN the system SHALL save translated text
3. WHEN transcription is stored THEN the system SHALL record source and target languages
4. WHEN transcription is retrieved THEN the system SHALL return both original and translated versions
5. WHEN transcription is updated THEN the system SHALL preserve translation metadata

### Requirement 7: Session Metadata Tracking

**User Story:** As a therapist, I want to track AI-generated content and edits, so that I can distinguish between AI and human input.

#### Acceptance Criteria

1. WHEN notes are AI-generated THEN the system SHALL set is_ai_generated flag to true
2. WHEN AI notes are edited THEN the system SHALL set edited_from_ai flag to true
3. WHEN notes are generated THEN the system SHALL record generation timestamp
4. WHEN notes are edited THEN the system SHALL record last edit timestamp
5. WHEN session is retrieved THEN the system SHALL include all metadata flags and timestamps

### Requirement 8: Data Isolation

**User Story:** As a therapist, I want to ensure I can only access sessions for my patients, so that patient privacy is protected.

#### Acceptance Criteria

1. WHEN a therapist queries sessions THEN the system SHALL verify patient belongs to therapist
2. WHEN a therapist updates session THEN the system SHALL verify ownership before allowing changes
3. WHEN a therapist deletes session THEN the system SHALL verify ownership before deletion
4. WHEN ownership verification fails THEN the system SHALL return 404 Not Found
5. WHEN session is accessed THEN the system SHALL use therapist ID from authentication token
