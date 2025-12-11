# Test Cases - Session Management

## Overview

This document contains comprehensive test cases for the Session Management system, covering session creation, audio recording, transcription integration, and session lifecycle management.

## Test Categories

### 1. Unit Tests
### 2. Integration Tests
### 3. Property-Based Tests
### 4. Audio Processing Tests
### 5. Performance Tests

---

## 1. Unit Tests

### TC-SM-001: Session Creation

**Test Objective:** Verify session creation with required and optional fields

**Prerequisites:**
- Patient exists in database
- Authenticated therapist session

**Test Steps:**
1. Send POST request to `/sessions/` with session data
2. Verify session is created with correct fields
3. Check auto-increment session number

**Expected Results:**
- Status Code: 200 OK
- Session created with unique ID
- Session number auto-incremented per patient
- Timestamps recorded correctly

**Test Data:**
```python
def test_session_creation():
    # Create patient first
    patient_response = client.post("/patients/",
        json={"full_name": "Test Patient"},
        headers=authenticated_headers
    )
    patient_id = patient_response.json()["patient"]["id"]
    
    # Create session
    session_data = {
        "patient_id": patient_id,
        "language": "english",
        "duration": 3600,
        "original_transcription": "Test session transcription",
        "notes": "Initial session notes"
    }
    
    response = client.post("/sessions/",
        json=session_data,
        headers=authenticated_headers
    )
    
    assert response.status_code == 200
    session = response.json()["session"]
    
    assert session["patient_id"] == patient_id
    assert session["session_number"] == 1  # First session
    assert session["language"] == "english"
    assert session["duration"] == 3600
    assert session["original_transcription"] == "Test session transcription"
    assert session["session_date"] is not None
    assert session["created_at"] is not None
```
---

### TC-SM-002: Session Number Auto-Increment

**Test Objective:** Verify session numbers auto-increment correctly per patient

**Test Steps:**
1. Create multiple sessions for same patient
2. Create sessions for different patients
3. Verify numbering is correct

**Expected Results:**
- Session numbers increment per patient (1, 2, 3...)
- Different patients have independent numbering
- No gaps in numbering sequence

**Test Data:**
```python
def test_session_number_increment():
    # Create two patients
    patient1_id = create_test_patient("Patient One")
    patient2_id = create_test_patient("Patient Two")
    
    # Create sessions for patient 1
    for i in range(3):
        response = client.post("/sessions/",
            json={
                "patient_id": patient1_id,
                "language": "english",
                "original_transcription": f"Session {i+1} for patient 1"
            },
            headers=authenticated_headers
        )
        session = response.json()["session"]
        assert session["session_number"] == i + 1
    
    # Create sessions for patient 2
    for i in range(2):
        response = client.post("/sessions/",
            json={
                "patient_id": patient2_id,
                "language": "english", 
                "original_transcription": f"Session {i+1} for patient 2"
            },
            headers=authenticated_headers
        )
        session = response.json()["session"]
        assert session["session_number"] == i + 1  # Should start from 1

---

### TC-SM-003: Session Retrieval by Patient

**Test Objective:** Verify retrieving all sessions for a specific patient

**Test Steps:**
1. Create patient with multiple sessions
2. Request sessions for patient
3. Verify correct sessions returned

**Expected Results:**
- Only sessions for specified patient returned
- Sessions ordered by date (newest first)
- All session fields included

**Test Data:**
```python
def test_session_retrieval_by_patient():
    patient_id = create_test_patient("Test Patient")
    
    # Create sessions with different dates
    session_data = [
        {"transcription": "First session", "date": "2024-01-01T10:00:00"},
        {"transcription": "Second session", "date": "2024-01-08T10:00:00"},
        {"transcription": "Third session", "date": "2024-01-15T10:00:00"}
    ]
    
    created_sessions = []
    for data in session_data:
        response = client.post("/sessions/",
            json={
                "patient_id": patient_id,
                "language": "english",
                "original_transcription": data["transcription"],
                "session_date": data["date"]
            },
            headers=authenticated_headers
        )
        created_sessions.append(response.json()["session"])
    
    # Retrieve sessions
    response = client.get(f"/sessions/patient/{patient_id}",
        headers=authenticated_headers
    )
    
    assert response.status_code == 200
    sessions = response.json()["sessions"]
    
    assert len(sessions) == 3
    # Should be ordered by date (newest first)
    assert sessions[0]["original_transcription"] == "Third session"
    assert sessions[1]["original_transcription"] == "Second session"
    assert sessions[2]["original_transcription"] == "First session"

---

### TC-SM-004: Session Update

