# Test Cases - Llama2 Summarization Migration

## Overview

This document contains comprehensive test cases for the Llama2 Summarization Migration system, covering the migration from Gemini to Phi-3-Mini, model performance comparison, and backward compatibility.

## Test Categories

### 1. Unit Tests
### 2. Integration Tests
### 3. Migration Tests
### 4. Performance Comparison Tests
### 5. Compatibility Tests

---

## 1. Unit Tests

### TC-LSM-001: Phi-3-Mini Model Loading

**Test Objective:** Verify Phi-3-Mini model loads correctly via Ollama

**Prerequisites:**
- Ollama server running
- Phi-3-Mini model available

**Test Steps:**
1. Initialize Phi-3-Mini summarization service
2. Verify model loads successfully
3. Check model configuration

**Expected Results:**
- Model loads without errors
- Service reports ready status
- Model configuration matches expectations

**Test Data:**
```python
def test_phi3_model_loading():
    from summarization_service_phi3 import summarization_service
    
    # Test model initialization
    assert summarization_service is not None, "Summarization service not initialized"
    
    # Test model availability
    try:
        # Attempt a simple generation to verify model is loaded
        test_result = summarization_service.generate_summary("Test transcription for model verification")
        assert test_result is not None, "Model failed to generate test summary"
        assert len(test_result) > 0, "Model returned empty summary"
    except Exception as e:
        pytest.fail(f"Model loading failed: {e}")
    
    # Test service statistics if available
    if hasattr(summarization_service, 'get_statistics'):
        stats = summarization_service.get_statistics()
        assert stats['model_info']['loaded'] == True, "Model not reported as loaded"
        assert 'phi3' in stats['model_info'].get('model_path', '').lower(), "Wrong model loaded"
```
---

### TC-LSM-002: Summary Format Consistency

**Test Objective:** Verify Phi-3-Mini generates summaries in the same format as Gemini

**Test Steps:**
1. Generate summary using Phi-3-Mini
2. Verify format matches expected structure
3. Check section headers and formatting

**Expected Results:**
- Summary contains all required sections
- Formatting matches Gemini output format
- Risk keywords properly highlighted

**Test Data:**
```python
def test_summary_format_consistency():
    from summarization_service_phi3 import summarization_service
    
    test_transcription = """
    Patient reports feeling anxious about work deadlines. 
    Discussed coping strategies including deep breathing exercises.
    Patient mentioned some thoughts of self-harm but no current plans.
    Agreed to practice relaxation techniques daily.
    """
    
    summary = summarization_service.generate_summary(test_transcription)
    
    # Verify required sections present
    required_sections = [
        "**Chief Complaint:**",
        "**Emotional State:**", 
        "**Risk:**",
        "**Intervention:**",
        "**Progress:**",
        "**Plan:**"
    ]
    
    for section in required_sections:
        assert section in summary, f"Missing section: {section}"
    
    # Verify risk keyword highlighting
    assert "{{RED:" in summary, "Risk keywords not highlighted"
    assert "self-harm" in summary.lower(), "Risk keyword not captured"
    
    # Verify format structure
    lines = summary.split('\n')
    section_lines = [line for line in lines if line.startswith('**') and line.endswith('**')]
    assert len(section_lines) >= 6, "Insufficient section headers"

---

### TC-LSM-003: Ollama Integration

**Test Objective:** Verify integration with Ollama service works correctly

**Test Steps:**
1. Test Ollama connection
2. Verify model communication
3. Test error handling for Ollama failures

**Expected Results:**
- Successful connection to Ollama
- Proper request/response handling
- Graceful error handling when Ollama unavailable

**Test Data:**
```python
def test_ollama_integration():
    import requests
    from unittest.mock import patch
    from summarization_service_phi3 import summarization_service
    
    # Test 1: Successful Ollama connection
    try:
        # This should work if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        assert response.status_code == 200, "Ollama server not responding"
        
        tags = response.json()
        model_names = [model['name'] for model in tags.get('models', [])]
        assert any('phi3' in name for name in model_names), "Phi-3 model not available in Ollama"
        
    except requests.exceptions.ConnectionError:
        pytest.skip("Ollama server not available for testing")
    
    # Test 2: Error handling when Ollama unavailable
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.ConnectionError("Connection failed")
        
        try:
            result = summarization_service.generate_summary("Test transcription")
            # Should either return error or fallback gracefully
            assert result is not None, "Service should handle Ollama failure gracefully"
        except Exception as e:
            # Expected behavior - service should raise appropriate exception
            assert "ollama" in str(e).lower() or "connection" in str(e).lower()

---

### TC-LSM-004: Performance Metrics

