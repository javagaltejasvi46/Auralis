# Requirements Document

## Introduction

This feature enhances the Auralis psychotherapy application to collect comprehensive patient information following the standard psychotherapy report format, generate structured session and overall summaries using the report template, and export complete patient reports as PDF documents for sharing with other healthcare providers.

Currently, the patient creation form only collects basic information (name, patient ID, phone, email). This enhancement will expand data collection to include medical history, psychiatric history, family history, and social history. The summarization system will be updated to generate reports following the professional psychotherapy report template format, and a PDF export feature will be added for sharing reports with other doctors.

## Glossary

- **Auralis_System**: The psychotherapy session management application that handles patient records, session recordings, transcriptions, and summaries
- **Patient_Information**: Core demographic data including name, age, gender, date of birth, residence, education, occupation, and marital status
- **Medical_History**: Patient's current and past medical conditions, medications, allergies, and hospitalizations
- **Psychiatric_History**: Previous psychiatric diagnoses, treatments, hospitalizations, suicide/self-harm history, and substance use history
- **Family_History**: Psychiatric and medical illness in family, family dynamics, and significant family events
- **Social_History**: Childhood/developmental history, educational history, occupational history, relationship history, social support system, living situation, and cultural/religious background
- **Session_Summary**: AI-generated summary of a single therapy session following the session recording form template
- **Overall_Summary**: Comprehensive summary aggregating all sessions for a patient, including baseline assessment and course of illness
- **PDF_Report**: Exportable document containing patient details and summaries formatted for sharing with other healthcare providers
- **Baseline_Assessment**: Initial mental status examination including appearance, behavior, speech, mood, affect, thought process, thought content, perception, cognition, insight, and judgment

## Requirements

### Requirement 1

**User Story:** As a therapist, I want to collect comprehensive patient information during registration, so that I have complete background data for treatment planning.

#### Acceptance Criteria

1. WHEN a therapist creates a new patient THEN the Auralis_System SHALL display input fields for all Patient_Information fields (name, age, gender, date of birth, residence, education, occupation, marital status, date of assessment)
2. WHEN a therapist creates a new patient THEN the Auralis_System SHALL display input fields for Medical_History (current medical conditions, past medical conditions, current medications, allergies, hospitalizations)
3. WHEN a therapist creates a new patient THEN the Auralis_System SHALL display input fields for Psychiatric_History (previous diagnoses, previous treatment, previous hospitalizations, suicide/self-harm history, substance use history)
4. WHEN a therapist creates a new patient THEN the Auralis_System SHALL display input fields for Family_History (psychiatric illness, medical illness, family dynamics, significant events)
5. WHEN a therapist creates a new patient THEN the Auralis_System SHALL display input fields for Social_History (childhood/developmental, educational, occupational, relationship history, social support, living situation, cultural/religious background)
6. WHEN a therapist submits the patient form with required fields completed THEN the Auralis_System SHALL persist all patient data to the database
7. WHEN a therapist views an existing patient profile THEN the Auralis_System SHALL display all collected patient information in organized sections

### Requirement 2

**User Story:** As a therapist, I want session summaries to follow a professional template format, so that my documentation is consistent and clinically appropriate.

#### Acceptance Criteria

1. WHEN the Auralis_System generates a session summary THEN the Auralis_System SHALL include the session number and session date in the output
2. WHEN the Auralis_System generates a session summary THEN the Auralis_System SHALL structure the summary with topics discussed, interventions used, client progress, homework assigned, and therapist observations
3. WHEN the Auralis_System generates a session summary THEN the Auralis_System SHALL include a plan for the next session section
4. WHEN a therapist views a session summary THEN the Auralis_System SHALL display the therapist name and session date

### Requirement 3

**User Story:** As a therapist, I want an overall summary report that aggregates all sessions, so that I can see the complete treatment history at a glance.

#### Acceptance Criteria

1. WHEN a therapist requests an overall summary for a patient THEN the Auralis_System SHALL generate a report containing all Patient_Information sections
2. WHEN a therapist requests an overall summary THEN the Auralis_System SHALL include chief complaints with primary complaint and description
3. WHEN a therapist requests an overall summary THEN the Auralis_System SHALL include course of illness (onset, progression, previous episodes, triggers, impact on functioning)
4. WHEN a therapist requests an overall summary THEN the Auralis_System SHALL include a Baseline_Assessment section with mental status examination fields
5. WHEN a therapist requests an overall summary THEN the Auralis_System SHALL aggregate key findings from all sessions in chronological order
6. WHEN the overall summary is generated THEN the Auralis_System SHALL use the current date as the report generation date

### Requirement 4

**User Story:** As a therapist, I want to export patient reports as PDF documents, so that I can share them with other healthcare providers.

#### Acceptance Criteria

1. WHEN a therapist selects export on a patient profile THEN the Auralis_System SHALL generate a PDF document containing all patient information sections
2. WHEN a therapist selects export on a patient profile THEN the Auralis_System SHALL include the overall summary in the PDF document
3. WHEN a therapist selects export on a patient profile THEN the Auralis_System SHALL include all session summaries with their respective dates in the PDF document
4. WHEN the PDF is generated THEN the Auralis_System SHALL format the document following the psychotherapy report template structure
5. WHEN the PDF is generated THEN the Auralis_System SHALL include the therapist name and generation date in the document header
6. WHEN the PDF generation completes THEN the Auralis_System SHALL allow the therapist to download or share the document

### Requirement 5

**User Story:** As a therapist, I want to edit patient information after initial creation, so that I can update records as new information becomes available.

#### Acceptance Criteria

1. WHEN a therapist opens a patient profile THEN the Auralis_System SHALL provide an edit option for all patient information fields
2. WHEN a therapist saves edited patient information THEN the Auralis_System SHALL persist the changes and update the modified timestamp
3. WHEN patient information is edited THEN the Auralis_System SHALL maintain the original creation date while updating the modification date
