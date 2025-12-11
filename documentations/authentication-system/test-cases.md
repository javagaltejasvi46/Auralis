# Test Cases - Authentication System

## Overview

This document contains comprehensive test cases for the Authentication System, covering unit tests, integration tests, and property-based tests to ensure secure and reliable user authentication and authorization.

## Test Categories

### 1. Unit Tests
### 2. Integration Tests  
### 3. Property-Based Tests
### 4. Security Tests
### 5. Performance Tests

---

## 1. Unit Tests

### TC-AUTH-001: Therapist Registration - Valid Data

**Test Objective:** Verify successful therapist registration with valid data

**Prerequisites:** 
- Database is empty
- API server is running

**Test Steps:**
1. Send POST request to `/auth/register` with valid data:
   ```json
   {
     "email": "dr.smith@example.com",
     "username": "drsmith",
     "password": "SecurePass123!",
     "full_name": "Dr. John Smith",
     "license_number": "PSY12345",
     "specialization": "Clinical Psychology",
     "phone": "+1234567890"
   }
   ```

**Expected Results:**
- Status Code: 201 Created
- Response contains therapist profile without password
- Password is hashed using bcrypt in database
- `is_active` flag is set to true
- `created_at` timestamp is recorded

**Test Data:**
```python
def test_therapist_registration_valid():
    response = client.post("/auth/register", json={
        "email": "dr.smith@example.com",
        "username": "drsmith", 
        "password": "SecurePass123!",
        "full_name": "Dr. John Smith"
    })
    assert response.status_code == 201
    assert "password" not in response.json()
    assert response.json()["email"] == "dr.smith@example.com"
```

---

### TC-AUTH-002: Therapist Registration - Duplicate Email

**Test Objective:** Verify registration fails with duplicate email

**Prerequisites:**
- Therapist with email "dr.smith@example.com" already exists

**Test Steps:**
1. Attempt to register with existing email
2. Verify error response

**Expected Results:**
- Status Code: 400 Bad Request
- Error message indicates email already exists
- No new record created in database

**Test Data:**
```python
def test_registration_duplicate_email():
    # First registration
    client.post("/auth/register", json=valid_therapist_data)
    
    # Duplicate registration
    response = client.post("/auth/register", json=valid_therapist_data)
    assert response.status_code == 400
    assert "email already exists" in response.json()["detail"].lower()
```

---

### TC-AUTH-003: Secure Login - Valid Credentials

**Test Objective:** Verify successful login with valid credentials

**Prerequisites:**
- Therapist account exists with username "drsmith" and password "SecurePass123!"

**Test Steps:**
1. Send POST request to `/auth/login` with form data:
   ```
   username=drsmith&password=SecurePass123!
   ```

**Expected Results:**
- Status Code: 200 OK
- Response contains JWT access token
- Token expires in 24 hours
- Last login timestamp updated
- Token payload contains therapist ID and username

**Test Data:**
```python
def test_login_valid_credentials():
    response = client.post("/auth/login", data={
        "username": "drsmith",
        "password": "SecurePass123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
    # Verify token payload
    token = response.json()["access_token"]
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == "drsmith"
```

---

### TC-AUTH-004: Secure Login - Invalid Credentials

**Test Objective:** Verify login fails with invalid credentials

**Test Steps:**
1. Attempt login with wrong password
2. Attempt login with non-existent username

