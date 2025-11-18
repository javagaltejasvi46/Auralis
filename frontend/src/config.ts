/**
 * App Configuration
 */

// Update this with your machine's IP address
export const API_BASE_URL = 'http://192.168.0.102:8002';
export const WS_BASE_URL = 'ws://192.168.0.102:8003';

export const API_ENDPOINTS = {
  // Auth
  register: `${API_BASE_URL}/auth/register`,
  login: `${API_BASE_URL}/auth/login`,
  me: `${API_BASE_URL}/auth/me`,
  logout: `${API_BASE_URL}/auth/logout`,
  
  // Patients
  patients: `${API_BASE_URL}/patients/`,
  
  // Sessions
  sessions: `${API_BASE_URL}/sessions/`,
  
  // Translation
  translate: `${API_BASE_URL}/translate`,
};

export const COLORS = {
  // Main palette
  raisinBlack: '#201E1F',
  paleAzure: '#90D7EF',
  ultraviolet: '#6457A6',
  saffron: '#E3B505',
  engineeringOrange: '#B81F00',
  
  // Gradients
  backgroundGradient: ['#201E1F', '#6457A6', '#90D7EF', '#201E1F'],
  
  // UI
  cardBackground: 'rgba(32, 30, 31, 0.85)',
  borderColor: 'rgba(144, 215, 239, 0.5)',
  textPrimary: '#90D7EF',
  textSecondary: 'rgba(144, 215, 239, 0.7)',
  
  // Status
  success: '#4ade80',
  error: '#ef4444',
  warning: '#fbbf24',
};
