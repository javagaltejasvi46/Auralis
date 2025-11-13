import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  FlatList,
  Alert,
  Animated,
  ScrollView,
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
  const [lastCheckTime, setLastCheckTime] = useState<Date>(new Date());

  // Animation refs for enhanced waveform (50 bars like web version)
  const waveAnimations = useRef(
    Array(50).fill(0).map(() => new Animated.Value(Math.random() * 0.2 + 0.1))
  ).current;

  // Logo pulse animation
  const logoPulse = useRef(new Animated.Value(1)).current;

  useEffect(() => {
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
    
    return () => {
      clearInterval(interval);
      if (sound) {
        sound.unloadAsync().catch(console.error);
      }
    };
  }, [sound]);
