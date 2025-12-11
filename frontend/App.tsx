import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { AuthProvider } from './src/context/AuthContext';
import AppNavigator from './src/navigation/AppNavigator';
import ConnectionManager from './src/services/ConnectionManager';

export default function App() {
  useEffect(() => {
    // Initialize connection manager on app startup
    const initializeConnection = async () => {
      console.log('🚀 Initializing Auralis connection...');
      const connectionManager = ConnectionManager.getInstance();
      await connectionManager.initialize();
    };

    initializeConnection();
  }, []);

  return (
    <AuthProvider>
      <StatusBar style="light" />
      <AppNavigator />
    </AuthProvider>
  );
}
