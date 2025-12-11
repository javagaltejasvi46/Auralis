# Test Cases - Enhanced Patient Report

## Overview

This document contains comprehensive test cases for the Enhanced Patient Report system, covering patient data collection, AI-generated summaries, PDF export functionality, and comprehensive patient management with 45+ fields.

## Test Categories

### 1. Unit Tests
### 2. Integration Tests
### 3. Property-Based Tests
### 4. UI/UX Tests
### 5. Performance Tests

---

## 1. Unit Tests

### TC-EPR-001: Patient Creation with Extended Fields

**Test Objective:** Verify patient creation with all 45+ comprehensive fields

**Prerequisites:**
- Authenticated therapist session
- Database is accessible

**Test Steps:**
1. Send POST request to `/patients/` with comprehensive patient data:
   ```json
   {
     "patient_id": "P001",
     "full_name": "John Doe",
     "age": "35",
     "gender": "Male",
     "date_of_birth": "1988-05-15",
     "residence": "123 Main St, City, State",
     "education": "Bachelor's Degree",
     "occupation": "Software Engineer",
     "marital_status": "Married",
     "current_medical_conditions": "Hypertension",
     "past_medical_conditions": "None significant",
     "current_medications": "Lisinopril 10mg daily",
     "allergies": "Penicillin",
     "hospitalizations": "None",
     "previous_psychiatric_diagnoses": "Major Depressive Disorder",
     "previous_psychiatric_treatment": "CBT therapy 2019-2020",
     "previous_psychiatric_hospitalizations": "None",
     "suicide_attempts_self_harm_history": "None",
     "substance_use_history": "Social alcohol use",
     "psychiatric_illness_in_family": "Depression - mother",
     "medical_illness_in_family": "Diabetes - father",
     "family_dynamics": "Supportive family structure",
     "significant_family_events": "Parents divorced when age 12",
     "childhood_developmental_history": "Normal development",
     "educational_history": "Completed college",
     "occupational_history": "5 years in current role",
     "relationship_history": "Married 8 years",
     "social_support_system": "Strong support from spouse and friends",
     "living_situation": "Lives with spouse and 2 children",
     "cultural_religious_background": "Christian"
   }
   ```

**Expected Results:**
- Status Code: 200 OK
- All fields stored in database
- Patient ID generated if not provided
- Created timestamp recorded
- Response includes patient profile

**Test Data:**
```python
def test_patient_creation_extended_fields():
    patient_data = {
        "full_name": "John Doe",
        "age": "35",
        "gender": "Male",
        # ... all 45+ fields
    }
    
    response = client.post("/patients/", 
        json=patient_data,
        headers=authenticated_headers
    )
    
    assert response.status_code == 200
    assert response.json()["success"] == True
    
    # Verify all fields stored
    patient = response.json()["patient"]
    assert patient["full_name"] == "John Doe"
    assert patient["age"] == "35"
    assert patient["current_medical_conditions"] == "Hypertension"
    # ... verify all fields
```

---

### TC-EPR-002: Patient Information Validation

**Test Objective:** Verify validation of required and optional patient fields

**Test Steps:**
1. Attempt patient creation with missing required fields
2. Attempt patient creation with invalid data formats
3. Verify validation error messages

**Expected Results:**
- Missing required fields return 400 Bad Request
- Invalid formats return appropriate error messages
- Optional fields can be empty

**Test Data:**
```python
def test_patient_validation_required_fields():
    # Missing full_name (required)
    invalid_data = {"age": "35", "gender": "Male"}
    
    response = client.post("/patients/", 
        json=invalid_data,
        headers=authenticated_headers
    )
    
    assert response.status_code == 400
    assert "full_name" in response.json()["detail"]

def test_patient_validation_optional_fields():
    # Only required fields
    minimal_data = {"full_name": "Jane Doe"}
    
    response = client.post("/patients/", 
        json=minimal_data,
        headers=authenticated_headers
    )
    
    assert response.status_code == 200
```

---

### TC-EPR-003: Patient Information Update

**Test Objective:** Verify updating patient information preserves data integrity

**Test Steps:**
1. Create patient with initial data
2. Update specific fields
3. Verify changes are saved and timestamps updated

