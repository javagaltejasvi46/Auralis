# Requirements Document

## Introduction

This feature provides a smart patient search functionality for doctors/therapists in the Auralis application. The search bar allows doctors to quickly find patients using any of three identifiers: patient name, phone number, or 6-digit patient ID. The search system intelligently interprets the input type and returns relevant results, enabling efficient navigation to patient profiles.

## Glossary

- **Therapist**: A doctor/healthcare provider who uses the Auralis application to manage patients
- **Patient**: An individual receiving therapy services, identified by name, phone, and a unique 6-digit patient ID
- **Patient ID**: A unique 6-digit alphanumeric identifier assigned to each patient (e.g., "PAT001", "123456")
- **Search Query**: The text input provided by the therapist to find patients
- **Search Results**: A list of patients matching the search query
- **Fuzzy Matching**: A search technique that finds approximate matches, tolerating minor typos or variations

## Requirements

### Requirement 1

**User Story:** As a therapist, I want to search for patients using a unified search bar, so that I can quickly find and access patient profiles without navigating through lists.

#### Acceptance Criteria

1. WHEN a therapist enters text in the search bar THEN the Search System SHALL display matching patients in real-time as results
2. WHEN the search bar is empty THEN the Search System SHALL display the full patient list or a prompt to search
3. WHEN a therapist selects a patient from search results THEN the Search System SHALL navigate to that patient's profile screen

### Requirement 2

**User Story:** As a therapist, I want to search by patient name with fuzzy matching, so that I can find patients even with partial or slightly misspelled names.

#### Acceptance Criteria

1. WHEN a therapist enters a partial name (minimum 2 characters) THEN the Search System SHALL return patients whose names contain the search term (case-insensitive)
2. WHEN a therapist enters a name with minor typos THEN the Search System SHALL return patients with similar names using fuzzy matching
3. WHEN multiple patients match the name search THEN the Search System SHALL display all matching patients sorted by relevance

### Requirement 3

**User Story:** As a therapist, I want to search by phone number, so that I can find patients when I only have their contact information.

#### Acceptance Criteria

1. WHEN a therapist enters digits that match a phone number pattern THEN the Search System SHALL search against patient phone numbers
2. WHEN a therapist enters a partial phone number (minimum 3 digits) THEN the Search System SHALL return patients whose phone numbers contain those digits
3. WHEN phone numbers are stored in different formats THEN the Search System SHALL normalize and match regardless of formatting (spaces, dashes, parentheses)

### Requirement 4

**User Story:** As a therapist, I want to search by 6-digit patient ID, so that I can directly access a specific patient's profile.

#### Acceptance Criteria

1. WHEN a therapist enters a 6-character alphanumeric string matching patient ID format THEN the Search System SHALL prioritize exact patient ID matches
2. WHEN an exact patient ID match exists THEN the Search System SHALL display that patient at the top of results
3. WHEN no exact patient ID match exists THEN the Search System SHALL fall back to searching other fields

### Requirement 5

**User Story:** As a therapist, I want the search system to intelligently detect what type of search I'm performing, so that I get the most relevant results without specifying the search type.

#### Acceptance Criteria

1. WHEN a therapist enters a query THEN the Search System SHALL automatically detect if the input is a patient ID, phone number, or name
2. WHEN the query contains only digits THEN the Search System SHALL search both phone numbers and patient IDs containing those digits
3. WHEN the query contains letters and numbers THEN the Search System SHALL search patient IDs and names
4. WHEN the query contains only letters and spaces THEN the Search System SHALL search patient names

### Requirement 6

**User Story:** As a therapist, I want clear visual feedback during search, so that I understand the search state and results.

#### Acceptance Criteria

1. WHEN a search is in progress THEN the Search System SHALL display a loading indicator
2. WHEN no results match the search query THEN the Search System SHALL display a "No patients found" message with the search term
3. WHEN results are displayed THEN the Search System SHALL highlight the matching portion of each result
4. WHEN the search bar has focus THEN the Search System SHALL provide visual indication of the active search state

### Requirement 7

**User Story:** As a therapist, I want to clear my search easily, so that I can start a new search or return to the full patient list.

#### Acceptance Criteria

1. WHEN text exists in the search bar THEN the Search System SHALL display a clear button
2. WHEN a therapist taps the clear button THEN the Search System SHALL empty the search bar and reset results
3. WHEN a therapist presses the device back button or escape key THEN the Search System SHALL clear the search if active
