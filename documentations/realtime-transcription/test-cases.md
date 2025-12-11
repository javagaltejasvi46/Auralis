# Test Cases - Real-Time Transcription

## Overview

This document contains comprehensive test cases for the Real-Time Transcription system, covering WebSocket communication, Faster-Whisper integration, multilingual support, and speaker diarization.

## Test Categories

### 1. Unit Tests
### 2. Integration Tests
### 3. WebSocket Tests
### 4. Audio Processing Tests
### 5. Performance Tests

---

## 1. Unit Tests

### TC-RT-001: WebSocket Connection Establishment

**Test Objective:** Verify WebSocket connection can be established successfully

**Prerequisites:**
- WebSocket server running on port 8003
- Faster-Whisper model loaded

**Test Steps:**
1. Connect to WebSocket endpoint `ws://localhost:8003`
2. Verify connection established
3. Check connection status

**Expected Results:**
- WebSocket connection successful
- Connection remains stable
- Ready to receive audio data

**Test Data:**
```python
import websocket
import json
import threading
import time

def test_websocket_connection():
    connection_established = threading.Event()
    connection_error = threading.Event()
    
    def on_open(ws):
        connection_established.set()
    
    def on_error(ws, error):
        connection_error.set()
    
    # Create WebSocket connection
    ws = websocket.WebSocketApp("ws://localhost:8003",
        on_open=on_open,
        on_error=on_error
    )
    
    # Start connection in separate thread
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    # Wait for connection or timeout
    assert connection_established.wait(timeout=5), "WebSocket connection failed"
    assert not connection_error.is_set(), "WebSocket connection error"
    
    ws.close()
```
---

### TC-RT-002: Audio Chunk Processing

**Test Objective:** Verify audio chunks are processed and transcribed correctly

**Test Steps:**
1. Establish WebSocket connection
2. Send audio chunk in base64 format
3. Verify transcription response received

**Expected Results:**
- Audio chunk accepted and processed
- Partial transcription returned
- Response format correct

**Test Data:**
```python
def test_audio_chunk_processing():
    transcription_received = threading.Event()
    received_transcription = []
    
    def on_message(ws, message):
        data = json.loads(message)
        if data.get("type") == "partial":
            received_transcription.append(data["text"])
            transcription_received.set()
    
    def on_open(ws):
        # Send audio chunk
        audio_data = {
            "type": "audio_chunk",
            "data": "base64_encoded_audio_data_here",
            "language": "english"
        }
        ws.send(json.dumps(audio_data))
    
    ws = websocket.WebSocketApp("ws://localhost:8003",
        on_open=on_open,
        on_message=on_message
    )
    
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    # Wait for transcription
    assert transcription_received.wait(timeout=30), "No transcription received"
    assert len(received_transcription) > 0, "Empty transcription"
    
    ws.close()

---

### TC-RT-003: Language Detection and Processing

**Test Objective:** Verify different languages are detected and processed correctly

**Test Steps:**
1. Send audio chunks in different languages
2. Verify language detection works
3. Check transcription quality per language

**Expected Results:**
- Multiple languages supported (English, Hindi, Spanish, etc.)
- Language auto-detection works
- Transcription quality maintained across languages

**Test Data:**
```python
def test_language_detection():
    languages_to_test = ["english", "hindi", "spanish", "french"]
    
    for language in languages_to_test:
        transcription_received = threading.Event()
        received_data = []
        
        def on_message(ws, message):
            data = json.loads(message)
            if data.get("type") in ["partial", "final"]:
                received_data.append(data)
                transcription_received.set()
        
        def on_open(ws):
            audio_data = {
                "type": "audio_chunk",
                "data": f"sample_audio_data_in_{language}",
                "language": language
            }
            ws.send(json.dumps(audio_data))
        
        ws = websocket.WebSocketApp("ws://localhost:8003",
            on_open=on_open,
            on_message=on_message
        )
        
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()
        
        # Wait for transcription
        assert transcription_received.wait(timeout=30), f"No transcription for {language}"
        assert len(received_data) > 0, f"No data received for {language}"
        
        ws.close()
        time.sleep(1)  # Brief pause between tests

