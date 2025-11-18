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

export type RootStackParamList = {
  Login: undefined;
  Register: undefined;
  Dashboard: undefined;
  PatientList: undefined;
  PatientProfile: { patientId: number };
  CreatePatient: undefined;
  SessionRecording: { patientId: number; sessionId?: number };
  SessionDetails: { sessionId: number };
};
