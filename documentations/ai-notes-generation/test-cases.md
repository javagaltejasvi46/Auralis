# Test Cases - AI Notes Generation

## Overview

This document contains comprehensive test cases for the AI Notes Generation system, covering automated clinical note generation using Phi-3-Mini, risk keyword detection, note editing, and performance optimization.

## Test Categories

### 1. Unit Tests
### 2. Integration Tests
### 3. Property-Based Tests
### 4. AI Model Tests
### 5. Performance Tests

---

## 1. Unit Tests

### TC-AIN-001: Basic AI Note Generation

**Test Objective:** Verify AI generates clinical notes from session transcription

**Prerequisites:**
- Ollama server running with Phi-3-Mini model
- Session exists with transcription data

**Test Steps:**
1. Send POST request to `/notes/{session_id}/generate-notes`
2. Verify AI generates structured clinical notes
3. Check response format and timing

**Expected Results:**
- Status Code: 200 OK
- Notes generated within 15 seconds
- Contains required sections: Chief Complaint, Emotional State, Risk, Intervention, Progress, Plan
- Sections formatted with **bold** headers
- Each section under 50 words

**Test Data:**
```python
def test_basic_ai_note_generation():
    # Create session with transcription
    session_data = {
        "patient_id": patient_id,
        "original_transcription": "Patient reports feeling anxious about work deadlines. Discussed coping strategies including deep breathing and time management. Patient seemed receptive to suggestions and agreed to practice techniques.",
        "language": "english"
    }
    
    session_response = client.post("/sessions/", 
        json=session_data,
        headers=authenticated_headers
    )
    session_id = session_response.json()["session"]["id"]
    
    # Generate AI notes
    start_time = time.time()
    notes_response = client.post(f"/notes/{session_id}/generate-notes",
        headers=authenticated_headers
    )
    generation_time = time.time() - start_time
    
    assert notes_response.status_code == 200
    assert generation_time < 15.0  # Under 15 seconds
    
    notes_data = notes_response.json()
    assert notes_data["success"] == True
    assert "notes" in notes_data
    assert notes_data["is_ai_generated"] == True
    
    # Verify note structure
    notes = notes_data["notes"]
    assert "**Chief Complaint:**" in notes
    assert "**Emotional State:**" in notes
    assert "**Risk:**" in notes
    assert "**Intervention:**" in notes
    assert "**Progress:**" in notes
    assert "**Plan:**" in notes
```
---

### TC-AIN-002: Risk Keyword Detection

**Test Objective:** Verify AI detects and highlights risk-related keywords

**Test Steps:**
1. Create session with transcription containing risk keywords
2. Generate AI notes
3. Verify risk keywords are properly formatted

**Expected Results:**
- Risk keywords detected: suicide, self-harm, violence, abuse, overdose
- Keywords formatted as {{RED:keyword}}
- Case-insensitive detection
- Multiple occurrences highlighted

**Test Data:**
```python
def test_risk_keyword_detection():
    risk_transcription = """
    Patient mentioned feeling suicidal thoughts last week. 
    Discussed history of self-harm behaviors in adolescence.
    No current plans for violence or abuse reported.
    Patient denies any overdose attempts.
    """
    
    session_id = create_session_with_transcription(risk_transcription)
    
    notes_response = client.post(f"/notes/{session_id}/generate-notes",
        headers=authenticated_headers
    )
    
    notes = notes_response.json()["notes"]
    
    # Verify risk keywords are highlighted
    assert "{{RED:suicidal}}" in notes or "{{RED:suicide}}" in notes
    assert "{{RED:self-harm}}" in notes
    assert "{{RED:violence}}" in notes
    assert "{{RED:abuse}}" in notes
    assert "{{RED:overdose}}" in notes
```

---

### TC-AIN-003: Note Editing and Metadata Tracking

**Test Objective:** Verify note editing preserves formatting and updates metadata

**Test Steps:**
1. Generate AI notes for session
2. Edit the generated notes
3. Verify metadata is updated correctly

**Expected Results:**
- Notes can be edited after generation
- Markdown formatting preserved
- edited_from_ai flag set to true
- Last edit timestamp recorded
- Original generation timestamp preserved