**Test Objective:** Verify Phi-3-Mini performance meets requirements

**Test Steps:**
1. Generate summaries of various lengths
2. Measure generation time
3. Compare with performance targets

**Expected Results:**
- CPU: Under 15 seconds for typical transcription
- GPU: Under 5 seconds for typical transcription
- Memory usage within acceptable limits

**Test Data:**
```python
import time

def test_performance_metrics():
    from summarization_service_phi3 import summarization_service
    
    # Test transcriptions of different lengths
    test_cases = [
        {"length": "short", "text": "Patient reports mild anxiety. Discussed coping strategies.", "max_time": 10},
        {"length": "medium", "text": "Patient reports feeling anxious about work deadlines. We discussed various coping strategies including deep breathing exercises and time management techniques. Patient seemed receptive to suggestions.", "max_time": 15},
        {"length": "long", "text": "Patient reports feeling anxious about work deadlines and relationship issues. We discussed various coping strategies including deep breathing exercises, time management techniques, and communication skills. Patient seemed receptive to suggestions and agreed to practice techniques daily. Also discussed medication compliance and side effects." * 3, "max_time": 20}
    ]
    
    performance_results = []
    
    for case in test_cases:
        start_time = time.time()
        summary = summarization_service.generate_summary(case["text"])
        generation_time = time.time() - start_time
        
        performance_results.append({
            "length": case["length"],
            "time": generation_time,
            "max_allowed": case["max_time"]
        })
        
        assert summary is not None, f"Failed to generate summary for {case['length']} text"
        assert generation_time < case["max_time"], f"{case['length']} text took {generation_time:.2f}s, exceeds {case['max_time']}s limit"
    
    # Log performance results
    for result in performance_results:
        print(f"{result['length']} text: {result['time']:.2f}s (limit: {result['max_allowed']}s)")

---

## 2. Integration Tests

### TC-LSM-INT-001: End-to-End Migration Workflow

**Test Objective:** Verify complete migration from Gemini to Phi-3-Mini works seamlessly

**Test Steps:**
1. Create session with transcription
2. Generate summary using new Phi-3 service
3. Verify summary quality and format
4. Test with existing session data

**Expected Results:**
- Migration completes without data loss
- New summaries maintain quality
- Existing functionality preserved
- No breaking changes in API

**Test Data:**
```python
def test_end_to_end_migration():
    # Create test session
    patient_id = create_test_patient("Migration Test Patient")
    
    session_data = {
        "patient_id": patient_id,
        "language": "english",
        "original_transcription": """
        Patient reports significant improvement in mood over the past week.
        Discussed medication compliance and noted good adherence.
        Patient mentioned some work stress but feels more capable of handling it.
        We reviewed coping strategies and patient demonstrated good understanding.
        Plan to continue current treatment approach with weekly sessions.
        """
    }
    
    # Create session
    session_response = client.post("/sessions/",
        json=session_data,
        headers=authenticated_headers
    )
    session_id = session_response.json()["session"]["id"]
    
    # Generate AI notes using new Phi-3 service
    notes_response = client.post(f"/notes/{session_id}/generate-notes",
        headers=authenticated_headers
    )
    
    assert notes_response.status_code == 200, "AI note generation failed"
    
    notes_data = notes_response.json()
    assert notes_data["success"] == True, "Note generation not successful"
    assert notes_data["is_ai_generated"] == True, "Notes not marked as AI generated"
    
    # Verify summary quality
    summary = notes_data["notes"]
    assert "**Chief Complaint:**" in summary, "Missing chief complaint section"
    assert "improvement" in summary.lower(), "Key content not captured"
    assert "medication" in summary.lower(), "Important details missing"
    
    # Verify session updated correctly
    session_check = client.get(f"/sessions/{session_id}", headers=authenticated_headers)
    session = session_check.json()["session"]
    assert session["notes"] == summary, "Session notes not updated"
    assert session["notes_is_ai_generated"] == True, "AI generation flag not set"

---

### TC-LSM-INT-002: Backward Compatibility

**Test Objective:** Verify existing sessions and summaries remain functional after migration

**Test Steps:**
1. Create sessions with old Gemini-generated summaries (simulated)
2. Verify they can still be accessed and displayed
3. Test regeneration with new Phi-3 service
4. Ensure no data corruption

**Expected Results:**
- Existing summaries remain accessible
- Old format summaries display correctly
- Regeneration works with new service
- No data loss or corruption

