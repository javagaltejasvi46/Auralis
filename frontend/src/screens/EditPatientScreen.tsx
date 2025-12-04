import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  TextInput,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { COLORS } from '../config';
import { patientAPI } from '../services/api';
import { Patient } from '../types';

interface SectionProps {
  title: string;
  expanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

const CollapsibleSection: React.FC<SectionProps> = ({ title, expanded, onToggle, children }) => (
  <View style={styles.section}>
    <TouchableOpacity style={styles.sectionHeader} onPress={onToggle}>
      <Text style={styles.sectionTitle}>{title}</Text>
      <Ionicons name={expanded ? "chevron-up" : "chevron-down"} size={20} color={COLORS.paleAzure} />
    </TouchableOpacity>
    {expanded && <View style={styles.sectionContent}>{children}</View>}
  </View>
);

interface InputFieldProps {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  multiline?: boolean;
  keyboardType?: 'default' | 'email-address' | 'phone-pad' | 'numeric';
}

const InputField: React.FC<InputFieldProps> = ({ label, value, onChangeText, placeholder, multiline, keyboardType }) => (
  <View style={styles.inputGroup}>
    <Text style={styles.label}>{label}</Text>
    <TextInput
      style={[styles.input, multiline && styles.multilineInput]}
      value={value}
      onChangeText={onChangeText}
      placeholder={placeholder || `Enter ${label.toLowerCase()}`}
      placeholderTextColor={COLORS.textSecondary}
      multiline={multiline}
      numberOfLines={multiline ? 3 : 1}
      keyboardType={keyboardType || 'default'}
    />
  </View>
);

export default function EditPatientScreen({ route, navigation }: any) {
  const { patientId } = route.params;
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [patient, setPatient] = useState<Patient | null>(null);
  
  const [expandedSections, setExpandedSections] = useState({
    patientInfo: true,
    medicalHistory: false,
    psychiatricHistory: false,
    familyHistory: false,
    socialHistory: false,
    clinicalAssessment: false,
    mentalStatus: false,
  });

  // Form state
  const [fullName, setFullName] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [residence, setResidence] = useState('');
  const [education, setEducation] = useState('');
  const [occupation, setOccupation] = useState('');
  const [maritalStatus, setMaritalStatus] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');

  // Medical History
  const [currentMedicalConditions, setCurrentMedicalConditions] = useState('');
  const [pastMedicalConditions, setPastMedicalConditions] = useState('');
  const [currentMedications, setCurrentMedications] = useState('');
  const [allergies, setAllergies] = useState('');
  const [hospitalizations, setHospitalizations] = useState('');

  // Psychiatric History
  const [previousPsychiatricDiagnoses, setPreviousPsychiatricDiagnoses] = useState('');
  const [previousPsychiatricTreatment, setPreviousPsychiatricTreatment] = useState('');
  const [previousPsychiatricHospitalizations, setPreviousPsychiatricHospitalizations] = useState('');
  const [suicideSelfHarmHistory, setSuicideSelfHarmHistory] = useState('');
  const [substanceUseHistory, setSubstanceUseHistory] = useState('');

  // Family History
  const [psychiatricIllnessFamily, setPsychiatricIllnessFamily] = useState('');
  const [medicalIllnessFamily, setMedicalIllnessFamily] = useState('');
  const [familyDynamics, setFamilyDynamics] = useState('');
  const [significantFamilyEvents, setSignificantFamilyEvents] = useState('');

  // Social History
  const [childhoodDevelopmentalHistory, setChildhoodDevelopmentalHistory] = useState('');
  const [educationalHistory, setEducationalHistory] = useState('');
  const [occupationalHistory, setOccupationalHistory] = useState('');
  const [relationshipHistory, setRelationshipHistory] = useState('');
  const [socialSupportSystem, setSocialSupportSystem] = useState('');
  const [livingSituation, setLivingSituation] = useState('');
  const [culturalReligiousBackground, setCulturalReligiousBackground] = useState('');

  // Clinical Assessment
  const [chiefComplaint, setChiefComplaint] = useState('');
  const [chiefComplaintDescription, setChiefComplaintDescription] = useState('');
  const [illnessOnset, setIllnessOnset] = useState('');
  const [illnessProgression, setIllnessProgression] = useState('');
  const [previousEpisodes, setPreviousEpisodes] = useState('');
  const [triggers, setTriggers] = useState('');
  const [impactOnFunctioning, setImpactOnFunctioning] = useState('');

  // Mental Status Examination
  const [mseAppearance, setMseAppearance] = useState('');
  const [mseBehavior, setMseBehavior] = useState('');
  const [mseSpeech, setMseSpeech] = useState('');
  const [mseMood, setMseMood] = useState('');
  const [mseAffect, setMseAffect] = useState('');
  const [mseThoughtProcess, setMseThoughtProcess] = useState('');
  const [mseThoughtContent, setMseThoughtContent] = useState('');
  const [msePerception, setMsePerception] = useState('');
  const [mseCognition, setMseCognition] = useState('');
  const [mseInsight, setMseInsight] = useState('');
  const [mseJudgment, setMseJudgment] = useState('');

  useEffect(() => {
    fetchPatient();
  }, []);

  const fetchPatient = async () => {
    try {
      const { patient: p } = await patientAPI.getById(patientId, false);
      setPatient(p);
      
      // Populate form fields
      setFullName(p.full_name || '');
      setAge(p.age?.toString() || '');
      setGender(p.gender || '');
      setDateOfBirth(p.date_of_birth ? p.date_of_birth.split('T')[0] : '');
      setResidence(p.residence || '');
      setEducation(p.education || '');
      setOccupation(p.occupation || '');
      setMaritalStatus(p.marital_status || '');
      setPhone(p.phone || '');
      setEmail(p.email || '');
      
      setCurrentMedicalConditions(p.current_medical_conditions || '');
      setPastMedicalConditions(p.past_medical_conditions || '');
      setCurrentMedications(p.current_medications || '');
      setAllergies(p.allergies || '');
      setHospitalizations(p.hospitalizations || '');
      
      setPreviousPsychiatricDiagnoses(p.previous_psychiatric_diagnoses || '');
      setPreviousPsychiatricTreatment(p.previous_psychiatric_treatment || '');
      setPreviousPsychiatricHospitalizations(p.previous_psychiatric_hospitalizations || '');
      setSuicideSelfHarmHistory(p.suicide_self_harm_history || '');
      setSubstanceUseHistory(p.substance_use_history || '');
      
      setPsychiatricIllnessFamily(p.psychiatric_illness_family || '');
      setMedicalIllnessFamily(p.medical_illness_family || '');
      setFamilyDynamics(p.family_dynamics || '');
      setSignificantFamilyEvents(p.significant_family_events || '');
      
      setChildhoodDevelopmentalHistory(p.childhood_developmental_history || '');
      setEducationalHistory(p.educational_history || '');
      setOccupationalHistory(p.occupational_history || '');
      setRelationshipHistory(p.relationship_history || '');
      setSocialSupportSystem(p.social_support_system || '');
      setLivingSituation(p.living_situation || '');
      setCulturalReligiousBackground(p.cultural_religious_background || '');
      
      setChiefComplaint(p.chief_complaint || '');
      setChiefComplaintDescription(p.chief_complaint_description || '');
      setIllnessOnset(p.illness_onset || '');
      setIllnessProgression(p.illness_progression || '');
      setPreviousEpisodes(p.previous_episodes || '');
      setTriggers(p.triggers || '');
      setImpactOnFunctioning(p.impact_on_functioning || '');
      
      setMseAppearance(p.mse_appearance || '');
      setMseBehavior(p.mse_behavior || '');
      setMseSpeech(p.mse_speech || '');
      setMseMood(p.mse_mood || '');
      setMseAffect(p.mse_affect || '');
      setMseThoughtProcess(p.mse_thought_process || '');
      setMseThoughtContent(p.mse_thought_content || '');
      setMsePerception(p.mse_perception || '');
      setMseCognition(p.mse_cognition || '');
      setMseInsight(p.mse_insight || '');
      setMseJudgment(p.mse_judgment || '');
    } catch (error) {
      Alert.alert('Error', 'Failed to load patient data');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const handleSave = async () => {
    if (!fullName) {
      Alert.alert('Required', 'Patient name is required');
      return;
    }

    setIsSaving(true);
    try {
      const updateData = {
        full_name: fullName,
        age: age ? parseInt(age) : undefined,
        gender: gender || undefined,
        date_of_birth: dateOfBirth || undefined,
        residence: residence || undefined,
        education: education || undefined,
        occupation: occupation || undefined,
        marital_status: maritalStatus || undefined,
        phone: phone || undefined,
        email: email || undefined,
        current_medical_conditions: currentMedicalConditions || undefined,
        past_medical_conditions: pastMedicalConditions || undefined,
        current_medications: currentMedications || undefined,
        allergies: allergies || undefined,
        hospitalizations: hospitalizations || undefined,
        previous_psychiatric_diagnoses: previousPsychiatricDiagnoses || undefined,
        previous_psychiatric_treatment: previousPsychiatricTreatment || undefined,
        previous_psychiatric_hospitalizations: previousPsychiatricHospitalizations || undefined,
        suicide_self_harm_history: suicideSelfHarmHistory || undefined,
        substance_use_history: substanceUseHistory || undefined,
        psychiatric_illness_family: psychiatricIllnessFamily || undefined,
        medical_illness_family: medicalIllnessFamily || undefined,
        family_dynamics: familyDynamics || undefined,
        significant_family_events: significantFamilyEvents || undefined,
        childhood_developmental_history: childhoodDevelopmentalHistory || undefined,
        educational_history: educationalHistory || undefined,
        occupational_history: occupationalHistory || undefined,
        relationship_history: relationshipHistory || undefined,
        social_support_system: socialSupportSystem || undefined,
        living_situation: livingSituation || undefined,
        cultural_religious_background: culturalReligiousBackground || undefined,
        chief_complaint: chiefComplaint || undefined,
        chief_complaint_description: chiefComplaintDescription || undefined,
        illness_onset: illnessOnset || undefined,
        illness_progression: illnessProgression || undefined,
        previous_episodes: previousEpisodes || undefined,
        triggers: triggers || undefined,
        impact_on_functioning: impactOnFunctioning || undefined,
        mse_appearance: mseAppearance || undefined,
        mse_behavior: mseBehavior || undefined,
        mse_speech: mseSpeech || undefined,
        mse_mood: mseMood || undefined,
        mse_affect: mseAffect || undefined,
        mse_thought_process: mseThoughtProcess || undefined,
        mse_thought_content: mseThoughtContent || undefined,
        mse_perception: msePerception || undefined,
        mse_cognition: mseCognition || undefined,
        mse_insight: mseInsight || undefined,
        mse_judgment: mseJudgment || undefined,
      };

      await patientAPI.update(patientId, updateData);
      Alert.alert('Success', 'Patient updated successfully', [
        { text: 'OK', onPress: () => navigation.goBack() }
      ]);
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to update patient');
    } finally {
      setIsSaving(false);
    }
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

  return (
    <LinearGradient colors={COLORS.backgroundGradient} locations={[0, 0.3, 0.7, 1]} style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={COLORS.paleAzure} />
        </TouchableOpacity>
        <Text style={styles.title}>Edit Patient</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        <View style={styles.form}>
          <CollapsibleSection title="Patient Information" expanded={expandedSections.patientInfo} onToggle={() => toggleSection('patientInfo')}>
            <InputField label="Full Name" value={fullName} onChangeText={setFullName} />
            <InputField label="Age" value={age} onChangeText={setAge} keyboardType="numeric" />
            <InputField label="Gender" value={gender} onChangeText={setGender} />
            <InputField label="Date of Birth" value={dateOfBirth} onChangeText={setDateOfBirth} placeholder="YYYY-MM-DD" />
            <InputField label="Residence" value={residence} onChangeText={setResidence} />
            <InputField label="Education" value={education} onChangeText={setEducation} />
            <InputField label="Occupation" value={occupation} onChangeText={setOccupation} />
            <InputField label="Marital Status" value={maritalStatus} onChangeText={setMaritalStatus} />
            <InputField label="Phone" value={phone} onChangeText={setPhone} keyboardType="phone-pad" />
            <InputField label="Email" value={email} onChangeText={setEmail} keyboardType="email-address" />
          </CollapsibleSection>

          <CollapsibleSection title="Medical History" expanded={expandedSections.medicalHistory} onToggle={() => toggleSection('medicalHistory')}>
            <InputField label="Current Medical Conditions" value={currentMedicalConditions} onChangeText={setCurrentMedicalConditions} multiline />
            <InputField label="Past Medical Conditions" value={pastMedicalConditions} onChangeText={setPastMedicalConditions} multiline />
            <InputField label="Current Medications" value={currentMedications} onChangeText={setCurrentMedications} multiline />
            <InputField label="Allergies" value={allergies} onChangeText={setAllergies} multiline />
            <InputField label="Hospitalizations" value={hospitalizations} onChangeText={setHospitalizations} multiline />
          </CollapsibleSection>

          <CollapsibleSection title="Psychiatric History" expanded={expandedSections.psychiatricHistory} onToggle={() => toggleSection('psychiatricHistory')}>
            <InputField label="Previous Diagnoses" value={previousPsychiatricDiagnoses} onChangeText={setPreviousPsychiatricDiagnoses} multiline />
            <InputField label="Previous Treatment" value={previousPsychiatricTreatment} onChangeText={setPreviousPsychiatricTreatment} multiline />
            <InputField label="Previous Hospitalizations" value={previousPsychiatricHospitalizations} onChangeText={setPreviousPsychiatricHospitalizations} multiline />
            <InputField label="Suicide/Self-Harm History" value={suicideSelfHarmHistory} onChangeText={setSuicideSelfHarmHistory} multiline />
            <InputField label="Substance Use History" value={substanceUseHistory} onChangeText={setSubstanceUseHistory} multiline />
          </CollapsibleSection>

          <CollapsibleSection title="Family History" expanded={expandedSections.familyHistory} onToggle={() => toggleSection('familyHistory')}>
            <InputField label="Psychiatric Illness in Family" value={psychiatricIllnessFamily} onChangeText={setPsychiatricIllnessFamily} multiline />
            <InputField label="Medical Illness in Family" value={medicalIllnessFamily} onChangeText={setMedicalIllnessFamily} multiline />
            <InputField label="Family Dynamics" value={familyDynamics} onChangeText={setFamilyDynamics} multiline />
            <InputField label="Significant Family Events" value={significantFamilyEvents} onChangeText={setSignificantFamilyEvents} multiline />
          </CollapsibleSection>

          <CollapsibleSection title="Social History" expanded={expandedSections.socialHistory} onToggle={() => toggleSection('socialHistory')}>
            <InputField label="Childhood/Developmental" value={childhoodDevelopmentalHistory} onChangeText={setChildhoodDevelopmentalHistory} multiline />
            <InputField label="Educational History" value={educationalHistory} onChangeText={setEducationalHistory} multiline />
            <InputField label="Occupational History" value={occupationalHistory} onChangeText={setOccupationalHistory} multiline />
            <InputField label="Relationship History" value={relationshipHistory} onChangeText={setRelationshipHistory} multiline />
            <InputField label="Social Support System" value={socialSupportSystem} onChangeText={setSocialSupportSystem} multiline />
            <InputField label="Living Situation" value={livingSituation} onChangeText={setLivingSituation} multiline />
            <InputField label="Cultural/Religious Background" value={culturalReligiousBackground} onChangeText={setCulturalReligiousBackground} multiline />
          </CollapsibleSection>

          <CollapsibleSection title="Clinical Assessment" expanded={expandedSections.clinicalAssessment} onToggle={() => toggleSection('clinicalAssessment')}>
            <InputField label="Chief Complaint" value={chiefComplaint} onChangeText={setChiefComplaint} multiline />
            <InputField label="Description" value={chiefComplaintDescription} onChangeText={setChiefComplaintDescription} multiline />
            <InputField label="Illness Onset" value={illnessOnset} onChangeText={setIllnessOnset} multiline />
            <InputField label="Progression" value={illnessProgression} onChangeText={setIllnessProgression} multiline />
            <InputField label="Previous Episodes" value={previousEpisodes} onChangeText={setPreviousEpisodes} multiline />
            <InputField label="Triggers" value={triggers} onChangeText={setTriggers} multiline />
            <InputField label="Impact on Functioning" value={impactOnFunctioning} onChangeText={setImpactOnFunctioning} multiline />
          </CollapsibleSection>

          <CollapsibleSection title="Mental Status Examination" expanded={expandedSections.mentalStatus} onToggle={() => toggleSection('mentalStatus')}>
            <InputField label="Appearance" value={mseAppearance} onChangeText={setMseAppearance} />
            <InputField label="Behavior" value={mseBehavior} onChangeText={setMseBehavior} />
            <InputField label="Speech" value={mseSpeech} onChangeText={setMseSpeech} />
            <InputField label="Mood" value={mseMood} onChangeText={setMseMood} />
            <InputField label="Affect" value={mseAffect} onChangeText={setMseAffect} />
            <InputField label="Thought Process" value={mseThoughtProcess} onChangeText={setMseThoughtProcess} />
            <InputField label="Thought Content" value={mseThoughtContent} onChangeText={setMseThoughtContent} />
            <InputField label="Perception" value={msePerception} onChangeText={setMsePerception} />
            <InputField label="Cognition" value={mseCognition} onChangeText={setMseCognition} />
            <InputField label="Insight" value={mseInsight} onChangeText={setMseInsight} />
            <InputField label="Judgment" value={mseJudgment} onChangeText={setMseJudgment} />
          </CollapsibleSection>

          <TouchableOpacity style={[styles.saveButton, isSaving && styles.saveButtonDisabled]} onPress={handleSave} disabled={isSaving}>
            {isSaving ? <ActivityIndicator color={COLORS.raisinBlack} /> : <Text style={styles.saveButtonText}>Save Changes</Text>}
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
    borderWidth: 2,
    borderColor: COLORS.borderColor,
  },
  title: { fontSize: 24, fontWeight: 'bold', color: COLORS.paleAzure },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  scrollContent: { paddingHorizontal: 20, paddingBottom: 40 },
  form: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 20,
    padding: 16,
    borderWidth: 2,
    borderColor: COLORS.borderColor,
  },
  section: {
    marginBottom: 16,
    borderWidth: 1,
    borderColor: COLORS.borderColor,
    borderRadius: 12,
    overflow: 'hidden',
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
  inputGroup: { marginBottom: 16 },
  label: { fontSize: 14, fontWeight: '600', color: COLORS.paleAzure, marginBottom: 8 },
  input: {
    backgroundColor: 'rgba(144, 215, 239, 0.1)',
    borderWidth: 2,
    borderColor: COLORS.borderColor,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    color: COLORS.paleAzure,
  },
  multilineInput: { minHeight: 80, textAlignVertical: 'top' },
  saveButton: {
    backgroundColor: COLORS.buttonBackground,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 10,
  },
  saveButtonDisabled: { opacity: 0.6 },
  saveButtonText: { fontSize: 18, fontWeight: '600', color: COLORS.buttonText },
});
