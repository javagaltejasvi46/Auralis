# Requirements Document - Real-Time Transcription

## Introduction

The Real-Time Transcription system provides live speech-to-text conversion during therapy sessions using Faster-Whisper. It supports 90+ languages, automatic translation, speaker diarization, and WebSocket-based streaming for real-time updates.

## Glossary

- **Faster-Whisper**: Optimized implementation of OpenAI Whisper for transcription
- **WebSocket**: Full-duplex communication protocol for real-time data streaming
- **Speaker Diarization**: Automatic identification of different speakers in audio
- **Language Detection**: Automatic identification of spoken language
- **Auto-Translation**: Automatic conversion of transcription to English
- **Audio Chunk**: Small segment of audio data sent for processing

## Requirements

### Requirement 1: Real-Time Audio Streaming

**User Story:** As a therapist, I want to stream audio in real-time during recording, so that I can see transcription appear as I speak.

#### Acceptance Criteria

1. WHEN a therapist starts recording THEN the system SHALL establish WebSocket connection on port 8003
2. WHEN audio is captured THEN the system SHALL send chunks every 2-3 seconds
3. WHEN audio chunks are sent THEN the system SHALL encode them as base64
4. WHEN connection is established THEN the system SHALL maintain it throughout recording
5. WHEN recording stops THEN the system SHALL close WebSocket connection gracefully

### Requirement 2: Multilingual Transcription

**User Story:** As a therapist, I want to transcribe sessions in multiple languages, so that I can work with diverse patient populations.

#### Acceptance Criteria

1. WHEN audio is processed THEN the system SHALL support 90+ languages
2. WHEN language is not specified THEN the system SHALL auto-detect language from audio
3. WHEN language is detected THEN the system SHALL use appropriate language model
4. WHEN transcription is generated THEN the system SHALL preserve original language text
5. WHEN Hindi, Tamil, Telugu, or Kannada is detected THEN the system SHALL prioritize accuracy for these languages

### Requirement 3: Automatic Translation

**User Story:** As a therapist, I want automatic translation to English, so that I can understand sessions in any language.

#### Acceptance Criteria

1. WHEN non-English language is detected THEN the system SHALL automatically translate to English
2. WHEN translation is generated THEN the system SHALL preserve original transcription
3. WHEN translation is generated THEN the system SHALL store both original and translated text
4. WHEN translation is generated THEN the system SHALL record source and target languages
5. WHEN translation fails THEN the system SHALL preserve original transcription only

### Requirement 4: Speaker Diarization

**User Story:** As a therapist, I want to identify different speakers in transcription, so that I can distinguish between therapist and patient speech.

#### Acceptance Criteria

1. WHEN audio contains multiple speakers THEN the system SHALL detect speaker changes automatically
2. WHEN speaker changes THEN the system SHALL label speakers as Person 1, Person 2, etc.
3. WHEN speaker is detected THEN the system SHALL use silence gaps greater than 2 seconds as indicators
4. WHEN transcription is formatted THEN the system SHALL prefix each segment with [Person N]:
5. WHEN 2-3 speakers are present THEN the system SHALL achieve 85%+ accuracy

### Requirement 5: Real-Time Updates

**User Story:** As a therapist, I want to see transcription appear in real-time, so that I can verify accuracy during recording.

#### Acceptance Criteria

1. WHEN audio is processed THEN the system SHALL send partial transcription updates
2. WHEN partial updates are sent THEN the system SHALL include type: "partial" in message
3. WHEN recording completes THEN the system SHALL send final transcription with type: "final"
4. WHEN updates are sent THEN the system SHALL maintain 2-3 second latency
5. WHEN connection is lost THEN the system SHALL attempt reconnection

### Requirement 6: Audio File Processing

**User Story:** As a therapist, I want to upload pre-recorded audio files for transcription, so that I can transcribe sessions recorded offline.

#### Acceptance Criteria

1. WHEN audio file is uploaded THEN the system SHALL accept WAV, M4A, and MP3 formats
2. WHEN audio file is processed THEN the system SHALL extract audio data from base64 encoding
3. WHEN audio file is processed THEN the system SHALL apply same transcription pipeline as streaming
4. WHEN processing completes THEN the system SHALL return complete transcription
5. WHEN file is invalid THEN the system SHALL return error message

### Requirement 7: Model Configuration

**User Story:** As a system administrator, I want to configure transcription model settings, so that I can optimize for my hardware.

#### Acceptance Criteria

1. WHEN system starts THEN the system SHALL load Whisper medium model by default
2. WHEN GPU is available THEN the system SHALL use CUDA device for acceleration
3. WHEN CPU is used THEN the system SHALL use INT8 quantization for efficiency
4. WHEN GPU is used THEN the system SHALL use FP16 precision for accuracy
5. WHEN model is loaded THEN the system SHALL cache it for subsequent requests

### Requirement 8: Performance Optimization

**User Story:** As a therapist, I want fast transcription, so that I can see results quickly during sessions.

#### Acceptance Criteria

1. WHEN using CPU THEN the system SHALL process audio at 0.5-1.0x real-time speed
2. WHEN using GPU THEN the system SHALL process audio at 5-10x real-time speed
3. WHEN transcribing THEN the system SHALL achieve 90%+ accuracy for clear speech
4. WHEN processing 1 minute of audio THEN the system SHALL complete within 60 seconds on CPU
5. WHEN processing 1 minute of audio THEN the system SHALL complete within 10 seconds on GPU

### Requirement 9: Error Handling

**User Story:** As a therapist, I want graceful error handling when transcription fails, so that I can retry or save audio for later.

#### Acceptance Criteria

1. WHEN WebSocket connection fails THEN the system SHALL return connection error message
2. WHEN audio format is invalid THEN the system SHALL return format error message
3. WHEN model fails THEN the system SHALL return model error message
4. WHEN timeout occurs THEN the system SHALL return timeout error after 60 seconds
5. WHEN error occurs THEN the system SHALL log error details for debugging

### Requirement 10: Connection Management

**User Story:** As a therapist, I want reliable WebSocket connections, so that transcription doesn't drop during sessions.

#### Acceptance Criteria

1. WHEN connection is established THEN the system SHALL send connection confirmation
2. WHEN connection is active THEN the system SHALL maintain heartbeat
3. WHEN connection is lost THEN the system SHALL notify client
4. WHEN client disconnects THEN the system SHALL clean up resources
5. WHEN multiple clients connect THEN the system SHALL handle them independently