**Expected Results:**
- Status Code: 401 Unauthorized
- Generic error message (doesn't reveal if username or password was wrong)
- No token generated
- No last login timestamp update

**Test Data:**
```python
def test_login_invalid_password():
    response = client.post("/auth/login", data={
        "username": "drsmith",
        "password": "WrongPassword"
    })
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()

def test_login_nonexistent_user():
    response = client.post("/auth/login", data={
        "username": "nonexistent",
        "password": "AnyPassword"
    })
    assert response.status_code == 401
```

---

### TC-AUTH-005: Token Validation - Valid Token

**Test Objective:** Verify API access with valid JWT token

**Prerequisites:**
- Valid JWT token obtained from login

**Test Steps:**
1. Make authenticated request to `/auth/me` with valid token
2. Verify response contains therapist profile

**Expected Results:**
- Status Code: 200 OK
- Response contains therapist information
- Patient count included
- Password not included

**Test Data:**
```python
def test_token_validation_valid():
    # Login and get token
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Use token for authenticated request
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    
    assert response.status_code == 200
    assert "password" not in response.json()
    assert "patient_count" in response.json()
```

---

### TC-AUTH-006: Token Validation - Expired Token

**Test Objective:** Verify API rejects expired tokens

**Test Steps:**
1. Create expired JWT token
2. Attempt API access with expired token

**Expected Results:**
- Status Code: 401 Unauthorized
- Error message indicates token expired
- Access denied to protected resource

**Test Data:**
```python
def test_token_validation_expired():
    # Create expired token
    expired_payload = {
        "sub": "drsmith",
        "therapist_id": 1,
        "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
    }
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm="HS256")
    
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/auth/me", headers=headers)
    
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()
```

---

### TC-AUTH-007: Password Security - bcrypt Hashing

**Test Objective:** Verify passwords are properly hashed with bcrypt

**Test Steps:**
1. Register therapist with password
2. Verify password is hashed in database
3. Verify hash uses bcrypt with appropriate cost factor

**Expected Results:**
- Plain text password never stored
- Hash starts with "$2b$" (bcrypt identifier)
- Cost factor is 12 or higher
- Each registration produces unique hash (due to salt)

**Test Data:**
```python
def test_password_hashing():
    password = "TestPassword123!"
    
    # Register therapist
    client.post("/auth/register", json={
        "username": "testuser",
        "password": password,
        "email": "test@example.com",
        "full_name": "Test User"
    })
    
    # Check database
    therapist = db.query(Therapist).filter(Therapist.username == "testuser").first()
    
    # Verify hash format
    assert therapist.hashed_password.startswith("$2b$")
    assert therapist.hashed_password != password
    
    # Verify hash can be verified
    assert bcrypt.checkpw(password.encode(), therapist.hashed_password.encode())
```

---

## 2. Integration Tests

### TC-AUTH-INT-001: Complete Authentication Flow

**Test Objective:** Verify complete registration → login → API access flow

**Test Steps:**
1. Register new therapist
2. Login with credentials
3. Use token to access protected resources
4. Logout

**Expected Results:**
- All steps complete successfully
- Data isolation works correctly
- Token lifecycle managed properly

**Test Data:**
```python
def test_complete_auth_flow():
    # 1. Register
    register_response = client.post("/auth/register", json=therapist_data)
    assert register_response.status_code == 201
    
    # 2. Login
    login_response = client.post("/auth/login", data={
        "username": therapist_data["username"],
        "password": therapist_data["password"]
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 3. Access protected resource
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = client.get("/auth/me", headers=headers)
    assert profile_response.status_code == 200
    
    # 4. Logout (client-side token removal)
    logout_response = client.post("/auth/logout", headers=headers)
    assert logout_response.status_code == 200
```

---

### TC-AUTH-INT-002: Data Isolation Between Therapists

**Test Objective:** Verify therapists can only access their own data

**Test Steps:**
1. Register two therapists
2. Login as therapist A, create patient
3. Login as therapist B, attempt to access therapist A's patient

**Expected Results:**
- Therapist B cannot see therapist A's patients
- API returns 404 Not Found for cross-therapist access
- No data leakage between accounts

**Test Data:**
```python
def test_data_isolation():
    # Register two therapists
    therapist_a = register_therapist("therapist_a")
    therapist_b = register_therapist("therapist_b")
    
    # Therapist A creates patient
    token_a = login_therapist("therapist_a")
    patient_response = client.post("/patients/", 
        json={"full_name": "Patient A"}, 
        headers={"Authorization": f"Bearer {token_a}"}
    )
    patient_id = patient_response.json()["patient"]["id"]
    
    # Therapist B tries to access Patient A
    token_b = login_therapist("therapist_b")
    access_response = client.get(f"/patients/{patient_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert access_response.status_code == 404
```

---

## 3. Property-Based Tests

### TC-AUTH-PBT-001: Password Hashing Consistency

**Property:** For any valid password, hashing should be consistent and verifiable

**Test Implementation:**
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=8, max_size=100))
def test_password_hashing_property(password):
    """Property: Any password should hash consistently and be verifiable"""
    # Hash the password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    # Property 1: Hash should be different from original
    assert hashed.decode() != password
    
    # Property 2: Hash should be verifiable
    assert bcrypt.checkpw(password.encode(), hashed)
    
    # Property 3: Hash should start with bcrypt identifier
    assert hashed.decode().startswith("$2b$")