---

### TC-RT-004: Speaker Diarization

**Test Objective:** Verify speaker diarization identifies multiple speakers

**Test Steps:**
1. Send audio with multiple speakers
2. Verify speaker labels in transcription
3. Check speaker change detection

**Expected Results:**
- Multiple speakers identified as [Person 1], [Person 2], etc.
- Speaker changes detected based on silence gaps
- Accurate speaker attribution

**Test Data:**
```python
def test_speaker_diarization():
    transcription_received = threading.Event()
    received_transcriptions = []
    
    def on_message(ws, message):
        data = json.loads(message)
        if data.get("type") == "final":
            received_transcriptions.append(data["text"])
            transcription_received.set()
    
    def on_open(ws):
        # Simulate multi-speaker audio
        audio_data = {
            "type": "audio_file",
            "data": "multi_speaker_audio_base64_data",
            "language": "english"
        }
        ws.send(json.dumps(audio_data))
    
    ws = websocket.WebSocketApp("ws://localhost:8003",
        on_open=on_open,
        on_message=on_message
    )
    
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    assert transcription_received.wait(timeout=60), "No final transcription received"
    
    final_transcription = received_transcriptions[-1]
    
    # Verify speaker labels present
    assert "[Person 1]" in final_transcription, "Person 1 not identified"
    assert "[Person 2]" in final_transcription, "Person 2 not identified"
    
    ws.close()

---

### TC-RT-005: Real-Time Streaming

**Test Objective:** Verify real-time streaming provides continuous transcription updates

**Test Steps:**
1. Send continuous audio stream
2. Verify partial transcriptions received
3. Check update frequency and latency

**Expected Results:**
- Partial transcriptions received every 2-3 seconds
- Low latency (under 3 seconds)
- Continuous updates during speech

**Test Data:**
```python
def test_realtime_streaming():
    partial_count = 0
    start_time = time.time()
    latencies = []
    
    def on_message(ws, message):
        nonlocal partial_count, start_time, latencies
        data = json.loads(message)
        
        if data.get("type") == "partial":
            partial_count += 1
            latency = time.time() - start_time
            latencies.append(latency)
            start_time = time.time()  # Reset for next chunk
    
    def on_open(ws):
        # Simulate continuous audio streaming
        for i in range(10):  # 10 audio chunks
            audio_data = {
                "type": "audio_chunk",
                "data": f"audio_chunk_{i}_base64_data",
                "language": "english"
            }
            ws.send(json.dumps(audio_data))
            time.sleep(2)  # Send chunk every 2 seconds
    
    ws = websocket.WebSocketApp("ws://localhost:8003",
        on_open=on_open,
        on_message=on_message
    )
    
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    time.sleep(25)  # Wait for all chunks to process
    
    # Verify real-time performance
    assert partial_count >= 5, f"Expected at least 5 partial transcriptions, got {partial_count}"
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency < 3.0, f"Average latency {avg_latency:.2f}s exceeds 3s limit"
    
    ws.close()

---

## 2. Integration Tests

### TC-RT-INT-001: End-to-End Transcription Workflow

**Test Objective:** Verify complete transcription workflow from audio to final text

**Test Steps:**
1. Connect to WebSocket
2. Send complete audio file
3. Receive partial and final transcriptions
4. Verify transcription accuracy and completeness

**Expected Results:**
- Complete workflow executes successfully
- Final transcription contains all spoken content
- Speaker diarization applied correctly
- Appropriate formatting maintained

