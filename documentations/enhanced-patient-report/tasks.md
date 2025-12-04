# Implementation Plan

- [x] 1. Extend Patient Database Model


  - [x] 1.1 Add new fields to Patient model in backend/models.py


    - Add Patient Information fields (age, residence, education, occupation, marital_status, date_of_assessment)
    - Add Medical History fields (current_medical_conditions, past_medical_conditions, current_medications, allergies, hospitalizations)
    - Add Psychiatric History fields (previous_psychiatric_diagnoses, previous_psychiatric_treatment, previous_psychiatric_hospitalizations, suicide_self_harm_history, substance_use_history)
    - Add Family History fields (psychiatric_illness_family, medical_illness_family, family_dynamics, significant_family_events)
    - Add Social History fields (childhood_developmental_history, educational_history, occupational_history, relationship_history, social_support_system, living_situation, cultural_religious_background)
    - Add Clinical Assessment fields (chief_complaint, chief_complaint_description, illness_onset, illness_progression, previous_episodes, triggers, impact_on_functioning)
    - Add Mental Status Examination fields (mse_appearance, mse_behavior, mse_speech, mse_mood, mse_affect, mse_thought_process, mse_thought_content, mse_perception, mse_cognition, mse_insight, mse_judgment)
    - Update to_dict() method to include all new fields
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_
  - [ ]* 1.2 Write property test for patient data round-trip
    - **Property 1: Patient Data Round-Trip Persistence**
    - **Validates: Requirements 1.6**

- [x] 2. Create Database Migration



  - [x] 2.1 Create migration script to add new columns to patients table

    - Write Alembic migration or manual SQL migration script
    - Handle existing patient records with NULL values for new fields
    - _Requirements: 1.6_


- [x] 3. Update Patient API Endpoints

  - [x] 3.1 Update patient router to handle all new fields


    - Modify create patient endpoint to accept all new fields
    - Modify get patient endpoint to return all new fields
    - Modify update patient endpoint to handle all new fields
    - Add input validation for new fields
    - _Requirements: 1.6, 5.1, 5.2, 5.3_
  - [ ]* 3.2 Write property test for patient view completeness
    - **Property 2: Patient View Completeness**
    - **Validates: Requirements 1.7**
  - [ ]* 3.3 Write property test for edit timestamp preservation
    - **Property 11: Edit Preserves Creation Timestamp**
    - **Validates: Requirements 5.2, 5.3**



- [x] 4. Update Frontend TypeScript Types

  - [x] 4.1 Extend Patient interface in frontend/src/types.ts

    - Add all new patient fields matching backend model
    - Add SessionSummary interface
    - Add OverallSummary interface
    - Add PDFReport interface
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_


- [x] 5. Enhance CreatePatientScreen


  - [x] 5.1 Create multi-section patient registration form

    - Add collapsible section for Patient Information (name, age, gender, DOB, residence, education, occupation, marital status)
    - Add collapsible section for Medical History
    - Add collapsible section for Psychiatric History
    - Add collapsible section for Family History
    - Add collapsible section for Social History
    - Implement form validation for required fields
    - Update API call to submit all new fields
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 6. Checkpoint - Verify patient creation flow

  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Enhance PatientProfileScreen



  - [x] 7.1 Display all patient information in organized sections

    - Create section components for each category (Patient Info, Medical, Psychiatric, Family, Social)
    - Display all fields with proper labels
    - Add edit button to navigate to edit screen
    - _Requirements: 1.7, 5.1_



- [x] 8. Create EditPatientScreen

  - [x] 8.1 Implement patient information editing screen

    - Create form pre-populated with existing patient data
    - Allow editing of all patient fields
    - Implement save functionality with API call
    - Handle loading and error states
    - _Requirements: 5.1, 5.2, 5.3_



- [x] 9. Update Summarization Service for Session Summaries

  - [x] 9.1 Update session summary generation to follow template format

    - Modify summarization prompt to generate structured output
    - Include session number and date in output
    - Structure output with: Topics Discussed, Interventions Used, Client Progress, Homework Assigned, Therapist Observations, Plan for Next Session
    - Include therapist name in output
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [ ]* 9.2 Write property test for session summary metadata
    - **Property 3: Session Summary Contains Required Metadata**
    - **Validates: Requirements 2.1**
  - [ ]* 9.3 Write property test for session summary structure
    - **Property 4: Session Summary Structure Completeness**
    - **Validates: Requirements 2.2, 2.3**

- [x] 10. Implement Overall Summary Generation



  - [x] 10.1 Create overall summary endpoint in backend

    - Create GET /api/patients/{id}/overall-summary endpoint
    - Aggregate all patient information sections
    - Include chief complaints and course of illness
    - Include baseline assessment (Mental Status Examination)
    - Aggregate all session summaries in chronological order
    - Include report generation date
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_
  - [ ]* 10.2 Write property test for overall summary patient info
    - **Property 5: Overall Summary Contains Patient Information**
    - **Validates: Requirements 3.1**
  - [ ]* 10.3 Write property test for overall summary clinical sections
    - **Property 6: Overall Summary Contains Clinical Sections**
    - **Validates: Requirements 3.2, 3.3, 3.4**
  - [ ]* 10.4 Write property test for session aggregation ordering
    - **Property 7: Session Aggregation Ordering**
    - **Validates: Requirements 3.5**


- [x] 11. Checkpoint - Verify summary generation
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Implement PDF Generation Service
  - [x] 12.1 Create PDF generator service in backend
    - Install reportlab or weasyprint for PDF generation
    - Create PDF template following psychotherapy report format
    - Include all patient information sections
    - Include overall summary
    - Include all session summaries with dates
    - Add therapist name and generation date to header
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  - [ ]* 12.2 Write property test for PDF patient sections
    - **Property 8: PDF Contains All Patient Sections**
    - **Validates: Requirements 4.1, 4.4**
  - [ ]* 12.3 Write property test for PDF session summaries
    - **Property 9: PDF Contains All Session Summaries**
    - **Validates: Requirements 4.2, 4.3**
  - [ ]* 12.4 Write property test for PDF header information
    - **Property 10: PDF Header Information**
    - **Validates: Requirements 4.5**

- [x] 13. Create PDF Export Endpoint
  - [x] 13.1 Create GET /api/patients/{id}/export-pdf endpoint
    - Generate PDF using PDF generator service
    - Return PDF file as downloadable response
    - Handle errors with appropriate error messages
    - _Requirements: 4.1, 4.6_

- [x] 14. Implement Frontend PDF Export
  - [x] 14.1 Add PDF export functionality to PatientProfileScreen
    - Add Export PDF button to patient profile
    - Call export-pdf endpoint
    - Handle PDF download/share using expo-sharing or expo-file-system
    - Show loading state during PDF generation
    - Handle errors with user-friendly messages
    - _Requirements: 4.6_

- [x] 15. Add Overall Summary View to Frontend

  - [x] 15.1 Create overall summary display component

    - Add Overall Summary section to PatientProfileScreen
    - Call overall-summary endpoint
    - Display formatted summary with all sections
    - Show loading and error states
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_



- [x] 16. Final Checkpoint - Complete integration testing

  - Ensure all tests pass, ask the user if questions arise.
