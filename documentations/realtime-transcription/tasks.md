# Implementation Plan

- [x] 1. Set Up Faster-Whisper
  - [x] 1.1 Install Faster-Whisper and dependencies
    - Install faster-whisper package
    - Install numpy and soundfile for audio processing
    - Download Whisper medium model (automatic on first use)
    - Verify model loads correctly
    - _Requirements: 2.1, 7.1, 7.5_

- [x] 2. Create Transcription Engine
  - [x] 2.1 Create transcription engine class
    - Initialize WhisperModel with medium size
    - Configure device (CPU or CUDA)
    - Configure compute type (int8 for CPU, float16 for GPU)
    - Set num_workers and cpu_threads
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  - [x]* 2.2 Write property test for model configuration
    - **Property 6: Model Configuration Persistence**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4**
  - [x] 2.2 Implement transcribe method
    - Accept audio data as numpy array
    - Support optional language parameter
    - Support task parameter (transcribe or translate)
    - Return transcription segments
    - Handle transcription errors
    - _Requirements: 2.1, 2.2, 2.3, 3.1_

- [x] 3. Implement Language Detection
  - [x] 3.1 Create language handler class
    - Define list of supported languages (90+)
    - Implement detect_language method using Whisper
    - Return detected language code
    - _Requirements: 2.1, 2.2, 2.3_
  - [x]* 3.2 Write property test for language detection
    - **Property 1: Language Detection Consistency**
    - **Validates: Requirements 2.2, 2.3**

- [x] 4. Implement Automatic Translation
  - [x] 4.1 Add translation support
    - Use Whisper's built-in translation (task="translate")
    - Translate non-English audio to English
    - Preserve original transcription
    - Store both original and translated text
    - Record source and target languages
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  - [x]* 4.2 Write property test for translation preservation
    - **Property 3: Translation Preservation**
    - **Validates: Requirements 3.2, 3.3, 3.4**

- [x] 5. Checkpoint - Verify transcription engine works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement Speaker Diarization
  - [x] 6.1 Create speaker diarization class
    - Set silence threshold (2 seconds)
    - Implement detect_speaker_change method
    - Track current speaker
    - _Requirements: 4.1, 4.3_
  - [x] 6.2 Implement segment labeling
    - Label segments with speaker IDs (Person 1, Person 2, etc.)
    - Detect speaker changes based on silence gaps
    - Format transcription with [Person N]: labels
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - [x]* 6.3 Write property test for speaker labeling
    - **Property 2: Speaker Label Continuity**
    - **Validates: Requirements 4.2, 4.3**

- [x] 7. Create Audio Processing Utilities
  - [x] 7.1 Create audio processor class
    - Set sample rate to 16kHz
    - Set channels to mono (1)
    - Set chunk duration to 3 seconds
    - _Requirements: 1.1, 6.1_
  - [x] 7.2 Implement audio decoding
    - Decode base64 audio data
    - Convert to numpy array
    - Handle various audio formats
    - _Requirements: 1.1, 6.1, 6.2_
  - [x] 7.3 Implement audio resampling
    - Resample audio to 16kHz if needed
    - Convert to mono if needed
    - Normalize audio amplitude
    - _Requirements: 1.1, 6.1_
  - [x]* 7.4 Write property test for audio format acceptance
    - **Property 5: Audio Format Acceptance**
    - **Validates: Requirements 6.1, 6.2**

- [x] 8. Create WebSocket Server
  - [x] 8.1 Create transcription_server.py
    - Set up WebSocket server on port 8003
    - Handle client connections
    - Send connection confirmation
    - Handle disconnections gracefully
    - _Requirements: 1.1, 1.2, 10.1, 10.2_
  - [x]* 8.2 Write property test for connection state
    - **Property 8: Connection State Consistency**
    - **Validates: Requirements 10.1, 10.2, 10.3**
  - [x] 8.2 Implement message handling
    - Parse incoming JSON messages
    - Route messages by type (audio_chunk, audio_file, stop)
    - Handle malformed messages
    - _Requirements: 1.1, 1.3, 6.1, 6.2_

