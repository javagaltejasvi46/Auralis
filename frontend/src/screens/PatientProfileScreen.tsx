import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, API_BASE_URL } from '../config';
import { patientAPI, sessionAPI } from '../services/api';
import { Patient, Session } from '../types';

export default function PatientProfileScreen({ route, navigation }: any) {
  const { patientId } = route.params;
  const [patient, setPatient] = useState<Patient | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [notes, setNotes] = useState('');
  const [isSavingNotes, setIsSavingNotes] = useState(false);
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [summary, setSummary] = useState('');

  useEffect(() => {
    fetchPatientData();
  }, []);

  const fetchPatientData = async () => {
    try {
      console.log('📋 Fetching patient data for ID:', patientId);
      const { patient: fetchedPatient } = await patientAPI.getById(patientId, true);
      setPatient(fetchedPatient);
      setNotes(fetchedPatient.notes || '');
      
      // Fetch sessions
      const { sessions: fetchedSessions } = await sessionAPI.getByPatient(patientId);
      setSessions(fetchedSessions);
      console.log('✅ Patient data loaded');
    } catch (error: any) {
      console.error('❌ Error fetching patient:', error);
      Alert.alert('Error', 'Failed to load patient data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveNotes = async () => {
    if (!patient) return;
    
    setIsSavingNotes(true);
    try {
      await patientAPI.update(patient.id, { notes });
      Alert.alert('Success', 'Notes saved successfully');
    } catch (error: any) {
      Alert.alert('Error', 'Failed to save notes');
    } finally {
      setIsSavingNotes(false);
    }
  };

  const handleStartSession = async () => {
    try {
      console.log('🎤 Creating new session...');
      const result = await sessionAPI.create({
        patient_id: patientId,
        language: 'hindi', // Default, can be changed in recording screen
      });
      console.log('✅ Session created:', result);
      
      // Navigate to recording screen
      navigation.navigate('SessionRecording', {
        sessionId: result.session.id,
        patientName: patient?.full_name,
      });
    } catch (error: any) {
      console.error('❌ Error creating session:', error);
      Alert.alert('Error', 'Failed to create session');
    }
  };

  const handleDeleteSession = (sessionId: number) => {
    Alert.alert(
      'Delete Session',
      'Are you sure you want to delete this session? This action cannot be undone.',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await sessionAPI.delete(sessionId);
              Alert.alert('Success', 'Session deleted');
              fetchPatientData();
            } catch (error) {
              Alert.alert('Error', 'Failed to delete session');
            }
          },
        },
      ]
    );
  };

  const handleSummarize = async () => {
    if (!sessions || sessions.length === 0) {
      Alert.alert('No Sessions', 'There are no sessions to summarize');
      return;
    }

    setIsSummarizing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/summarize-sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ patient_id: patientId }),
      });

      const data = await response.json();

      if (data.success) {
        setSummary(data.summary);
        Alert.alert(
          'Summary Generated',
          `Summarized ${data.session_count} sessions`,
          [{ text: 'OK' }]
        );
      } else {
        Alert.alert('Error', data.message || 'Failed to generate summary');
      }
    } catch (error) {
      console.error('❌ Summarization error:', error);
      Alert.alert('Error', 'Failed to generate summary');
    } finally {
      setIsSummarizing(false);
    }
  };

  if (isLoading) {
    return (
      <LinearGradient
        colors={COLORS.backgroundGradient}
        locations={[0, 0.3, 0.7, 1]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.container}
      >
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={COLORS.paleAzure} />
        </View>
      </LinearGradient>
    );
  }

  if (!patient) {
    return (
      <LinearGradient
        colors={COLORS.backgroundGradient}
        locations={[0, 0.3, 0.7, 1]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.container}
      >
        <View style={styles.loadingContainer}>
          <Text style={styles.errorText}>Patient not found</Text>
        </View>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient
      colors={COLORS.backgroundGradient}
      locations={[0, 0.3, 0.7, 1]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.container}
    >
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={COLORS.paleAzure} />
        </TouchableOpacity>
        <Text style={styles.title}>Patient Profile</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Patient Info Card */}
        <View style={styles.infoCard}>
          <View style={styles.avatarContainer}>
            <Ionicons name="person" size={40} color={COLORS.raisinBlack} />
          </View>
          <Text style={styles.patientName}>{patient.full_name}</Text>
          <Text style={styles.patientId}>ID: {patient.patient_id}</Text>
          
          <View style={styles.detailsContainer}>
            {patient.phone && (
              <View style={styles.detailRow}>
                <Ionicons name="call" size={16} color={COLORS.paleAzure} />
                <Text style={styles.detailText}>{patient.phone}</Text>
              </View>
            )}
            {patient.email && (
              <View style={styles.detailRow}>
                <Ionicons name="mail" size={16} color={COLORS.paleAzure} />
                <Text style={styles.detailText}>{patient.email}</Text>
              </View>
            )}
          </View>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionButtons}>
          <TouchableOpacity style={styles.startSessionButton} onPress={handleStartSession}>
            <Ionicons name="mic" size={24} color={COLORS.buttonText} />
            <Text style={styles.startSessionText}>Start New Session</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.summarizeButton, isSummarizing && styles.summarizeButtonDisabled]} 
            onPress={handleSummarize}
            disabled={isSummarizing || sessions.length === 0}
          >
            {isSummarizing ? (
              <ActivityIndicator color={COLORS.buttonText} />
            ) : (
              <>
                <Ionicons name="document-text" size={24} color={COLORS.buttonText} />
                <Text style={styles.summarizeButtonText}>Summarize</Text>
              </>
            )}
          </TouchableOpacity>
        </View>

        {/* Summary Display */}
        {summary && (
          <View style={styles.summaryCard}>
            <View style={styles.summaryHeader}>
              <Ionicons name="star" size={20} color={COLORS.textOnDarkTeal} />
              <Text style={styles.summaryTitle}>AI Summary</Text>
            </View>
            <Text style={styles.summaryText}>{summary}</Text>
          </View>
        )}

        {/* Sessions List */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Sessions ({sessions.length})</Text>
          {sessions.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="document-text-outline" size={40} color={COLORS.textSecondary} />
              <Text style={styles.emptyText}>No sessions yet</Text>
            </View>
          ) : (
            sessions.map((session) => (
              <TouchableOpacity
                key={session.id}
                style={styles.sessionCard}
                onPress={() => navigation.navigate('SessionDetail', {
                  sessionId: session.id,
                  patientName: patient?.full_name,
                })}
              >
                <View style={styles.sessionHeader}>
                  <Text style={styles.sessionNumber}>Session #{session.session_number}</Text>
                  <View style={styles.sessionActions}>
                    <Text style={styles.sessionDate}>
                      {new Date(session.session_date).toLocaleDateString()}
                    </Text>
                    <TouchableOpacity
                      onPress={(e) => {
                        e.stopPropagation();
                        handleDeleteSession(session.id);
                      }}
                      style={styles.deleteButton}
                    >
                      <Ionicons name="trash-outline" size={18} color={COLORS.coolSteel} />
                    </TouchableOpacity>
                  </View>
                </View>
                <View style={styles.sessionDetails}>
                  <View style={styles.sessionBadge}>
                    <Ionicons name="language" size={12} color={COLORS.saffron} />
                    <Text style={styles.sessionBadgeText}>{session.language}</Text>
                  </View>
                  {session.duration && (
                    <View style={styles.sessionBadge}>
                      <Ionicons name="time" size={12} color={COLORS.paleAzure} />
                      <Text style={styles.sessionBadgeText}>
                        {Math.floor(session.duration / 60)}m
                      </Text>
                    </View>
                  )}
                </View>
                {session.original_transcription && (
                  <Text style={styles.transcriptionPreview} numberOfLines={2}>
                    {session.original_transcription}
                  </Text>
                )}
                <View style={styles.viewDetailHint}>
                  <Text style={styles.viewDetailText}>Tap to view details</Text>
                  <Ionicons name="chevron-forward" size={16} color={COLORS.paleAzure} />
                </View>
              </TouchableOpacity>
            ))
          )}
        </View>

        {/* Notes Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Clinical Notes</Text>
          <TextInput
            style={styles.notesInput}
            value={notes}
            onChangeText={setNotes}
            placeholder="Add clinical notes, observations, treatment plans..."
            placeholderTextColor={COLORS.textSecondary}
            multiline
            textAlignVertical="top"
          />
          <TouchableOpacity
            style={[styles.saveButton, isSavingNotes && styles.saveButtonDisabled]}
            onPress={handleSaveNotes}
            disabled={isSavingNotes}
          >
            {isSavingNotes ? (
              <ActivityIndicator color={COLORS.raisinBlack} />
            ) : (
              <>
                <Ionicons name="save" size={20} color={COLORS.raisinBlack} />
                <Text style={styles.saveButtonText}>Save Notes</Text>
              </>
            )}
          </TouchableOpacity>
        </View>
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 60,
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  backButton: {
    padding: 10,
    backgroundColor: COLORS.cardBackground,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: COLORS.borderColor,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.paleAzure,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    fontSize: 16,
    color: COLORS.error,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  infoCard: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 20,
    padding: 24,
    borderWidth: 2,
    borderColor: COLORS.borderColor,
    alignItems: 'center',
    marginBottom: 20,
  },
  avatarContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: COLORS.buttonBackground,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  patientName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.textOnDarkTeal,
    marginBottom: 4,
  },
  patientId: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginBottom: 16,
  },
  detailsContainer: {
    width: '100%',
    gap: 8,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  detailText: {
    fontSize: 14,
    color: COLORS.textOnDarkTeal,
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  startSessionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.buttonBackground,
    paddingVertical: 16,
    borderRadius: 16,
    gap: 8,
  },
  startSessionText: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.buttonText,
  },
  summarizeButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.darkTeal,
    paddingVertical: 16,
    borderRadius: 16,
    gap: 8,
  },
  summarizeButtonDisabled: {
    opacity: 0.6,
  },
  summarizeButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.buttonText,
  },
  summaryCard: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
    borderWidth: 2,
    borderColor: COLORS.borderColor,
  },
  summaryHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 12,
  },
  summaryTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.textOnDarkTeal,
  },
  summaryText: {
    fontSize: 15,
    color: COLORS.textOnDarkTeal,
    lineHeight: 22,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.textPrimary,
    marginBottom: 12,
  },
  emptyState: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 16,
    padding: 40,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: COLORS.borderColor,
  },
  emptyText: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginTop: 12,
  },
  sessionCard: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: COLORS.borderColor,
  },
  sessionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  sessionNumber: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.textOnDarkTeal,
  },
  sessionActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  sessionDate: {
    fontSize: 12,
    color: COLORS.textSecondary,
  },
  deleteButton: {
    padding: 4,
  },
  viewDetailHint: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    marginTop: 8,
    gap: 4,
  },
  viewDetailText: {
    fontSize: 12,
    color: COLORS.coolSteel,
    fontStyle: 'italic',
  },
  sessionDetails: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 8,
  },
  sessionBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 8,
    paddingVertical: 4,
    backgroundColor: 'rgba(144, 215, 239, 0.1)',
    borderRadius: 8,
  },
  sessionBadgeText: {
    fontSize: 12,
    color: COLORS.textPrimary,
  },
  transcriptionPreview: {
    fontSize: 14,
    color: COLORS.textSecondary,
    fontStyle: 'italic',
  },
  notesInput: {
    backgroundColor: COLORS.cardBackground,
    borderWidth: 2,
    borderColor: COLORS.borderColor,
    borderRadius: 16,
    padding: 16,
    fontSize: 14,
    color: COLORS.textPrimary,
    minHeight: 150,
    marginBottom: 12,
  },
  saveButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.buttonBackground,
    paddingVertical: 14,
    borderRadius: 12,
    gap: 8,
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.raisinBlack,
  },
});
