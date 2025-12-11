# Test Cases - Patient Search

## Overview

This document contains comprehensive test cases for the Patient Search system, covering intelligent search functionality with fuzzy matching, relevance scoring, and multi-field search capabilities.

## Test Categories

### 1. Unit Tests
### 2. Integration Tests
### 3. Property-Based Tests
### 4. Performance Tests
### 5. Search Algorithm Tests

---

## 1. Unit Tests

### TC-PS-001: Basic Name Search

**Test Objective:** Verify basic patient search by name functionality

**Prerequisites:**
- Multiple patients exist in database
- Authenticated therapist session

**Test Steps:**
1. Send GET request to `/patients/search?q=John`
2. Verify patients with "John" in name are returned
3. Check relevance scoring

**Expected Results:**
- Status Code: 200 OK
- Patients with matching names returned
- Results sorted by relevance score
- Match positions indicated

**Test Data:**
```python
def test_basic_name_search():
    # Create test patients
    patients = [
        {"full_name": "John Doe", "phone": "+1234567890"},
        {"full_name": "Jane Smith", "phone": "+1987654321"},
        {"full_name": "John Johnson", "phone": "+1555666777"},
        {"full_name": "Mary Johnson", "phone": "+1444555666"}
    ]
    
    patient_ids = []
    for patient_data in patients:
        response = client.post("/patients/", 
            json=patient_data,
            headers=authenticated_headers
        )
        patient_ids.append(response.json()["patient"]["id"])
    
    # Search for "John"
    search_response = client.get("/patients/search?q=John",
        headers=authenticated_headers
    )
    
    assert search_response.status_code == 200
    results = search_response.json()
    
    assert results["success"] == True
    assert results["query"] == "John"
    assert results["query_type"] == "name"
    assert results["count"] == 2
    
    # Verify correct patients returned
    returned_names = [r["patient"]["full_name"] for r in results["results"]]
    assert "John Doe" in returned_names
    assert "John Johnson" in returned_names
    assert "Jane Smith" not in returned_names
```
---

### TC-PS-002: Phone Number Search

**Test Objective:** Verify patient search by phone number with normalization

**Test Steps:**
1. Create patients with various phone formats
2. Search using different phone number formats
3. Verify normalization works correctly

**Expected Results:**
- Phone numbers normalized before matching
- Different formats match same number
- Partial phone numbers work

**Test Data:**
```python
def test_phone_number_search():
    # Create patients with different phone formats
    patients = [
        {"full_name": "Alice Brown", "phone": "+1-234-567-8900"},
        {"full_name": "Bob Wilson", "phone": "(555) 123-4567"},
        {"full_name": "Carol Davis", "phone": "9876543210"},
        {"full_name": "David Miller", "phone": "+1 (555) 987-6543"}
    ]
    
    for patient_data in patients:
        client.post("/patients/", json=patient_data, headers=authenticated_headers)
    
    # Test various search formats
    search_cases = [
        {"query": "2345678900", "expected_name": "Alice Brown"},
        {"query": "555-123-4567", "expected_name": "Bob Wilson"},
        {"query": "(987) 654-3210", "expected_name": "Carol Davis"},
        {"query": "555987", "expected_name": "David Miller"}  # Partial match
    ]
    
    for case in search_cases:
        response = client.get(f"/patients/search?q={case['query']}",
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        results = response.json()
        assert results["query_type"] == "phone"
        assert results["count"] >= 1
        
        found_names = [r["patient"]["full_name"] for r in results["results"]]
        assert case["expected_name"] in found_names

---

### TC-PS-003: Patient ID Search

**Test Objective:** Verify search by patient ID with exact and partial matching

**Test Steps:**
1. Create patients with specific patient IDs
2. Search by exact and partial patient IDs
3. Verify ID-based matching

**Expected Results:**
- Exact patient ID matches return highest relevance
- Partial patient ID matches work
- Case-insensitive matching

**Test Data:**
```python
def test_patient_id_search():
    # Create patients with specific IDs
    patients = [
        {"full_name": "Test Patient 1", "patient_id": "P001"},
        {"full_name": "Test Patient 2", "patient_id": "P002"},
        {"full_name": "Test Patient 3", "patient_id": "ABC123"},
        {"full_name": "Test Patient 4", "patient_id": "XYZ789"}
    ]
    
    for patient_data in patients:
        client.post("/patients/", json=patient_data, headers=authenticated_headers)
    
    # Test exact ID match
    response = client.get("/patients/search?q=P001", headers=authenticated_headers)
    results = response.json()
    
    assert results["query_type"] == "patient_id"
    assert results["count"] == 1
    assert results["results"][0]["patient"]["patient_id"] == "P001"
    assert results["results"][0]["relevance_score"] == 100  # Exact match
    
    # Test partial ID match
    response = client.get("/patients/search?q=P00", headers=authenticated_headers)
    results = response.json()
    
    assert results["count"] == 2  # P001 and P002
    
    # Test case insensitive
    response = client.get("/patients/search?q=abc123", headers=authenticated_headers)
    results = response.json()
    
    assert results["count"] == 1
    assert results["results"][0]["patient"]["patient_id"] == "ABC123"

