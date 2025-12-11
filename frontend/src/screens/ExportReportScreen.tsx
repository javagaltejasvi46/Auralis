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
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { COLORS, API_BASE_URL } from '../config';
import { patientAPI, getToken } from '../services/api';
import { OverallSummary, ExportReportData } from '../types';

interface EditableSectionProps {
  title: string;
  expanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

const EditableSection: React.FC<EditableSectionProps> = ({ title, expanded, onToggle, children }) => (
  <View style={styles.section}>
    <TouchableOpacity style={styles.sectionHeader} onPress={onToggle}>
      <Text style={styles.sectionTitle}>{title}</Text>
      <Ionicons name={expanded ? "chevron-up" : "chevron-down"} size={20} color={COLORS.paleAzure} />
    </TouchableOpacity>
    {expanded && <View style={styles.sectionContent}>{children}</View>}
  </View>
);

interface EditableFieldProps {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  multiline?: boolean;
}

const EditableField: React.FC<EditableFieldProps> = ({ label, value, onChangeText, multiline }) => (
  <View style={styles.fieldContainer}>
    <Text style={styles.fieldLabel}>{label}</Text>
    <TextInput
      style={[styles.fieldInput, multiline && styles.multilineInput]}
      value={value}
      onChangeText={onChangeText}
      placeholder={`Enter ${label.toLowerCase()}`}
      placeholderTextColor={COLORS.textSecondary}
      multiline={multiline}
    />
  </View>
);

export default function ExportReportScreen({ route, navigation }: any) {
  const { patientId } = route.params;
  const [isLoading, setIsLoading] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [reportData, setReportData] = useState<ExportReportData>({});
  const [originalData, setOriginalData] = useState<OverallSummary | null>(null);

  const [expandedSections, setExpandedSections] = useState({
    patientInfo: true,
    medicalHistory: false,
    psychiatricHistory: false,
    familyHistory: false,
    socialHistory: false,
    chiefComplaints: false,
    courseOfIllness: false,
    mentalStatus: false,
    sessions: false,
  });

  useEffect(() => {
    fetchReportData();
  }, []);

  const fetchReportData = async () => {
    try {
      const response = await patientAPI.getReportData(patientId);
      console.log('📊 Report data response:', JSON.stringify(response, null, 2));
      if (response.success) {
        setOriginalData(response.report_data);
        // Initialize editable fields from report data
        const data = response.report_data;
        console.log('📊 Chief complaints:', data.chief_complaints);
        console.log('📊 Course of illness:', data.course_of_illness);
        console.log('📊 Baseline assessment:', data.baseline_assessment);
        setReportData({
          patient_name: data.patient_information?.name || '',
          patient_age: data.patient_information?.age || '',
          patient_gender: data.patient_information?.gender || '',
          patient_dob: data.patient_information?.date_of_birth || '',
          patient_residence: data.patient_information?.residence || '',
          patient_education: data.patient_information?.education || '',
          patient_occupation: data.patient_information?.occupation || '',
          patient_marital_status: data.patient_information?.marital_status || '',
          date_of_assessment: data.patient_information?.date_of_assessment || '',
          // Medical History
          current_medical_conditions: data.medical_history?.current_medical_conditions || '',
          past_medical_conditions: data.medical_history?.past_medical_conditions || '',
          current_medications: data.medical_history?.current_medications || '',
          allergies: data.medical_history?.allergies || '',
          hospitalizations: data.medical_history?.hospitalizations || '',
          // Psychiatric History
          previous_diagnoses: data.psychiatric_history?.previous_diagnoses || '',
          previous_treatment: data.psychiatric_history?.previous_treatment || '',
          previous_hospitalizations: data.psychiatric_history?.previous_hospitalizations || '',
          suicide_self_harm_history: data.psychiatric_history?.suicide_self_harm_history || '',
          substance_use_history: data.psychiatric_history?.substance_use_history || '',
          // Family History
          psychiatric_illness_family: data.family_history?.psychiatric_illness || '',
          medical_illness_family: data.family_history?.medical_illness || '',
          family_dynamics: data.family_history?.family_dynamics || '',
          significant_family_events: data.family_history?.significant_events || '',
          // Social History
          childhood_developmental: data.social_history?.childhood_developmental || '',
          educational_history: data.social_history?.educational || '',
          occupational_history: data.social_history?.occupational || '',
          relationship_history: data.social_history?.relationship || '',
          social_support: data.social_history?.social_support || '',
          living_situation: data.social_history?.living_situation || '',
          cultural_religious: data.social_history?.cultural_religious || '',
          // Chief Complaints
          chief_complaint: data.chief_complaints?.primary || '',
          chief_complaint_description: data.chief_complaints?.description || '',
          // Course of Illness
          illness_onset: data.course_of_illness?.onset || '',
          illness_progression: data.course_of_illness?.progression || '',
          previous_episodes: data.course_of_illness?.previous_episodes || '',
          triggers: data.course_of_illness?.triggers || '',
          impact_on_functioning: data.course_of_illness?.impact_on_functioning || '',
          // Mental Status Examination
          mse_appearance: data.baseline_assessment?.appearance || '',
          mse_behavior: data.baseline_assessment?.behavior || '',
          mse_speech: data.baseline_assessment?.speech || '',
          mse_mood: data.baseline_assessment?.mood || '',
          mse_affect: data.baseline_assessment?.affect || '',
          mse_thought_process: data.baseline_assessment?.thought_process || '',
          mse_thought_content: data.baseline_assessment?.thought_content || '',
          mse_perception: data.baseline_assessment?.perception || '',
          mse_cognition: data.baseline_assessment?.cognition || '',
          mse_insight: data.baseline_assessment?.insight || '',
          mse_judgment: data.baseline_assessment?.judgment || '',
          // Session summaries
          session_summaries: data.session_summaries?.map(s => ({
            session_number: s.session_number,
            session_date: s.session_date,
            summary: s.summary,
          })) || [],
        });
      }
    } catch (error: any) {
      Alert.alert('Error', 'Failed to load report data');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const updateField = (field: keyof ExportReportData, value: string) => {
    setReportData(prev => ({ ...prev, [field]: value }));
  };

  const updateSessionSummary = (index: number, summary: string) => {
    setReportData(prev => {
      const sessions = [...(prev.session_summaries || [])];
      if (sessions[index]) {
        sessions[index] = { ...sessions[index], summary };
      }
      return { ...prev, session_summaries: sessions };
    });
  };

  const handleExportPDF = async () => {
    setIsExporting(true);
    try {
      const token = await getToken();
      
      if (Platform.OS === 'web') {
        // Web: Use fetch and blob download
        const response = await fetch(`${API_BASE_URL}/patients/${patientId}/export-pdf`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify(reportData),
        });

        if (!response.ok) {
          throw new Error('PDF export failed');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `patient_report_${patientId}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
        Alert.alert('Success', 'PDF downloaded successfully');
      } else {
        // Mobile: Use FileSystem to download and Sharing to share
        const fileUri = `${FileSystem.documentDirectory}patient_report_${patientId}.pdf`;
        
        // Download the PDF using FileSystem
        const downloadResult = await FileSystem.downloadAsync(
          `${API_BASE_URL}/patients/${patientId}/export-pdf`,
          fileUri,
          {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (downloadResult.status !== 200) {
          // Try POST method with uploadAsync workaround
          // Since downloadAsync doesn't support POST, we'll use a different approach
          const response = await fetch(`${API_BASE_URL}/patients/${patientId}/export-pdf`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(reportData),
          });

          if (!response.ok) {
            throw new Error('PDF export failed');
          }

          // Convert response to base64 and save
          const blob = await response.blob();
          const reader = new FileReader();
          
          await new Promise<void>((resolve, reject) => {
            reader.onload = async () => {
              try {
                const base64 = (reader.result as string).split(',')[1];
                await FileSystem.writeAsStringAsync(fileUri, base64, {
                  encoding: FileSystem.EncodingType.Base64,
                });
                resolve();
              } catch (e) {
                reject(e);
              }
            };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
          });
        }

        // Share the PDF
        if (await Sharing.isAvailableAsync()) {
          await Sharing.shareAsync(fileUri, {
            mimeType: 'application/pdf',
            dialogTitle: 'Save Patient Report',
            UTI: 'com.adobe.pdf',
          });
        } else {
          Alert.alert('Success', `PDF saved to: ${fileUri}`);
        }
      }
    } catch (error) {
      console.error('Export error:', error);
      Alert.alert('Error', 'Failed to export PDF. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  if (isLoading) {
    return (
      <LinearGradient colors={COLORS.backgroundGradient} locations={[0, 0.3, 0.7, 1]} style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={COLORS.paleAzure} />
          <Text style={styles.loadingText}>Generating report data...</Text>
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
        <Text style={styles.title}>Export Report</Text>
        <TouchableOpacity 
          style={[styles.exportButton, isExporting && styles.exportButtonDisabled]} 
          onPress={handleExportPDF}
          disabled={isExporting}
        >
          {isExporting ? (
            <ActivityIndicator color={COLORS.buttonText} size="small" />
          ) : (
            <Ionicons name="download" size={24} color={COLORS.buttonText} />
          )}
        </TouchableOpacity>
      </View>

      <Text style={styles.subtitle}>Review and edit before exporting</Text>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Patient Information */}
        <EditableSection title="Patient Information" expanded={expandedSections.patientInfo} onToggle={() => toggleSection('patientInfo')}>
          <EditableField label="Name" value={reportData.patient_name || ''} onChangeText={(v) => updateField('patient_name', v)} />
          <EditableField label="Age" value={reportData.patient_age || ''} onChangeText={(v) => updateField('patient_age', v)} />
          <EditableField label="Gender" value={reportData.patient_gender || ''} onChangeText={(v) => updateField('patient_gender', v)} />
          <EditableField label="Date of Birth" value={reportData.patient_dob || ''} onChangeText={(v) => updateField('patient_dob', v)} />
          <EditableField label="Residence" value={reportData.patient_residence || ''} onChangeText={(v) => updateField('patient_residence', v)} />
          <EditableField label="Education" value={reportData.patient_education || ''} onChangeText={(v) => updateField('patient_education', v)} />
          <EditableField label="Occupation" value={reportData.patient_occupation || ''} onChangeText={(v) => updateField('patient_occupation', v)} />
          <EditableField label="Marital Status" value={reportData.patient_marital_status || ''} onChangeText={(v) => updateField('patient_marital_status', v)} />
        </EditableSection>

        {/* Medical History */}
        <EditableSection title="Medical History" expanded={expandedSections.medicalHistory} onToggle={() => toggleSection('medicalHistory')}>
          <EditableField label="Current Medical Conditions" value={reportData.current_medical_conditions || ''} onChangeText={(v) => updateField('current_medical_conditions', v)} />
          <EditableField label="Past Medical Conditions" value={reportData.past_medical_conditions || ''} onChangeText={(v) => updateField('past_medical_conditions', v)} />
          <EditableField label="Current Medications" value={reportData.current_medications || ''} onChangeText={(v) => updateField('current_medications', v)} />
          <EditableField label="Allergies" value={reportData.allergies || ''} onChangeText={(v) => updateField('allergies', v)} />
          <EditableField label="Hospitalizations" value={reportData.hospitalizations || ''} onChangeText={(v) => updateField('hospitalizations', v)} />
        </EditableSection>

        {/* Psychiatric History */}
        <EditableSection title="Psychiatric History" expanded={expandedSections.psychiatricHistory} onToggle={() => toggleSection('psychiatricHistory')}>
          <EditableField label="Previous Diagnoses" value={reportData.previous_diagnoses || ''} onChangeText={(v) => updateField('previous_diagnoses', v)} />
          <EditableField label="Previous Treatment" value={reportData.previous_treatment || ''} onChangeText={(v) => updateField('previous_treatment', v)} />
          <EditableField label="Previous Hospitalizations" value={reportData.previous_hospitalizations || ''} onChangeText={(v) => updateField('previous_hospitalizations', v)} />
          <EditableField label="Suicide/Self-Harm History" value={reportData.suicide_self_harm_history || ''} onChangeText={(v) => updateField('suicide_self_harm_history', v)} />
          <EditableField label="Substance Use History" value={reportData.substance_use_history || ''} onChangeText={(v) => updateField('substance_use_history', v)} />
        </EditableSection>

        {/* Family History */}
        <EditableSection title="Family History" expanded={expandedSections.familyHistory} onToggle={() => toggleSection('familyHistory')}>
          <EditableField label="Psychiatric Illness in Family" value={reportData.psychiatric_illness_family || ''} onChangeText={(v) => updateField('psychiatric_illness_family', v)} />
          <EditableField label="Medical Illness in Family" value={reportData.medical_illness_family || ''} onChangeText={(v) => updateField('medical_illness_family', v)} />
          <EditableField label="Family Dynamics" value={reportData.family_dynamics || ''} onChangeText={(v) => updateField('family_dynamics', v)} />
          <EditableField label="Significant Family Events" value={reportData.significant_family_events || ''} onChangeText={(v) => updateField('significant_family_events', v)} />
        </EditableSection>

        {/* Social History */}
        <EditableSection title="Social History" expanded={expandedSections.socialHistory} onToggle={() => toggleSection('socialHistory')}>
          <EditableField label="Childhood/Developmental" value={reportData.childhood_developmental || ''} onChangeText={(v) => updateField('childhood_developmental', v)} />
          <EditableField label="Educational History" value={reportData.educational_history || ''} onChangeText={(v) => updateField('educational_history', v)} />
          <EditableField label="Occupational History" value={reportData.occupational_history || ''} onChangeText={(v) => updateField('occupational_history', v)} />
          <EditableField label="Relationship History" value={reportData.relationship_history || ''} onChangeText={(v) => updateField('relationship_history', v)} />
          <EditableField label="Social Support" value={reportData.social_support || ''} onChangeText={(v) => updateField('social_support', v)} />
          <EditableField label="Living Situation" value={reportData.living_situation || ''} onChangeText={(v) => updateField('living_situation', v)} />
          <EditableField label="Cultural/Religious" value={reportData.cultural_religious || ''} onChangeText={(v) => updateField('cultural_religious', v)} />
        </EditableSection>

        {/* Chief Complaints */}
        <EditableSection title="Chief Complaints" expanded={expandedSections.chiefComplaints} onToggle={() => toggleSection('chiefComplaints')}>
          <EditableField label="Primary Complaint" value={reportData.chief_complaint || ''} onChangeText={(v) => updateField('chief_complaint', v)} />
          <EditableField label="Description" value={reportData.chief_complaint_description || ''} onChangeText={(v) => updateField('chief_complaint_description', v)} multiline />
        </EditableSection>

        {/* Course of Illness */}
        <EditableSection title="Course of Illness" expanded={expandedSections.courseOfIllness} onToggle={() => toggleSection('courseOfIllness')}>
          <EditableField label="Onset" value={reportData.illness_onset || ''} onChangeText={(v) => updateField('illness_onset', v)} />
          <EditableField label="Progression" value={reportData.illness_progression || ''} onChangeText={(v) => updateField('illness_progression', v)} />
          <EditableField label="Previous Episodes" value={reportData.previous_episodes || ''} onChangeText={(v) => updateField('previous_episodes', v)} />
          <EditableField label="Triggers" value={reportData.triggers || ''} onChangeText={(v) => updateField('triggers', v)} />
          <EditableField label="Impact on Functioning" value={reportData.impact_on_functioning || ''} onChangeText={(v) => updateField('impact_on_functioning', v)} />
        </EditableSection>

        {/* Mental Status Examination */}
        <EditableSection title="Mental Status Examination" expanded={expandedSections.mentalStatus} onToggle={() => toggleSection('mentalStatus')}>
          <EditableField label="Appearance" value={reportData.mse_appearance || ''} onChangeText={(v) => updateField('mse_appearance', v)} />
          <EditableField label="Behavior" value={reportData.mse_behavior || ''} onChangeText={(v) => updateField('mse_behavior', v)} />
          <EditableField label="Speech" value={reportData.mse_speech || ''} onChangeText={(v) => updateField('mse_speech', v)} />
          <EditableField label="Mood" value={reportData.mse_mood || ''} onChangeText={(v) => updateField('mse_mood', v)} />
          <EditableField label="Affect" value={reportData.mse_affect || ''} onChangeText={(v) => updateField('mse_affect', v)} />
          <EditableField label="Thought Process" value={reportData.mse_thought_process || ''} onChangeText={(v) => updateField('mse_thought_process', v)} />
          <EditableField label="Thought Content" value={reportData.mse_thought_content || ''} onChangeText={(v) => updateField('mse_thought_content', v)} />
          <EditableField label="Perception" value={reportData.mse_perception || ''} onChangeText={(v) => updateField('mse_perception', v)} />
          <EditableField label="Cognition" value={reportData.mse_cognition || ''} onChangeText={(v) => updateField('mse_cognition', v)} />
          <EditableField label="Insight" value={reportData.mse_insight || ''} onChangeText={(v) => updateField('mse_insight', v)} />
          <EditableField label="Judgment" value={reportData.mse_judgment || ''} onChangeText={(v) => updateField('mse_judgment', v)} />
        </EditableSection>

        {/* Session Summaries */}
        <EditableSection title={`Session Summaries (${reportData.session_summaries?.length || 0})`} expanded={expandedSections.sessions} onToggle={() => toggleSection('sessions')}>
          {reportData.session_summaries?.map((session, index) => (
            <View key={index} style={styles.sessionCard}>
              <Text style={styles.sessionHeader}>Session #{session.session_number} - {session.session_date}</Text>
              <TextInput
                style={styles.sessionSummaryInput}
                value={session.summary}
                onChangeText={(v) => updateSessionSummary(index, v)}
                placeholder="Session summary..."
                placeholderTextColor={COLORS.textSecondary}
                multiline
              />
            </View>
          ))}
          {(!reportData.session_summaries || reportData.session_summaries.length === 0) && (
            <Text style={styles.noSessionsText}>No sessions recorded</Text>
          )}
        </EditableSection>

        {/* Export Button */}
        <TouchableOpacity 
          style={[styles.exportButtonLarge, isExporting && styles.exportButtonDisabled]} 
          onPress={handleExportPDF}
          disabled={isExporting}
        >
          {isExporting ? (
            <ActivityIndicator color={COLORS.buttonText} />
          ) : (
            <>
              <Ionicons name="download" size={24} color={COLORS.buttonText} />
              <Text style={styles.exportButtonText}>Export as PDF</Text>
            </>
          )}
        </TouchableOpacity>
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
    marginBottom: 10,
  },
  backButton: {
    padding: 10,
    backgroundColor: COLORS.cardBackground,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.borderColor,
  },
  title: { fontSize: 22, fontWeight: 'bold', color: COLORS.paleAzure },
  exportButton: {
    padding: 10,
    backgroundColor: COLORS.buttonBackground,
    borderRadius: 12,
  },
  exportButtonDisabled: { opacity: 0.6 },
  subtitle: {
    fontSize: 14,
    color: COLORS.textSecondary,
    textAlign: 'center',
    marginBottom: 15,
  },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { marginTop: 12, color: COLORS.textSecondary, fontSize: 14 },
  scrollContent: { paddingHorizontal: 20, paddingBottom: 40 },
  section: {
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.borderColor,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: COLORS.cardBackground,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: 'rgba(144, 215, 239, 0.1)',
  },
  sectionTitle: { fontSize: 16, fontWeight: '600', color: COLORS.paleAzure },
  sectionContent: { padding: 16, paddingTop: 8 },
  fieldContainer: { marginBottom: 12 },
  fieldLabel: { fontSize: 12, color: COLORS.textSecondary, marginBottom: 4 },
  fieldInput: {
    backgroundColor: 'rgba(0,0,0,0.2)',
    borderWidth: 1,
    borderColor: COLORS.borderColor,
    borderRadius: 8,
    padding: 10,
    fontSize: 14,
    color: COLORS.textOnDarkTeal,
  },
  multilineInput: { minHeight: 80, textAlignVertical: 'top' },
  sessionCard: {
    backgroundColor: 'rgba(0,0,0,0.2)',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  sessionHeader: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.paleAzure,
    marginBottom: 8,
  },
  sessionSummaryInput: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderWidth: 1,
    borderColor: COLORS.borderColor,
    borderRadius: 8,
    padding: 10,
    fontSize: 13,
    color: COLORS.textOnDarkTeal,
    minHeight: 100,
    textAlignVertical: 'top',
  },
  noSessionsText: {
    fontSize: 14,
    color: COLORS.textSecondary,
    fontStyle: 'italic',
    textAlign: 'center',
    padding: 20,
  },
  exportButtonLarge: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.buttonBackground,
    paddingVertical: 16,
    borderRadius: 12,
    gap: 10,
    marginTop: 20,
  },
  exportButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.buttonText,
  },
});