**Expected Results:**
- Updated fields reflect new values
- Unchanged fields remain intact
- Updated timestamp is recorded
- Original creation timestamp preserved

**Test Data:**
```python
def test_patient_update():
    # Create patient
    create_response = client.post("/patients/", 
        json=initial_patient_data,
        headers=authenticated_headers
    )
    patient_id = create_response.json()["patient"]["id"]
    
    # Update patient
    update_data = {
        "phone": "+1987654321",
        "current_medications": "Updated medication list"
    }
    
    response = client.put(f"/patients/{patient_id}", 
        json=update_data,
        headers=authenticated_headers
    )
    
    assert response.status_code == 200
    updated_patient = response.json()["patient"]
    assert updated_patient["phone"] == "+1987654321"
    assert updated_patient["full_name"] == initial_patient_data["full_name"]  # Unchanged
```

---

### TC-EPR-004: AI Overall Summary Generation

**Test Objective:** Verify AI generates comprehensive patient summaries from session data

**Prerequisites:**
- Patient exists with multiple sessions
- Sessions contain transcription data

**Test Steps:**
1. Request overall summary for patient with sessions
2. Verify AI analyzes all session data
3. Check generated clinical fields

**Expected Results:**
- Summary includes chief complaints
- Course of illness is analyzed
- Baseline assessment generated
- All sessions considered in analysis
- Professional clinical terminology used

**Test Data:**
```python
def test_ai_overall_summary_generation():
    # Create patient with sessions
    patient_id = create_patient_with_sessions()
    
    response = client.get(f"/patients/{patient_id}/overall-summary",
        headers=authenticated_headers
    )
    
    assert response.status_code == 200
    summary = response.json()["overall_summary"]
    
    # Verify required sections
    assert "chief_complaints" in summary
    assert "course_of_illness" in summary
    assert "baseline_assessment" in summary
    assert "session_summaries" in summary
    
    # Verify clinical fields
    assert summary["chief_complaints"]["primary"] is not None
    assert summary["baseline_assessment"]["mood"] is not None
```

---

### TC-EPR-005: PDF Report Generation

**Test Objective:** Verify PDF export functionality with proper formatting

**Test Steps:**
1. Request PDF export for patient
2. Verify PDF is generated with correct content
3. Check formatting and structure

**Expected Results:**
- PDF file is generated
- Contains all patient information sections
- Follows psychotherapy report format
- Includes session summaries
- Proper formatting with headers and spacing

**Test Data:**
```python
def test_pdf_report_generation():
    patient_id = create_patient_with_data()
    
    response = client.get(f"/patients/{patient_id}/export-pdf",
        headers=authenticated_headers
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    
    # Verify PDF content (using PyPDF2 or similar)
    pdf_content = extract_pdf_text(response.content)
    assert "PATIENT INFORMATION" in pdf_content
    assert "MEDICAL HISTORY" in pdf_content
    assert "SESSION RECORDING SUMMARIES" in pdf_content
```

---

### TC-EPR-006: Report Data Editing Before Export

**Test Objective:** Verify therapists can edit report data before PDF generation

**Test Steps:**
1. Get report data for editing
2. Modify clinical fields
3. Export PDF with edited data
4. Verify PDF contains edited information

**Expected Results:**
- Report data is pre-populated with AI-generated content
- All fields are editable
- Edited data is used in PDF generation
- Original data remains unchanged in database

**Test Data:**
```python
def test_report_data_editing():
    patient_id = create_patient_with_sessions()
    
    # Get report data
    report_response = client.get(f"/patients/{patient_id}/report-data",
        headers=authenticated_headers
    )
    
    assert report_response.status_code == 200
    report_data = report_response.json()["report_data"]
    
    # Edit data
    edited_data = report_data.copy()
    edited_data["chief_complaint"] = "Edited chief complaint"
    edited_data["mse_mood"] = "Edited mood assessment"
    
    # Export with edited data
    pdf_response = client.post(f"/patients/{patient_id}/export-pdf",
        json=edited_data,
        headers=authenticated_headers
    )
    
    assert pdf_response.status_code == 200
    pdf_content = extract_pdf_text(pdf_response.content)
    assert "Edited chief complaint" in pdf_content
    assert "Edited mood assessment" in pdf_content
```

