/**
 * Authentication Context
 */
import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI, getToken } from '../services/api';
import { Therapist } from '../types';

interface AuthContextType {
  therapist: Therapist | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [therapist, setTherapist] = useState<Therapist | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      console.log('🔍 Checking authentication...');
      const token = await getToken();
      console.log('🔑 Token:', token ? 'Found' : 'Not found');
      if (token) {
        console.log('📡 Fetching user data...');
        const { therapist } = await authAPI.getMe();
        console.log('✅ User authenticated:', therapist.username);
        setTherapist(therapist);
      } else {
        console.log('⚠️ No token found');
      }
    } catch (error: any) {
      console.log('❌ Auth check failed:', error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    console.log('🔐 Attempting login for:', username);
    const response = await authAPI.login(username, password);
    console.log('✅ Login successful:', response.therapist.username);
    console.log('🔑 Token saved');
    setTherapist(response.therapist);
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.log('Logout error:', error);
    } finally {
      setTherapist(null);
    }
  };

  const refreshUser = async () => {
    try {
      console.log('🔄 Refreshing user data...');
      const { therapist } = await authAPI.getMe();
      console.log('✅ User data refreshed:', therapist.username);
      setTherapist(therapist);
    } catch (error: any) {
      console.log('❌ Refresh user error:', error.message);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        therapist,
        isLoading,
        isAuthenticated: !!therapist,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
