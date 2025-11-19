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
import { sessionAPI } from '../services/api';
import { Session } from '../types';

export default function SessionDetailScreen({ route, navigation }: any) {
  const { sessionId, patientName } = route.params;
  
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [transcription, setTranscription] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [isTranslating, setIsTranslating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showTranslation, setShowTranslation] = useState(false);

  useEffect(() => {
    fetchSession();
  }, []);

  const fetchSession = async () => {
    try {
      const { session: fetchedSession } = await sessionAPI.getById(sessionId);
      setSession(fetchedSession);
      setTranscription(fetchedSession.original_transcription || '');
      setTranslatedText(fetchedSession.translated_transcription || '');
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
        headers: {
          'Content-Type': 'application/json',
        },
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

  if (!session) {
    return (
      <LinearGradient
        colors={COLORS.backgroundGradient}
        locations={[0, 0.3, 0.7, 1]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.container}
      >
        <View style={styles.loadingContainer}>
          <Text style={styles.errorText}>Session not found</Text>
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
        <View style={styles.headerInfo}>
          <Text style={styles.headerTitle}>Session #{session.session_number}</Text>
          <Text style={styles.headerSubtitle}>{patientName}</Text>
        </View>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Session Info */}
        <View style={styles.infoCard}>
          <View style={styles.infoRow}>
            <Ionicons name="calendar" size={16} color={COLORS.paleAzure} />
            <Text style={styles.infoText}>
              {new Date(session.session_date).toLocaleDateString()}
            </Text>
          </View>
          <View style={styles.infoRow}>
            <Ionicons name="language" size={16} color={COLORS.saffron} />
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
            style={styles.textInput}
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
                style={styles.translateButton}
                onPress={() => handleTranslate('en')}
                disabled={isTranslating}
              >
                <Text style={styles.translateButtonText}>
                  {isTranslating ? '...' : 'EN'}
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.translateButton}
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
              style={styles.textInput}
              value={translatedText}
              onChangeText={setTranslatedText}
              placeholder="Translation will appear here"
              placeholderTextColor={COLORS.textSecondary}
              multiline
              textAlignVertical="top"
            />
          )}
        </View>

        {/* Save Button */}
        <TouchableOpacity
          style={[styles.saveButton, isSaving && styles.saveButtonDisabled]}
          onPress={handleSave}
          disabled={isSaving}
        >
          {isSaving ? (
            <ActivityIndicator color={COLORS.raisinBlack} />
          ) : (
            <>
              <Ionicons name="save" size={20} color={COLORS.raisinBlack} />
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
    borderWidth: 2,
    borderColor: COLORS.borderColor,
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
    borderWidth: 2,
    borderColor: COLORS.borderColor,
    gap: 12,
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
    marginBottom: 12,
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
  },
  translateButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.buttonText,
  },
  textInput: {
    backgroundColor: COLORS.cardBackground,
    borderWidth: 2,
    borderColor: COLORS.borderColor,
    borderRadius: 16,
    padding: 16,
    fontSize: 16,
    color: COLORS.textOnDarkTeal,
    minHeight: 150,
  },
  saveButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.success,
    paddingVertical: 16,
    borderRadius: 16,
    gap: 12,
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