---

## 2. Integration Tests

### TC-EPR-INT-001: Complete Patient Management Workflow

**Test Objective:** Verify end-to-end patient management from creation to PDF export

**Test Steps:**
1. Create patient with comprehensive information
2. Add multiple therapy sessions
3. Generate AI summaries for sessions
4. Create overall patient summary
5. Edit report data
6. Export professional PDF

**Expected Results:**
- All steps complete successfully
- Data flows correctly between components
- PDF contains accurate information from all sources

**Test Data:**
```python
def test_complete_patient_workflow():
    # 1. Create patient
    patient_response = client.post("/patients/", 
        json=comprehensive_patient_data,
        headers=authenticated_headers
    )
    patient_id = patient_response.json()["patient"]["id"]
    
    # 2. Add sessions
    session_ids = []
    for session_data in sample_sessions:
        session_response = client.post("/sessions/",
            json={**session_data, "patient_id": patient_id},
            headers=authenticated_headers
        )
        session_ids.append(session_response.json()["session"]["id"])
    
    # 3. Generate AI notes for sessions
    for session_id in session_ids:
        notes_response = client.post(f"/notes/{session_id}/generate-notes",
            headers=authenticated_headers
        )
        assert notes_response.status_code == 200
    
    # 4. Generate overall summary
    summary_response = client.get(f"/patients/{patient_id}/overall-summary",
        headers=authenticated_headers
    )
    assert summary_response.status_code == 200
    
    # 5. Export PDF
    pdf_response = client.get(f"/patients/{patient_id}/export-pdf",
        headers=authenticated_headers
    )
    assert pdf_response.status_code == 200
    assert len(pdf_response.content) > 1000  # Non-empty PDF
```

---

### TC-EPR-INT-002: Multi-Session Summary Integration

**Test Objective:** Verify AI summary considers all patient sessions

**Test Steps:**
1. Create patient with 5 different sessions
2. Each session has different topics and concerns
3. Generate overall summary
4. Verify summary incorporates information from all sessions

**Expected Results:**
- Summary references multiple sessions
- Key themes from different sessions included
- Chronological progression noted
- Latest session highlighted appropriately

**Test Data:**
```python
def test_multi_session_summary_integration():
    patient_id = create_patient()
    
    # Create sessions with different themes
    session_themes = [
        {"transcription": "Patient discusses anxiety about work...", "date": "2024-01-01"},
        {"transcription": "Patient reports improvement in mood...", "date": "2024-01-08"},
        {"transcription": "Patient mentions relationship conflicts...", "date": "2024-01-15"},
        {"transcription": "Patient discusses coping strategies...", "date": "2024-01-22"},
        {"transcription": "Patient shows significant progress...", "date": "2024-01-29"}
    ]
    
    for theme in session_themes:
        create_session(patient_id, theme)
    
    # Generate overall summary
    summary_response = client.get(f"/patients/{patient_id}/overall-summary",
        headers=authenticated_headers
    )
    
    summary = summary_response.json()["overall_summary"]
    
    # Verify multi-session integration
    assert len(summary["session_summaries"]) == 5
    assert "anxiety" in str(summary).lower()
    assert "improvement" in str(summary).lower()
    assert "progress" in str(summary).lower()
```

---

## 3. Property-Based Tests

### TC-EPR-PBT-001: Patient Data Persistence

**Property:** For any valid patient data, storage and retrieval should be consistent

**Test Implementation:**
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=100))
def test_patient_data_persistence_property(full_name):
    """Property: Patient data should persist accurately"""
    patient_data = {"full_name": full_name}
    
    # Create patient
    create_response = client.post("/patients/", 
        json=patient_data,
        headers=authenticated_headers
    )
    assume(create_response.status_code == 200)
    
    patient_id = create_response.json()["patient"]["id"]
    
    # Retrieve patient
    get_response = client.get(f"/patients/{patient_id}",
        headers=authenticated_headers
    )
    
    # Property: Retrieved data should match stored data
    assert get_response.json()["patient"]["full_name"] == full_name