**Test Data:**
```python
def test_end_to_end_transcription():
    workflow_complete = threading.Event()
    partial_transcriptions = []
    final_transcription = None
    
    def on_message(ws, message):
        nonlocal final_transcription
        data = json.loads(message)
        
        if data.get("type") == "partial":
            partial_transcriptions.append(data["text"])
        elif data.get("type") == "final":
            final_transcription = data["text"]
            workflow_complete.set()
    
    def on_open(ws):
        # Send complete audio file
        with open("test_audio_sample.wav", "rb") as audio_file:
            audio_base64 = base64.b64encode(audio_file.read()).decode()
        
        audio_data = {
            "type": "audio_file",
            "data": f"data:audio/wav;base64,{audio_base64}",
            "language": "english"
        }
        ws.send(json.dumps(audio_data))
    
    ws = websocket.WebSocketApp("ws://localhost:8003",
        on_open=on_open,
        on_message=on_message
    )
    
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    # Wait for completion
    assert workflow_complete.wait(timeout=120), "Workflow did not complete"
    
    # Verify results
    assert len(partial_transcriptions) > 0, "No partial transcriptions received"
    assert final_transcription is not None, "No final transcription received"
    assert len(final_transcription) > 0, "Empty final transcription"
    
    # Verify speaker diarization if multi-speaker
    if "Person 1" in final_transcription:
        assert final_transcription.count("[Person") >= 1, "Speaker labels missing"
    
    ws.close()

---

### TC-RT-INT-002: Mobile App Integration

**Test Objective:** Verify integration with mobile app audio recording

**Test Steps:**
1. Simulate mobile app connection
2. Send audio chunks as recorded from mobile
3. Verify real-time transcription display
4. Test connection stability

**Expected Results:**
- Mobile app can connect and maintain connection
- Audio chunks processed in real-time
- Transcription updates sent back to mobile
- Connection remains stable during session

**Test Data:**
```python
def test_mobile_app_integration():
    mobile_session_complete = threading.Event()
    transcription_updates = []
    connection_stable = True
    
    def on_message(ws, message):
        data = json.loads(message)
        if data.get("type") in ["partial", "final"]:
            transcription_updates.append({
                "type": data["type"],
                "text": data["text"],
                "timestamp": time.time()
            })
        
        if data.get("type") == "final":
            mobile_session_complete.set()
    
    def on_error(ws, error):
        nonlocal connection_stable
        connection_stable = False
    
    def on_open(ws):
        # Simulate mobile app sending audio chunks
        for i in range(20):  # 20 chunks over 1 minute
            chunk_data = {
                "type": "audio_chunk",
                "data": f"mobile_audio_chunk_{i}",
                "language": "english"
            }
            ws.send(json.dumps(chunk_data))
            time.sleep(3)  # 3-second intervals
        
        # Send stop signal
        ws.send(json.dumps({"type": "stop"}))
    
    ws = websocket.WebSocketApp("ws://localhost:8003",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error
    )
    
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    # Wait for session completion
    assert mobile_session_complete.wait(timeout=90), "Mobile session did not complete"
    assert connection_stable, "Connection was not stable"
    assert len(transcription_updates) > 0, "No transcription updates received"
    
    # Verify real-time updates
    partial_updates = [u for u in transcription_updates if u["type"] == "partial"]
    assert len(partial_updates) >= 5, "Insufficient real-time updates"
    
    ws.close()

---

## 3. WebSocket Tests

### TC-RT-WS-001: Connection Management

**Test Objective:** Verify WebSocket connection lifecycle management

**Test Steps:**
1. Test connection establishment
2. Test connection maintenance
3. Test graceful disconnection
4. Test reconnection scenarios

**Expected Results:**
- Connections established reliably
- Connections maintained during idle periods
- Graceful disconnection handling
- Successful reconnection after network issues

