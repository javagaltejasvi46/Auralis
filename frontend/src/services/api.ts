/**
 * API Service Layer
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_ENDPOINTS } from '../config';
import { AuthResponse, Therapist, Patient, Session, SearchResult, SearchResponse } from '../types';

const TOKEN_KEY = '@auralis_token';

// Token management
export const saveToken = async (token: string) => {
  await AsyncStorage.setItem(TOKEN_KEY, token);
};

export const getToken = async (): Promise<string | null> => {
  return await AsyncStorage.getItem(TOKEN_KEY);
};

export const removeToken = async () => {
  await AsyncStorage.removeItem(TOKEN_KEY);
};

// API request helper
const apiRequest = async (
  url: string,
  options: RequestInit = {}
): Promise<any> => {
  console.log('🌐 API Request to:', url);
  const token = await getToken();
  console.log('🔑 Token retrieved:', token ? `${token.substring(0, 20)}...` : 'NULL');
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
    console.log('✅ Authorization header added');
  } else {
    console.log('⚠️ No token available for request');
  }
  
  console.log('📤 Sending request...');
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  console.log('📥 Response status:', response.status);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    console.log('❌ Request failed:', error);
    throw new Error(error.detail || 'Request failed');
  }
  
  return await response.json();
};

// Auth API
export const authAPI = {
  register: async (data: {
    email: string;
    username: string;
    password: string;
    full_name: string;
    license_number: string;
    specialization?: string;
    phone?: string;
  }) => {
    return await apiRequest(API_ENDPOINTS.register, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  login: async (username: string, password: string): Promise<AuthResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch(API_ENDPOINTS.login, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }
    
    const data = await response.json();
    await saveToken(data.access_token);
    return data;
  },
  
  getMe: async (): Promise<{ therapist: Therapist }> => {
    return await apiRequest(API_ENDPOINTS.me);
  },
  
  logout: async () => {
    await removeToken();
    return await apiRequest(API_ENDPOINTS.logout, { method: 'POST' });
  },
};

// Patient API
export const patientAPI = {
  getAll: async (activeOnly: boolean = true): Promise<{ patients: Patient[] }> => {
    return await apiRequest(`${API_ENDPOINTS.patients}?active_only=${activeOnly}`);
  },
  
  getById: async (id: number, includeSessions: boolean = true): Promise<{ patient: Patient }> => {
    return await apiRequest(`${API_ENDPOINTS.patients}${id}?include_sessions=${includeSessions}`);
  },
  
  search: async (query: string): Promise<SearchResponse> => {
    return await apiRequest(`${API_ENDPOINTS.patients}search?q=${encodeURIComponent(query)}`);
  },
  
  create: async (data: Partial<Patient>) => {
    return await apiRequest(API_ENDPOINTS.patients, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  update: async (id: number, data: Partial<Patient>) => {
    return await apiRequest(`${API_ENDPOINTS.patients}${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },
  
  delete: async (id: number) => {
    return await apiRequest(`${API_ENDPOINTS.patients}${id}`, {
      method: 'DELETE',
    });
  },
};

// Session API
export const sessionAPI = {
  getByPatient: async (patientId: number): Promise<{ sessions: Session[] }> => {
    return await apiRequest(`${API_ENDPOINTS.sessions}patient/${patientId}`);
  },
  
  getById: async (id: number): Promise<{ session: Session }> => {
    return await apiRequest(`${API_ENDPOINTS.sessions}${id}`);
  },
  
  create: async (data: {
    patient_id: number;
    language: string;
    duration?: number;
    original_transcription?: string;
    notes?: string;
  }) => {
    return await apiRequest(API_ENDPOINTS.sessions, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  update: async (id: number, data: Partial<Session>) => {
    return await apiRequest(`${API_ENDPOINTS.sessions}${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },
  
  uploadAudio: async (sessionId: number, audioUri: string) => {
    const formData = new FormData();
    formData.append('file', {
      uri: audioUri,
      type: 'audio/m4a',
      name: `session_${sessionId}.m4a`,
    } as any);
    
    const token = await getToken();
    const response = await fetch(`${API_ENDPOINTS.sessions}${sessionId}/audio`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error('Audio upload failed');
    }
    
    return await response.json();
  },
  
  delete: async (id: number) => {
    return await apiRequest(`${API_ENDPOINTS.sessions}${id}`, {
      method: 'DELETE',
    });
  },
};

// Translation API
export const translateText = async (
  text: string,
  targetLanguage: string,
  sourceLanguage: string = 'auto'
) => {
  return await apiRequest(API_ENDPOINTS.translate, {
    method: 'POST',
    body: JSON.stringify({
      text,
      target_language: targetLanguage,
      source_language: sourceLanguage,
    }),
  });
};