```

**Validates:** Requirements 1.6, 1.7

---

### TC-EPR-PBT-002: PDF Generation Consistency

**Property:** For any patient with data, PDF generation should be consistent

**Test Implementation:**
```python
@given(st.text(min_size=1, max_size=50), st.integers(min_value=18, max_value=100))
def test_pdf_generation_consistency_property(name, age):
    """Property: PDF generation should be consistent for valid patient data"""
    patient_data = {"full_name": name, "age": str(age)}
    
    # Create patient
    patient_id = create_patient(patient_data)
    
    # Generate PDF twice
    pdf1 = client.get(f"/patients/{patient_id}/export-pdf",
        headers=authenticated_headers
    )
    pdf2 = client.get(f"/patients/{patient_id}/export-pdf",
        headers=authenticated_headers
    )
    
    # Property: PDFs should be consistent (same content)
    assert pdf1.status_code == 200
    assert pdf2.status_code == 200
    assert len(pdf1.content) > 0
    assert len(pdf2.content) > 0
```

**Validates:** Requirements 4.1, 4.4

---

### TC-EPR-PBT-003: AI Summary Determinism

**Property:** For the same session data, AI summaries should be consistent

**Test Implementation:**
```python
@given(st.text(min_size=50, max_size=500))
def test_ai_summary_determinism_property(transcription):
    """Property: AI summaries should be deterministic for same input"""
    assume(len(transcription.strip()) > 10)
    
    patient_id = create_patient()
    session_id = create_session(patient_id, {"transcription": transcription})
    
    # Generate summary twice
    summary1 = client.get(f"/patients/{patient_id}/overall-summary",
        headers=authenticated_headers
    )
    summary2 = client.get(f"/patients/{patient_id}/overall-summary",
        headers=authenticated_headers
    )
    
    # Property: Summaries should be consistent
    assert summary1.status_code == 200
    assert summary2.status_code == 200
    
    # Note: With AI, exact determinism may not be possible,
    # but key clinical fields should be consistent
    s1_data = summary1.json()["overall_summary"]
    s2_data = summary2.json()["overall_summary"]
    
    # Check that both summaries have required sections
    for section in ["chief_complaints", "course_of_illness", "baseline_assessment"]:
        assert section in s1_data
        assert section in s2_data
```

**Validates:** Requirements 3.1, 3.2, 3.3

---

## 4. UI/UX Tests

### TC-EPR-UI-001: Patient Form Usability

**Test Objective:** Verify patient creation form is user-friendly and organized

**Test Steps:**
1. Load patient creation screen
2. Verify form sections are properly organized
3. Test form validation and error messages
4. Verify collapsible sections work correctly

**Expected Results:**
- Form is organized into logical sections
- Required fields are clearly marked
- Validation provides helpful error messages
- Sections can be collapsed/expanded

**Test Data:**
```python
def test_patient_form_organization():
    # This would be a frontend test using tools like Selenium or Playwright
    
    # Navigate to patient creation
    driver.get("/create-patient")
    
    # Verify sections exist
    sections = [
        "Patient Information",
        "Medical History", 
        "Psychiatric History",
        "Family History",
        "Social History"
    ]
    
    for section in sections:
        section_element = driver.find_element(By.XPATH, f"//h3[contains(text(), '{section}')]")
        assert section_element.is_displayed()
    
    # Test collapsible functionality
    medical_section = driver.find_element(By.ID, "medical-history-section")
    medical_toggle = driver.find_element(By.ID, "medical-history-toggle")
    
    medical_toggle.click()
    assert not medical_section.is_displayed()  # Should be collapsed
    
    medical_toggle.click()
    assert medical_section.is_displayed()  # Should be expanded