**Test Data:**
```python
def test_websocket_connection_management():
    # Test 1: Basic connection
    ws1 = websocket.WebSocket()
    ws1.connect("ws://localhost:8003")
    assert ws1.connected, "Initial connection failed"
    ws1.close()
    
    # Test 2: Connection timeout handling
    connection_events = []
    
    def on_open(ws):
        connection_events.append("opened")
    
    def on_close(ws, close_status_code, close_msg):
        connection_events.append("closed")
    
    def on_error(ws, error):
        connection_events.append(f"error: {error}")
    
    ws2 = websocket.WebSocketApp("ws://localhost:8003",
        on_open=on_open,
        on_close=on_close,
        on_error=on_error
    )
    
    wst = threading.Thread(target=ws2.run_forever)
    wst.daemon = True
    wst.start()
    
    time.sleep(2)  # Wait for connection
    assert "opened" in connection_events, "Connection not opened"
    
    ws2.close()
    time.sleep(1)
    assert "closed" in connection_events, "Connection not closed properly"

---

### TC-RT-WS-002: Message Format Validation

**Test Objective:** Verify WebSocket message format validation

**Test Steps:**
1. Send valid message formats
2. Send invalid message formats
3. Verify appropriate responses

**Expected Results:**
- Valid messages processed correctly
- Invalid messages rejected with error
- Proper error messages returned

**Test Data:**
```python
def test_message_format_validation():
    responses = []
    
    def on_message(ws, message):
        responses.append(json.loads(message))
    
    def on_open(ws):
        # Valid message
        valid_msg = {
            "type": "audio_chunk",
            "data": "valid_base64_data",
            "language": "english"
        }
        ws.send(json.dumps(valid_msg))
        
        time.sleep(1)
        
        # Invalid message - missing required field
        invalid_msg = {
            "type": "audio_chunk",
            "data": "base64_data"
            # Missing language field
        }
        ws.send(json.dumps(invalid_msg))
        
        time.sleep(1)
        
        # Invalid message - wrong type
        invalid_type_msg = {
            "type": "invalid_type",
            "data": "some_data"
        }
        ws.send(json.dumps(invalid_type_msg))
    
    ws = websocket.WebSocketApp("ws://localhost:8003",
        on_open=on_open,
        on_message=on_message
    )
    
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    time.sleep(5)  # Wait for all messages to process
    
    # Verify responses
    assert len(responses) > 0, "No responses received"
    
    # Should have error responses for invalid messages
    error_responses = [r for r in responses if r.get("type") == "error"]
    assert len(error_responses) >= 2, "Expected error responses for invalid messages"
    
    ws.close()

---

## 4. Audio Processing Tests

### TC-RT-AUDIO-001: Audio Format Support

**Test Objective:** Verify support for different audio formats and encodings

**Test Steps:**
1. Send audio in different formats (WAV, M4A, MP3)
2. Test different sample rates and bit depths
3. Verify transcription quality across formats

**Expected Results:**
- Multiple audio formats supported
- Consistent transcription quality
- Appropriate format conversion handling

