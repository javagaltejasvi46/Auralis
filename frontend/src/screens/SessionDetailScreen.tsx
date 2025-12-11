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
import { COLORS, API_BASE_URL, CARD_GLOW_STYLE, CARD_WITH_GLOW } from '../config';
import { sessionAPI, getToken } from '../services/api';
import { Session } from '../types';
import { SummaryRenderer, hasFormatting } from '../components/SummaryRenderer';

export default function SessionDetailScreen({ route, navigation }: any) {
  const { sessionId, patientName } = route.params;
  
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [transcription, setTranscription] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [notes, setNotes] = useState('');
  const [isTranslating, setIsTranslating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showTranslation, setShowTranslation] = useState(false);
  const [isGeneratingNotes, setIsGeneratingNotes] = useState(false);
  const [isEditingNotes, setIsEditingNotes] = useState(false);

  useEffect(() => {
    fetchSession();
  }, []);

  const fetchSession = async () => {
    try {
      const { session: fetchedSession } = await sessionAPI.getById(sessionId);
      setSession(fetchedSession);
      setTranscription(fetchedSession.original_transcription || '');
      setTranslatedText(fetchedSession.translated_transcription || '');
      setNotes(fetchedSession.notes || '');
    } catch (error) {
      Alert.alert('Error', 'Failed to load session');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await sessionAPI.update(sessionId, {
        original_transcription: transcription,
        translated_transcription: translatedText || undefined,
        notes: notes || undefined,
      });
      Alert.alert('Success', 'Session updated successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to save changes');
    } finally {
      setIsSaving(false);
    }
  };

  const handleTranslate = async (targetLang: string) => {
    if (!transcription) {
      Alert.alert('No Text', 'Please add transcription first');
      return;
    }

    setIsTranslating(true);
    try {
      const response = await fetch(`${API_BASE_URL}/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: transcription,
          target_language: targetLang,
          source_language: 'auto',
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setTranslatedText(result.translated_text);
        setShowTranslation(true);
        Alert.alert('Success', 'Translation completed');
      } else {
        Alert.alert('Error', 'Translation failed');
      }
    } catch (error) {
      Alert.alert('Error', 'Translation failed');
    } finally {
      setIsTranslating(false);
    }
  };

  const handleGenerateAINotes = async () => {
    if (!transcription || transcription.trim().length < 50) {
      Alert.alert('Insufficient Text', 'Please add more transcription text first (at least 50 characters)');
      return;
    }

    if (notes && notes.trim().length > 0) {
      Alert.alert(
        'Regenerate Notes?',
        'This will replace your existing notes with new AI-generated notes. Continue?',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Regenerate', onPress: () => generateNotes() }
        ]
      );
    } else {
      generateNotes();
    }
  };

  const generateNotes = async () => {
    setIsGeneratingNotes(true);
    try {
      const token = await getToken();
      const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/generate-notes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ regenerate: true }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setNotes(data.generated_notes);
        Alert.alert(
          'AI Notes Generated',
          `Clinical notes generated in ${data.inference_time || 'N/A'}s. You can edit them below.`
        );
      } else {
        Alert.alert('Error', data.detail || 'Failed to generate notes');
      }
    } catch (error: any) {
      console.error('❌ Generate notes error:', error);
      Alert.alert('Error', 'Failed to generate AI notes. Make sure the backend is running.');
    } finally {
      setIsGeneratingNotes(false);
    }
  };

  if (isLoading) {
    return (
      <LinearGradient colors={COLORS.backgroundGradient} style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={COLORS.paleAzure} />
        </View>
      </LinearGradient>
    );
  }

  if (!session) {
    return (
      <LinearGradient colors={COLORS.backgroundGradient} style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.errorText}>Session not found</Text>
        </View>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient colors={COLORS.backgroundGradient} style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={[styles.backButton, CARD_GLOW_STYLE]}>
          <Ionicons name="arrow-back" size={24} color={COLORS.paleAzure} />
        </TouchableOpacity>
        <View style={styles.headerInfo}>
          <Text style={styles.headerTitle}>Session #{session.session_number}</Text>
          <Text style={styles.headerSubtitle}>{patientName}</Text>
        </View>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Session Info */}
        <View style={[styles.infoCard, CARD_GLOW_STYLE]}>
          <View style={styles.infoRow}>
            <Ionicons name="calendar" size={16} color={COLORS.paleAzure} />
            <Text style={styles.infoText}>
              {new Date(session.session_date).toLocaleDateString()}
            </Text>
          </View>
          <View style={styles.infoRow}>
            <Ionicons name="language" size={16} color={COLORS.success} />
            <Text style={styles.infoText}>{session.language}</Text>
          </View>
          {session.duration && (
            <View style={styles.infoRow}>
              <Ionicons name="time" size={16} color={COLORS.paleAzure} />
              <Text style={styles.infoText}>{Math.floor(session.duration / 60)} minutes</Text>
            </View>
          )}
        </View>

        {/* Transcription */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Transcription</Text>
          <TextInput
            style={[styles.textInput, CARD_GLOW_STYLE]}
            value={transcription}
            onChangeText={setTranscription}
            placeholder="No transcription available"
            placeholderTextColor={COLORS.textSecondary}
            multiline
            textAlignVertical="top"
          />
        </View>

        {/* Translation Controls */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Translation</Text>
            <View style={styles.translateButtons}>
              <TouchableOpacity
                style={[styles.translateButton, CARD_GLOW_STYLE]}
                onPress={() => handleTranslate('en')}
                disabled={isTranslating}
              >
                <Text style={styles.translateButtonText}>
                  {isTranslating ? '...' : 'EN'}
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.translateButton, CARD_GLOW_STYLE]}
                onPress={() => handleTranslate('hi')}
                disabled={isTranslating}
              >
                <Text style={styles.translateButtonText}>
                  {isTranslating ? '...' : 'HI'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
          
          {showTranslation && (
            <TextInput
              style={[styles.textInput, CARD_GLOW_STYLE]}
              value={translatedText}
              onChangeText={setTranslatedText}
              placeholder="Translation will appear here"
              placeholderTextColor={COLORS.textSecondary}
              multiline
              textAlignVertical="top"
            />
          )}
        </View>

        {/* Clinical Notes Section - Formatted view with edit capability */}
        <View style={styles.section}>
          <View style={styles.notesHeader}>
            <Text style={styles.sectionTitle}>Clinical Notes</Text>
            <TouchableOpacity
              style={[styles.aiButton, isGeneratingNotes && styles.aiButtonDisabled]}
              onPress={handleGenerateAINotes}
              disabled={isGeneratingNotes}
            >
              {isGeneratingNotes ? (
                <ActivityIndicator size="small" color={COLORS.buttonText} />
              ) : (
                <>
                  <Ionicons name="flash" size={16} color={COLORS.buttonText} />
                  <Text style={styles.aiButtonText}>AI Generate</Text>
                </>
              )}
            </TouchableOpacity>
          </View>
          
          {/* Single box: Formatted view or Edit mode */}
          {isEditingNotes ? (
            <View style={[styles.notesContainer, CARD_GLOW_STYLE]}>
              <TextInput
                style={styles.notesTextInput}
                value={notes}
                onChangeText={setNotes}
                placeholder="Add clinical notes..."
                placeholderTextColor={COLORS.textSecondary}
                multiline
                textAlignVertical="top"
                autoFocus
                onBlur={() => setIsEditingNotes(false)}
              />
              <TouchableOpacity 
                style={styles.doneButton}
                onPress={() => setIsEditingNotes(false)}
              >
                <Ionicons name="checkmark" size={18} color={COLORS.buttonText} />
                <Text style={styles.doneButtonText}>Done</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <TouchableOpacity 
              style={[styles.notesContainer, CARD_GLOW_STYLE]}
              onPress={() => setIsEditingNotes(true)}
              activeOpacity={0.8}
            >
              {notes ? (
                <SummaryRenderer summary={notes} style={styles.formattedNotes} />
              ) : (
                <Text style={styles.placeholderText}>
                  Tap to add clinical notes, observations, diagnosis, treatment plans...
                </Text>
              )}
              <View style={styles.editHint}>
                <Ionicons name="pencil" size={14} color={COLORS.textSecondary} />
                <Text style={styles.editHintText}>Tap to edit</Text>
              </View>
            </TouchableOpacity>
          )}
        </View>

        {/* Save Button */}
        <TouchableOpacity
          style={[styles.saveButton, CARD_GLOW_STYLE, isSaving && styles.saveButtonDisabled]}
          onPress={handleSave}
          disabled={isSaving}
        >
          {isSaving ? (
            <ActivityIndicator color={COLORS.textOnDarkTeal} />
          ) : (
            <>
              <Ionicons name="save" size={20} color={COLORS.textOnDarkTeal} />
              <Text style={styles.saveButtonText}>Save Changes</Text>
            </>
          )}
        </TouchableOpacity>
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
    ...CARD_WITH_GLOW,
  },
  headerInfo: {
    flex: 1,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.textPrimary,
  },
  headerSubtitle: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginTop: 2,
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
    borderRadius: 16,
    padding: 16,
    marginBottom: 24,
    gap: 12,
    ...CARD_WITH_GLOW,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  infoText: {
    fontSize: 14,
    color: COLORS.textOnDarkTeal,
  },
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.textPrimary,
  },
  notesHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  aiButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.success,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    gap: 6,
  },
  aiButtonDisabled: {
    opacity: 0.6,
  },
  aiButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.buttonText,
  },
  translateButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  translateButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: COLORS.buttonBackground,
    borderRadius: 8,
    ...CARD_GLOW_STYLE,
  },
  translateButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.buttonText,
  },
  textInput: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 16,
    padding: 16,
    fontSize: 16,
    color: COLORS.textOnDarkTeal,
    minHeight: 150,
    ...CARD_WITH_GLOW,
  },
  notesContainer: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 16,
    padding: 16,
    minHeight: 150,
    maxHeight: undefined,
    ...CARD_WITH_GLOW,
  },
  notesTextInput: {
    fontSize: 16,
    color: COLORS.textOnDarkTeal,
    minHeight: 120,
    textAlignVertical: 'top',
  },
  formattedNotes: {
    fontSize: 16,
    color: COLORS.textOnDarkTeal,
    lineHeight: 24,
    flex: 1,
  },
  placeholderText: {
    fontSize: 16,
    color: COLORS.textSecondary,
    fontStyle: 'italic',
  },
  editHint: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.1)',
  },
  editHintText: {
    fontSize: 12,
    color: COLORS.textSecondary,
  },
  doneButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.success,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    gap: 6,
    marginTop: 12,
    alignSelf: 'flex-end',
  },
  doneButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.buttonText,
  },
  saveButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.success,
    paddingVertical: 16,
    borderRadius: 16,
    gap: 12,
    ...CARD_GLOW_STYLE,
    shadowColor: COLORS.success,
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.textOnDarkTeal,
  },
});