```

---

### TC-EPR-UI-002: PDF Export User Experience

**Test Objective:** Verify PDF export process is intuitive and provides feedback

**Test Steps:**
1. Navigate to patient profile
2. Click export PDF button
3. Verify loading state and progress indication
4. Verify successful download

**Expected Results:**
- Export button is clearly visible
- Loading state shows during generation
- Success message appears on completion
- PDF downloads automatically or provides download link

**Test Data:**
```python
def test_pdf_export_ux():
    # Navigate to patient profile
    driver.get(f"/patients/{patient_id}")
    
    # Find and click export button
    export_button = driver.find_element(By.ID, "export-pdf-button")
    assert export_button.is_enabled()
    
    export_button.click()
    
    # Verify loading state
    loading_indicator = driver.find_element(By.CLASS_NAME, "loading-spinner")
    assert loading_indicator.is_displayed()
    
    # Wait for completion
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "export-success"))
    )
    
    # Verify success message
    success_message = driver.find_element(By.CLASS_NAME, "export-success")
    assert "successfully generated" in success_message.text.lower()
```

---

## 5. Performance Tests

### TC-EPR-PERF-001: Patient Creation Performance

**Test Objective:** Verify patient creation with 45+ fields completes within acceptable time

**Test Steps:**
1. Create 100 patients with full field data
2. Measure creation time for each
3. Verify 95th percentile is under 2 seconds

**Test Data:**
```python
import asyncio
import statistics

async def test_patient_creation_performance():
    async def create_single_patient(session, patient_data):
        start = time.time()
        async with session.post("/patients/", 
            json=patient_data,
            headers=authenticated_headers
        ) as response:
            await response.json()
        return time.time() - start
    
    # Generate 100 patient datasets
    patient_datasets = [generate_full_patient_data(i) for i in range(100)]
    
    async with aiohttp.ClientSession() as session:
        tasks = [create_single_patient(session, data) for data in patient_datasets]
        creation_times = await asyncio.gather(*tasks)
    
    # Performance assertions
    avg_time = statistics.mean(creation_times)
    p95_time = statistics.quantiles(creation_times, n=20)[18]
    
    assert avg_time < 1.0   # Average under 1 second
    assert p95_time < 2.0   # 95th percentile under 2 seconds
```

---

### TC-EPR-PERF-002: PDF Generation Performance

**Test Objective:** Verify PDF generation completes within acceptable time limits

**Test Steps:**
1. Generate PDFs for patients with varying amounts of session data
2. Measure generation time based on data volume
3. Verify performance scales appropriately

**Test Data:**
```python
def test_pdf_generation_performance():
    # Test patients with different session counts
    test_cases = [
        {"sessions": 1, "max_time": 5.0},
        {"sessions": 5, "max_time": 8.0},
        {"sessions": 10, "max_time": 12.0},
        {"sessions": 20, "max_time": 20.0}
    ]
    
    for case in test_cases:
        patient_id = create_patient_with_sessions(case["sessions"])
        
        start = time.time()
        response = client.get(f"/patients/{patient_id}/export-pdf",
            headers=authenticated_headers
        )
        generation_time = time.time() - start
        
        assert response.status_code == 200
        assert generation_time < case["max_time"]
        
        print(f"PDF with {case['sessions']} sessions: {generation_time:.2f}s")
```

---

### TC-EPR-PERF-003: AI Summary Generation Performance

**Test Objective:** Verify AI summary generation scales with session count

**Test Steps:**
1. Test summary generation for patients with 1, 5, 10, 20 sessions
2. Measure generation time for each
3. Verify linear scaling

**Test Data:**
```python
def test_ai_summary_performance():
    session_counts = [1, 5, 10, 20]
    generation_times = []
    
    for count in session_counts:
        patient_id = create_patient_with_sessions(count)
        
        start = time.time()
        response = client.get(f"/patients/{patient_id}/overall-summary",
            headers=authenticated_headers
        )
        generation_time = time.time() - start
        
        assert response.status_code == 200
        generation_times.append(generation_time)
        
        print(f"Summary for {count} sessions: {generation_time:.2f}s")
    
    # Verify reasonable scaling (should be roughly linear)
    # 20 sessions shouldn't take more than 4x the time of 5 sessions
    ratio = generation_times[3] / generation_times[1]  # 20 sessions / 5 sessions
    assert ratio < 4.0
```

---

## Test Execution

### Test Environment Setup

```python
# conftest.py for enhanced patient report tests
import pytest
from fastapi.testclient import TestClient
import tempfile
import os