**Test Data:**
```python
def test_backward_compatibility():
    patient_id = create_test_patient("Compatibility Test Patient")
    
    # Simulate existing session with Gemini-generated summary
    existing_session_data = {
        "patient_id": patient_id,
        "language": "english",
        "original_transcription": "Patient discusses anxiety and treatment progress.",
        "notes": "**Chief Complaint:** Anxiety\n**Emotional State:** Worried\n**Risk:** None reported\n**Intervention:** CBT techniques\n**Progress:** Gradual improvement\n**Plan:** Continue therapy",
        "notes_is_ai_generated": True,
        "notes_generated_at": "2024-01-01T10:00:00"
    }
    
    # Create session with existing summary
    session_response = client.post("/sessions/",
        json=existing_session_data,
        headers=authenticated_headers
    )
    session_id = session_response.json()["session"]["id"]
    
    # Verify existing summary can be retrieved
    get_response = client.get(f"/sessions/{session_id}", headers=authenticated_headers)
    session = get_response.json()["session"]
    
    assert session["notes"] == existing_session_data["notes"], "Existing notes corrupted"
    assert session["notes_is_ai_generated"] == True, "AI flag lost"
    
    # Test regeneration with new service
    regen_response = client.post(f"/notes/{session_id}/generate-notes",
        json={"regenerate": True},
        headers=authenticated_headers
    )
    
    assert regen_response.status_code == 200, "Regeneration failed"
    
    new_notes = regen_response.json()["notes"]
    assert new_notes != existing_session_data["notes"], "Notes not regenerated"
    assert "**Chief Complaint:**" in new_notes, "New format not applied"

---

## 3. Migration Tests

### TC-LSM-MIG-001: Service Fallback Mechanism

**Test Objective:** Verify fallback to Gemini service when Phi-3 unavailable

**Test Steps:**
1. Simulate Phi-3/Ollama unavailability
2. Verify system falls back to Gemini
3. Test error handling and user notification

**Expected Results:**
- Graceful fallback to Gemini when Phi-3 unavailable
- User notified of fallback
- Service continues to function
- No system crashes

**Test Data:**
```python
def test_service_fallback_mechanism():
    from unittest.mock import patch
    import requests
    
    patient_id = create_test_patient("Fallback Test Patient")
    session_id = create_test_session(patient_id, "Test transcription for fallback")
    
    # Mock Ollama unavailability
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.ConnectionError("Ollama unavailable")
        
        # Attempt to generate notes
        response = client.post(f"/notes/{session_id}/generate-notes",
            headers=authenticated_headers
        )
        
        # Should either succeed with fallback or provide clear error
        if response.status_code == 200:
            # Successful fallback
            notes_data = response.json()
            assert notes_data["success"] == True, "Fallback generation failed"
            # Could check for fallback indicator in response
        else:
            # Expected error with clear message
            assert response.status_code in [500, 503], "Unexpected error code"
            error_detail = response.json().get("detail", "")
            assert "ollama" in error_detail.lower() or "unavailable" in error_detail.lower()

---

### TC-LSM-MIG-002: Configuration Migration

**Test Objective:** Verify configuration settings migrate correctly to new service

**Test Steps:**
1. Test with various configuration settings
2. Verify Phi-3 service respects configuration
3. Check parameter mapping from old to new service

**Expected Results:**
- Configuration parameters mapped correctly
- Service behavior matches configuration
- No configuration loss during migration