- [x] 9. Implement Real-Time Audio Streaming
  - [x] 9.1 Handle audio chunk messages
    - Receive base64 encoded audio chunks
    - Decode and buffer audio data
    - Accumulate chunks for processing
    - Process when chunk duration reached (3 seconds)
    - _Requirements: 1.1, 1.2, 1.3_
  - [x] 9.2 Send partial transcription updates
    - Transcribe accumulated audio
    - Apply speaker diarization
    - Send partial update to client
    - Continue buffering for next chunk
    - _Requirements: 5.1, 5.2, 5.4_
  - [x]* 9.3 Write property test for update ordering
    - **Property 4: Real-Time Update Ordering**
    - **Validates: Requirements 5.1, 5.2, 5.4**

- [x] 10. Checkpoint - Verify real-time streaming works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement Audio File Processing
  - [x] 11.1 Handle audio file messages
    - Receive base64 encoded audio file
    - Extract audio data from data URI
    - Decode audio file
    - Process entire file at once
    - _Requirements: 6.1, 6.2, 6.3_
  - [x] 11.2 Send final transcription
    - Transcribe complete audio file
    - Apply speaker diarization
    - Translate if non-English
    - Send final transcription to client
    - _Requirements: 5.3, 6.3, 6.4_

- [x] 12. Implement Stop Recording
  - [x] 12.1 Handle stop messages
    - Process any remaining buffered audio
    - Generate final transcription
    - Apply speaker diarization and translation
    - Send final transcription to client
    - Clean up resources
    - _Requirements: 5.3, 10.4_

- [x] 13. Implement Error Handling
  - [x] 13.1 Add comprehensive error handling
    - Handle connection errors
    - Handle audio format errors
    - Handle model errors
    - Handle timeout errors (60 seconds)
    - Handle memory errors
    - Send error messages to client
    - Log errors for debugging
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 14. Optimize Performance
  - [x] 14.1 Implement performance optimizations
    - Use INT8 quantization for CPU
    - Use FP16 precision for GPU
    - Optimize chunk size (3 seconds)
    - Use async processing
    - Cache model in memory
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  - [x]* 14.2 Write property test for performance
    - **Property 7: Performance Target Achievement**
    - **Validates: Requirements 8.1, 8.4**

- [x] 15. Checkpoint - Verify performance and error handling
  - Ensure all tests pass, ask the user if questions arise.

- [x] 16. Create Frontend WebSocket Client
  - [x] 16.1 Create WebSocket service in frontend/src/services/
    - Connect to ws://localhost:8003
    - Handle connection events
    - Send audio chunks
    - Receive transcription updates
    - Handle disconnection and reconnection
    - _Requirements: 1.1, 1.2, 5.1, 10.1, 10.5_

- [x] 17. Create Audio Recorder Component
  - [x] 17.1 Create audio recorder in SessionRecordingScreen
    - Request microphone permission
    - Configure audio recording (16kHz, mono, PCM)
    - Record audio in chunks (3 seconds)
    - Encode chunks as base64
    - Send chunks via WebSocket
    - _Requirements: 1.1, 1.2, 1.3_

- [x] 18. Create Transcription Display
  - [x] 18.1 Add transcription display to SessionRecordingScreen
    - Show real-time partial transcriptions
    - Update display as new chunks arrive
    - Show final transcription when recording stops
    - Display speaker labels ([Person 1], [Person 2])
    - Show language indicator
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 19. Implement Connection Management
  - [x] 19.1 Add connection state management
    - Show connection status indicator
    - Handle connection failures
    - Implement automatic reconnection
    - Show error messages
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 20. Add Language Selection
  - [x] 20.1 Add language selection to recording screen
    - Dropdown for language selection
    - Auto-detect option
    - Send selected language with audio chunks
    - Display detected language
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 21. Implement Audio File Upload
  - [x] 21.1 Add audio file upload functionality
    - File picker for audio files (.wav, .m4a, .mp3)
    - Read file as base64
    - Send via WebSocket
    - Show upload progress
    - Display transcription result
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 22. Add Translation Display
  - [x] 22.1 Show translation alongside original
    - Display original transcription
    - Display English translation (if available)
    - Show source and target languages
    - Toggle between original and translation
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 23. Final Checkpoint - Complete integration testing
  - Ensure all tests pass, ask the user if questions arise.
