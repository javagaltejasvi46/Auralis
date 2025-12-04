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
import { useAuth } from '../context/AuthContext';

// Generate random patient ID in format "abc-123"
const generatePatientId = (): string => {
  const letters = 'abcdefghijklmnopqrstuvwxyz';
  const numbers = '0123456789';
  let id = '';
  for (let i = 0; i < 3; i++) {
    id += letters.charAt(Math.floor(Math.random() * letters.length));
  }
  id += '-';
  for (let i = 0; i < 3; i++) {
    id += numbers.charAt(Math.floor(Math.random() * numbers.length));
  }
  return id;
};

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
      <Ionicons 
        name={expanded ? "chevron-up" : "chevron-down"} 
        size={20} 
        color={COLORS.paleAzure} 
      />
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
  required?: boolean;
}

const InputField: React.FC<InputFieldProps> = ({ 
  label, value, onChangeText, placeholder, multiline, keyboardType, required 
}) => (
  <View style={styles.inputGroup}>
    <Text style={styles.label}>{label}{required && ' *'}</Text>
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

export default function CreatePatientScreen({ navigation }: any) {
  const [isLoading, setIsLoading] = useState(false);
  const { refreshUser } = useAuth();
  
  // Section expansion states
  const [expandedSections, setExpandedSections] = useState({
    patientInfo: true,
    medicalHistory: false,
    psychiatricHistory: false,
    familyHistory: false,
    socialHistory: false,
  });

  // Patient Information
  const [patientId, setPatientId] = useState('');
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

  useEffect(() => {
    setPatientId(generatePatientId());
  }, []);

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const handleCreate = async () => {
    if (!fullName || !patientId) {
      Alert.alert('Required Fields', 'Please fill in patient name and ID');
      return;
    }

    setIsLoading(true);
    try {
      const patientData = {
        patient_id: patientId,
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
        date_of_assessment: new Date().toISOString(),
        
        // Medical History
        current_medical_conditions: currentMedicalConditions || undefined,
        past_medical_conditions: pastMedicalConditions || undefined,
        current_medications: currentMedications || undefined,
        allergies: allergies || undefined,
        hospitalizations: hospitalizations || undefined,
        
        // Psychiatric History
        previous_psychiatric_diagnoses: previousPsychiatricDiagnoses || undefined,
        previous_psychiatric_treatment: previousPsychiatricTreatment || undefined,
        previous_psychiatric_hospitalizations: previousPsychiatricHospitalizations || undefined,
        suicide_self_harm_history: suicideSelfHarmHistory || undefined,
        substance_use_history: substanceUseHistory || undefined,
        
        // Family History
        psychiatric_illness_family: psychiatricIllnessFamily || undefined,
        medical_illness_family: medicalIllnessFamily || undefined,
        family_dynamics: familyDynamics || undefined,
        significant_family_events: significantFamilyEvents || undefined,
        
        // Social History
        childhood_developmental_history: childhoodDevelopmentalHistory || undefined,
        educational_history: educationalHistory || undefined,
        occupational_history: occupationalHistory || undefined,
        relationship_history: relationshipHistory || undefined,
        social_support_system: socialSupportSystem || undefined,
        living_situation: livingSituation || undefined,
        cultural_religious_background: culturalReligiousBackground || undefined,
        
        is_active: true,
      };

      await patientAPI.create(patientData);
      await refreshUser();
      Alert.alert('Success', 'Patient created successfully', [
        { text: 'OK', onPress: () => navigation.goBack() }
      ]);
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to create patient');
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
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={COLORS.paleAzure} />
        </TouchableOpacity>
        <Text style={styles.title}>New Patient</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        <View style={styles.form}>
          {/* Patient Information Section */}
          <CollapsibleSection
            title="Patient Information"
            expanded={expandedSections.patientInfo}
            onToggle={() => toggleSection('patientInfo')}
          >
            <View style={styles.inputGroup}>
              <View style={styles.labelRow}>
                <Text style={styles.label}>Patient ID *</Text>
                <TouchableOpacity
                  onPress={() => setPatientId(generatePatientId())}
                  style={styles.regenerateButton}
                >
                  <Ionicons name="refresh" size={16} color={COLORS.saffron} />
                  <Text style={styles.regenerateText}>Regenerate</Text>
                </TouchableOpacity>
              </View>
              <View style={styles.idInputContainer}>
                <TextInput
                  style={[styles.input, styles.idInput]}
                  value={patientId}
                  editable={false}
                  placeholderTextColor={COLORS.textSecondary}
                />
                <View style={styles.autoGeneratedBadge}>
                  <Text style={styles.autoGeneratedText}>Auto-generated</Text>
                </View>
              </View>
            </View>
            
            <InputField label="Full Name" value={fullName} onChangeText={setFullName} required />
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

          {/* Medical History Section */}
          <CollapsibleSection
            title="Medical History"
            expanded={expandedSections.medicalHistory}
            onToggle={() => toggleSection('medicalHistory')}
          >
            <InputField label="Current Medical Conditions" value={currentMedicalConditions} onChangeText={setCurrentMedicalConditions} multiline />
            <InputField label="Past Medical Conditions" value={pastMedicalConditions} onChangeText={setPastMedicalConditions} multiline />
            <InputField label="Current Medications" value={currentMedications} onChangeText={setCurrentMedications} multiline />
            <InputField label="Allergies" value={allergies} onChangeText={setAllergies} multiline />
            <InputField label="Hospitalizations" value={hospitalizations} onChangeText={setHospitalizations} multiline />
          </CollapsibleSection>

          {/* Psychiatric History Section */}
          <CollapsibleSection
            title="Psychiatric History"
            expanded={expandedSections.psychiatricHistory}
            onToggle={() => toggleSection('psychiatricHistory')}
          >
            <InputField label="Previous Psychiatric Diagnoses" value={previousPsychiatricDiagnoses} onChangeText={setPreviousPsychiatricDiagnoses} multiline />
            <InputField label="Previous Psychiatric Treatment" value={previousPsychiatricTreatment} onChangeText={setPreviousPsychiatricTreatment} multiline />
            <InputField label="Previous Psychiatric Hospitalizations" value={previousPsychiatricHospitalizations} onChangeText={setPreviousPsychiatricHospitalizations} multiline />
            <InputField label="Suicide/Self-Harm History" value={suicideSelfHarmHistory} onChangeText={setSuicideSelfHarmHistory} multiline />
            <InputField label="Substance Use History" value={substanceUseHistory} onChangeText={setSubstanceUseHistory} multiline />
          </CollapsibleSection>

          {/* Family History Section */}
          <CollapsibleSection
            title="Family History"
            expanded={expandedSections.familyHistory}
            onToggle={() => toggleSection('familyHistory')}
          >
            <InputField label="Psychiatric Illness in Family" value={psychiatricIllnessFamily} onChangeText={setPsychiatricIllnessFamily} multiline />
            <InputField label="Medical Illness in Family" value={medicalIllnessFamily} onChangeText={setMedicalIllnessFamily} multiline />
            <InputField label="Family Dynamics" value={familyDynamics} onChangeText={setFamilyDynamics} multiline />
            <InputField label="Significant Family Events" value={significantFamilyEvents} onChangeText={setSignificantFamilyEvents} multiline />
          </CollapsibleSection>

          {/* Social History Section */}
          <CollapsibleSection
            title="Social History"
            expanded={expandedSections.socialHistory}
            onToggle={() => toggleSection('socialHistory')}
          >
            <InputField label="Childhood/Developmental History" value={childhoodDevelopmentalHistory} onChangeText={setChildhoodDevelopmentalHistory} multiline />
            <InputField label="Educational History" value={educationalHistory} onChangeText={setEducationalHistory} multiline />
            <InputField label="Occupational History" value={occupationalHistory} onChangeText={setOccupationalHistory} multiline />
            <InputField label="Relationship History" value={relationshipHistory} onChangeText={setRelationshipHistory} multiline />
            <InputField label="Social Support System" value={socialSupportSystem} onChangeText={setSocialSupportSystem} multiline />
            <InputField label="Living Situation" value={livingSituation} onChangeText={setLivingSituation} multiline />
            <InputField label="Cultural/Religious Background" value={culturalReligiousBackground} onChangeText={setCulturalReligiousBackground} multiline />
          </CollapsibleSection>

          <TouchableOpacity 
            style={[styles.createButton, isLoading && styles.createButtonDisabled]} 
            onPress={handleCreate}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color={COLORS.raisinBlack} />
            ) : (
              <Text style={styles.createButtonText}>Create Patient</Text>
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
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
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
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.paleAzure,
  },
  sectionContent: {
    padding: 16,
    paddingTop: 8,
  },
  inputGroup: {
    marginBottom: 16,
  },
  labelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.paleAzure,
    marginBottom: 8,
  },
  regenerateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 4,
    backgroundColor: 'rgba(227, 181, 5, 0.1)',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(227, 181, 5, 0.3)',
  },
  regenerateText: {
    fontSize: 12,
    color: COLORS.saffron,
    marginLeft: 4,
    fontWeight: '500',
  },
  idInputContainer: {
    position: 'relative',
  },
  idInput: {
    backgroundColor: 'rgba(144, 215, 239, 0.05)',
    opacity: 0.8,
  },
  autoGeneratedBadge: {
    position: 'absolute',
    right: 12,
    top: 14,
    backgroundColor: 'rgba(144, 215, 239, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  autoGeneratedText: {
    fontSize: 10,
    color: COLORS.paleAzure,
    fontWeight: '600',
  },
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
  multilineInput: {
    minHeight: 80,
    textAlignVertical: 'top',
  },
  createButton: {
    backgroundColor: COLORS.buttonBackground,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 10,
  },
  createButtonDisabled: {
    opacity: 0.6,
  },
  createButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.buttonText,
  },
});
