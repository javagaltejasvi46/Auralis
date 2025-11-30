# Implementation Plan

- [x] 1. Implement backend search service and utilities



  - [x] 1.1 Create query type detector utility

    - Create `backend/search_utils.py` with `QueryType` enum and `detect_query_type()` function
    - Implement pattern matching for PHONE (digits only), NAME (letters/spaces), MIXED (alphanumeric), PATIENT_ID
    - Add `normalize_phone()` function to strip formatting characters
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 3.3_
  - [ ]* 1.2 Write property test for query type detection
    - **Property 4: Query type detection correctness**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
  - [ ]* 1.3 Write property test for phone normalization
    - **Property 2: Phone number normalization consistency**
    - **Validates: Requirements 3.3**

- [x] 2. Implement fuzzy matching and relevance scoring
  - [x] 2.1 Create fuzzy matching function
    - Add `fuzzy_match()` function using simple character similarity (Levenshtein-like)
    - Set threshold at 0.6 similarity for matches
    - _Requirements: 2.2_
  - [x] 2.2 Create relevance scoring function
    - Implement `calculate_relevance()` that scores exact matches highest
    - Score partial matches based on position and length of match
    - _Requirements: 2.3, 4.1, 4.2_
  - [ ]* 2.3 Write property test for fuzzy matching tolerance
    - **Property 5: Fuzzy name matching tolerance**
    - **Validates: Requirements 2.2**

- [x] 3. Implement search endpoint in patient router



  - [x] 3.1 Add search endpoint to patient_router.py

    - Create `GET /patients/search` endpoint with query parameter `q`
    - Implement multi-field search across patient_id, full_name, phone
    - Return results sorted by relevance score with match field and positions
    - Filter to only current therapist's active patients
    - _Requirements: 1.1, 2.1, 3.1, 3.2, 4.1, 4.3_
  - [ ]* 3.2 Write property test for search results validity
    - **Property 1: Search results contain query match**
    - **Validates: Requirements 1.1, 2.1**
  - [ ]* 3.3 Write property test for exact ID prioritization
    - **Property 3: Exact patient ID match prioritization**
    - **Validates: Requirements 4.1, 4.2**
  - [ ]* 3.4 Write property test for empty query behavior
    - **Property 6: Empty query returns all patients**
    - **Validates: Requirements 1.2**

- [x] 4. Checkpoint - Ensure all backend tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement frontend search API integration


  - [x] 5.1 Add search API function to api.ts


    - Add `search()` method to `patientAPI` object
    - Handle debouncing at component level
    - Define TypeScript interfaces for SearchResult and SearchResponse
    - _Requirements: 1.1_

- [x] 6. Implement SearchBar component


  - [x] 6.1 Create SearchBar component


    - Create `frontend/src/components/SearchBar.tsx`
    - Implement text input with search icon, clear button, loading indicator
    - Style to match existing app theme (COLORS, CARD_GLOW_STYLE)
    - _Requirements: 6.1, 6.4, 7.1, 7.2_

- [x] 7. Implement highlight utility


  - [x] 7.1 Create text highlight utility


    - Create `frontend/src/utils/highlight.tsx`
    - Implement `findMatchPositions()` and `highlightText()` functions
    - Return React nodes with highlighted spans
    - _Requirements: 6.3_
  - [ ]* 7.2 Write property test for highlight positions validity
    - **Property 7: Highlight positions validity**
    - **Validates: Requirements 6.3**

- [x] 8. Integrate search into PatientListScreen


  - [x] 8.1 Add search state and UI to PatientListScreen


    - Add search query state with debounced search effect (300ms)
    - Integrate SearchBar component in header
    - Display search results or full patient list based on query
    - Show "No patients found" message when results are empty
    - Navigate to PatientProfile on result selection
    - _Requirements: 1.1, 1.2, 1.3, 6.2, 7.3_


- [x] 9. Final Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.