---

### TC-PS-004: Fuzzy Name Matching

**Test Objective:** Verify fuzzy matching handles typos and variations

**Test Steps:**
1. Create patients with specific names
2. Search with typos and variations
3. Verify fuzzy matching works

**Expected Results:**
- Typos in names still return matches
- Similar names ranked appropriately
- Relevance scores reflect match quality

**Test Data:**
```python
def test_fuzzy_name_matching():
    # Create patients
    patients = [
        {"full_name": "Jennifer Smith"},
        {"full_name": "Jonathan Davis"},
        {"full_name": "Jessica Johnson"},
        {"full_name": "Michael Brown"}
    ]
    
    for patient_data in patients:
        client.post("/patients/", json=patient_data, headers=authenticated_headers)
    
    # Test fuzzy matching with typos
    fuzzy_cases = [
        {"query": "Jenifer", "expected": "Jennifer Smith"},  # Missing 'n'
        {"query": "Johnathan", "expected": "Jonathan Davis"},  # Extra 'h'
        {"query": "Jesica", "expected": "Jessica Johnson"},  # Missing 's'
        {"query": "Micheal", "expected": "Michael Brown"}  # Swapped 'ae'
    ]
    
    for case in fuzzy_cases:
        response = client.get(f"/patients/search?q={case['query']}",
            headers=authenticated_headers
        )
        
        results = response.json()
        assert results["count"] >= 1
        
        # Check if expected name is in results (may not be first due to fuzzy matching)
        found_names = [r["patient"]["full_name"] for r in results["results"]]
        assert case["expected"] in found_names

---

### TC-PS-005: Relevance Scoring

**Test Objective:** Verify relevance scoring ranks results appropriately

**Test Steps:**
1. Create patients with varying name similarities
2. Search with partial name
3. Verify scoring and ranking

**Expected Results:**
- Exact matches score highest (100)
- Partial matches score lower
- Results sorted by relevance score descending

**Test Data:**
```python
def test_relevance_scoring():
    # Create patients with varying similarities to "John"
    patients = [
        {"full_name": "John"},  # Exact match
        {"full_name": "John Smith"},  # Exact first name
        {"full_name": "Johnny Davis"},  # Similar
        {"full_name": "Johnson Wilson"},  # Contains
        {"full_name": "Mary Johnson"}  # Contains in last name
    ]
    
    for patient_data in patients:
        client.post("/patients/", json=patient_data, headers=authenticated_headers)
    
    response = client.get("/patients/search?q=John", headers=authenticated_headers)
    results = response.json()["results"]
    
    # Verify scoring order
    scores = [r["relevance_score"] for r in results]
    assert scores == sorted(scores, reverse=True)  # Descending order
    
    # Verify exact match scores highest
    exact_match = next(r for r in results if r["patient"]["full_name"] == "John")
    assert exact_match["relevance_score"] == 100
    
    # Verify partial matches score lower
    partial_matches = [r for r in results if r["patient"]["full_name"] != "John"]
    for match in partial_matches:
        assert match["relevance_score"] < 100

