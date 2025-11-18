# AURALIS API Documentation v2.0

Complete API reference for authentication, patient management, and session handling.

## Base URL
```
http://localhost:8002
```

## Authentication

All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### Register Therapist
```http
POST /auth/register
Content-Type: application/json

{
  "email": "doctor@example.com",
  "username": "drsmith",
  "password": "securepassword123",
  "full_name": "Dr. John Smith",
  "license_number": "MED12345",
  "specialization": "Clinical Psychology",
  "phone": "+1234567890"
}

Response: 200 OK
{
  "success": true,
  "message": "Account created successfully",
  "therapist": {
    "id": 1,
    "email": "doctor@example.com",
    "username": "drsmith",
    "full_name": "Dr. John Smith",
    ...
  }
}
```

### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=drsmith&password=securepassword123

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "therapist": {
    "id": 1,
    "email": "doctor@example.com",
    ...
  }
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "therapist": {
    "id": 1,
    "email": "doctor@example.com",
    "patient_count": 5
  }
}
```

### Logout
```http
POST /auth/logout
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## Patient Management

### Create Patient
```http
POST /patients/
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "Jane Doe",
  "date_of_birth": "1990-05-15",
  "gender": "Female",
  "phone": "+1234567890",
  "email": "jane@example.com",
  "address": "123 Main St, City",
  "emergency_contact": "John Doe: +0987654321",
  "medical_history": "No known allergies",
  "notes": "First consultation"
}

Response: 200 OK
{
  "success": true,
  "message": "Patient created successfully",
  "patient": {
    "id": 1,
    "patient_id": "P20241116ABC12345",
    "full_name": "Jane Doe",
    "session_count": 0,
    ...
  }
}
```

### Get All Patients
```http
GET /patients/?active_only=true
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "count": 5,
  "patients": [
    {
      "id": 1,
      "patient_id": "P20241116ABC12345",
      "full_name": "Jane Doe",
      "session_count": 3,
      ...
    },
    ...
  ]
}
```

### Get Patient Details
```http
GET /patients/1?include_sessions=true
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "patient": {
    "id": 1,
    "patient_id": "P20241116ABC12345",
    "full_name": "Jane Doe",
    "session_count": 3,
    "sessions": [
      {
        "id": 1,
        "session_number": 1,
        "session_date": "2024-11-16T10:00:00",
        ...
      },
      ...
    ]
  }
}
```

### Update Patient
```http
PUT /patients/1
Authorization: Bearer <token>
Content-Type: application/json

{
  "phone": "+1111111111",
  "notes": "Updated contact information"
}

Response: 200 OK
{
  "success": true,
  "message": "Patient updated successfully",
  "patient": { ... }
}
```

### Delete Patient (Soft Delete)
```http
DELETE /patients/1
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "message": "Patient deactivated successfully"
}
```

---

## Session Management

### Create Session
```http
POST /sessions/
Authorization: Bearer <token>
Content-Type: application/json

{
  "patient_id": 1,
  "language": "hindi",
  "duration": 1800,
  "original_transcription": "नमस्ते, आज हम...",
  "notes": "Initial consultation"
}

Response: 200 OK
{
  "success": true,
  "message": "Session created successfully",
  "session": {
    "id": 1,
    "patient_id": 1,
    "session_number": 1,
    "session_date": "2024-11-16T10:00:00",
    ...
  }
}
```

### Get Patient Sessions
```http
GET /sessions/patient/1
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "count": 3,
  "sessions": [
    {
      "id": 3,
      "session_number": 3,
      "session_date": "2024-11-16T10:00:00",
      "duration": 1800,
      "language": "hindi",
      "original_transcription": "...",
      ...
    },
    ...
  ]
}
```

### Get Session Details
```http
GET /sessions/1
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "session": {
    "id": 1,
    "patient_id": 1,
    "session_number": 1,
    "original_transcription": "...",
    "translated_transcription": "...",
    "notes": "...",
    "diagnosis": "...",
    "treatment_plan": "...",
    ...
  }
}
```

### Update Session
```http
PUT /sessions/1
Authorization: Bearer <token>
Content-Type: application/json

{
  "translated_transcription": "Hello, today we...",
  "translation_language": "en",
  "diagnosis": "Mild anxiety",
  "treatment_plan": "CBT sessions recommended",
  "is_completed": true
}

Response: 200 OK
{
  "success": true,
  "message": "Session updated successfully",
  "session": { ... }
}
```

### Upload Session Audio
```http
POST /sessions/1/audio
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <audio_file.m4a>

Response: 200 OK
{
  "success": true,
  "message": "Audio uploaded successfully",
  "file_path": "uploads/sessions/1/session_1_abc123.m4a"
}
```

### Delete Session
```http
DELETE /sessions/1
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "message": "Session deleted successfully"
}
```

---

## Translation (Public)

### Translate Text
```http
POST /translate
Content-Type: application/json

{
  "text": "Hello, how are you?",
  "target_language": "hi",
  "source_language": "en"
}

Response: 200 OK
{
  "success": true,
  "original_text": "Hello, how are you?",
  "translated_text": "नमस्ते, आप कैसे हैं?",
  "source_language": "en",
  "target_language": "hi"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Account not verified"
}
```

### 404 Not Found
```json
{
  "detail": "Patient not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

---

## Database Schema

### Therapist
- id (Integer, PK)
- email (String, Unique)
- username (String, Unique)
- hashed_password (String)
- full_name (String)
- license_number (String, Unique)
- specialization (String)
- phone (String)
- is_active (Boolean)
- is_verified (Boolean)
- created_at (DateTime)
- last_login (DateTime)

### Patient
- id (Integer, PK)
- therapist_id (Integer, FK)
- patient_id (String, Unique)
- full_name (String)
- date_of_birth (DateTime)
- gender (String)
- phone (String)
- email (String)
- address (Text)
- emergency_contact (String)
- medical_history (Text)
- notes (Text)
- is_active (Boolean)
- created_at (DateTime)
- updated_at (DateTime)

### Session
- id (Integer, PK)
- patient_id (Integer, FK)
- session_number (Integer)
- session_date (DateTime)
- duration (Integer)
- language (String)
- original_transcription (Text)
- translated_transcription (Text)
- translation_language (String)
- audio_file_path (String)
- audio_file_size (Integer)
- notes (Text)
- diagnosis (Text)
- treatment_plan (Text)
- is_completed (Boolean)
- created_at (DateTime)
- updated_at (DateTime)

---

## Security Notes

1. **Password Hashing**: Passwords are hashed using bcrypt
2. **JWT Tokens**: Access tokens expire after 24 hours
3. **HTTPS**: Use HTTPS in production
4. **CORS**: Configure allowed origins in production
5. **Rate Limiting**: Implement rate limiting for production
6. **Data Encryption**: Encrypt sensitive patient data at rest

---

## Testing with cURL

### Register
```bash
curl -X POST http://localhost:8002/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@example.com",
    "username": "drsmith",
    "password": "test123",
    "full_name": "Dr. Smith",
    "license_number": "MED123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=drsmith&password=test123"
```

### Create Patient (with token)
```bash
curl -X POST http://localhost:8002/patients/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Doe",
    "phone": "+1234567890"
  }'
```

---

**For more information, visit the interactive API docs at: http://localhost:8002/docs**
