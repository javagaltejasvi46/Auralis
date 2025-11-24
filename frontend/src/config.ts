/**
 * App Configuration
 */

// Update this with your machine's IP address
export const API_BASE_URL = 'http://192.168.0.116:8002';
export const WS_BASE_URL = 'ws://192.168.0.116:8003';

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
  // Main palette - New Color Scheme
  parchment: '#F2EFEB',
  darkTeal: '#113845',
  coolSteel: '#85A3B3',
  
  // Legacy colors (replaced)
  raisinBlack: '#F2EFEB',  // Now Parchment
  paleAzure: '#85A3B3',    // Now Cool Steel
  ultraviolet: '#113845',  // Now Dark Teal
  saffron: '#113845',      // Now Dark Teal
  engineeringOrange: '#113845',  // Now Dark Teal
  
  // Gradients - Solid Parchment background
  backgroundGradient: ['#F2EFEB', '#F2EFEB', '#F2EFEB', '#F2EFEB'],
  
  // UI
  cardBackground: 'rgba(17, 56, 69, 0.95)',  // Dark Teal sections
  borderColor: 'rgba(133, 163, 179, 0.5)',   // Cool Steel border
  textPrimary: '#85A3B3',      // Cool Steel text (on parchment background)
  textSecondary: 'rgba(133, 163, 179, 0.7)',    // Cool Steel text lighter
  textOnDarkTeal: '#FFFFFF',   // White text on dark teal background
  buttonBackground: '#85A3B3', // Cool Steel buttons
  buttonText: '#FFFFFF',       // White text on buttons
  
  // Status
  success: '#4ade80',
  error: '#ef4444',
  warning: '#fbbf24',
};
