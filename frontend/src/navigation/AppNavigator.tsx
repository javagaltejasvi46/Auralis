import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { ActivityIndicator, View, StyleSheet } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { COLORS } from '../config';

// Import screens
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import DashboardScreen from '../screens/DashboardScreen';
import PatientListScreen from '../screens/PatientListScreen';
import CreatePatientScreen from '../screens/CreatePatientScreen';
import PatientProfileScreen from '../screens/PatientProfileScreen';
import EditPatientScreen from '../screens/EditPatientScreen';
import SessionRecordingScreen from '../screens/SessionRecordingScreen';
import SessionDetailScreen from '../screens/SessionDetailScreen';
import ExportReportScreen from '../screens/ExportReportScreen';

const Stack = createStackNavigator();

export default function AppNavigator() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.paleAzure} />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {!isAuthenticated ? (
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Register" component={RegisterScreen} />
          </>
        ) : (
          <>
            <Stack.Screen name="Dashboard" component={DashboardScreen} />
            <Stack.Screen name="PatientList" component={PatientListScreen} />
            <Stack.Screen name="CreatePatient" component={CreatePatientScreen} />
            <Stack.Screen name="PatientProfile" component={PatientProfileScreen} />
            <Stack.Screen name="EditPatient" component={EditPatientScreen} />
            <Stack.Screen name="SessionRecording" component={SessionRecordingScreen} />
            <Stack.Screen name="SessionDetail" component={SessionDetailScreen} />
            <Stack.Screen name="ExportReport" component={ExportReportScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.raisinBlack,
  },
});