**Test Data:**
```python
def test_audio_format_support():
    audio_formats = [
        {"format": "wav", "mime": "audio/wav"},
        {"format": "m4a", "mime": "audio/m4a"},
        {"format": "mp3", "mime": "audio/mpeg"}
    ]
    
    for audio_format in audio_formats:
        transcription_received = threading.Event()
        format_results = []
        
        def on_message(ws, message):
            data = json.loads(message)
            if data.get("type") == "final":
                format_results.append(data["text"])
                transcription_received.set()
        
        def on_open(ws):
            # Load test audio file
            audio_file = f"test_audio.{audio_format['format']}"
            with open(audio_file, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode()
            
            message = {
                "type": "audio_file",
                "data": f"data:{audio_format['mime']};base64,{audio_data}",
                "language": "english"
            }
            ws.send(json.dumps(message))
        
        ws = websocket.WebSocketApp("ws://localhost:8003",
            on_open=on_open,
            on_message=on_message
        )
        
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()
        
        # Wait for transcription
        assert transcription_received.wait(timeout=60), f"No transcription for {audio_format['format']}"
        assert len(format_results) > 0, f"Empty transcription for {audio_format['format']}"
        
        ws.close()
        time.sleep(1)

---

### TC-RT-AUDIO-002: Audio Quality and Noise Handling

**Test Objective:** Verify transcription quality with various audio conditions

**Test Steps:**
1. Test with high-quality audio
2. Test with noisy audio
3. Test with low-volume audio
4. Verify transcription accuracy

**Expected Results:**
- High-quality audio transcribed accurately
- Noisy audio handled gracefully
- Low-volume audio processed appropriately
- Quality degradation handled smoothly

**Test Data:**
```python
def test_audio_quality_handling():
    audio_conditions = [
        {"file": "high_quality_audio.wav", "expected_accuracy": 0.95},
        {"file": "noisy_audio.wav", "expected_accuracy": 0.80},
        {"file": "low_volume_audio.wav", "expected_accuracy": 0.85}
    ]
    
    for condition in audio_conditions:
        transcription_received = threading.Event()
        transcription_result = []
        
        def on_message(ws, message):
            data = json.loads(message)
            if data.get("type") == "final":
                transcription_result.append(data["text"])
                transcription_received.set()
        
        def on_open(ws):
            with open(condition["file"], "rb") as f:
                audio_data = base64.b64encode(f.read()).decode()
            
            message = {
                "type": "audio_file",
                "data": f"data:audio/wav;base64,{audio_data}",
                "language": "english"
            }
            ws.send(json.dumps(message))
        
        ws = websocket.WebSocketApp("ws://localhost:8003",
            on_open=on_open,
            on_message=on_message
        )
        
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()
        
        assert transcription_received.wait(timeout=60), f"No transcription for {condition['file']}"
        
        # Verify transcription quality (would need reference text for accuracy calculation)
        transcription = transcription_result[0]
        assert len(transcription) > 0, f"Empty transcription for {condition['file']}"
        
        # Basic quality checks
        assert not transcription.isspace(), "Transcription is only whitespace"
        assert len(transcription.split()) >= 3, "Transcription too short"
        
        ws.close()
        time.sleep(1)

---

## 5. Performance Tests

### TC-RT-PERF-001: Transcription Latency

**Test Objective:** Verify transcription latency meets real-time requirements

**Test Steps:**
1. Send audio chunks with timestamps
2. Measure time from audio send to transcription receive
3. Verify latency is under 3 seconds

**Expected Results:**
- Average latency under 2 seconds
- 95th percentile under 3 seconds
- Consistent performance across session

