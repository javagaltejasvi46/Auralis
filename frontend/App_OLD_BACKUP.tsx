import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  FlatList,
  Alert,
  Animated,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Audio } from 'expo-av';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';

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
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const [playingId, setPlayingId] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const [audioLevel, setAudioLevel] = useState(0);

  // Note: React Native doesn't support window.addEventListener
  // Unhandled promise rejections are handled by proper try-catch blocks
  
  // Animation refs for waveform
  const waveAnimations = useRef([
    new Animated.Value(0.3),
    new Animated.Value(0.5),
    new Animated.Value(0.4),
    new Animated.Value(0.6),
    new Animated.Value(0.3),
    new Animated.Value(0.7),
    new Animated.Value(0.4),
  ]).current;

  useEffect(() => {
    // Wrap in async function to handle any promise rejections
    const initializeConnectivity = async () => {
      try {
        await checkBackendConnectivity();
      } catch (error) {
        console.log('Initial connectivity check failed:', error);
        setBackendStatus('disconnected');
      }
    };
    
    initializeConnectivity();
    
    const interval = setInterval(async () => {
      try {
        await checkBackendConnectivity();
      } catch (error) {
        console.log('Periodic connectivity check failed:', error);
        setBackendStatus('disconnected');
      }
    }, 10000);
    
    return () => {
      clearInterval(interval);
      if (sound) {
        sound.unloadAsync().catch(console.error);
      }
    };
  }, [sound]);

  // Simple network test
  const testNetworkConnection = async () => {
    try {
      console.log('Testing network connectivity...');
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
      }, 8000);
      
      const response = await fetch('https://httpbin.org/get', {
        method: 'GET',
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
        },
      });
      
      clearTimeout(timeoutId);
      console.log('Network test successful:', response.status);
      Alert.alert('Network Test', 'Network connectivity is working!');
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.log('Network test failed:', errorMessage);
      Alert.alert('Network Test', 'Network connectivity failed. Check your internet connection.');
      return false;
    }
  };

  // Check backend connectivity
  async function checkBackendConnectivity() {
    try {
      setBackendStatus('checking');
      
      // Try multiple backend URLs
      const urls = ['http://192.168.0.140:8000', 'http://127.0.0.1:8000', 'http://localhost:8000'];
      
      for (const url of urls) {
        try {
          console.log(`Checking connectivity to: ${url}`);
          
          const controller = new AbortController();
          const timeoutId = setTimeout(() => {
            controller.abort();
          }, 5000);
          
          const response = await fetch(url, { 
            method: 'GET',
            signal: controller.signal
          });
          
          clearTimeout(timeoutId);
          console.log(`Connectivity check response: ${response.status}`);
          
          if (response.ok) {
            console.log(`Successfully connected to: ${url}`);
            setBackendStatus('connected');
            return; // Successfully connected, exit the loop
          }
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : String(err);
          console.log(`Connectivity check failed for ${url}:`, errorMessage);
          continue;
        }
      }
      
      // If we get here, none of the URLs worked
      setBackendStatus('disconnected');
    } catch (error) {
      setBackendStatus('disconnected');
    }
  }

  // Start waveform animation
  function startWaveformAnimation() {
    const animations = waveAnimations.map((anim, index) => {
      return Animated.loop(
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
      );
    });

    Animated.stagger(50, animations).start();
  }

  // Stop waveform animation
  function stopWaveformAnimation() {
    waveAnimations.forEach(anim => {
      anim.stopAnimation();
      Animated.timing(anim, {
        toValue: 0.3,
        duration: 200,
        useNativeDriver: false,
      }).start();
    });
  }

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

      const { recording } = await Audio.Recording.createAsync({
        ...Audio.RecordingOptionsPresets.HIGH_QUALITY,
        android: {
          ...Audio.RecordingOptionsPresets.HIGH_QUALITY.android,
          audioEncoder: Audio.AndroidAudioEncoder.AAC,
          sampleRate: 44100,
          numberOfChannels: 2,
          bitRate: 128000,
        },
        ios: {
          ...Audio.RecordingOptionsPresets.HIGH_QUALITY.ios,
          audioQuality: Audio.IOSAudioQuality.HIGH,
          sampleRate: 44100,
          numberOfChannels: 2,
          bitRate: 128000,
          linearPCMBitDepth: 16,
          linearPCMIsBigEndian: false,
          linearPCMIsFloat: false,
        },
      });
      
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

      // Try multiple backend URLs
      const urls = [
        'http://192.168.0.140:8000/upload-audio',
        'http://127.0.0.1:8000/upload-audio',
        'http://localhost:8000/upload-audio'
      ];

      let uploadSuccess = false;
      
      for (const url of urls) {
        try {
          console.log(`Trying to upload to: ${url}`);
          
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 15000);
          
          const response = await fetch(url, {
            method: 'POST',
            body: formData,
            signal: controller.signal,
            // Don't set Content-Type header - let FormData set it automatically with boundary
          });

          clearTimeout(timeoutId);

          console.log(`Response status: ${response.status}`);
          
          if (response.ok) {
            const result = await response.json();
            console.log('Recording uploaded successfully:', result);
            uploadSuccess = true;
            break;
          } else {
            const errorText = await response.text();
            console.log(`Upload failed with status: ${response.status}, error: ${errorText}`);
          }
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : String(err);
          console.log(`Upload to ${url} failed:`, errorMessage);
          if (err instanceof Error && err.name === 'AbortError') {
            console.log('Upload timed out');
          }
          continue;
        }
      }
      
      if (!uploadSuccess) {
        console.error('Failed to upload to any backend URL');
        // Don't show alert - recording is still saved locally
        console.log('Recording saved locally. Backend upload will work after app rebuild.');
      } else {
        console.log('✅ Recording uploaded and saved successfully!');
      }
    } catch (error) {
      console.error('Upload failed:', error);
      Alert.alert('Upload Error', 'An error occurred while uploading');
    }
  }

  async function playSound(uri: string, id: string) {
    try {
      if (sound) {
        await sound.unloadAsync();
      }

      const { sound: newSound } = await Audio.Sound.createAsync({ uri });
      setSound(newSound);
      setPlayingId(id);
      
      await newSound.playAsync();
      
      newSound.setOnPlaybackStatusUpdate((status) => {
        if (status.isLoaded && status.didJustFinish) {
          setPlayingId(null);
        }
      });
      
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (error) {
      console.error('Error playing sound:', error);
    }
  }

  function formatDuration(milliseconds: number) {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }

  function formatTime(date: Date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  const renderRecording = ({ item }: { item: Recording }) => (
    <View style={styles.recordingItem}>
      <View style={styles.recordingInfo}>
        <Text style={styles.recordingTime}>{formatTime(item.timestamp)}</Text>
        <Text style={styles.recordingDuration}>{formatDuration(item.duration)}</Text>
      </View>
      <TouchableOpacity
        style={[styles.playButton, playingId === item.id && styles.playingButton]}
        onPress={() => playSound(item.uri, item.id)}
      >
        <Ionicons
          name={playingId === item.id ? "pause" : "play"}
          size={24}
          color="#fff"
        />
      </TouchableOpacity>
    </View>
  );

  return (
    <LinearGradient
      colors={['#0a0a0a', '#1a1a2e', '#16213e']}
      style={styles.container}
    >
      <StatusBar style="light" />
      
      <View style={styles.header}>
        <Text style={styles.title}>Auralis</Text>
        <Text style={styles.subtitle}>Tap to record, hold for continuous recording</Text>
        
        {/* Backend Status Indicator */}
        <View style={styles.statusContainer}>
          <View style={[
            styles.statusDot, 
            { backgroundColor: 
              backendStatus === 'connected' ? '#4ade80' : 
              backendStatus === 'disconnected' ? '#ef4444' : '#fbbf24' 
            }
          ]} />
          <Text style={styles.statusText}>
            Backend: {backendStatus === 'connected' ? 'Connected ✓' : 
                     backendStatus === 'disconnected' ? 'Upload needs rebuild' : 'Checking...'}
          </Text>
          <TouchableOpacity 
            onPress={checkBackendConnectivity}
            style={styles.refreshButton}
          >
            <Ionicons name="refresh" size={16} color="#a0a0a0" />
          </TouchableOpacity>
          <TouchableOpacity 
            onPress={() => Alert.alert(
              'Upload Info', 
              'Recordings are saved locally. For backend upload, restart Expo with: npx expo start --clear'
            )}
            style={styles.testButton}
          >
            <Text style={styles.testButtonText}>Info</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.recordingSection}>
        <TouchableOpacity
          style={[styles.recordButton, isRecording && styles.recordingActive]}
          onPress={isRecording ? stopRecording : startRecording}
          activeOpacity={0.8}
        >
          <View style={[styles.recordButtonInner, isRecording && styles.recordingInner]}>
            <Ionicons
              name={isRecording ? "stop" : "mic"}
              size={48}
              color="#fff"
            />
          </View>
        </TouchableOpacity>
        
        {isRecording && (
          <View style={styles.recordingIndicator}>
            <View style={styles.recordingDot} />
            <Text style={styles.recordingText}>Recording...</Text>
          </View>
        )}

        {/* Waveform Animation */}
        {isRecording && (
          <View style={styles.waveformContainer}>
            {waveAnimations.map((anim, index) => (
              <Animated.View
                key={index}
                style={[
                  styles.waveBar,
                  {
                    height: anim.interpolate({
                      inputRange: [0, 1],
                      outputRange: [4, 40],
                    }),
                    backgroundColor: '#ff4757',
                  }
                ]}
              />
            ))}
          </View>
        )}
      </View>

      <View style={styles.recordingsSection}>
        <Text style={styles.sectionTitle}>Recent Recordings</Text>
        {recordings.length === 0 ? (
          <Text style={styles.emptyText}>No recordings yet</Text>
        ) : (
          <FlatList
            data={recordings}
            renderItem={renderRecording}
            keyExtractor={(item) => item.id}
            showsVerticalScrollIndicator={false}
            style={styles.recordingsList}
          />
        )}
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 60,
    paddingHorizontal: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#a0a0a0',
    textAlign: 'center',
  },
  recordingSection: {
    alignItems: 'center',
    marginBottom: 50,
  },
  recordButton: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 3,
    borderColor: '#ff4757',
    shadowColor: '#ff4757',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 10,
  },
  recordingActive: {
    backgroundColor: 'rgba(255, 71, 87, 0.2)',
    borderColor: '#ff3742',
    shadowOpacity: 0.6,
  },
  recordButtonInner: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#ff4757',
    justifyContent: 'center',
    alignItems: 'center',
  },
  recordingInner: {
    backgroundColor: '#ff3742',
  },
  recordingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 20,
  },
  recordingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#ff4757',
    marginRight: 8,
  },
  recordingText: {
    color: '#ff4757',
    fontSize: 16,
    fontWeight: '600',
  },
  recordingsSection: {
    flex: 1,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 20,
  },
  emptyText: {
    color: '#a0a0a0',
    fontSize: 16,
    textAlign: 'center',
    marginTop: 40,
  },
  recordingsList: {
    flex: 1,
  },
  recordingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  recordingInfo: {
    flex: 1,
  },
  recordingTime: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  recordingDuration: {
    color: '#a0a0a0',
    fontSize: 14,
  },
  playButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#4834d4',
    justifyContent: 'center',
    alignItems: 'center',
  },
  playingButton: {
    backgroundColor: '#ff4757',
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    color: '#a0a0a0',
    fontSize: 12,
    fontWeight: '500',
  },
  waveformContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 20,
    height: 50,
  },
  waveBar: {
    width: 3,
    marginHorizontal: 2,
    borderRadius: 2,
    minHeight: 4,
  },
  refreshButton: {
    marginLeft: 8,
    padding: 4,
  },
  testButton: {
    marginLeft: 8,
    paddingHorizontal: 8,
    paddingVertical: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 4,
  },
  testButtonText: {
    color: '#a0a0a0',
    fontSize: 10,
  },
});