**Test Data:**
```python
def test_note_editing_metadata():
    session_id = create_session_with_transcription("Test transcription")
    
    # Generate initial notes
    generate_response = client.post(f"/notes/{session_id}/generate-notes",
        headers=authenticated_headers
    )
    original_notes = generate_response.json()["notes"]
    
    # Edit notes
    edited_notes = original_notes + "\n\n**Additional Observations:** Patient showed good engagement."
    
    edit_response = client.put(f"/notes/{session_id}/notes",
        json={
            "notes": edited_notes,
            "is_ai_generated": True,
            "edited_from_ai": True
        },
        headers=authenticated_headers
    )
    
    assert edit_response.status_code == 200
    
    # Verify metadata
    session_response = client.get(f"/sessions/{session_id}",
        headers=authenticated_headers
    )
    session_data = session_response.json()["session"]
    
    assert session_data["notes"] == edited_notes
    assert session_data["notes_is_ai_generated"] == True
    assert session_data["notes_edited_from_ai"] == True
    assert session_data["notes_last_edited_at"] is not None
```

---

### TC-AIN-004: Note Regeneration

**Test Objective:** Verify notes can be regenerated with updated content

**Test Steps:**
1. Generate initial AI notes
2. Request regeneration
3. Verify new notes replace old ones and metadata is reset

**Expected Results:**
- New notes generated from same transcription
- Previous notes replaced
- edited_from_ai flag reset to false
- New generation timestamp recorded

**Test Data:**
```python
def test_note_regeneration():
    session_id = create_session_with_transcription("Patient discusses anxiety and coping strategies")
    
    # Generate initial notes
    initial_response = client.post(f"/notes/{session_id}/generate-notes",
        headers=authenticated_headers
    )
    initial_notes = initial_response.json()["notes"]
    
    # Edit notes first
    client.put(f"/notes/{session_id}/notes",
        json={
            "notes": initial_notes + " EDITED",
            "is_ai_generated": True,
            "edited_from_ai": True
        },
        headers=authenticated_headers
    )
    
    # Regenerate notes
    regen_response = client.post(f"/notes/{session_id}/generate-notes",
        json={"regenerate": True},
        headers=authenticated_headers
    )
    
    assert regen_response.status_code == 200
    
    # Verify regeneration
    new_notes = regen_response.json()["notes"]
    assert new_notes != initial_notes + " EDITED"  # Should be different
    assert "EDITED" not in new_notes  # Should not contain manual edits
    
    # Check metadata reset
    session_response = client.get(f"/sessions/{session_id}", headers=authenticated_headers)
    session_data = session_response.json()["session"]
    assert session_data["notes_edited_from_ai"] == False
```

---

## 2. Integration Tests

### TC-AIN-INT-001: End-to-End Note Generation Workflow

**Test Objective:** Verify complete workflow from session creation to note editing

**Test Steps:**
1. Create patient and session
2. Generate AI notes
3. Edit notes
4. Verify notes appear in patient summary
5. Export PDF with notes

**Expected Results:**
- All steps complete successfully
- Notes flow through entire system
- Formatting preserved in all contexts

**Test Data:**
```python
def test_end_to_end_note_workflow():
    # 1. Create patient and session
    patient_id = create_test_patient()
    session_data = {
        "patient_id": patient_id,
        "original_transcription": "Comprehensive therapy session discussing patient's progress with depression treatment. Patient reports improved mood and better sleep patterns.",
        "language": "english",
        "duration": 3600
    }
    
    session_response = client.post("/sessions/", 
        json=session_data,
        headers=authenticated_headers
    )
    session_id = session_response.json()["session"]["id"]
    
    # 2. Generate AI notes
    notes_response = client.post(f"/notes/{session_id}/generate-notes",
        headers=authenticated_headers
    )
    assert notes_response.status_code == 200
    
    # 3. Edit notes
    original_notes = notes_response.json()["notes"]
    edited_notes = original_notes + "\n\n**Therapist Observations:** Patient demonstrated excellent insight."
    
    edit_response = client.put(f"/notes/{session_id}/notes",
        json={"notes": edited_notes, "is_ai_generated": True, "edited_from_ai": True},
        headers=authenticated_headers
    )
    assert edit_response.status_code == 200
    
    # 4. Verify in patient summary
    summary_response = client.get(f"/patients/{patient_id}/overall-summary",
        headers=authenticated_headers
    )
    assert "Therapist Observations" in str(summary_response.json())
    
    # 5. Export PDF
    pdf_response = client.get(f"/patients/{patient_id}/export-pdf",
        headers=authenticated_headers
    )
    assert pdf_response.status_code == 200
```