**Test Objective:** Verify session details can be updated after creation

**Test Steps:**
1. Create session with initial data
2. Update various session fields
3. Verify changes are saved

**Expected Results:**
- Updated fields reflect new values
- Unchanged fields remain intact
- Update timestamp recorded

**Test Data:**
```python
def test_session_update():
    patient_id = create_test_patient("Test Patient")
    
    # Create initial session
    initial_data = {
        "patient_id": patient_id,
        "language": "english",
        "original_transcription": "Initial transcription",
        "notes": "Initial notes"
    }
    
    create_response = client.post("/sessions/",
        json=initial_data,
        headers=authenticated_headers
    )
    session_id = create_response.json()["session"]["id"]
    
    # Update session
    update_data = {
        "original_transcription": "Updated transcription",
        "notes": "Updated notes with additional observations",
        "diagnosis": "Major Depressive Disorder",
        "treatment_plan": "CBT therapy, weekly sessions",
        "is_completed": True
    }
    
    update_response = client.put(f"/sessions/{session_id}",
        json=update_data,
        headers=authenticated_headers
    )
    
    assert update_response.status_code == 200
    
    # Verify updates
    get_response = client.get(f"/sessions/{session_id}",
        headers=authenticated_headers
    )
    session = get_response.json()["session"]
    
    assert session["original_transcription"] == "Updated transcription"
    assert session["notes"] == "Updated notes with additional observations"
    assert session["diagnosis"] == "Major Depressive Disorder"
    assert session["treatment_plan"] == "CBT therapy, weekly sessions"
    assert session["is_completed"] == True
    assert session["language"] == "english"  # Unchanged

---

### TC-SM-005: Audio File Upload

**Test Objective:** Verify audio file upload and association with session

**Test Steps:**
1. Create session
2. Upload audio file for session
3. Verify file is stored and linked

**Expected Results:**
- Audio file uploaded successfully
- File path stored in session record
- File size recorded
- Supported audio formats accepted

**Test Data:**
```python
def test_audio_file_upload():
    patient_id = create_test_patient("Test Patient")
    
    # Create session
    session_response = client.post("/sessions/",
        json={
            "patient_id": patient_id,
            "language": "english"
        },
        headers=authenticated_headers
    )
    session_id = session_response.json()["session"]["id"]
    
    # Create test audio file
    audio_content = b"fake_audio_data_for_testing"
    
    # Upload audio
    files = {"file": ("test_audio.m4a", audio_content, "audio/m4a")}
    upload_response = client.post(f"/sessions/{session_id}/audio",
        files=files,
        headers={"Authorization": authenticated_headers["Authorization"]}
    )
    
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    
    assert upload_data["success"] == True
    assert "file_path" in upload_data
    
    # Verify session updated
    session_response = client.get(f"/sessions/{session_id}",
        headers=authenticated_headers
    )
    session = session_response.json()["session"]
    
    assert session["audio_file_path"] is not None
    assert session["audio_file_size"] > 0

---

### TC-SM-006: Session Deletion

**Test Objective:** Verify session can be deleted permanently

**Test Steps:**
1. Create session with audio file
2. Delete session
3. Verify session and associated files removed

**Expected Results:**
- Session removed from database
- Associated audio file deleted
- Cannot retrieve deleted session