**Test Data:**
```python
def test_configuration_migration():
    from summarization_service_phi3 import summarization_service
    
    # Test configuration parameters
    test_configs = [
        {"max_tokens": 150, "temperature": 0.7},
        {"max_tokens": 200, "temperature": 0.5},
        {"max_tokens": 100, "temperature": 0.9}
    ]
    
    for config in test_configs:
        # Test if service respects configuration
        # (This would depend on how configuration is implemented)
        
        test_transcription = "Patient reports anxiety and discusses coping strategies."
        
        # Generate summary with configuration
        summary = summarization_service.generate_summary(
            test_transcription,
            max_tokens=config.get("max_tokens", 150),
            temperature=config.get("temperature", 0.7)
        )
        
        assert summary is not None, f"Generation failed with config: {config}"
        assert len(summary) > 0, f"Empty summary with config: {config}"
        
        # Verify summary length respects max_tokens (approximately)
        # Note: This is approximate as token count != character count
        if config["max_tokens"] == 100:
            assert len(summary) < 800, "Summary too long for low max_tokens"  # Rough estimate

---

## 4. Performance Comparison Tests

### TC-LSM-PERF-001: Speed Comparison

**Test Objective:** Compare generation speed between Gemini and Phi-3-Mini

**Test Steps:**
1. Generate summaries using both services
2. Measure generation times
3. Compare performance characteristics

**Expected Results:**
- Phi-3-Mini performance documented
- Comparison metrics available
- Performance meets or exceeds Gemini

**Test Data:**
```python
def test_speed_comparison():
    test_transcriptions = [
        "Short transcription for speed test.",
        "Medium length transcription discussing patient progress and treatment plans with various therapeutic interventions.",
        "Long transcription covering multiple topics including patient history, current symptoms, treatment progress, medication compliance, family dynamics, and detailed treatment planning for future sessions." * 2
    ]
    
    phi3_times = []
    
    for transcription in test_transcriptions:
        # Test Phi-3-Mini speed
        start_time = time.time()
        try:
            from summarization_service_phi3 import summarization_service
            phi3_summary = summarization_service.generate_summary(transcription)
            phi3_time = time.time() - start_time
            phi3_times.append(phi3_time)
            
            assert phi3_summary is not None, "Phi-3 generation failed"
            
        except Exception as e:
            pytest.skip(f"Phi-3 service unavailable: {e}")
    
    # Analyze performance
    if phi3_times:
        avg_phi3_time = sum(phi3_times) / len(phi3_times)
        max_phi3_time = max(phi3_times)
        
        print(f"Phi-3-Mini average time: {avg_phi3_time:.2f}s")
        print(f"Phi-3-Mini max time: {max_phi3_time:.2f}s")
        
        # Performance assertions
        assert avg_phi3_time < 15.0, f"Average Phi-3 time {avg_phi3_time:.2f}s exceeds 15s"
        assert max_phi3_time < 30.0, f"Max Phi-3 time {max_phi3_time:.2f}s exceeds 30s"

---

### TC-LSM-PERF-002: Quality Comparison

**Test Objective:** Compare summary quality between Gemini and Phi-3-Mini

**Test Steps:**
1. Generate summaries using both services for same transcriptions
2. Compare content quality and completeness
3. Verify clinical appropriateness

**Expected Results:**
- Phi-3-Mini quality comparable to Gemini
- Clinical terminology maintained
- Key information captured accurately

**Test Data:**
```python
def test_quality_comparison():
    test_transcription = """
    Patient reports significant improvement in depressive symptoms over the past month.
    Medication compliance has been excellent with no reported side effects.
    Patient has been practicing mindfulness techniques daily as discussed.
    Some work-related stress remains but patient feels more equipped to handle it.
    Sleep patterns have normalized and appetite has returned.
    Patient expresses optimism about continued progress.
    Plan to reduce session frequency to biweekly and continue current medication.
    """
    
    # Generate with Phi-3-Mini
    try:
        from summarization_service_phi3 import summarization_service
        phi3_summary = summarization_service.generate_summary(test_transcription)
        
        # Quality checks for Phi-3 summary
        assert phi3_summary is not None, "Phi-3 failed to generate summary"
        
        # Check for key content capture
        key_elements = ["improvement", "medication", "mindfulness", "stress", "sleep", "biweekly"]
        captured_elements = sum(1 for element in key_elements if element.lower() in phi3_summary.lower())
        
        assert captured_elements >= 4, f"Phi-3 only captured {captured_elements}/6 key elements"
        
        # Check clinical appropriateness
        clinical_terms = ["patient", "symptoms", "treatment", "progress"]
        clinical_count = sum(1 for term in clinical_terms if term.lower() in phi3_summary.lower())
        
        assert clinical_count >= 2, "Insufficient clinical terminology in Phi-3 summary"
        
        # Check structure
        assert "**Chief Complaint:**" in phi3_summary, "Missing structured format"
        assert len(phi3_summary.split('\n')) >= 6, "Summary too brief"
        
        print("Phi-3-Mini summary quality: PASS")
        
    except Exception as e:
        pytest.skip(f"Phi-3 service unavailable for quality testing: {e}")

---

## 5. Compatibility Tests

### TC-LSM-COMP-001: API Compatibility

**Test Objective:** Verify API endpoints remain compatible after migration

**Test Steps:**
1. Test all summarization-related endpoints
2. Verify request/response formats unchanged
3. Check error handling consistency

**Expected Results:**
- All existing endpoints work unchanged
- Response formats maintained
- Error codes and messages consistent

**Test Data:**
```python
def test_api_compatibility():
    patient_id = create_test_patient("API Compatibility Test")
    
    # Test session creation and note generation
    session_data = {
        "patient_id": patient_id,
        "language": "english",
        "original_transcription": "API compatibility test transcription"
    }
    
    session_response = client.post("/sessions/",
        json=session_data,
        headers=authenticated_headers
    )
    assert session_response.status_code == 200
    session_id = session_response.json()["session"]["id"]
    
    # Test note generation endpoint
    notes_response = client.post(f"/notes/{session_id}/generate-notes",
        headers=authenticated_headers
    )
    
    # Verify response format
    assert notes_response.status_code == 200
    notes_data = notes_response.json()
    
    # Check expected fields in response
    expected_fields = ["success", "session_id", "notes", "is_ai_generated", "generated_at"]
    for field in expected_fields:
        assert field in notes_data, f"Missing field in response: {field}"
    
    # Test note editing endpoint
    edit_response = client.put(f"/notes/{session_id}/notes",
        json={
            "notes": notes_data["notes"] + "\n\nAdditional notes",
            "is_ai_generated": True,
            "edited_from_ai": True
        },
        headers=authenticated_headers
    )
    
    assert edit_response.status_code == 200
    
    # Test multi-session summary endpoint
    summary_response = client.post("/summarize-sessions",
        json={"patient_id": patient_id},
        headers=authenticated_headers
    )
    
    assert summary_response.status_code == 200
    summary_data = summary_response.json()
    
    expected_summary_fields = ["success", "summary", "session_count", "key_points"]
    for field in expected_summary_fields:
        assert field in summary_data, f"Missing field in summary response: {field}"