---

## 2. Integration Tests

### TC-PS-INT-001: Multi-Field Search Integration

**Test Objective:** Verify search works across all patient fields

**Test Steps:**
1. Create patients with data in different fields
2. Search by various field types
3. Verify correct field detection and matching

**Expected Results:**
- Search automatically detects field type
- Appropriate matching algorithm applied
- Match field indicated in results

**Test Data:**
```python
def test_multi_field_search_integration():
    # Create diverse patient data
    patients = [
        {
            "full_name": "Alice Johnson",
            "patient_id": "ALI001", 
            "phone": "+1234567890",
            "email": "alice@example.com"
        },
        {
            "full_name": "Bob Smith",
            "patient_id": "BOB002",
            "phone": "+1987654321", 
            "email": "bob@example.com"
        }
    ]
    
    for patient_data in patients:
        client.post("/patients/", json=patient_data, headers=authenticated_headers)
    
    # Test different field searches
    search_tests = [
        {"query": "Alice", "expected_type": "name", "expected_field": "name"},
        {"query": "ALI001", "expected_type": "patient_id", "expected_field": "patient_id"},
        {"query": "1234567890", "expected_type": "phone", "expected_field": "phone"},
        {"query": "alice@example.com", "expected_type": "email", "expected_field": "email"}
    ]
    
    for test in search_tests:
        response = client.get(f"/patients/search?q={test['query']}",
            headers=authenticated_headers
        )
        
        results = response.json()
        assert results["query_type"] == test["expected_type"]
        assert results["count"] >= 1
        assert results["results"][0]["match_field"] == test["expected_field"]

---

### TC-PS-INT-002: Search with Large Dataset

**Test Objective:** Verify search performance and accuracy with large patient dataset

**Test Steps:**
1. Create 1000+ patients with varied data
2. Perform various searches
3. Verify performance and accuracy

**Expected Results:**
- Search completes within 2 seconds
- Accurate results returned
- Proper pagination if needed

**Test Data:**
```python
def test_search_large_dataset():
    # Create 1000 patients with realistic data
    import random
    import string
    
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Mary"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]
    
    patients = []
    for i in range(1000):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        patient_data = {
            "full_name": f"{first_name} {last_name}",
            "patient_id": f"P{i:04d}",
            "phone": f"+1{random.randint(1000000000, 9999999999)}"
        }
        patients.append(patient_data)
        
        # Create in batches to avoid timeout
        if len(patients) == 100:
            for patient in patients:
                client.post("/patients/", json=patient, headers=authenticated_headers)
            patients = []
    
    # Test search performance
    start_time = time.time()
    response = client.get("/patients/search?q=John", headers=authenticated_headers)
    search_time = time.time() - start_time
    
    assert response.status_code == 200
    assert search_time < 2.0  # Under 2 seconds
    
    results = response.json()
    assert results["count"] > 0
    assert len(results["results"]) <= 50  # Reasonable limit

---

## 3. Property-Based Tests

### TC-PS-PBT-001: Search Consistency

**Property:** For any valid search query, results should be consistent and relevant

**Test Implementation:**
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=2, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
def test_search_consistency_property(query):
    """Property: Search should return consistent results for valid queries"""
    assume(len(query.strip()) >= 2)
    
    # Perform search twice
    response1 = client.get(f"/patients/search?q={query}", headers=authenticated_headers)
    response2 = client.get(f"/patients/search?q={query}", headers=authenticated_headers)
    
    # Property: Results should be identical
    if response1.status_code == 200 and response2.status_code == 200:
        results1 = response1.json()
        results2 = response2.json()
        
        assert results1["count"] == results2["count"]
        assert results1["query_type"] == results2["query_type"]
        
        # Results should be in same order
        if results1["count"] > 0:
            ids1 = [r["patient"]["id"] for r in results1["results"]]
            ids2 = [r["patient"]["id"] for r in results2["results"]]
            assert ids1 == ids2
