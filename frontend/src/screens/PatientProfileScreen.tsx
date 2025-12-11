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
import { COLORS, API_BASE_URL, CARD_GLOW_STYLE } from '../config';
import { patientAPI, sessionAPI } from '../services/api';
import { Patient, Session } from '../types';
import { SummaryRenderer } from '../components/SummaryRenderer';

interface InfoSectionProps {
  title: string;
  expanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

const InfoSection: React.FC<InfoSectionProps> = ({ title, expanded, onToggle, children }) => (
  <View style={styles.infoSection}>
    <TouchableOpacity style={styles.infoSectionHeader} onPress={onToggle}>
      <Text style={styles.infoSectionTitle}>{title}</Text>
      <Ionicons name={expanded ? "chevron-up" : "chevron-down"} size={20} color={COLORS.paleAzure} />
    </TouchableOpacity>
    {expanded && <View style={styles.infoSectionContent}>{children}</View>}
  </View>
);

const InfoRow: React.FC<{ label: string; value?: string | null }> = ({ label, value }) => {
  if (!value) return null;
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}:</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
};

export default function PatientProfileScreen({ route, navigation }: any) {
  const { patientId } = route.params;
  const [patient, setPatient] = useState<Patient | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [notes, setNotes] = useState('');
  const [isSavingNotes, setIsSavingNotes] = useState(false);
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [summary, setSummary] = useState('');
  
  const [expandedSections, setExpandedSections] = useState({
    patientInfo: true,
    medicalHistory: false,
    psychiatricHistory: false,
    familyHistory: false,
    socialHistory: false,
    clinicalAssessment: false,
    mentalStatus: false,
  });

  useEffect(() => {
    fetchPatientData();
  }, []);

  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', () => {
      fetchPatientData();
    });
    return unsubscribe;
  }, [navigation]);

  const fetchPatientData = async () => {
    try {
      const { patient: fetchedPatient } = await patientAPI.getById(patientId, true);
      setPatient(fetchedPatient);
      setNotes(fetchedPatient.notes || '');
      const { sessions: fetchedSessions } = await sessionAPI.getByPatient(patientId);
      setSessions(fetchedSessions);
    } catch (error: any) {
      Alert.alert('Error', 'Failed to load patient data');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
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
      const result = await sessionAPI.create({
        patient_id: patientId,
        language: 'hindi',
      });
      navigation.navigate('SessionRecording', {
        sessionId: result.session.id,
        patientName: patient?.full_name,
      });
    } catch (error: any) {
      Alert.alert('Error', 'Failed to create session');
    }
  };

  const handleDeleteSession = (sessionId: number) => {
    Alert.alert(
      'Delete Session',
      'Are you sure you want to delete this session?',
      [
        { text: 'Cancel', style: 'cancel' },
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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_id: patientId }),
      });
      const data = await response.json();
      if (data.success) {
        setSummary(data.summary);
        Alert.alert('Summary Generated', `Summarized ${data.session_count} sessions`);
      } else {
        Alert.alert('Error', data.message || 'Failed to generate summary');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to generate summary');
    } finally {
      setIsSummarizing(false);
    }
  };

  const handleExportPDF = () => {
    if (!patient) return;
    // Navigate to export report screen for editing before export
    navigation.navigate('ExportReport', { patientId: patient.id });
  };

  const handleEditPatient = () => {
    navigation.navigate('EditPatient', { patientId: patient?.id });
  };

  if (isLoading) {
    return (
      <LinearGradient colors={COLORS.backgroundGradient} locations={[0, 0.3, 0.7, 1]} style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={COLORS.paleAzure} />
        </View>
      </LinearGradient>
    );
  }

  if (!patient) {
    return (
      <LinearGradient colors={COLORS.backgroundGradient} locations={[0, 0.3, 0.7, 1]} style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.errorText}>Patient not found</Text>
        </View>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient colors={COLORS.backgroundGradient} locations={[0, 0.3, 0.7, 1]} style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={COLORS.paleAzure} />
        </TouchableOpacity>
        <Text style={styles.title}>Patient Profile</Text>
        <TouchableOpacity onPress={handleEditPatient} style={styles.editButton}>
          <Ionicons name="create-outline" size={24} color={COLORS.paleAzure} />
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Patient Header Card */}
        <View style={styles.headerCard}>
          <View style={styles.avatarContainer}>
            <Ionicons name="person" size={40} color={COLORS.raisinBlack} />
          </View>
          <Text style={styles.patientName}>{patient.full_name}</Text>
          <Text style={styles.patientId}>ID: {patient.patient_id}</Text>
          {patient.phone && (
            <View style={styles.contactRow}>
              <Ionicons name="call" size={16} color={COLORS.paleAzure} />
              <Text style={styles.contactText}>{patient.phone}</Text>
            </View>
          )}
        </View>

        {/* Action Buttons */}
        <View style={styles.actionButtons}>
          <TouchableOpacity style={styles.actionButton} onPress={handleStartSession}>
            <Ionicons name="mic" size={20} color={COLORS.buttonText} />
            <Text style={styles.actionButtonText}>New Session</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.actionButton, styles.summarizeBtn]} 
            onPress={handleSummarize}
            disabled={isSummarizing}
          >
            {isSummarizing ? <ActivityIndicator color={COLORS.buttonText} size="small" /> : (
              <>
                <Ionicons name="document-text" size={20} color={COLORS.buttonText} />
                <Text style={styles.actionButtonText}>Summarize</Text>
              </>
            )}
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.actionButton, styles.exportBtn]} 
            onPress={handleExportPDF}
          >
            <Ionicons name="download" size={20} color={COLORS.buttonText} />
            <Text style={styles.actionButtonText}>Export PDF</Text>
          </TouchableOpacity>
        </View>

        {/* Summary Display */}
        {summary && (
          <View style={styles.summaryCard}>
            <View style={styles.summaryHeader}>
              <Ionicons name="star" size={20} color={COLORS.textOnDarkTeal} />
              <Text style={styles.summaryTitle}>AI Summary</Text>
            </View>
            <SummaryRenderer summary={summary} style={styles.summaryText} />
          </View>
        )}

        {/* Patient Information Sections */}
        <InfoSection title="Patient Information" expanded={expandedSections.patientInfo} onToggle={() => toggleSection('patientInfo')}>
          <InfoRow label="Age" value={patient.age?.toString()} />
          <InfoRow label="Gender" value={patient.gender} />
          <InfoRow label="Date of Birth" value={patient.date_of_birth ? new Date(patient.date_of_birth).toLocaleDateString() : undefined} />
          <InfoRow label="Residence" value={patient.residence} />
          <InfoRow label="Education" value={patient.education} />
          <InfoRow label="Occupation" value={patient.occupation} />
          <InfoRow label="Marital Status" value={patient.marital_status} />
          <InfoRow label="Email" value={patient.email} />
        </InfoSection>

        <InfoSection title="Medical History" expanded={expandedSections.medicalHistory} onToggle={() => toggleSection('medicalHistory')}>
          <InfoRow label="Current Medical Conditions" value={patient.current_medical_conditions} />
          <InfoRow label="Past Medical Conditions" value={patient.past_medical_conditions} />
          <InfoRow label="Current Medications" value={patient.current_medications} />
          <InfoRow label="Allergies" value={patient.allergies} />
          <InfoRow label="Hospitalizations" value={patient.hospitalizations} />
        </InfoSection>

        <InfoSection title="Psychiatric History" expanded={expandedSections.psychiatricHistory} onToggle={() => toggleSection('psychiatricHistory')}>
          <InfoRow label="Previous Diagnoses" value={patient.previous_psychiatric_diagnoses} />
          <InfoRow label="Previous Treatment" value={patient.previous_psychiatric_treatment} />
          <InfoRow label="Previous Hospitalizations" value={patient.previous_psychiatric_hospitalizations} />
          <InfoRow label="Suicide/Self-Harm History" value={patient.suicide_self_harm_history} />
          <InfoRow label="Substance Use History" value={patient.substance_use_history} />
        </InfoSection>

        <InfoSection title="Family History" expanded={expandedSections.familyHistory} onToggle={() => toggleSection('familyHistory')}>
          <InfoRow label="Psychiatric Illness in Family" value={patient.psychiatric_illness_family} />
          <InfoRow label="Medical Illness in Family" value={patient.medical_illness_family} />
          <InfoRow label="Family Dynamics" value={patient.family_dynamics} />
          <InfoRow label="Significant Family Events" value={patient.significant_family_events} />
        </InfoSection>

        <InfoSection title="Social History" expanded={expandedSections.socialHistory} onToggle={() => toggleSection('socialHistory')}>
          <InfoRow label="Childhood/Developmental" value={patient.childhood_developmental_history} />
          <InfoRow label="Educational History" value={patient.educational_history} />
          <InfoRow label="Occupational History" value={patient.occupational_history} />
          <InfoRow label="Relationship History" value={patient.relationship_history} />
          <InfoRow label="Social Support System" value={patient.social_support_system} />
          <InfoRow label="Living Situation" value={patient.living_situation} />
          <InfoRow label="Cultural/Religious Background" value={patient.cultural_religious_background} />
        </InfoSection>

        <InfoSection title="Clinical Assessment" expanded={expandedSections.clinicalAssessment} onToggle={() => toggleSection('clinicalAssessment')}>
          <InfoRow label="Chief Complaint" value={patient.chief_complaint} />
          <InfoRow label="Description" value={patient.chief_complaint_description} />
          <InfoRow label="Illness Onset" value={patient.illness_onset} />
          <InfoRow label="Progression" value={patient.illness_progression} />
          <InfoRow label="Previous Episodes" value={patient.previous_episodes} />
          <InfoRow label="Triggers" value={patient.triggers} />
          <InfoRow label="Impact on Functioning" value={patient.impact_on_functioning} />
        </InfoSection>

        <InfoSection title="Mental Status Examination" expanded={expandedSections.mentalStatus} onToggle={() => toggleSection('mentalStatus')}>
          <InfoRow label="Appearance" value={patient.mse_appearance} />
          <InfoRow label="Behavior" value={patient.mse_behavior} />
          <InfoRow label="Speech" value={patient.mse_speech} />
          <InfoRow label="Mood" value={patient.mse_mood} />
          <InfoRow label="Affect" value={patient.mse_affect} />
          <InfoRow label="Thought Process" value={patient.mse_thought_process} />
          <InfoRow label="Thought Content" value={patient.mse_thought_content} />
          <InfoRow label="Perception" value={patient.mse_perception} />
          <InfoRow label="Cognition" value={patient.mse_cognition} />
          <InfoRow label="Insight" value={patient.mse_insight} />
          <InfoRow label="Judgment" value={patient.mse_judgment} />
        </InfoSection>

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
                onPress={() => navigation.navigate('SessionDetail', { sessionId: session.id, patientName: patient?.full_name })}
              >
                <View style={styles.sessionHeader}>
                  <Text style={styles.sessionNumber}>Session #{session.session_number}</Text>
                  <View style={styles.sessionActions}>
                    <Text style={styles.sessionDate}>{new Date(session.session_date).toLocaleDateString()}</Text>
                    <TouchableOpacity onPress={() => handleDeleteSession(session.id)} style={styles.deleteButton}>
                      <Ionicons name="trash-outline" size={18} color={COLORS.coolSteel} />
                    </TouchableOpacity>
                  </View>
                </View>
                {session.original_transcription && (
                  <Text style={styles.transcriptionPreview} numberOfLines={2}>{session.original_transcription}</Text>
                )}
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
            placeholder="Add clinical notes..."
            placeholderTextColor={COLORS.textSecondary}
            multiline
            textAlignVertical="top"
          />
          <TouchableOpacity style={[styles.saveButton, isSavingNotes && styles.saveButtonDisabled]} onPress={handleSaveNotes} disabled={isSavingNotes}>
            {isSavingNotes ? <ActivityIndicator color={COLORS.raisinBlack} /> : (
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
  container: { flex: 1 },
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
    borderWidth: 1,
    borderColor: COLORS.borderColor,
  },
  editButton: {
    padding: 10,
    backgroundColor: COLORS.cardBackground,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.borderColor,
  },
  title: { fontSize: 24, fontWeight: 'bold', color: COLORS.paleAzure },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  errorText: { fontSize: 16, color: COLORS.error },
  scrollContent: { paddingHorizontal: 20, paddingBottom: 40 },
  headerCard: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 20,
    padding: 24,
    borderWidth: 1,
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
  patientName: { fontSize: 24, fontWeight: 'bold', color: COLORS.textOnDarkTeal, marginBottom: 4 },
  patientId: { fontSize: 14, color: COLORS.textSecondary, marginBottom: 12 },
  contactRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  contactText: { fontSize: 14, color: COLORS.textOnDarkTeal },
  actionButtons: { flexDirection: 'row', gap: 8, marginBottom: 20, flexWrap: 'wrap' },
  actionButton: {
    flex: 1,
    minWidth: 100,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.buttonBackground,
    paddingVertical: 12,
    borderRadius: 12,
    gap: 6,
  },
  summarizeBtn: { backgroundColor: COLORS.darkTeal },
  exportBtn: { backgroundColor: '#4A90A4' },
  actionButtonText: { fontSize: 14, fontWeight: '600', color: COLORS.buttonText },
  summaryCard: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: COLORS.success,
  },
  summaryHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 12 },
  summaryTitle: { fontSize: 18, fontWeight: '600', color: COLORS.textOnDarkTeal },
  summaryText: { fontSize: 15, color: COLORS.textOnDarkTeal, lineHeight: 22 },
  infoSection: {
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.borderColor,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: COLORS.cardBackground,
  },
  infoSectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: 'rgba(144, 215, 239, 0.1)',
  },
  infoSectionTitle: { fontSize: 16, fontWeight: '600', color: COLORS.paleAzure },
  infoSectionContent: { padding: 16, paddingTop: 8 },
  infoRow: { marginBottom: 12 },
  infoLabel: { fontSize: 12, color: COLORS.textSecondary, marginBottom: 2 },
  infoValue: { fontSize: 14, color: COLORS.textOnDarkTeal },
  section: { marginBottom: 24 },
  sectionTitle: { fontSize: 18, fontWeight: '600', color: COLORS.textPrimary, marginBottom: 12 },
  emptyState: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 16,
    padding: 40,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.borderColor,
  },
  emptyText: { fontSize: 14, color: COLORS.textSecondary, marginTop: 12 },
  sessionCard: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.borderColor,
  },
  sessionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  sessionNumber: { fontSize: 16, fontWeight: '600', color: COLORS.textOnDarkTeal },
  sessionActions: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  sessionDate: { fontSize: 12, color: COLORS.textSecondary },
  deleteButton: { padding: 4 },
  transcriptionPreview: { fontSize: 14, color: COLORS.textSecondary, fontStyle: 'italic' },
  notesInput: {
    backgroundColor: COLORS.cardBackground,
    borderWidth: 1,
    borderColor: COLORS.borderColor,
    borderRadius: 16,
    padding: 16,
    fontSize: 14,
    color: COLORS.textOnDarkTeal,
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
  saveButtonDisabled: { opacity: 0.6 },
  saveButtonText: { fontSize: 16, fontWeight: '600', color: COLORS.raisinBlack },
});