**Test Data:**
```python
def test_session_deletion():
    patient_id = create_test_patient("Test Patient")
    
    # Create session
    session_response = client.post("/sessions/",
        json={
            "patient_id": patient_id,
            "language": "english",
            "original_transcription": "Session to be deleted"
        },
        headers=authenticated_headers
    )
    session_id = session_response.json()["session"]["id"]
    
    # Verify session exists
    get_response = client.get(f"/sessions/{session_id}",
        headers=authenticated_headers
    )
    assert get_response.status_code == 200
    
    # Delete session
    delete_response = client.delete(f"/sessions/{session_id}",
        headers=authenticated_headers
    )
    assert delete_response.status_code == 200
    
    # Verify session no longer exists
    get_response = client.get(f"/sessions/{session_id}",
        headers=authenticated_headers
    )
    assert get_response.status_code == 404

---

## 2. Integration Tests

### TC-SM-INT-001: Complete Session Workflow

**Test Objective:** Verify end-to-end session management workflow

**Test Steps:**
1. Create patient
2. Create session
3. Upload audio
4. Generate AI notes
5. Update session details
6. Retrieve session history

**Expected Results:**
- All steps complete successfully
- Data flows correctly between components
- Session history maintained properly

**Test Data:**
```python
def test_complete_session_workflow():
    # 1. Create patient
    patient_response = client.post("/patients/",
        json={"full_name": "Workflow Test Patient"},
        headers=authenticated_headers
    )
    patient_id = patient_response.json()["patient"]["id"]
    
    # 2. Create session
    session_response = client.post("/sessions/",
        json={
            "patient_id": patient_id,
            "language": "english",
            "duration": 3600,
            "original_transcription": "Patient discusses anxiety and coping strategies during this therapy session."
        },
        headers=authenticated_headers
    )
    session_id = session_response.json()["session"]["id"]
    
    # 3. Upload audio (simulated)
    audio_content = b"simulated_audio_data"
    files = {"file": ("session_audio.m4a", audio_content, "audio/m4a")}
    upload_response = client.post(f"/sessions/{session_id}/audio",
        files=files,
        headers={"Authorization": authenticated_headers["Authorization"]}
    )
    assert upload_response.status_code == 200
    
    # 4. Generate AI notes
    notes_response = client.post(f"/notes/{session_id}/generate-notes",
        headers=authenticated_headers
    )
    assert notes_response.status_code == 200
    
    # 5. Update session details
    update_response = client.put(f"/sessions/{session_id}",
        json={
            "diagnosis": "Generalized Anxiety Disorder",
            "treatment_plan": "CBT techniques, relaxation training",
            "is_completed": True
        },
        headers=authenticated_headers
    )
    assert update_response.status_code == 200
    
    # 6. Retrieve session history
    history_response = client.get(f"/sessions/patient/{patient_id}",
        headers=authenticated_headers
    )
    assert history_response.status_code == 200
    
    sessions = history_response.json()["sessions"]
    assert len(sessions) == 1
    assert sessions[0]["diagnosis"] == "Generalized Anxiety Disorder"
    assert sessions[0]["is_completed"] == True

---

### TC-SM-INT-002: Multi-Session Patient History

**Test Objective:** Verify patient session history across multiple sessions

**Test Steps:**
1. Create patient
2. Create multiple sessions over time
3. Update various sessions
4. Retrieve complete history
5. Verify chronological order and completeness

**Expected Results:**
- All sessions maintained in history
- Proper chronological ordering
- Session numbers sequential
- All updates preserved

**Test Data:**
```python
def test_multi_session_patient_history():
    patient_id = create_test_patient("Multi-Session Patient")
    
    # Create sessions over time
    sessions_data = [
        {
            "date": "2024-01-01T10:00:00",
            "transcription": "Initial assessment session",
            "diagnosis": "Initial evaluation"
        },
        {
            "date": "2024-01-08T10:00:00", 
            "transcription": "Follow-up session discussing progress",
            "diagnosis": "Major Depressive Disorder"
        },
        {
            "date": "2024-01-15T10:00:00",
            "transcription": "Therapy session with CBT techniques",
            "diagnosis": "Major Depressive Disorder"
        },
        {
            "date": "2024-01-22T10:00:00",
            "transcription": "Progress review and treatment adjustment",
            "diagnosis": "Major Depressive Disorder - Improving"
        }
    ]
    
    created_session_ids = []
    for i, session_data in enumerate(sessions_data):
        # Create session
        response = client.post("/sessions/",
            json={
                "patient_id": patient_id,
                "language": "english",
                "session_date": session_data["date"],
                "original_transcription": session_data["transcription"]
            },
            headers=authenticated_headers
        )
        session_id = response.json()["session"]["id"]
        created_session_ids.append(session_id)
        
        # Update with diagnosis
        client.put(f"/sessions/{session_id}",
            json={"diagnosis": session_data["diagnosis"]},
            headers=authenticated_headers
        )
    
    # Retrieve complete history
    history_response = client.get(f"/sessions/patient/{patient_id}",
        headers=authenticated_headers
    )
    
    sessions = history_response.json()["sessions"]
    
    # Verify all sessions present
    assert len(sessions) == 4
    
    # Verify chronological order (newest first)
    assert sessions[0]["session_number"] == 4
    assert sessions[1]["session_number"] == 3
    assert sessions[2]["session_number"] == 2
    assert sessions[3]["session_number"] == 1
    
    # Verify diagnoses preserved
    assert sessions[0]["diagnosis"] == "Major Depressive Disorder - Improving"
    assert sessions[3]["diagnosis"] == "Initial evaluation"

---

## 3. Property-Based Tests

### TC-SM-PBT-001: Session Data Persistence

**Property:** For any valid session data, storage and retrieval should be consistent

**Test Implementation:**
```python
from hypothesis import given, strategies as st