```

**Validates:** Search consistency and determinism

---

### TC-PS-PBT-002: Query Type Detection

**Property:** Query type should be correctly detected for different input patterns

**Test Implementation:**
```python
@given(st.integers(min_value=1000000000, max_value=9999999999))
def test_phone_detection_property(phone_number):
    """Property: Phone numbers should be detected as phone type"""
    query = str(phone_number)
    
    response = client.get(f"/patients/search?q={query}", headers=authenticated_headers)
    
    if response.status_code == 200:
        results = response.json()
        assert results["query_type"] == "phone"

@given(st.text(min_size=3, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Nd'))))
def test_patient_id_detection_property(patient_id):
    """Property: Patient ID patterns should be detected correctly"""
    assume(any(c.isdigit() for c in patient_id))
    assume(any(c.isalpha() for c in patient_id))
    
    response = client.get(f"/patients/search?q={patient_id}", headers=authenticated_headers)
    
    if response.status_code == 200:
        results = response.json()
        assert results["query_type"] in ["patient_id", "name"]  # Could be either
```

**Validates:** Query type detection accuracy

---

## 4. Performance Tests

### TC-PS-PERF-001: Search Response Time

**Test Objective:** Verify search responds within acceptable time limits

**Test Steps:**
1. Create dataset of varying sizes
2. Perform searches with different query types
3. Measure response times

**Expected Results:**
- Small dataset (< 100 patients): Under 100ms
- Medium dataset (100-1000 patients): Under 500ms  
- Large dataset (1000+ patients): Under 2 seconds

**Test Data:**
```python
def test_search_response_time():
    dataset_sizes = [50, 500, 1000]
    time_limits = [0.1, 0.5, 2.0]  # seconds
    
    for size, limit in zip(dataset_sizes, time_limits):
        # Create dataset
        create_patient_dataset(size)
        
        # Test different query types
        queries = ["John", "P001", "1234567890"]
        
        for query in queries:
            start_time = time.time()
            response = client.get(f"/patients/search?q={query}",
                headers=authenticated_headers
            )
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            assert response_time < limit
            
            print(f"Dataset {size}, Query '{query}': {response_time:.3f}s")

def create_patient_dataset(size):
    """Helper to create patient dataset of specified size"""
    for i in range(size):
        patient_data = {
            "full_name": f"Patient {i:04d}",
            "patient_id": f"P{i:04d}",
            "phone": f"+1{1000000000 + i}"
        }
        client.post("/patients/", json=patient_data, headers=authenticated_headers)

---

### TC-PS-PERF-002: Concurrent Search Performance

**Test Objective:** Verify search handles concurrent requests efficiently

**Test Steps:**
1. Submit multiple concurrent search requests
2. Measure total processing time
3. Verify all requests complete successfully

**Expected Results:**
- All concurrent requests complete successfully
- No significant performance degradation
- Response times remain within limits

**Test Data:**
```python
import asyncio
import aiohttp

async def test_concurrent_search_performance():
    # Create test dataset
    create_patient_dataset(500)
    
    # Define concurrent search queries
    queries = ["John", "Jane", "P001", "P002", "1234567890", "Smith", "Johnson", "Brown"]
    
    async def single_search(session, query):
        start = time.time()
        async with session.get(f"/patients/search?q={query}",
            headers=authenticated_headers
        ) as response:
            result = await response.json()
        return time.time() - start, response.status, len(result.get("results", []))
    
    # Submit concurrent requests
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [single_search(session, query) for query in queries * 5]  # 40 total requests
        results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    # Verify all succeeded
    for response_time, status, result_count in results:
        assert status == 200
        assert response_time < 2.0  # Individual request under 2s
    
    # Total time should be much less than sequential
    assert total_time < 10.0  # All 40 requests in under 10s
    
    print(f"40 concurrent searches completed in {total_time:.2f}s")

---

## 5. Search Algorithm Tests

### TC-PS-ALG-001: Fuzzy Matching Algorithm

**Test Objective:** Verify fuzzy matching algorithm accuracy

**Test Steps:**
1. Test various edit distances
2. Verify scoring algorithm
3. Test edge cases

**Expected Results:**
- Single character differences handled
- Transpositions detected
- Appropriate scoring based on similarity

**Test Data:**
```python
def test_fuzzy_matching_algorithm():
    # Create base patient
    client.post("/patients/", 
        json={"full_name": "Alexander Johnson"},
        headers=authenticated_headers
    )
    
    # Test various fuzzy matches with expected scores
    fuzzy_tests = [
        {"query": "Alexander Johnson", "min_score": 100},  # Exact
        {"query": "Alexander Jonson", "min_score": 90},   # 1 char diff
        {"query": "Alexnader Johnson", "min_score": 85},  # Transposition
        {"query": "Alex Johnson", "min_score": 80},       # Truncation
        {"query": "Alexander J", "min_score": 70},        # Partial
        {"query": "Aleksandr Johnson", "min_score": 75}   # Multiple diffs
    ]
    
    for test in fuzzy_tests:
        response = client.get(f"/patients/search?q={test['query']}",
            headers=authenticated_headers
        )
        
        results = response.json()
        if results["count"] > 0:
            score = results["results"][0]["relevance_score"]
            assert score >= test["min_score"], f"Query '{test['query']}' scored {score}, expected >= {test['min_score']}"

---

### TC-PS-ALG-002: Phone Number Normalization

**Test Objective:** Verify phone number normalization handles various formats

**Test Steps:**
1. Test different phone number formats
2. Verify normalization consistency
3. Test international formats

**Expected Results:**
- All formats normalized to same pattern
- Consistent matching across formats
- International numbers handled

**Test Data:**
```python
def test_phone_normalization_algorithm():
    # Create patient with base phone number
    client.post("/patients/",
        json={
            "full_name": "Test Patient",
            "phone": "+1-234-567-8900"
        },
        headers=authenticated_headers
    )
    
    # Test various equivalent formats
    equivalent_formats = [
        "12345678900",
        "(234) 567-8900", 
        "234.567.8900",
        "+1 234 567 8900",
        "1-234-567-8900",
        "234-567-8900"
    ]
    
    for phone_format in equivalent_formats:
        response = client.get(f"/patients/search?q={phone_format}",
            headers=authenticated_headers
        )
        
        results = response.json()
        assert results["count"] == 1, f"Format '{phone_format}' should match"
        assert results["query_type"] == "phone"
        assert results["results"][0]["match_field"] == "phone"

---

## Test Execution

### Test Environment Setup

```python
# conftest.py for patient search tests
import pytest
import time

@pytest.fixture
def search_test_patients():
    """Create standard set of patients for search testing"""
    patients = [
        {"full_name": "John Smith", "patient_id": "JS001", "phone": "+1234567890"},
        {"full_name": "Jane Doe", "patient_id": "JD002", "phone": "+1987654321"},
        {"full_name": "Michael Johnson", "patient_id": "MJ003", "phone": "+1555666777"},
        {"full_name": "Sarah Wilson", "patient_id": "SW004", "phone": "+1444555666"},
        {"full_name": "David Brown", "patient_id": "DB005", "phone": "+1333444555"}
    ]
    
    created_patients = []
    for patient_data in patients:
        response = client.post("/patients/", 
            json=patient_data,
            headers=authenticated_headers
        )
        created_patients.append(response.json()["patient"])
    
    return created_patients

@pytest.fixture
def cleanup_patients():
    """Clean up patients after tests"""
    yield
    # Cleanup code would go here if needed
    pass
```

### Running Tests

```bash
# Run all patient search tests
pytest documentations/patient-search/test-cases.md -v

# Run specific test categories
pytest -k "test_ps" -v                      # Unit tests
pytest -k "test_ps_int" -v                 # Integration tests
pytest -k "test_ps_pbt" -v                 # Property-based tests
pytest -k "test_ps_perf" -v                # Performance tests
pytest -k "test_ps_alg" -v                 # Algorithm tests

# Run with coverage
pytest --cov=patient_router --cov-report=html

# Performance tests with timing
pytest -k "perf" -v -s --tb=short
```

### Continuous Integration

```yaml
# .github/workflows/patient-search-tests.yml
name: Patient Search Tests
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
      - name: Run patient search tests
        run: pytest documentations/patient-search/ -v --cov=search
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```