/**
 * TypeScript type definitions
 */

export interface Therapist {
  id: number;
  email: string;
  username: string;
  full_name: string;
  license_number?: string;
  specialization?: string;
  phone?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  patient_count: number;
}

export interface Patient {
  id: number;
  patient_id: string;
  full_name: string;
  date_of_birth?: string;
  gender?: string;
  phone?: string;
  email?: string;
  address?: string;
  emergency_contact?: string;
  medical_history?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  session_count: number;
  sessions?: Session[];
  
  // Patient Information (Extended)
  age?: number;
  residence?: string;
  education?: string;
  occupation?: string;
  marital_status?: string;
  date_of_assessment?: string;
  
  // Medical History (Detailed)
  current_medical_conditions?: string;
  past_medical_conditions?: string;
  current_medications?: string;
  allergies?: string;
  hospitalizations?: string;
  
  // Psychiatric History
  previous_psychiatric_diagnoses?: string;
  previous_psychiatric_treatment?: string;
  previous_psychiatric_hospitalizations?: string;
  suicide_self_harm_history?: string;
  substance_use_history?: string;
  
  // Family History
  psychiatric_illness_family?: string;
  medical_illness_family?: string;
  family_dynamics?: string;
  significant_family_events?: string;
  
  // Social History
  childhood_developmental_history?: string;
  educational_history?: string;
  occupational_history?: string;
  relationship_history?: string;
  social_support_system?: string;
  living_situation?: string;
  cultural_religious_background?: string;
  
  // Clinical Assessment
  chief_complaint?: string;
  chief_complaint_description?: string;
  illness_onset?: string;
  illness_progression?: string;
  previous_episodes?: string;
  triggers?: string;
  impact_on_functioning?: string;
  
  // Mental Status Examination
  mse_appearance?: string;
  mse_behavior?: string;
  mse_speech?: string;
  mse_mood?: string;
  mse_affect?: string;
  mse_thought_process?: string;
  mse_thought_content?: string;
  mse_perception?: string;
  mse_cognition?: string;
  mse_insight?: string;
  mse_judgment?: string;
}

export interface Session {
  id: number;
  patient_id: number;
  session_number: number;
  session_date: string;
  duration?: number;
  language: string;
  original_transcription?: string;
  translated_transcription?: string;
  translation_language?: string;
  audio_file_path?: string;
  audio_file_size?: number;
  notes?: string;
  diagnosis?: string;
  treatment_plan?: string;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  therapist: Therapist;
}

export interface MatchPosition {
  start: number;
  end: number;
}

export interface SearchResult {
  patient: Patient;
  relevance_score: number;
  match_field: 'patient_id' | 'name' | 'phone';
  match_positions: MatchPosition[];
}

export interface SearchResponse {
  success: boolean;
  query: string;
  query_type: string;
  count: number;
  results: SearchResult[];
}

export interface SessionSummary {
  session_number: number;
  session_date: string;
  topics_discussed: string;
  interventions_used: string;
  client_progress: string;
  homework_assigned: string;
  therapist_observations: string;
  plan_for_next_session: string;
  therapist_name: string;
}

export interface CourseOfIllness {
  onset: string;
  progression: string;
  previous_episodes: string;
  triggers: string;
  impact_on_functioning: string;
}

export interface BaselineAssessment {
  appearance: string;
  behavior: string;
  speech: string;
  mood: string;
  affect: string;
  thought_process: string;
  thought_content: string;
  perception: string;
  cognition: string;
  insight: string;
  judgment: string;
}

export interface PatientInformation {
  name: string;
  age: string;
  gender: string;
  date_of_birth: string;
  residence: string;
  education: string;
  occupation: string;
  marital_status: string;
  date_of_assessment: string;
}

export interface MedicalHistory {
  current_medical_conditions: string;
  past_medical_conditions: string;
  current_medications: string;
  allergies: string;
  hospitalizations: string;
}

export interface PsychiatricHistory {
  previous_diagnoses: string;
  previous_treatment: string;
  previous_hospitalizations: string;
  suicide_self_harm_history: string;
  substance_use_history: string;
}

export interface FamilyHistory {
  psychiatric_illness: string;
  medical_illness: string;
  family_dynamics: string;
  significant_events: string;
}

export interface SocialHistory {
  childhood_developmental: string;
  educational: string;
  occupational: string;
  relationship: string;
  social_support: string;
  living_situation: string;
  cultural_religious: string;
}

export interface OverallSummary {
  patient_information: PatientInformation;
  medical_history: MedicalHistory;
  psychiatric_history: PsychiatricHistory;
  family_history: FamilyHistory;
  social_history: SocialHistory;
  chief_complaints: {
    primary: string;
    description: string;
  };
  course_of_illness: CourseOfIllness;
  baseline_assessment: BaselineAssessment;
  session_summaries: Array<{
    session_number: number;
    session_date: string;
    summary: string;
    therapist_name: string;
  }>;
  generated_date: string;
  therapist_name: string;
  session_count: number;
}

export interface ReportDataResponse {
  success: boolean;
  report_data: OverallSummary;
  therapist_name: string;
  generated_date: string;
}

export interface ExportReportData {
  // Patient Information
  patient_name?: string;
  patient_age?: string;
  patient_gender?: string;
  patient_dob?: string;
  patient_residence?: string;
  patient_education?: string;
  patient_occupation?: string;
  patient_marital_status?: string;
  date_of_assessment?: string;
  
  // Medical History
  current_medical_conditions?: string;
  past_medical_conditions?: string;
  current_medications?: string;
  allergies?: string;
  hospitalizations?: string;
  
  // Psychiatric History
  previous_diagnoses?: string;
  previous_treatment?: string;
  previous_hospitalizations?: string;
  suicide_self_harm_history?: string;
  substance_use_history?: string;
  
  // Family History
  psychiatric_illness_family?: string;
  medical_illness_family?: string;
  family_dynamics?: string;
  significant_family_events?: string;
  
  // Social History
  childhood_developmental?: string;
  educational_history?: string;
  occupational_history?: string;
  relationship_history?: string;
  social_support?: string;
  living_situation?: string;
  cultural_religious?: string;
  
  // Chief Complaints
  chief_complaint?: string;
  chief_complaint_description?: string;
  
  // Course of Illness
  illness_onset?: string;
  illness_progression?: string;
  previous_episodes?: string;
  triggers?: string;
  impact_on_functioning?: string;
  
  // Mental Status Examination
  mse_appearance?: string;
  mse_behavior?: string;
  mse_speech?: string;
  mse_mood?: string;
  mse_affect?: string;
  mse_thought_process?: string;
  mse_thought_content?: string;
  mse_perception?: string;
  mse_cognition?: string;
  mse_insight?: string;
  mse_judgment?: string;
  
  // Session summaries
  session_summaries?: Array<{
    session_number: number;
    session_date: string;
    summary: string;
  }>;
}

export interface PDFReport {
  patient_info: Patient;
  overall_summary: OverallSummary;
  session_summaries: SessionSummary[];
  generated_date: string;
  therapist_name: string;
}

export type RootStackParamList = {
  Login: undefined;
  Register: undefined;
  Dashboard: undefined;
  PatientList: undefined;
  PatientProfile: { patientId: number };
  CreatePatient: undefined;
  EditPatient: { patientId: number };
  SessionRecording: { patientId: number; sessionId?: number };
  SessionDetails: { sessionId: number };
  ExportReport: { patientId: number };
};
