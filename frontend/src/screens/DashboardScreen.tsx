import React from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { COLORS, CARD_GLOW_STYLE } from '../config';

export default function DashboardScreen({ navigation }: any) {
  const { therapist, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <LinearGradient
      colors={COLORS.backgroundGradient}
      locations={[0, 0.3, 0.7, 1]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Welcome back,</Text>
            <Text style={styles.name}>{therapist?.full_name}</Text>
          </View>
          <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
            <Ionicons name="log-out-outline" size={24} color={COLORS.engineeringOrange} />
          </TouchableOpacity>
        </View>

        {/* Stats Card */}
        <View style={styles.statsCard}>
          <View style={styles.statItem}>
            <Ionicons name="people" size={40} color={COLORS.paleAzure} />
            <Text style={styles.statNumber}>{therapist?.patient_count || 0}</Text>
            <Text style={styles.statLabel}>Total Patients</Text>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.actionsContainer}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('PatientList')}
          >
            <View style={styles.actionIconContainer}>
              <Ionicons name="list" size={28} color={COLORS.raisinBlack} />
            </View>
            <View style={styles.actionTextContainer}>
              <Text style={styles.actionTitle}>View All Patients</Text>
              <Text style={styles.actionSubtitle}>Manage patient profiles</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color={COLORS.paleAzure} />
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('CreatePatient')}
          >
            <View style={styles.actionIconContainer}>
              <Ionicons name="person-add" size={28} color={COLORS.raisinBlack} />
            </View>
            <View style={styles.actionTextContainer}>
              <Text style={styles.actionTitle}>New Patient</Text>
              <Text style={styles.actionSubtitle}>Create patient profile</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color={COLORS.paleAzure} />
          </TouchableOpacity>
        </View>

        {/* Info Card */}
        <View style={styles.infoCard}>
          <Ionicons name="information-circle" size={24} color={COLORS.saffron} />
          <Text style={styles.infoText}>
            Select a patient to start a new therapy session with voice transcription
          </Text>
        </View>
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingTop: 60,
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 30,
  },
  greeting: {
    fontSize: 16,
    color: COLORS.textSecondary,
  },
  name: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.paleAzure,
    marginTop: 4,
  },
  logoutButton: {
    padding: 10,
    backgroundColor: COLORS.cardBackground,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.borderColor,
    ...CARD_GLOW_STYLE,
  },
  statsCard: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 20,
    padding: 30,
    borderWidth: 1,
    borderColor: COLORS.borderColor,
    marginBottom: 30,
    alignItems: 'center',
    ...CARD_GLOW_STYLE,
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 48,
    fontWeight: 'bold',
    color: COLORS.paleAzure,
    marginTop: 10,
  },
  statLabel: {
    fontSize: 16,
    color: COLORS.textSecondary,
    marginTop: 5,
  },
  actionsContainer: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: COLORS.paleAzure,
    marginBottom: 15,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.cardBackground,
    borderRadius: 16,
    padding: 20,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.borderColor,
    ...CARD_GLOW_STYLE,
  },
  actionIconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: COLORS.buttonBackground,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  actionTextContainer: {
    flex: 1,
  },
  actionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.paleAzure,
    marginBottom: 4,
  },
  actionSubtitle: {
    fontSize: 14,
    color: COLORS.textSecondary,
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: 'rgba(227, 181, 5, 0.1)',
    borderRadius: 12,
    padding: 15,
    borderWidth: 1,
    borderColor: 'rgba(227, 181, 5, 0.3)',
  },
  infoText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 14,
    color: COLORS.textPrimary,
    lineHeight: 20,
  },
});