```

**Validates:** Requirements 6.1, 6.2, 6.3

---

### TC-AUTH-PBT-002: JWT Token Round Trip

**Property:** For any valid therapist data, JWT encoding and decoding should be consistent

**Test Implementation:**
```python
@given(st.integers(min_value=1), st.text(min_size=1, max_size=50))
def test_jwt_round_trip_property(therapist_id, username):
    """Property: JWT tokens should encode and decode consistently"""
    # Create payload
    payload = {
        "sub": username,
        "therapist_id": therapist_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    # Encode token
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    # Decode token
    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    
    # Property: Decoded data should match original
    assert decoded["sub"] == username
    assert decoded["therapist_id"] == therapist_id
```

**Validates:** Requirements 2.1, 2.4, 3.1

---

## 4. Security Tests

### TC-AUTH-SEC-001: SQL Injection Prevention

**Test Objective:** Verify authentication endpoints are protected against SQL injection

**Test Steps:**
1. Attempt login with SQL injection payloads in username/password
2. Verify no database errors or unauthorized access

**Test Data:**
```python
def test_sql_injection_prevention():
    injection_payloads = [
        "admin'; DROP TABLE therapists; --",
        "' OR '1'='1",
        "admin'/**/OR/**/1=1#",
        "'; UNION SELECT * FROM therapists; --"
    ]
    
    for payload in injection_payloads:
        response = client.post("/auth/login", data={
            "username": payload,
            "password": "any_password"
        })
        # Should fail authentication, not cause database error
        assert response.status_code == 401
        assert "sql" not in response.json().get("detail", "").lower()
```

---

### TC-AUTH-SEC-002: Timing Attack Prevention

**Test Objective:** Verify login timing doesn't reveal username validity

**Test Steps:**
1. Measure login time for valid username + wrong password
2. Measure login time for invalid username + any password
3. Verify timing difference is minimal

**Test Data:**
```python
import time

def test_timing_attack_prevention():
    # Valid username, wrong password
    start = time.time()
    client.post("/auth/login", data={
        "username": "drsmith",  # exists
        "password": "wrong"
    })
    valid_user_time = time.time() - start
    
    # Invalid username, any password
    start = time.time()
    client.post("/auth/login", data={
        "username": "nonexistent",
        "password": "any"
    })
    invalid_user_time = time.time() - start
    
    # Timing difference should be minimal (< 100ms)
    time_diff = abs(valid_user_time - invalid_user_time)
    assert time_diff < 0.1
```

---

### TC-AUTH-SEC-003: Token Tampering Detection

**Test Objective:** Verify tampered JWT tokens are rejected

**Test Steps:**
1. Get valid JWT token
2. Modify token payload or signature
3. Attempt API access with tampered token

**Expected Results:**
- Tampered tokens are rejected
- Status Code: 401 Unauthorized
- No access granted to protected resources

**Test Data:**
```python
def test_token_tampering_detection():
    # Get valid token
    login_response = client.post("/auth/login", data=valid_credentials)
    valid_token = login_response.json()["access_token"]
    
    # Tamper with token (change one character)
    tampered_token = valid_token[:-1] + "X"
    
    # Attempt access with tampered token
    headers = {"Authorization": f"Bearer {tampered_token}"}
    response = client.get("/auth/me", headers=headers)
    
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()
```

---

## 5. Performance Tests

### TC-AUTH-PERF-001: Login Performance

**Test Objective:** Verify login completes within acceptable time limits

**Test Steps:**
1. Perform 100 concurrent login requests
2. Measure response times
3. Verify 95th percentile is under 500ms

**Test Data:**
```python
import asyncio
import aiohttp
import statistics

async def test_login_performance():
    async def single_login(session):
        start = time.time()
        async with session.post("/auth/login", data=valid_credentials) as response:
            await response.json()
        return time.time() - start
    
    async with aiohttp.ClientSession() as session:
        tasks = [single_login(session) for _ in range(100)]
        response_times = await asyncio.gather(*tasks)
    
    # Performance assertions
    avg_time = statistics.mean(response_times)
    p95_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
    
    assert avg_time < 0.2  # Average under 200ms
    assert p95_time < 0.5  # 95th percentile under 500ms
```

---

### TC-AUTH-PERF-002: Password Hashing Performance

**Test Objective:** Verify bcrypt hashing completes within reasonable time

**Test Steps:**
1. Hash 10 different passwords
2. Measure hashing time for each
3. Verify average time is under 1 second

**Test Data:**
```python
def test_password_hashing_performance():
    passwords = [f"TestPassword{i}!" for i in range(10)]
    hash_times = []
    
    for password in passwords:
        start = time.time()
        bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        hash_time = time.time() - start
        hash_times.append(hash_time)
    
    avg_hash_time = statistics.mean(hash_times)
    assert avg_hash_time < 1.0  # Under 1 second average
```

---

## Test Execution

### Test Environment Setup

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def client():
    # Create test database
    engine = create_engine("sqlite:///./test.db")
    TestingSessionLocal = sessionmaker(bind=engine)
    
    # Override database dependency
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield TestClient(app)
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
```

### Running Tests

```bash
# Run all authentication tests
pytest documentations/authentication-system/test-cases.md -v

# Run specific test categories
pytest -k "test_auth" -v                    # Unit tests
pytest -k "test_auth_int" -v               # Integration tests  
pytest -k "test_auth_pbt" -v               # Property-based tests
pytest -k "test_auth_sec" -v               # Security tests
pytest -k "test_auth_perf" -v              # Performance tests

# Generate coverage report
pytest --cov=auth_router --cov-report=html
```

### Test Data Management

```python
# Test fixtures
@pytest.fixture
def valid_therapist_data():
    return {
        "email": "dr.test@example.com",
        "username": "drtest",
        "password": "SecurePass123!",
        "full_name": "Dr. Test User",
        "license_number": "TEST123",
        "specialization": "Test Psychology"
    }

@pytest.fixture
def authenticated_headers(client, valid_therapist_data):
    # Register and login
    client.post("/auth/register", json=valid_therapist_data)
    login_response = client.post("/auth/login", data={
        "username": valid_therapist_data["username"],
        "password": valid_therapist_data["password"]
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

---

## Test Coverage Goals

- **Unit Tests**: 95% code coverage
- **Integration Tests**: All user workflows covered
- **Property-Based Tests**: Core authentication properties verified
- **Security Tests**: All OWASP Top 10 vulnerabilities addressed
- **Performance Tests**: All endpoints meet SLA requirements

## Continuous Integration

```yaml
# .github/workflows/auth-tests.yml
name: Authentication Tests
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
      - name: Run authentication tests
        run: pytest documentations/authentication-system/ -v --cov=auth
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```