---

### TC-AIN-INT-002: Multi-Session Note Integration

**Test Objective:** Verify AI notes from multiple sessions integrate properly

**Test Steps:**
1. Create patient with 3 sessions
2. Generate AI notes for each session
3. Request overall summary
4. Verify all session notes are considered

**Expected Results:**
- Each session has individual AI-generated notes
- Overall summary incorporates all session notes
- Chronological order maintained
- Key themes from all sessions included

**Test Data:**
```python
def test_multi_session_note_integration():
    patient_id = create_test_patient()
    
    # Create 3 sessions with different themes
    sessions = [
        {"transcription": "Initial session - patient reports severe anxiety and panic attacks", "theme": "anxiety"},
        {"transcription": "Follow-up session - patient shows improvement with breathing techniques", "theme": "progress"},
        {"transcription": "Recent session - patient discusses work-life balance and stress management", "theme": "coping"}
    ]
    
    session_ids = []
    for session_data in sessions:
        session_response = client.post("/sessions/",
            json={
                "patient_id": patient_id,
                "original_transcription": session_data["transcription"],
                "language": "english"
            },
            headers=authenticated_headers
        )
        session_id = session_response.json()["session"]["id"]
        session_ids.append(session_id)
        
        # Generate AI notes for each session
        notes_response = client.post(f"/notes/{session_id}/generate-notes",
            headers=authenticated_headers
        )
        assert notes_response.status_code == 200
    
    # Get overall summary
    summary_response = client.get(f"/patients/{patient_id}/overall-summary",
        headers=authenticated_headers
    )
    
    summary_text = str(summary_response.json())
    
    # Verify all themes are represented
    assert "anxiety" in summary_text.lower()
    assert "improvement" in summary_text.lower() or "progress" in summary_text.lower()
    assert "stress" in summary_text.lower() or "coping" in summary_text.lower()
```

---

## 3. Property-Based Tests

### TC-AIN-PBT-001: Note Generation Consistency

**Property:** For any valid transcription, note generation should produce structured output

**Test Implementation:**
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=50, max_size=1000))
def test_note_generation_consistency_property(transcription):
    """Property: Any valid transcription should generate structured notes"""
    assume(len(transcription.strip()) > 20)
    assume(not all(c.isspace() or c.isdigit() for c in transcription))
    
    session_id = create_session_with_transcription(transcription)
    
    response = client.post(f"/notes/{session_id}/generate-notes",
        headers=authenticated_headers
    )
    
    if response.status_code == 200:
        notes = response.json()["notes"]
        
        # Property: Notes should contain required sections
        required_sections = ["**Chief Complaint:**", "**Emotional State:**", "**Risk:**", 
                           "**Intervention:**", "**Progress:**", "**Plan:**"]
        
        for section in required_sections:
            assert section in notes, f"Missing section: {section}"
        
        # Property: Notes should not be empty
        assert len(notes.strip()) > 0
        
        # Property: Notes should be reasonably sized (not too short or too long)
        assert 50 < len(notes) < 2000
```

**Validates:** Requirements 1.3, 1.4, 1.5

---

### TC-AIN-PBT-002: Risk Keyword Detection Property

**Property:** Any text containing risk keywords should have them highlighted

**Test Implementation:**
```python
@given(st.sampled_from(["suicide", "self-harm", "violence", "abuse", "overdose"]))
def test_risk_keyword_detection_property(risk_keyword):
    """Property: Risk keywords should always be detected and highlighted"""
    
    # Create transcription with risk keyword
    transcription = f"Patient mentioned {risk_keyword} during the session. We discussed safety planning."
    
    session_id = create_session_with_transcription(transcription)
    
    response = client.post(f"/notes/{session_id}/generate-notes",
        headers=authenticated_headers
    )
    
    if response.status_code == 200:
        notes = response.json()["notes"]
        
        # Property: Risk keyword should be highlighted
        assert f"{{{{RED:{risk_keyword}}}}}" in notes or f"{{{{RED:{risk_keyword.upper()}}}}}" in notes