@given(
    st.text(min_size=10, max_size=1000),
    st.sampled_from(["english", "spanish", "french", "hindi"]),
    st.integers(min_value=300, max_value=7200)
)
def test_session_data_persistence_property(transcription, language, duration):
    """Property: Session data should persist accurately"""
    patient_id = create_test_patient("Property Test Patient")
    
    session_data = {
        "patient_id": patient_id,
        "original_transcription": transcription,
        "language": language,
        "duration": duration
    }
    
    # Create session
    create_response = client.post("/sessions/",
        json=session_data,
        headers=authenticated_headers
    )
    assume(create_response.status_code == 200)
    
    session_id = create_response.json()["session"]["id"]
    
    # Retrieve session
    get_response = client.get(f"/sessions/{session_id}",
        headers=authenticated_headers
    )
    
    session = get_response.json()["session"]
    
    # Property: Retrieved data should match stored data
    assert session["original_transcription"] == transcription
    assert session["language"] == language
    assert session["duration"] == duration
```

**Validates:** Session data integrity

---

### TC-SM-PBT-002: Session Number Consistency

**Property:** Session numbers should always be sequential and unique per patient

**Test Implementation:**
```python
@given(st.integers(min_value=1, max_value=10))
def test_session_number_consistency_property(session_count):
    """Property: Session numbers should be sequential per patient"""
    patient_id = create_test_patient("Sequential Test Patient")
    
    created_sessions = []
    for i in range(session_count):
        response = client.post("/sessions/",
            json={
                "patient_id": patient_id,
                "language": "english",
                "original_transcription": f"Session {i+1}"
            },
            headers=authenticated_headers
        )
        assume(response.status_code == 200)
        created_sessions.append(response.json()["session"])
    
    # Property: Session numbers should be sequential
    session_numbers = [s["session_number"] for s in created_sessions]
    expected_numbers = list(range(1, session_count + 1))
    assert session_numbers == expected_numbers
    
    # Property: All session numbers should be unique
    assert len(set(session_numbers)) == len(session_numbers)
```

**Validates:** Session numbering logic

---

## 4. Audio Processing Tests

### TC-SM-AUDIO-001: Supported Audio Formats

**Test Objective:** Verify all supported audio formats can be uploaded

**Test Steps:**
1. Create session
2. Upload files in different supported formats
3. Verify all uploads succeed

**Expected Results:**
- WAV, M4A, MP3 formats accepted
- File size limits enforced
- Unsupported formats rejected

**Test Data:**
```python
def test_supported_audio_formats():
    patient_id = create_test_patient("Audio Test Patient")
    session_id = create_test_session(patient_id)
    
    # Test supported formats
    supported_formats = [
        ("test.wav", "audio/wav"),
        ("test.m4a", "audio/m4a"), 
        ("test.mp3", "audio/mpeg")
    ]
    
    for filename, content_type in supported_formats:
        audio_content = b"fake_audio_data"
        files = {"file": (filename, audio_content, content_type)}
        
        response = client.post(f"/sessions/{session_id}/audio",
            files=files,
            headers={"Authorization": authenticated_headers["Authorization"]}
        )
        
        assert response.status_code == 200, f"Format {content_type} should be supported"
    
    # Test unsupported format
    unsupported_files = {"file": ("test.txt", b"text_data", "text/plain")}
    response = client.post(f"/sessions/{session_id}/audio",
        files=unsupported_files,
        headers={"Authorization": authenticated_headers["Authorization"]}
    )
    
    assert response.status_code == 400  # Should be rejected

---

### TC-SM-AUDIO-002: File Size Limits

**Test Objective:** Verify audio file size limits are enforced

**Test Steps:**
1. Upload files of various sizes
2. Verify size limits enforced
3. Check error messages for oversized files

**Expected Results:**
- Files under limit accepted
- Files over limit rejected with clear error
- Appropriate HTTP status codes

