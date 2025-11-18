import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  Alert,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { authAPI } from '../services/api';
import { COLORS } from '../config';

export default function RegisterScreen({ navigation }: any) {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    license_number: '',
    specialization: '',
    phone: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const updateField = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleRegister = async () => {
    // Validation
    if (!formData.email || !formData.username || !formData.password || !formData.full_name || !formData.license_number) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      Alert.alert('Error', 'Password must be at least 6 characters');
      return;
    }

    setIsLoading(true);
    try {
      await authAPI.register({
        email: formData.email,
        username: formData.username,
        password: formData.password,
        full_name: formData.full_name,
        license_number: formData.license_number,
        specialization: formData.specialization || undefined,
        phone: formData.phone || undefined,
      });

      Alert.alert(
        'Success',
        'Account created successfully! Please login.',
        [{ text: 'OK', onPress: () => navigation.navigate('Login') }]
      );
    } catch (error: any) {
      Alert.alert('Registration Failed', error.message || 'Please try again');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <LinearGradient
      colors={COLORS.backgroundGradient}
      locations={[0, 0.3, 0.7, 1]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.container}
    >
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          <View style={styles.header}>
            <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
              <Ionicons name="arrow-back" size={24} color={COLORS.paleAzure} />
            </TouchableOpacity>
            <Text style={styles.title}>Create Account</Text>
            <Text style={styles.subtitle}>Register as a Therapist</Text>
          </View>

          <View style={styles.formContainer}>
            <InputField
              icon="mail-outline"
              placeholder="Email *"
              value={formData.email}
              onChangeText={(text) => updateField('email', text)}
              keyboardType="email-address"
              autoCapitalize="none"
            />

            <InputField
              icon="person-outline"
              placeholder="Username *"
              value={formData.username}
              onChangeText={(text) => updateField('username', text)}
              autoCapitalize="none"
            />

            <InputField
              icon="lock-closed-outline"
              placeholder="Password *"
              value={formData.password}
              onChangeText={(text) => updateField('password', text)}
              secureTextEntry={!showPassword}
              rightIcon={
                <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                  <Ionicons
                    name={showPassword ? 'eye-outline' : 'eye-off-outline'}
                    size={20}
                    color={COLORS.paleAzure}
                  />
                </TouchableOpacity>
              }
            />

            <InputField
              icon="lock-closed-outline"
              placeholder="Confirm Password *"
              value={formData.confirmPassword}
              onChangeText={(text) => updateField('confirmPassword', text)}
              secureTextEntry={!showPassword}
            />

            <InputField
              icon="person-circle-outline"
              placeholder="Full Name *"
              value={formData.full_name}
              onChangeText={(text) => updateField('full_name', text)}
            />

            <InputField
              icon="card-outline"
              placeholder="License Number *"
              value={formData.license_number}
              onChangeText={(text) => updateField('license_number', text)}
            />

            <InputField
              icon="medical-outline"
              placeholder="Specialization"
              value={formData.specialization}
              onChangeText={(text) => updateField('specialization', text)}
            />

            <InputField
              icon="call-outline"
              placeholder="Phone"
              value={formData.phone}
              onChangeText={(text) => updateField('phone', text)}
              keyboardType="phone-pad"
            />

            <TouchableOpacity
              style={styles.registerButton}
              onPress={handleRegister}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color={COLORS.raisinBlack} />
              ) : (
                <Text style={styles.registerButtonText}>Register</Text>
              )}
            </TouchableOpacity>

            <View style={styles.loginContainer}>
              <Text style={styles.loginText}>Already have an account? </Text>
              <TouchableOpacity onPress={() => navigation.navigate('Login')}>
                <Text style={styles.loginLink}>Login</Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const InputField = ({ icon, rightIcon, ...props }: any) => (
  <View style={styles.inputContainer}>
    <Ionicons name={icon} size={20} color={COLORS.paleAzure} style={styles.inputIcon} />
    <TextInput
      style={styles.input}
      placeholderTextColor={COLORS.textSecondary}
      {...props}
    />
    {rightIcon}
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 30,
    paddingTop: 60,
    paddingBottom: 40,
  },
  header: {
    alignItems: 'center',
    marginBottom: 30,
  },
  backButton: {
    position: 'absolute',
    left: 0,
    top: 0,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: COLORS.paleAzure,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: COLORS.textSecondary,
  },
  formContainer: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 20,
    padding: 25,
    borderWidth: 2,
    borderColor: COLORS.borderColor,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(32, 30, 31, 0.6)',
    borderRadius: 12,
    paddingHorizontal: 15,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.borderColor,
  },
  inputIcon: {
    marginRight: 10,
  },
  input: {
    flex: 1,
    color: COLORS.textPrimary,
    fontSize: 16,
    paddingVertical: 15,
  },
  registerButton: {
    backgroundColor: COLORS.paleAzure,
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 10,
    shadowColor: COLORS.paleAzure,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 6,
  },
  registerButtonText: {
    color: COLORS.raisinBlack,
    fontSize: 18,
    fontWeight: '600',
    letterSpacing: 1,
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 20,
  },
  loginText: {
    color: COLORS.textSecondary,
    fontSize: 14,
  },
  loginLink: {
    color: COLORS.paleAzure,
    fontSize: 14,
    fontWeight: '600',
  },
});