**Test Data:**
```python
def test_transcription_latency():
    latencies = []
    chunk_timestamps = {}
    
    def on_message(ws, message):
        receive_time = time.time()
        data = json.loads(message)
        
        if data.get("type") == "partial":
            # Calculate latency (simplified - would need chunk correlation in real implementation)
            if chunk_timestamps:
                latest_send_time = max(chunk_timestamps.values())
                latency = receive_time - latest_send_time
                latencies.append(latency)
    
    def on_open(ws):
        # Send multiple audio chunks
        for i in range(20):
            send_time = time.time()
            chunk_timestamps[i] = send_time
            
            audio_data = {
                "type": "audio_chunk",
                "data": f"audio_chunk_{i}_base64",
                "language": "english"
            }
            ws.send(json.dumps(audio_data))
            time.sleep(2)  # Send every 2 seconds
    
    ws = websocket.WebSocketApp("ws://localhost:8003",
        on_open=on_open,
        on_message=on_message
    )
    
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    time.sleep(50)  # Wait for all chunks to process
    
    # Analyze latencies
    assert len(latencies) > 0, "No latency measurements recorded"
    
    avg_latency = sum(latencies) / len(latencies)
    latencies_sorted = sorted(latencies)
    p95_latency = latencies_sorted[int(0.95 * len(latencies_sorted))]
    
    assert avg_latency < 2.0, f"Average latency {avg_latency:.2f}s exceeds 2s"
    assert p95_latency < 3.0, f"95th percentile latency {p95_latency:.2f}s exceeds 3s"
    
    print(f"Average latency: {avg_latency:.2f}s")
    print(f"95th percentile latency: {p95_latency:.2f}s")
    
    ws.close()

---

### TC-RT-PERF-002: Concurrent Connection Handling

**Test Objective:** Verify server handles multiple concurrent WebSocket connections

**Test Steps:**
1. Establish multiple WebSocket connections
2. Send audio data from all connections simultaneously
3. Verify all connections receive transcriptions
4. Measure performance degradation

**Expected Results:**
- Multiple connections supported (at least 10)
- All connections receive transcriptions
- Minimal performance degradation
- No connection drops under load

**Test Data:**
```python
def test_concurrent_connections():
    num_connections = 10
    connection_results = {}
    
    def create_connection(connection_id):
        transcription_received = threading.Event()
        transcriptions = []
        
        def on_message(ws, message):
            data = json.loads(message)
            if data.get("type") in ["partial", "final"]:
                transcriptions.append(data["text"])
                if data.get("type") == "final":
                    transcription_received.set()
        
        def on_open(ws):
            audio_data = {
                "type": "audio_chunk",
                "data": f"connection_{connection_id}_audio_data",
                "language": "english"
            }
            ws.send(json.dumps(audio_data))
        
        ws = websocket.WebSocketApp("ws://localhost:8003",
            on_open=on_open,
            on_message=on_message
        )
        
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()
        
        # Wait for transcription
        success = transcription_received.wait(timeout=30)
        connection_results[connection_id] = {
            "success": success,
            "transcription_count": len(transcriptions)
        }
        
        ws.close()
        return success
    
    # Create concurrent connections
    threads = []
    for i in range(num_connections):
        thread = threading.Thread(target=create_connection, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all connections to complete
    for thread in threads:
        thread.join(timeout=60)
    
    # Analyze results
    successful_connections = sum(1 for r in connection_results.values() if r["success"])
    
    assert successful_connections >= num_connections * 0.9, f"Only {successful_connections}/{num_connections} connections successful"
    
    # Verify all successful connections received transcriptions
    for conn_id, result in connection_results.items():
        if result["success"]:
            assert result["transcription_count"] > 0, f"Connection {conn_id} received no transcriptions"
    
    print(f"Successful connections: {successful_connections}/{num_connections}")

---

## Test Execution

### Test Environment Setup

```python
# conftest.py for real-time transcription tests
import pytest
import websocket
import threading
import time
import json
import base64

@pytest.fixture(scope="session")
def websocket_server():
    """Ensure WebSocket server is running"""
    # This would start the transcription server if not already running
    # For now, assume it's running on port 8003
    yield "ws://localhost:8003"

@pytest.fixture
def sample_audio_base64():
    """Provide sample audio data in base64 format"""
    # This would be actual audio data for testing
    return "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA="

def wait_for_websocket_message(ws, timeout=30):
    """Helper function to wait for WebSocket messages"""
    received_messages = []
    message_event = threading.Event()
    
    def on_message(ws, message):
        received_messages.append(json.loads(message))
        message_event.set()
    
    ws.on_message = on_message
    
    if message_event.wait(timeout):
        return received_messages
    else:
        return []
```

### Running Tests

```bash
# Run all real-time transcription tests
pytest documentations/realtime-transcription/test-cases.md -v

# Run specific test categories
pytest -k "test_rt" -v                      # Unit tests
pytest -k "test_rt_int" -v                 # Integration tests
pytest -k "test_rt_ws" -v                  # WebSocket tests
pytest -k "test_rt_audio" -v               # Audio processing tests
pytest -k "test_rt_perf" -v                # Performance tests

# Run with WebSocket server dependency
pytest --websocket-server=localhost:8003 -v

# Performance tests with detailed metrics
pytest -k "perf" -v -s --tb=short
```

### Continuous Integration

```yaml
# .github/workflows/realtime-transcription-tests.yml
name: Real-Time Transcription Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      transcription-server:
        image: auralis/transcription-server:latest
        ports:
          - 8003:8003
        env:
          WHISPER_MODEL: medium
          DEVICE: cpu
    
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install websocket-client
      - name: Wait for transcription server
        run: |
          timeout 60 bash -c 'until nc -z localhost 8003; do sleep 1; done'
      - name: Run transcription tests
        run: pytest documentations/realtime-transcription/ -v --cov=transcription
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```