**Test Data:**
```python
def test_audio_file_size_limits():
    patient_id = create_test_patient("Size Test Patient")
    session_id = create_test_session(patient_id)
    
    # Test acceptable size (1MB)
    small_audio = b"x" * (1024 * 1024)  # 1MB
    files = {"file": ("small.m4a", small_audio, "audio/m4a")}
    
    response = client.post(f"/sessions/{session_id}/audio",
        files=files,
        headers={"Authorization": authenticated_headers["Authorization"]}
    )
    assert response.status_code == 200
    
    # Test oversized file (100MB - assuming 50MB limit)
    large_audio = b"x" * (100 * 1024 * 1024)  # 100MB
    files = {"file": ("large.m4a", large_audio, "audio/m4a")}
    
    response = client.post(f"/sessions/{session_id}/audio",
        files=files,
        headers={"Authorization": authenticated_headers["Authorization"]}
    )
    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()

---

## 5. Performance Tests

### TC-SM-PERF-001: Session Creation Performance

**Test Objective:** Verify session creation meets performance requirements

**Test Steps:**
1. Create multiple sessions rapidly
2. Measure creation time per session
3. Verify performance scales appropriately

**Expected Results:**
- Individual session creation under 200ms
- Batch creation scales linearly
- No performance degradation with volume

**Test Data:**
```python
def test_session_creation_performance():
    patient_id = create_test_patient("Performance Test Patient")
    
    # Test individual session creation time
    session_times = []
    for i in range(50):
        start_time = time.time()
        
        response = client.post("/sessions/",
            json={
                "patient_id": patient_id,
                "language": "english",
                "original_transcription": f"Performance test session {i+1}"
            },
            headers=authenticated_headers
        )
        
        creation_time = time.time() - start_time
        session_times.append(creation_time)
        
        assert response.status_code == 200
        assert creation_time < 0.2  # Under 200ms
    
    # Verify average performance
    avg_time = sum(session_times) / len(session_times)
    assert avg_time < 0.1  # Average under 100ms
    
    print(f"Average session creation time: {avg_time:.3f}s")

---

### TC-SM-PERF-002: Session Retrieval Performance

**Test Objective:** Verify session retrieval performance with large datasets

**Test Steps:**
1. Create patient with many sessions
2. Measure retrieval time
3. Test with different session counts

**Expected Results:**
- Retrieval time scales reasonably with session count
- Large session lists (100+) retrieved under 1 second
- Proper pagination if needed

**Test Data:**
```python
def test_session_retrieval_performance():
    patient_id = create_test_patient("Large Dataset Patient")
    
    # Create varying numbers of sessions
    session_counts = [10, 50, 100, 200]
    
    for count in session_counts:
        # Create sessions
        for i in range(count):
            client.post("/sessions/",
                json={
                    "patient_id": patient_id,
                    "language": "english",
                    "original_transcription": f"Session {i+1} content"
                },
                headers=authenticated_headers
            )
        
        # Measure retrieval time
        start_time = time.time()
        response = client.get(f"/sessions/patient/{patient_id}",
            headers=authenticated_headers
        )
        retrieval_time = time.time() - start_time
        
        assert response.status_code == 200
        sessions = response.json()["sessions"]
        assert len(sessions) == count
        
        # Performance assertions
        if count <= 50:
            assert retrieval_time < 0.5  # Under 500ms for small datasets
        else:
            assert retrieval_time < 1.0  # Under 1s for large datasets
        
        print(f"{count} sessions retrieved in {retrieval_time:.3f}s")

---

## Test Execution

### Test Environment Setup

```python
# conftest.py for session management tests
import pytest
import tempfile
import os

@pytest.fixture
def test_patient():
    """Create a test patient for session tests"""
    response = client.post("/patients/",
        json={"full_name": "Session Test Patient"},
        headers=authenticated_headers
    )
    return response.json()["patient"]["id"]

@pytest.fixture
def test_session(test_patient):
    """Create a test session"""
    response = client.post("/sessions/",
        json={
            "patient_id": test_patient,
            "language": "english",
            "original_transcription": "Test session transcription"
        },
        headers=authenticated_headers
    )
    return response.json()["session"]

def create_test_patient(name="Test Patient"):
    """Helper to create test patient"""
    response = client.post("/patients/",
        json={"full_name": name},
        headers=authenticated_headers
    )
    return response.json()["patient"]["id"]

def create_test_session(patient_id, transcription="Test transcription"):
    """Helper to create test session"""
    response = client.post("/sessions/",
        json={
            "patient_id": patient_id,
            "language": "english",
            "original_transcription": transcription
        },
        headers=authenticated_headers
    )
    return response.json()["session"]["id"]
```

### Running Tests

```bash
# Run all session management tests
pytest documentations/session-management/test-cases.md -v

# Run specific test categories
pytest -k "test_sm" -v                      # Unit tests
pytest -k "test_sm_int" -v                 # Integration tests
pytest -k "test_sm_pbt" -v                 # Property-based tests
pytest -k "test_sm_audio" -v               # Audio processing tests
pytest -k "test_sm_perf" -v                # Performance tests

# Run with coverage
pytest --cov=session_router --cov-report=html

# Performance tests with detailed output
pytest -k "perf" -v -s --tb=short
```

### Continuous Integration

```yaml
# .github/workflows/session-management-tests.yml
name: Session Management Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run session management tests
        run: pytest documentations/session-management/ -v --cov=session
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```