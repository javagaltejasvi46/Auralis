import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
  Alert,
  Animated,
  Dimensions,
  TextInput,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Audio } from 'expo-av';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';

const { width, height } = Dimensions.get('window');

interface Recording {
  id: string;
  uri: string;
  duration: number;
  timestamp: Date;
}

export default function App() {
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');

  // Animation refs for waveform
  const waveAnimations = useRef(
    Array(50).fill(0).map(() => new Animated.Value(Math.random() * 0.3 + 0.1))
  ).current;

  // Logo pulse animation
  const logoPulse = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    // Logo pulse animation
    Animated.loop(
      Animated.sequence([
        Animated.timing(logoPulse, {
          toValue: 1.05,
          duration: 2000,
          useNativeDriver: true,
        }),
        Animated.timing(logoPulse, {
          toValue: 1,
          duration: 2000,
          useNativeDriver: true,
        }),
      ])
    ).start();

    // Check backend connectivity
    checkBackendConnectivity();
    const interval = setInterval(checkBackendConnectivity, 10000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  // Check backend connectivity
  const checkBackendConnectivity = async () => {
    try {
      setBackendStatus('checking');
      const urls = ['http://192.168.0.140:8000', 'http://127.0.0.1:8000', 'http://localhost:8000'];
      
      for (const url of urls) {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 5000);
          
          const response = await fetch(url, { 
            method: 'GET',
            signal: controller.signal
          });
          
          clearTimeout(timeoutId);
          
          if (response.ok) {
            setBackendStatus('connected');
            return;
          }
        } catch (err) {
          continue;
        }
      }
      
      setBackendStatus('disconnected');
    } catch (error) {
      setBackendStatus('disconnected');
    }
  };

  // Start waveform animation
  const startWaveformAnimation = () => {
    waveAnimations.forEach((anim, index) => {
      Animated.loop(
        Animated.sequence([
          Animated.timing(anim, {
            toValue: Math.random() * 0.8 + 0.2,
            duration: 150 + Math.random() * 100,
            useNativeDriver: false,
          }),
          Animated.timing(anim, {
            toValue: Math.random() * 0.6 + 0.1,
            duration: 150 + Math.random() * 100,
            useNativeDriver: false,
          }),
        ])
      ).start();
    });
  };

  // Stop waveform animation
  const stopWaveformAnimation = () => {
    waveAnimations.forEach(anim => {
      anim.stopAnimation();
      Animated.timing(anim, {
        toValue: Math.random() * 0.3 + 0.1,
        duration: 200,
        useNativeDriver: false,
      }).start();
    });
  };

  async function startRecording() {
    try {
      const permission = await Audio.requestPermissionsAsync();
      
      if (permission.status !== 'granted') {
        Alert.alert('Permission required', 'Please grant microphone permission to record audio.');
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      
      setRecording(recording);
      setIsRecording(true);
      startWaveformAnimation();
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    } catch (err) {
      console.error('Failed to start recording', err);
      Alert.alert('Error', 'Failed to start recording');
    }
  }

  async function stopRecording() {
    if (!recording) return;

    setIsRecording(false);
    setRecording(null);
    stopWaveformAnimation();
    
    await recording.stopAndUnloadAsync();
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: false,
    });
    
    const uri = recording.getURI();
    const status = await recording.getStatusAsync();
    
    if (uri) {
      const newRecording: Recording = {
        id: Date.now().toString(),
        uri,
        duration: status.durationMillis || 0,
        timestamp: new Date(),
      };
      
      setRecordings(prev => [newRecording, ...prev]);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      
      // Upload to backend
      uploadRecording(uri, newRecording.id);
    }
  }

  async function uploadRecording(uri: string, recordingId: string) {
    try {
      const formData = new FormData();
      formData.append('file', {
        uri,
        type: 'audio/m4a',
        name: `recording_${recordingId}.m4a`,
      } as any);

      const urls = [
        'http://192.168.0.140:8000/upload-audio',
        'http://127.0.0.1:8000/upload-audio',
        'http://localhost:8000/upload-audio'
      ];

      for (const url of urls) {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 15000);
          
          const response = await fetch(url, {
            method: 'POST',
            body: formData,
            signal: controller.signal,
          });

          clearTimeout(timeoutId);

          if (response.ok) {
            console.log('✅ Recording uploaded successfully!');
            return;
          }
        } catch (err) {
          continue;
        }
      }
      
      console.log('Recording saved locally. Backend upload will work after app rebuild.');
    } catch (error) {
      console.error('Upload failed:', error);
    }
  }

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <LinearGradient
      colors={['#f0f9ff', '#e0f2fe', '#bae6fd']}
      style={styles.container}
    >
      <StatusBar style="dark" />
      
      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header with Logo */}
        <View style={styles.header}>
          <Animated.View style={[styles.logoContainer, { transform: [{ scale: logoPulse }] }]}>
            <View style={styles.logo}>
              <Ionicons name="medical" size={40} color="#38bdf8" />
            </View>
          </Animated.View>
          
          <View style={styles.titleContainer}>
            <Text style={styles.title}>AURALIS</Text>
            <View style={styles.titleGlow} />
          </View>
          
          <Text style={styles.subtitle}>Medical Voice Transcription</Text>
        </View>

        {/* Main Content Card */}
        <View style={styles.mainCard}>
          {/* Instruction Text */}
          <Text style={styles.instructionText}>
            Begin recording patient notes or medical documentation
          </Text>

          {/* Waveform Display */}
          <View style={styles.waveformContainer}>
            <View style={styles.waveformInner}>
              {waveAnimations.map((anim, index) => (
                <Animated.View
                  key={index}
                  style={[
                    styles.waveBar,
                    {
                      height: anim.interpolate({
                        inputRange: [0, 1],
                        outputRange: [8, 120],
                      }),
                      backgroundColor: isRecording ? '#38bdf8' : '#93c5fd',
                      opacity: isRecording ? 0.9 : 0.6,
                    }
                  ]}
                />
              ))}
            </View>
          </View>

          {/* Microphone Button */}
          <View style={styles.microphoneSection}>
            <TouchableOpacity
              style={[
                styles.micButton,
                isRecording && styles.micButtonActive
              ]}
              onPress={toggleRecording}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={isRecording ? ['#38bdf8', '#0ea5e9'] : ['#38bdf8', '#3b82f6']}
                style={styles.micButtonGradient}
              >
                <Ionicons
                  name={isRecording ? "mic-off" : "mic"}
                  size={40}
                  color="#fff"
                />
              </LinearGradient>
            </TouchableOpacity>
            
            <Text style={styles.micButtonLabel}>
              {isRecording ? 'Recording...' : 'Start Recording'}
            </Text>
          </View>

          {/* Transcription Display (Empty for now) */}
          <View style={styles.transcriptionSection}>
            <View style={styles.transcriptionHeader}>
              <Text style={styles.transcriptionLabel}>Clinical Notes</Text>
              {transcription && (
                <TouchableOpacity onPress={() => setTranscription('')}>
                  <Text style={styles.clearButton}>Clear</Text>
                </TouchableOpacity>
              )}
            </View>
            
            <View style={styles.transcriptionBox}>
              <TextInput
                style={styles.transcriptionInput}
                value={transcription}
                onChangeText={setTranscription}
                placeholder="Medical transcription will appear here..."
                placeholderTextColor="#94a3b8"
                multiline
                editable={false}
              />
            </View>
            
            <Text style={styles.transcriptionNote}>
              🔮 Voice-to-text transcription coming soon
            </Text>
          </View>

          {/* Backend Status */}
          <View style={styles.statusBar}>
            <View style={[
              styles.statusDot,
              { backgroundColor: 
                backendStatus === 'connected' ? '#4ade80' : 
                backendStatus === 'disconnected' ? '#ef4444' : '#fbbf24' 
              }
            ]} />
            <Text style={styles.statusText}>
              Backend: {backendStatus === 'connected' ? 'Connected' : 
                       backendStatus === 'disconnected' ? 'Disconnected' : 'Checking...'}
            </Text>
          </View>
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
    alignItems: 'center',
    marginBottom: 30,
  },
  logoContainer: {
    marginBottom: 20,
  },
  logo: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(186, 230, 253, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#38bdf8',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 20,
    elevation: 10,
  },
  titleContainer: {
    position: 'relative',
    marginBottom: 12,
  },
  title: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#0ea5e9',
    letterSpacing: 12,
    textAlign: 'center',
  },
  titleGlow: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#38bdf8',
    opacity: 0.2,
    borderRadius: 10,
    transform: [{ scaleX: 1.1 }, { scaleY: 1.3 }],
  },
  subtitle: {
    fontSize: 16,
    color: '#64748b',
    letterSpacing: 2,
  },
  mainCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    borderRadius: 24,
    padding: 24,
    shadowColor: '#38bdf8',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 20,
    elevation: 8,
    borderWidth: 1,
    borderColor: 'rgba(186, 230, 253, 0.5)',
  },
  instructionText: {
    fontSize: 14,
    color: '#64748b',
    textAlign: 'center',
    marginBottom: 20,
  },
  waveformContainer: {
    height: 200,
    backgroundColor: 'rgba(240, 249, 255, 0.5)',
    borderRadius: 16,
    padding: 16,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: 'rgba(186, 230, 253, 0.5)',
    overflow: 'hidden',
  },
  waveformInner: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
  },
  waveBar: {
    width: 3,
    borderRadius: 2,
    minHeight: 8,
  },
  microphoneSection: {
    alignItems: 'center',
    marginBottom: 24,
  },
  micButton: {
    width: 96,
    height: 96,
    borderRadius: 48,
    marginBottom: 12,
    shadowColor: '#38bdf8',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 8,
  },
  micButtonActive: {
    shadowOpacity: 0.6,
    shadowRadius: 16,
  },
  micButtonGradient: {
    width: '100%',
    height: '100%',
    borderRadius: 48,
    justifyContent: 'center',
    alignItems: 'center',
  },
  micButtonLabel: {
    fontSize: 16,
    color: '#64748b',
    fontWeight: '500',
  },
  transcriptionSection: {
    marginBottom: 20,
  },
  transcriptionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  transcriptionLabel: {
    fontSize: 16,
    color: '#334155',
    fontWeight: '600',
  },
  clearButton: {
    fontSize: 14,
    color: '#38bdf8',
    fontWeight: '500',
  },
  transcriptionBox: {
    minHeight: 150,
    backgroundColor: 'rgba(255, 255, 255, 0.6)',
    borderRadius: 12,
    borderWidth: 2,
    borderColor: 'rgba(186, 230, 253, 0.5)',
    padding: 12,
    marginBottom: 8,
  },
  transcriptionInput: {
    flex: 1,
    fontSize: 14,
    color: '#334155',
    textAlignVertical: 'top',
  },
  transcriptionNote: {
    fontSize: 12,
    color: '#94a3b8',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  statusBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: 'rgba(240, 249, 255, 0.5)',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(186, 230, 253, 0.5)',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    fontSize: 12,
    color: '#64748b',
    fontWeight: '500',
  },
});