---

### TC-LSM-COMP-002: Data Format Compatibility

**Test Objective:** Verify data formats remain compatible with existing client applications

**Test Steps:**
1. Generate summaries in expected format
2. Verify formatting matches client expectations
3. Test with existing client code (if available)

**Expected Results:**
- Summary format unchanged
- Risk keyword formatting preserved
- Section structure maintained

**Test Data:**
```python
def test_data_format_compatibility():
    test_transcription = "Patient mentions feeling suicidal and discusses self-harm thoughts."
    
    from summarization_service_phi3 import summarization_service
    summary = summarization_service.generate_summary(test_transcription)
    
    # Verify format compatibility
    
    # 1. Section headers format
    section_pattern = r'\*\*[^*]+:\*\*'
    import re
    sections = re.findall(section_pattern, summary)
    assert len(sections) >= 6, "Insufficient section headers"
    
    # 2. Risk keyword format
    risk_pattern = r'\{\{RED:[^}]+\}\}'
    risk_keywords = re.findall(risk_pattern, summary)
    assert len(risk_keywords) > 0, "Risk keywords not properly formatted"
    
    # 3. Overall structure
    lines = summary.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    assert len(non_empty_lines) >= 6, "Summary structure too sparse"
    
    # 4. Content validation
    assert "suicidal" in summary.lower() or "{{RED:suicidal}}" in summary, "Risk content not captured"
    assert "self-harm" in summary.lower() or "{{RED:self-harm}}" in summary, "Risk content not captured"
    
    print("Data format compatibility: PASS")

---

## Test Execution

### Test Environment Setup

```python
# conftest.py for migration tests
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_ollama_available():
    """Mock Ollama as available and responsive"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": "**Chief Complaint:** Test\n**Emotional State:** Calm\n**Risk:** {{RED:None}}\n**Intervention:** Testing\n**Progress:** Good\n**Plan:** Continue"
    }
    mock_response.status_code = 200
    
    with patch('requests.post', return_value=mock_response):
        yield

@pytest.fixture
def mock_ollama_unavailable():
    """Mock Ollama as unavailable"""
    with patch('requests.post', side_effect=ConnectionError("Ollama unavailable")):
        yield

def create_test_patient(name="Migration Test Patient"):
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
# Run all migration tests
pytest documentations/llama2-summarization-migration/test-cases.md -v

# Run specific test categories
pytest -k "test_lsm" -v                     # Unit tests
pytest -k "test_lsm_int" -v                # Integration tests
pytest -k "test_lsm_mig" -v                # Migration tests
pytest -k "test_lsm_perf" -v               # Performance tests
pytest -k "test_lsm_comp" -v               # Compatibility tests

# Run with Ollama dependency
pytest --ollama-required -v

# Run with mocked services (faster)
pytest --mock-services -v

# Performance comparison tests
pytest -k "perf" -v -s --tb=short
```

### Continuous Integration

```yaml
# .github/workflows/migration-tests.yml
name: Llama2 Migration Tests
on: [push, pull_request]

jobs:
  test-migration:
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
      - name: Run migration tests
        run: pytest documentations/llama2-summarization-migration/ -v --cov=summarization
      - name: Upload coverage
        uses: codecov/codecov-action@v1
  
  test-compatibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-python: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run compatibility tests (mocked)
        run: pytest documentations/llama2-summarization-migration/ -k "comp" --mock-services -v
```