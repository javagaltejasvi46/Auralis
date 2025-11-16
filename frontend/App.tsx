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
  const [partialTranscript, setPartialTranscript] = useState('');
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const [wsStatus, setWsStatus] = useState<string>('Not connected');
  const [selectedLanguage, setSelectedLanguage] = useState<'hindi' | 'english'>('hindi');
  const [translatedText, setTranslatedText] = useState('');
  const [isTranslating, setIsTranslating] = useState(false);
  const [showTranslateModal, setShowTranslateModal] = useState(false);
  const [displayMode, setDisplayMode] = useState<'original' | 'translated'>('original');
  const wsRef = useRef<WebSocket | null>(null);

  // Animation refs for waveform
  const waveAnimations = useRef(
    Array(50).fill(0).map(() => new Animated.Value(Math.random() * 0.3 + 0.1))
  ).current;

  // Logo pulse animation
  const logoPulse = useRef(new Animated.Value(1)).current;

  // Transition animation for record button
  const recordTransition = useRef(new Animated.Value(0)).current;
  const buttonScale = useRef(new Animated.Value(1)).current;

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
    console.log('🔍 Checking backend connectivity...');
    try {
      setBackendStatus('checking');
      const urls = ['http://192.168.0.102:8002', 'http://127.0.0.1:8002', 'http://localhost:8002'];
      
      for (const url of urls) {
        try {
          console.log(`📡 Trying: ${url}`);
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 5000);
          
          const response = await fetch(url, { 
            method: 'GET',
            signal: controller.signal
          });
          
          clearTimeout(timeoutId);
          
          if (response.ok) {
            console.log(`✅ Backend connected: ${url}`);
            setBackendStatus('connected');
            return;
          }
        } catch (err) {
          console.log(`❌ Failed: ${url}`);
          continue;
        }
      }
      
      console.log('⚠️ All backend URLs failed');
      setBackendStatus('disconnected');
    } catch (error) {
      console.log('❌ Backend check error:', error);
      setBackendStatus('disconnected');
    }
  };

  // Change transcription language
  const changeLanguage = (language: 'hindi' | 'english') => {
    console.log(`🌍 Changing language to: ${language}`);
    setSelectedLanguage(language);
    
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'set_language',
        language: language
      }));
    }
  };

  // Translate text
  const translateText = async (targetLang: string) => {
    if (!transcription) {
      Alert.alert('No Text', 'Please record and transcribe audio first');
      return;
    }

    setShowTranslateModal(false);
    setIsTranslating(true);
    console.log(`🔄 Translating to ${targetLang}...`);

    try {
      const urls = ['http://192.168.0.102:8002/translate', 'http://127.0.0.1:8002/translate'];
      
      for (const url of urls) {
        try {
          const response = await fetch(url, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              text: transcription,
              target_language: targetLang,
              source_language: 'auto'
            })
          });

          if (response.ok) {
            const result = await response.json();
            console.log('✅ Translation successful:', result.translated_text);
            setTranslatedText(result.translated_text);
            setDisplayMode('translated');
            setIsTranslating(false);
            return;
          }
        } catch (err) {
          continue;
        }
      }
      
      Alert.alert('Translation Error', 'Failed to translate text');
      setIsTranslating(false);
    } catch (error) {
      console.error('❌ Translation error:', error);
      Alert.alert('Error', 'Translation failed');
      setIsTranslating(false);
    }
  };

  // Send audio file for transcription via WebSocket
  const sendAudioForTranscription = async (uri: string) => {
    try {
      console.log('🔄 Converting audio to base64...');
      
      // Read the audio file
      const response = await fetch(uri);
      const blob = await response.blob();
      
      console.log(`📦 Audio file size: ${blob.size} bytes`);
      
      // Convert to base64
      const reader = new FileReader();
      reader.readAsDataURL(blob);
      
      reader.onloadend = () => {
        const base64data = reader.result as string;
        console.log('✅ Audio converted to base64');
        
        // Connect WebSocket and send audio
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
          console.log('🔌 Reconnecting WebSocket...');
          const ws = connectWebSocket();
          if (ws) {
            ws.onopen = () => {
              console.log('📤 Sending audio data...');
              ws.send(JSON.stringify({
                type: 'audio_file',
                data: base64data,
                format: 'm4a'
              }));
            };
          }
        } else {
          console.log('📤 Sending audio data via existing connection...');
          wsRef.current.send(JSON.stringify({
            type: 'audio_file',
            data: base64data,
            format: 'm4a'
          }));
        }
      };
      
      reader.onerror = (error) => {
        console.log('❌ Error reading audio file:', error);
      };
      
    } catch (error) {
      console.log('❌ Error sending audio for transcription:', error);
    }
  };

  // Connect to WebSocket for transcription
  const connectWebSocket = () => {
    console.log('🔌 Attempting WebSocket connection...');
    const wsUrls = ['ws://192.168.0.102:8003', 'ws://127.0.0.1:8003', 'ws://localhost:8003'];
    
    for (const wsUrl of wsUrls) {
      try {
        console.log(`🔗 Trying WebSocket: ${wsUrl}`);
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          console.log('✅ WebSocket connected!');
          setWsStatus('Connected');
          wsRef.current = ws;
          
          // Set the selected language immediately after connection
          console.log(`🌍 Setting language to: ${selectedLanguage}`);
          ws.send(JSON.stringify({
            type: 'set_language',
            language: selectedLanguage
          }));
        };
        
        ws.onmessage = (event) => {
          console.log('📨 Received message:', event.data);
          try {
            const data = JSON.parse(event.data);
            console.log('📝 Parsed data:', data);
            
            if (data.type === 'connected' || data.type === 'welcome') {
              console.log('👋 Server welcome:', data.message);
              setWsStatus('Ready');
            } else if (data.type === 'processing') {
              console.log('⏳ Processing:', data.message);
              setPartialTranscript(data.message);
            } else if (data.type === 'partial') {
              console.log('⏳ Partial transcript:', data.text);
              setPartialTranscript(data.text);
            } else if (data.type === 'final') {
              console.log('✅ Final transcript:', data.text);
              setTranscription(prev => prev + (prev ? ' ' : '') + data.text);
              setPartialTranscript('');
            } else if (data.type === 'error') {
              console.log('❌ Server error:', data.message);
              Alert.alert('Transcription Error', data.message);
              setPartialTranscript('');
            } else {
              console.log('ℹ️ Other message type:', data.type);
            }
          } catch (err) {
            console.log('❌ Error parsing message:', err, event.data);
          }
        };
        
        ws.onerror = (error) => {
          console.log('❌ WebSocket error:', error);
          console.log('Error details:', JSON.stringify(error));
          setWsStatus('Error');
        };
        
        ws.onclose = () => {
          console.log('🔌 WebSocket closed');
          setWsStatus('Disconnected');
          wsRef.current = null;
        };
        
        return ws;
      } catch (err) {
        console.log(`❌ Failed to connect to ${wsUrl}:`, err);
        continue;
      }
    }
    
    console.log('⚠️ All WebSocket URLs failed');
    setWsStatus('Failed to connect');
    return null;
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
    console.log('🎤 Starting recording...');
    try {
      const permission = await Audio.requestPermissionsAsync();
      console.log('🔐 Permission status:', permission.status);
      
      if (permission.status !== 'granted') {
        console.log('❌ Permission denied');
        Alert.alert('Permission required', 'Please grant microphone permission to record audio.');
        return;
      }

      // Connect WebSocket for transcription
      console.log('🔌 Connecting WebSocket...');
      connectWebSocket();

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      console.log('🎙️ Creating audio recording...');
      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      
      console.log('✅ Recording started successfully');
      setRecording(recording);
      setIsRecording(true);
      
      // Animate transition
      Animated.parallel([
        Animated.spring(recordTransition, {
          toValue: 1,
          tension: 50,
          friction: 7,
          useNativeDriver: true,
        }),
        Animated.sequence([
          Animated.timing(buttonScale, {
            toValue: 0.8,
            duration: 150,
            useNativeDriver: true,
          }),
          Animated.spring(buttonScale, {
            toValue: 1,
            tension: 100,
            friction: 5,
            useNativeDriver: true,
          }),
        ]),
      ]).start();
      
      startWaveformAnimation();
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    } catch (err) {
      console.error('❌ Failed to start recording:', err);
      Alert.alert('Error', 'Failed to start recording');
    }
  }

  async function stopRecording() {
    console.log('⏹️ Stopping recording...');
    if (!recording) {
      console.log('⚠️ No recording to stop');
      return;
    }

    setIsRecording(false);
    
    // Animate transition back
    Animated.parallel([
      Animated.spring(recordTransition, {
        toValue: 0,
        tension: 50,
        friction: 7,
        useNativeDriver: true,
      }),
      Animated.sequence([
        Animated.timing(buttonScale, {
          toValue: 0.8,
          duration: 150,
          useNativeDriver: true,
        }),
        Animated.spring(buttonScale, {
          toValue: 1,
          tension: 100,
          friction: 5,
          useNativeDriver: true,
        }),
      ]),
    ]).start();
    
    stopWaveformAnimation();
    
    console.log('🛑 Stopping audio recording...');
    await recording.stopAndUnloadAsync();
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: false,
    });
    
    const uri = recording.getURI();
    const status = await recording.getStatusAsync();
    console.log('📁 Recording URI:', uri);
    console.log('⏱️ Duration:', status.durationMillis);
    
    setRecording(null);
    
    if (uri) {
      const newRecording: Recording = {
        id: Date.now().toString(),
        uri,
        duration: status.durationMillis || 0,
        timestamp: new Date(),
      };
      
      // Send audio file to WebSocket for transcription
      console.log('📤 Sending audio file for transcription...');
      await sendAudioForTranscription(uri);
      
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
        'http://192.168.0.102:8002/upload-audio',
        'http://127.0.0.1:8002/upload-audio',
        'http://localhost:8002/upload-audio'
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
    <View style={styles.container}>
      <LinearGradient
        colors={['#201E1F', '#6457A6', '#201E1F']}
        locations={[0, 0.5, 1]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
        style={StyleSheet.absoluteFill}
      />
      <LinearGradient
        colors={['transparent', '#90D7EF', 'transparent']}
        locations={[0, 0.5, 1]}
        start={{ x: 0, y: 0 }}
        end={{ x: 0, y: 1 }}
        style={[StyleSheet.absoluteFill, { opacity: 0.6 }]}
      />
      <LinearGradient
        colors={['transparent', '#6457A6', 'transparent']}
        locations={[0.3, 0.6, 0.9]}
        start={{ x: 0, y: 1 }}
        end={{ x: 1, y: 0 }}
        style={[StyleSheet.absoluteFill, { opacity: 0.4 }]}
      />
      <StatusBar style="light" />
      
      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header with Logo */}
        <View style={styles.header}>
          <Animated.View style={[styles.logoContainer, { transform: [{ scale: logoPulse }] }]}>
            <View style={styles.logo}>
              <Ionicons name="medical" size={40} color="#90D7EF" />
            </View>
          </Animated.View>
          
          <View style={styles.titleContainer}>
            <Text style={styles.title}>AURALIS</Text>
            <View style={styles.titleGlow} />
          </View>
          
          <Text style={styles.subtitle}>Hear . Understand . Heal</Text>
        </View>

        {/* Main Content Card */}
        <View style={styles.mainCard}>
          {/* Language Selector */}
          <View style={styles.languageSelector}>
            <Text style={styles.languageSelectorLabel}>Transcription Language:</Text>
            <View style={styles.languageButtons}>
              <TouchableOpacity
                style={[
                  styles.languageButton,
                  selectedLanguage === 'hindi' && styles.languageButtonActive
                ]}
                onPress={() => changeLanguage('hindi')}
              >
                <Text style={[
                  styles.languageButtonText,
                  selectedLanguage === 'hindi' && styles.languageButtonTextActive
                ]}>
                  हिंदी
                </Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[
                  styles.languageButton,
                  selectedLanguage === 'english' && styles.languageButtonActive
                ]}
                onPress={() => changeLanguage('english')}
              >
                <Text style={[
                  styles.languageButtonText,
                  selectedLanguage === 'english' && styles.languageButtonTextActive
                ]}>
                  English
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Microphone Button / Waveform */}
          <View style={styles.microphoneSection}>
            <Animated.View
              style={{
                transform: [{ scale: buttonScale }],
              }}
            >
              {!isRecording ? (
                // Start Recording Button
                <Animated.View
                  style={{
                    opacity: recordTransition.interpolate({
                      inputRange: [0, 1],
                      outputRange: [1, 0],
                    }),
                    transform: [
                      {
                        scale: recordTransition.interpolate({
                          inputRange: [0, 1],
                          outputRange: [1, 0.5],
                        }),
                      },
                    ],
                  }}
                >
                  <TouchableOpacity
                    style={styles.micButton}
                    onPress={toggleRecording}
                    activeOpacity={0.8}
                  >
                    <LinearGradient
                      colors={['#90D7EF', '#A8DAEF']}
                      style={styles.micButtonGradient}
                    >
                      <Ionicons
                        name="mic"
                        size={40}
                        color="#201E1F"
                      />
                    </LinearGradient>
                  </TouchableOpacity>
                  
                  <Text style={styles.micButtonLabel}>
                    Start Recording
                  </Text>
                </Animated.View>
              ) : (
                // Recording Waveform (Circular)
                <Animated.View
                  style={{
                    opacity: recordTransition.interpolate({
                      inputRange: [0, 1],
                      outputRange: [0, 1],
                    }),
                    transform: [
                      {
                        scale: recordTransition.interpolate({
                          inputRange: [0, 1],
                          outputRange: [0.5, 1],
                        }),
                      },
                    ],
                  }}
                >
                  <View style={styles.circularWaveformContainer}>
                    <View style={styles.circularWaveform}>
                      {waveAnimations.map((anim, index) => {
                        const angle = (index / waveAnimations.length) * 2 * Math.PI;
                        const radius = 60;
                        return (
                          <Animated.View
                            key={index}
                            style={[
                              styles.circularWaveBar,
                              {
                                height: anim.interpolate({
                                  inputRange: [0, 1],
                                  outputRange: [15, 45],
                                }),
                                transform: [
                                  { translateX: Math.cos(angle) * radius },
                                  { translateY: Math.sin(angle) * radius },
                                  { rotate: `${(angle * 180) / Math.PI + 90}deg` },
                                ],
                              }
                            ]}
                          />
                        );
                      })}
                    </View>
                    
                    {/* Center Mic Icon */}
                    <View style={styles.centerMicIcon}>
                      <Ionicons name="mic" size={32} color="#E3B505" />
                    </View>
                  </View>
                  
                  {/* Stop Button */}
                  <TouchableOpacity
                    style={styles.stopButton}
                    onPress={toggleRecording}
                    activeOpacity={0.8}
                  >
                    <Text style={styles.stopButtonText}>Stop</Text>
                  </TouchableOpacity>
                </Animated.View>
              )}
            </Animated.View>
          </View>

          {/* Transcription Box - Only shows after transcription */}
          {(transcription || partialTranscript) && (
            <View style={styles.transcriptionBoxContainer}>
              <View style={styles.transcriptionHeader}>
                <Text style={styles.transcriptionLabel}>Transcription</Text>
                <View style={styles.headerButtons}>
                  <TouchableOpacity
                    style={styles.translateIconButton}
                    onPress={() => setShowTranslateModal(true)}
                    disabled={isTranslating}
                  >
                    <Ionicons name="language" size={20} color="#3b82f6" />
                    <Text style={styles.translateIconText}>
                      {isTranslating ? 'Translating...' : 'Translate'}
                    </Text>
                  </TouchableOpacity>
                  <TouchableOpacity onPress={() => {
                    setTranscription('');
                    setTranslatedText('');
                    setDisplayMode('original');
                  }}>
                    <Text style={styles.clearButton}>Clear</Text>
                  </TouchableOpacity>
                </View>
              </View>
              
              <TextInput
                style={styles.transcriptionText}
                value={displayMode === 'original' 
                  ? transcription + (partialTranscript ? ' ' + partialTranscript : '')
                  : translatedText || transcription
                }
                multiline
                editable={false}
                textAlignVertical="top"
              />
              
              {partialTranscript && displayMode === 'original' && (
                <Text style={styles.partialLabel}>⏳ Processing...</Text>
              )}
              
              {displayMode === 'translated' && translatedText && (
                <TouchableOpacity
                  style={styles.showOriginalButton}
                  onPress={() => setDisplayMode('original')}
                >
                  <Text style={styles.showOriginalText}>Show Original</Text>
                </TouchableOpacity>
              )}
            </View>
          )}

          {/* Translation Language Modal */}
          {showTranslateModal && (
            <View style={styles.modalOverlay}>
              <View style={styles.modalContent}>
                <Text style={styles.modalTitle}>Translate to:</Text>
                
                <TouchableOpacity
                  style={styles.modalButton}
                  onPress={() => translateText('en')}
                >
                  <Text style={styles.modalButtonText}>🇬🇧 English</Text>
                </TouchableOpacity>
                
                <TouchableOpacity
                  style={styles.modalButton}
                  onPress={() => translateText('hi')}
                >
                  <Text style={styles.modalButtonText}>🇮🇳 हिंदी (Hindi)</Text>
                </TouchableOpacity>
                
                <TouchableOpacity
                  style={styles.modalCancelButton}
                  onPress={() => setShowTranslateModal(false)}
                >
                  <Text style={styles.modalCancelText}>Cancel</Text>
                </TouchableOpacity>
              </View>
            </View>
          )}

          {/* Status Bar */}
          <View style={styles.statusBar}>
            <View style={styles.statusItem}>
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
            <View style={styles.statusItem}>
              <View style={[
                styles.statusDot,
                { backgroundColor: 
                  wsStatus === 'Connected' ? '#4ade80' : 
                  wsStatus === 'Disconnected' || wsStatus === 'Not connected' ? '#94a3b8' : '#ef4444' 
                }
              ]} />
              <Text style={styles.statusText}>
                WS: {wsStatus}
              </Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingTop: 50,
    paddingHorizontal: 16,
    paddingBottom: 30,
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
    backgroundColor: 'transparent',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#90D7EF',
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
    color: '#90D7EF',
    letterSpacing: 12,
    textAlign: 'center',
  },
  titleGlow: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#90D7EF',
    opacity: 0.2,
    borderRadius: 10,
    transform: [{ scaleX: 1.1 }, { scaleY: 1.3 }],
  },
  subtitle: {
    fontSize: 16,
    color: '#90D7EF',
    letterSpacing: 2,
    opacity: 0.8,
  },
  mainCard: {
    backgroundColor: 'rgba(32, 30, 31, 0.85)',
    borderRadius: 24,
    padding: 24,
    borderWidth: 2,
    borderColor: 'rgba(144, 215, 239, 0.5)',
    alignItems: 'center',
    shadowColor: '#B81F00',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.9,
    shadowRadius: 30,
    elevation: 20,
  },
  instructionText: {
    fontSize: 14,
    color: '#90D7EF',
    textAlign: 'center',
    marginBottom: 20,
    opacity: 0.8,
  },
  circularWaveformContainer: {
    width: 200,
    height: 200,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  circularWaveform: {
    width: 200,
    height: 200,
    borderRadius: 100,
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
    backgroundColor: 'transparent',
  },
  circularWaveBar: {
    position: 'absolute',
    width: 4,
    backgroundColor: '#E3B505',
    borderRadius: 2,
    opacity: 0.9,
  },
  centerMicIcon: {
    position: 'absolute',
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: 'rgba(32, 30, 31, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  stopButton: {
    paddingHorizontal: 40,
    paddingVertical: 14,
    backgroundColor: '#B81F00',
    borderRadius: 25,
    shadowColor: '#B81F00',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 6,
  },
  stopButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    letterSpacing: 1,
  },
  microphoneSection: {
    alignItems: 'center',
    marginBottom: 24,
    width: '100%',
    marginLeft: 20,
  },
  micButton: {
    width: 96,
    height: 96,
    borderRadius: 48,
    marginBottom: 12,
    shadowColor: '#90D7EF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.6,
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
    color: '#90D7EF',
    fontWeight: '500',
    marginLeft: -15,
  },
  transcriptionSection: {
    marginBottom: 20,
  },
  clearButton: {
    fontSize: 14,
    color: '#B81F00',
    fontWeight: '500',
  },
  transcriptionBoxContainer: {
    backgroundColor: 'rgba(32, 30, 31, 0.85)',
    borderRadius: 16,
    padding: 20,
    marginTop: 24,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: 'rgba(144, 215, 239, 0.5)',
    width: '100%',
  },
  transcriptionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    width: '100%',
  },
  headerButtons: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  translateIconButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#90D7EF',
    borderRadius: 8,
  },
  translateIconText: {
    fontSize: 14,
    color: '#201E1F',
    fontWeight: '600',
  },
  transcriptionInput: {
    flex: 1,
    fontSize: 14,
    color: '#334155',
    textAlignVertical: 'top',
  },
  transcriptionLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#90D7EF',
    marginBottom: 8,
    textAlign: 'center',
  },
  transcriptionText: {
    fontSize: 16,
    color: '#90D7EF',
    minHeight: 100,
    maxHeight: 200,
    textAlignVertical: 'top',
  },
  partialLabel: {
    fontSize: 12,
    color: '#E3B505',
    fontStyle: 'italic',
    marginTop: 8,
  },
  statusBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: 'rgba(32, 30, 31, 0.6)',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(144, 215, 239, 0.3)',
    width: '100%',
  },
  statusItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  languageSelector: {
    marginBottom: 20,
    alignItems: 'center',
    width: '100%',
  },
  languageSelectorLabel: {
    fontSize: 14,
    color: '#90D7EF',
    marginBottom: 10,
    fontWeight: '500',
    textAlign: 'center',
  },
  languageButtons: {
    flexDirection: 'row',
    gap: 12,
    justifyContent: 'center',
  },
  languageButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: 'rgba(32, 30, 31, 0.6)',
    borderRadius: 20,
    borderWidth: 2,
    borderColor: 'rgba(144, 215, 239, 0.4)',
  },
  languageButtonActive: {
    backgroundColor: '#90D7EF',
    borderColor: '#90D7EF',
  },
  languageButtonText: {
    fontSize: 16,
    color: '#90D7EF',
    fontWeight: '600',
  },
  languageButtonTextActive: {
    color: '#201E1F',
  },
  translationSection: {
    marginTop: 16,
    padding: 16,
    backgroundColor: 'rgba(240, 249, 255, 0.5)',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e0f2fe',
  },
  translationLabel: {
    fontSize: 14,
    color: '#334155',
    fontWeight: '600',
    marginBottom: 12,
  },
  translationButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  translateButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#3b82f6',
    borderRadius: 8,
  },
  translateButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  translatedTextBox: {
    marginTop: 12,
    padding: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e0f2fe',
  },
  translatedLabel: {
    fontSize: 12,
    color: '#64748b',
    marginBottom: 6,
    fontWeight: '500',
  },
  translatedText: {
    fontSize: 16,
    color: '#1e293b',
    lineHeight: 24,
  },
  showOriginalButton: {
    marginTop: 12,
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: '#90D7EF',
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  showOriginalText: {
    fontSize: 14,
    color: '#201E1F',
    fontWeight: '600',
  },
  modalOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  modalContent: {
    backgroundColor: 'rgba(32, 30, 31, 0.95)',
    borderRadius: 20,
    padding: 24,
    width: '80%',
    maxWidth: 300,
    shadowColor: '#90D7EF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 10,
    elevation: 10,
    borderWidth: 2,
    borderColor: 'rgba(144, 215, 239, 0.5)',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#90D7EF',
    marginBottom: 20,
    textAlign: 'center',
  },
  modalButton: {
    backgroundColor: '#90D7EF',
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 12,
    marginBottom: 12,
  },
  modalButtonText: {
    fontSize: 16,
    color: '#201E1F',
    fontWeight: '600',
    textAlign: 'center',
  },
  modalCancelButton: {
    backgroundColor: 'transparent',
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 12,
    marginTop: 8,
    borderWidth: 2,
    borderColor: 'rgba(144, 215, 239, 0.4)',
  },
  modalCancelText: {
    fontSize: 16,
    color: '#90D7EF',
    fontWeight: '500',
    textAlign: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    fontSize: 12,
    color: '#90D7EF',
    fontWeight: '500',
  },
});