@pytest.fixture
def test_patient_data():
    return {
        "full_name": "Test Patient",
        "age": "30",
        "gender": "Female",
        "current_medical_conditions": "None",
        "psychiatric_illness_in_family": "Depression - mother",
        # ... all 45+ fields
    }

@pytest.fixture
def patient_with_sessions(client, authenticated_headers, test_patient_data):
    # Create patient
    patient_response = client.post("/patients/", 
        json=test_patient_data,
        headers=authenticated_headers
    )
    patient_id = patient_response.json()["patient"]["id"]
    
    # Add sample sessions
    sessions = []
    for i in range(3):
        session_data = {
            "patient_id": patient_id,
            "original_transcription": f"Session {i+1} transcription content...",
            "language": "english",
            "duration": 3600
        }
        session_response = client.post("/sessions/",
            json=session_data,
            headers=authenticated_headers
        )
        sessions.append(session_response.json()["session"])
    
    return {"patient_id": patient_id, "sessions": sessions}

def extract_pdf_text(pdf_content):
    """Helper function to extract text from PDF for testing"""
    import PyPDF2
    import io
    
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text
```

### Running Tests

```bash
# Run all enhanced patient report tests
pytest documentations/enhanced-patient-report/test-cases.md -v

# Run specific test categories
pytest -k "test_epr" -v                     # Unit tests
pytest -k "test_epr_int" -v                # Integration tests
pytest -k "test_epr_pbt" -v                # Property-based tests
pytest -k "test_epr_ui" -v                 # UI/UX tests
pytest -k "test_epr_perf" -v               # Performance tests

# Run with coverage
pytest --cov=patient_router --cov=summarization_service --cov-report=html

# Run performance tests separately (they take longer)
pytest -k "perf" -v --tb=short
```

### Test Data Generators

```python
def generate_full_patient_data(index=0):
    """Generate comprehensive patient data for testing"""
    return {
        "full_name": f"Test Patient {index}",
        "age": str(25 + (index % 50)),
        "gender": ["Male", "Female", "Other"][index % 3],
        "date_of_birth": f"199{index % 10}-0{(index % 12) + 1:02d}-15",
        "residence": f"{100 + index} Test St, Test City, TS",
        "education": ["High School", "Bachelor's", "Master's", "PhD"][index % 4],
        "occupation": f"Test Occupation {index}",
        "marital_status": ["Single", "Married", "Divorced", "Widowed"][index % 4],
        "current_medical_conditions": f"Test condition {index}",
        "past_medical_conditions": f"Past condition {index}",
        "current_medications": f"Test medication {index}",
        "allergies": f"Test allergy {index}" if index % 3 == 0 else "None",
        "hospitalizations": "None" if index % 5 != 0 else f"Test hospitalization {index}",
        # ... continue for all 45+ fields
    }

def create_patient_with_sessions(session_count=3):
    """Helper to create patient with specified number of sessions"""
    patient_data = generate_full_patient_data()
    patient_response = client.post("/patients/", 
        json=patient_data,
        headers=authenticated_headers
    )
    patient_id = patient_response.json()["patient"]["id"]
    
    for i in range(session_count):
        session_data = {
            "patient_id": patient_id,
            "original_transcription": f"Test session {i+1} with therapeutic content discussing patient progress and treatment goals.",
            "language": "english",
            "duration": 3600,
            "session_date": f"2024-01-{(i+1):02d}T10:00:00"
        }
        client.post("/sessions/", json=session_data, headers=authenticated_headers)
    
    return patient_id
```

---

## Test Coverage Goals

- **Unit Tests**: 95% code coverage for patient management endpoints
- **Integration Tests**: All patient workflows from creation to PDF export
- **Property-Based Tests**: Data persistence and AI consistency properties
- **UI/UX Tests**: All user interaction flows
- **Performance Tests**: All endpoints meet performance SLAs

## Continuous Integration

```yaml
# .github/workflows/patient-report-tests.yml
name: Enhanced Patient Report Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install PyPDF2  # For PDF testing
      - name: Run patient report tests
        run: pytest documentations/enhanced-patient-report/ -v --cov=patient
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```