```

**Validates:** Requirements 2.1, 2.2, 2.4

---

## 4. AI Model Tests

### TC-AIN-AI-001: Model Response Validation

**Test Objective:** Verify Phi-3-Mini model produces valid clinical responses

**Test Steps:**
1. Send various clinical scenarios to model
2. Verify responses follow clinical format
3. Check for appropriate medical terminology

**Expected Results:**
- Responses use professional clinical language
- Sections are appropriately filled
- No inappropriate or harmful content
- Consistent formatting

**Test Data:**
```python
def test_model_response_validation():
    clinical_scenarios = [
        "Patient reports depression and anxiety symptoms",
        "Patient discusses relationship conflicts and stress",
        "Patient shows improvement in mood and behavior",
        "Patient expresses concerns about medication side effects"
    ]
    
    for scenario in clinical_scenarios:
        session_id = create_session_with_transcription(scenario)
        
        response = client.post(f"/notes/{session_id}/generate-notes",
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        notes = response.json()["notes"]
        
        # Verify clinical appropriateness
        assert not any(inappropriate in notes.lower() 
                      for inappropriate in ["funny", "weird", "crazy", "nuts"])
        
        # Verify professional terminology
        clinical_terms = ["patient", "therapy", "treatment", "assessment", "intervention"]
        assert any(term in notes.lower() for term in clinical_terms)
        
        # Verify structure
        assert notes.count("**") >= 12  # At least 6 sections with bold formatting
```

---

### TC-AIN-AI-002: Model Error Handling

**Test Objective:** Verify graceful handling of model failures

**Test Steps:**
1. Test with Ollama server unavailable
2. Test with invalid model responses
3. Test with timeout scenarios

**Expected Results:**
- Clear error messages returned
- No system crashes
- Existing notes preserved
- Appropriate HTTP status codes

**Test Data:**
```python
def test_model_error_handling():
    session_id = create_session_with_transcription("Test transcription")
    
    # Mock Ollama unavailable
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.ConnectionError("Ollama unavailable")
        
        response = client.post(f"/notes/{session_id}/generate-notes",
            headers=authenticated_headers
        )
        
        assert response.status_code == 500
        assert "ollama" in response.json()["detail"].lower()
    
    # Mock timeout
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.Timeout("Request timeout")
        
        response = client.post(f"/notes/{session_id}/generate-notes",
            headers=authenticated_headers
        )
        
        assert response.status_code == 500
        assert "timeout" in response.json()["detail"].lower()
```

---

## 5. Performance Tests

### TC-AIN-PERF-001: Note Generation Performance

**Test Objective:** Verify note generation meets performance requirements

**Test Steps:**
1. Generate notes for various transcription lengths
2. Measure generation time
3. Verify performance scales appropriately

**Expected Results:**
- CPU: Under 15 seconds for typical transcription
- GPU: Under 5 seconds for typical transcription
- Performance scales linearly with input length

**Test Data:**
```python
def test_note_generation_performance():
    # Test different transcription lengths
    test_cases = [
        {"length": 100, "max_time_cpu": 10, "max_time_gpu": 3},
        {"length": 500, "max_time_cpu": 15, "max_time_gpu": 5},
        {"length": 1000, "max_time_cpu": 20, "max_time_gpu": 7},
        {"length": 2000, "max_time_cpu": 30, "max_time_gpu": 10}
    ]
    
    for case in test_cases:
        # Generate transcription of specified length
        transcription = generate_transcription(case["length"])
        session_id = create_session_with_transcription(transcription)
        
        start_time = time.time()
        response = client.post(f"/notes/{session_id}/generate-notes",
            headers=authenticated_headers
        )
        generation_time = time.time() - start_time
        
        assert response.status_code == 200
        
        # Check performance (assume CPU for this test)
        assert generation_time < case["max_time_cpu"]
        
        print(f"Length {case['length']}: {generation_time:.2f}s")

def generate_transcription(target_length):
    """Generate realistic transcription of specified length"""
    base_text = "Patient discusses feelings of anxiety and stress. Therapist provides coping strategies. "
    repetitions = target_length // len(base_text) + 1
    return (base_text * repetitions)[:target_length]
```

---

### TC-AIN-PERF-002: Concurrent Note Generation

**Test Objective:** Verify system handles multiple concurrent note generation requests

**Test Steps:**
1. Submit 10 concurrent note generation requests
2. Verify all complete successfully
3. Measure total processing time

**Expected Results:**
- All requests complete successfully
- No significant performance degradation
- Proper queuing and resource management

**Test Data:**
```python
import asyncio
import aiohttp

async def test_concurrent_note_generation():
    # Create 10 sessions
    session_ids = []
    for i in range(10):
        transcription = f"Session {i} - Patient discusses various therapeutic topics and progress."
        session_id = create_session_with_transcription(transcription)
        session_ids.append(session_id)
    
    async def generate_notes_async(session, session_id):
        start = time.time()
        async with session.post(f"/notes/{session_id}/generate-notes",
            headers=authenticated_headers
        ) as response:
            result = await response.json()
        return time.time() - start, response.status
    
    # Submit all requests concurrently
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [generate_notes_async(session, sid) for sid in session_ids]
        results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    # Verify all succeeded
    for generation_time, status in results:
        assert status == 200
        assert generation_time < 30  # Individual request under 30s
    
    # Total time should be much less than sequential (10 * 15s = 150s)
    assert total_time < 60  # Should complete in under 1 minute
    
    print(f"10 concurrent generations completed in {total_time:.2f}s")
```

---

## Test Execution

### Test Environment Setup

```python
# conftest.py for AI notes generation tests
import pytest
from unittest.mock import patch, MagicMock
import requests

@pytest.fixture
def mock_ollama_success():
    """Mock successful Ollama response"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": "**Chief Complaint:** Test complaint\n**Emotional State:** Anxious\n**Risk:** {{RED:None}}\n**Intervention:** CBT techniques\n**Progress:** Improving\n**Plan:** Continue weekly sessions"
    }
    mock_response.status_code = 200
    
    with patch('requests.post', return_value=mock_response):
        yield mock_response

@pytest.fixture
def session_with_transcription():
    """Create a session with sample transcription"""
    def _create_session(transcription="Default test transcription"):
        patient_id = create_test_patient()
        session_data = {
            "patient_id": patient_id,
            "original_transcription": transcription,
            "language": "english",
            "duration": 3600
        }
        
        response = client.post("/sessions/", 
            json=session_data,
            headers=authenticated_headers
        )
        return response.json()["session"]["id"]
    
    return _create_session
```

### Running Tests

```bash
# Run all AI notes generation tests
pytest documentations/ai-notes-generation/test-cases.md -v

# Run with Ollama integration (requires Ollama running)
pytest -k "test_ain and not mock" -v

# Run with mocked AI responses (faster)
pytest -k "test_ain" --mock-ai -v

# Performance tests (run separately)
pytest -k "perf" -v --tb=short

# Property-based tests with more examples
pytest -k "pbt" --hypothesis-max-examples=1000 -v
```

### Continuous Integration

```yaml
# .github/workflows/ai-notes-tests.yml
name: AI Notes Generation Tests
on: [push, pull_request]

jobs:
  test-mocked:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run mocked AI tests
        run: pytest documentations/ai-notes-generation/ -k "not integration" -v
  
  test-integration:
    runs-on: ubuntu-latest
    services:
      ollama:
        image: ollama/ollama:latest
        ports:
          - 11434:11434
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Pull Phi-3 model
        run: |
          curl -X POST http://localhost:11434/api/pull -d '{"name": "phi3:mini"}'
      - name: Run integration tests
        run: pytest documentations/ai-notes-generation/ -k "integration" -v
```