import React, { useState, useEffect, useRef } from "react";
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
  Alert,
  Animated,
  TextInput,
  ActivityIndicator,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { Audio } from "expo-av";
import * as Haptics from "expo-haptics";
import { COLORS, WS_BASE_URL } from "../config";
import { sessionAPI } from "../services/api";

export default function SessionRecordingScreen({ route, navigation }: any) {
  const { sessionId, patientName } = route.params;

  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState("");
  const [partialTranscript, setPartialTranscript] = useState("");
  const [wsStatus, setWsStatus] = useState<string>("Not connected");
  const [isSaving, setIsSaving] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const waveAnimations = useRef(
    Array(50)
      .fill(0)
      .map(() => new Animated.Value(Math.random() * 0.3 + 0.1))
  ).current;
  const recordTransition = useRef(new Animated.Value(0)).current;
  const buttonScale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    console.log("🔌 Connecting WebSocket for transcription...");
    const ws = new WebSocket(WS_BASE_URL);

    ws.onopen = () => {
      console.log("✅ WebSocket connected - Multilingual mode");
      setWsStatus("Connected");
      wsRef.current = ws;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === "processing") {
          setIsTranscribing(true);
        } else if (data.type === "partial") {
          setPartialTranscript(data.text);
          setIsTranscribing(true);
        } else if (data.type === "final") {
          setTranscription((prev) => prev + (prev ? " " : "") + data.text);
          setPartialTranscript("");
          setIsTranscribing(false);
        } else if (data.type === "error") {
          setIsTranscribing(false);
          Alert.alert("Transcription Error", data.message);
        }
      } catch (err) {
        console.log("❌ Error parsing message:", err);
        setIsTranscribing(false);
      }
    };

    ws.onerror = (error) => {
      console.log("❌ WebSocket error:", error);
      setWsStatus("Error");
    };

    ws.onclose = () => {
      console.log("🔌 WebSocket closed");
      setWsStatus("Disconnected");
      wsRef.current = null;
    };

    return ws;
  };

  const startWaveformAnimation = () => {
    waveAnimations.forEach((anim) => {
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

  const stopWaveformAnimation = () => {
    waveAnimations.forEach((anim) => {
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

      if (permission.status !== "granted") {
        Alert.alert(
          "Permission required",
          "Please grant microphone permission"
        );
        return;
      }

      connectWebSocket();

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );

      setRecording(recording);
      setIsRecording(true);

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
      console.error("❌ Failed to start recording:", err);
      Alert.alert("Error", "Failed to start recording");
    }
  }

  async function stopRecording() {
    if (!recording) return;

    setIsRecording(false);

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

    await recording.stopAndUnloadAsync();
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: false,
    });

    const uri = recording.getURI();
    const status = await recording.getStatusAsync();

    setRecording(null);

    if (uri) {
      // Send audio to WebSocket for transcription
      const response = await fetch(uri);
      const blob = await response.blob();

      const reader = new FileReader();
      reader.readAsDataURL(blob);

      reader.onloadend = () => {
        const base64data = reader.result as string;

        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          setIsTranscribing(true);
          wsRef.current.send(
            JSON.stringify({
              type: "audio_file",
              data: base64data,
              format: "m4a",
            })
          );
        }
      };

      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    }
  }

  const handleSaveSession = async () => {
    if (!transcription) {
      Alert.alert("No Transcription", "Please record audio first");
      return;
    }

    setIsSaving(true);
    try {
      await sessionAPI.update(sessionId, {
        original_transcription: transcription,
        language: "multilingual",
        is_completed: true,
      });

      Alert.alert("Success", "Session saved successfully", [
        {
          text: "OK",
          onPress: () => navigation.navigate("PatientList"),
        },
      ]);
    } catch (error: any) {
      Alert.alert("Error", "Failed to save session");
    } finally {
      setIsSaving(false);
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
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
        >
          <Ionicons name="arrow-back" size={24} color={COLORS.paleAzure} />
        </TouchableOpacity>
        <View style={styles.headerInfo}>
          <Text style={styles.headerTitle}>Recording Session</Text>
          <Text style={styles.headerSubtitle}>{patientName}</Text>
        </View>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Multilingual Mode Info */}
        <View style={styles.multilingualInfo}>
          <Ionicons name="globe-outline" size={20} color={COLORS.textPrimary} />
          <Text style={styles.multilingualText}>
            Multilingual Mode - Automatic Language Detection
          </Text>
        </View>

        {/* Recording Button / Waveform */}
        <View style={styles.recordingSection}>
          <Animated.View style={{ transform: [{ scale: buttonScale }] }}>
            {!isRecording ? (
              <Animated.View
                style={{
                  opacity: recordTransition.interpolate({
                    inputRange: [0, 1],
                    outputRange: [1, 0],
                  }),
                }}
              >
                <TouchableOpacity
                  style={styles.micButton}
                  onPress={startRecording}
                >
                  <LinearGradient
                    colors={[COLORS.buttonBackground, COLORS.coolSteel]}
                    style={styles.micButtonGradient}
                  >
                    <Ionicons name="mic" size={40} color={COLORS.parchment} />
                  </LinearGradient>
                </TouchableOpacity>
                <Text style={styles.micButtonLabel}>Start Recording</Text>
              </Animated.View>
            ) : (
              <Animated.View
                style={{
                  opacity: recordTransition.interpolate({
                    inputRange: [0, 1],
                    outputRange: [0, 1],
                  }),
                }}
              >
                <View style={styles.waveformContainer}>
                  <View style={styles.waveform}>
                    {waveAnimations.map((anim, index) => {
                      const angle =
                        (index / waveAnimations.length) * 2 * Math.PI;
                      const radius = 60;
                      return (
                        <Animated.View
                          key={index}
                          style={[
                            styles.waveBar,
                            {
                              height: anim.interpolate({
                                inputRange: [0, 1],
                                outputRange: [15, 45],
                              }),
                              transform: [
                                { translateX: Math.cos(angle) * radius },
                                { translateY: Math.sin(angle) * radius },
                                {
                                  rotate: `${(angle * 180) / Math.PI + 90}deg`,
                                },
                              ],
                            },
                          ]}
                        />
                      );
                    })}
                  </View>
                  <View style={styles.centerMicIcon}>
                    <Ionicons name="mic" size={32} color={COLORS.saffron} />
                  </View>
                </View>

                <TouchableOpacity
                  style={styles.stopButton}
                  onPress={stopRecording}
                >
                  <Text style={styles.stopButtonText}>Stop Recording</Text>
                </TouchableOpacity>
              </Animated.View>
            )}
          </Animated.View>
        </View>

        {/* Transcription Box */}
        {(transcription || partialTranscript) && (
          <View style={styles.transcriptionBox}>
            <View style={styles.transcriptionHeader}>
              <Text style={styles.transcriptionLabel}>Transcription</Text>
              <TouchableOpacity
                onPress={() => {
                  setTranscription("");
                  setPartialTranscript("");
                }}
              >
                <Text style={styles.clearButton}>Clear</Text>
              </TouchableOpacity>
            </View>

            <TextInput
              style={styles.transcriptionText}
              value={
                transcription +
                (partialTranscript ? " " + partialTranscript : "")
              }
              onChangeText={setTranscription}
              multiline
              textAlignVertical="top"
            />

            {partialTranscript && (
              <Text style={styles.partialLabel}>⏳ Processing...</Text>
            )}
          </View>
        )}

        {/* Save Button */}
        {transcription && (
          <TouchableOpacity
            style={[styles.saveButton, isSaving && styles.saveButtonDisabled]}
            onPress={handleSaveSession}
            disabled={isSaving}
          >
            {isSaving ? (
              <ActivityIndicator color={COLORS.raisinBlack} />
            ) : (
              <>
                <Ionicons
                  name="checkmark-circle"
                  size={24}
                  color={COLORS.raisinBlack}
                />
                <Text style={styles.saveButtonText}>Save Session</Text>
              </>
            )}
          </TouchableOpacity>
        )}

        {/* Status */}
        <View style={styles.statusBar}>
          <View
            style={[
              styles.statusDot,
              {
                backgroundColor:
                  wsStatus === "Connected"
                    ? COLORS.success
                    : wsStatus === "Disconnected"
                    ? "#94a3b8"
                    : COLORS.error,
              },
            ]}
          />
          <Text style={styles.statusText}>WebSocket: {wsStatus}</Text>
        </View>
      </ScrollView>

      {/* Transcription Loading Overlay */}
      {isTranscribing && (
        <View style={styles.loadingOverlay}>
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={COLORS.buttonBackground} />
            <Text style={styles.loadingText}>Transcribing audio...</Text>
            <Text style={styles.loadingSubtext}>
              Processing with Faster-Whisper AI
            </Text>
          </View>
        </View>
      )}
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
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
    alignItems: "center",
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: COLORS.textPrimary,
  },
  headerSubtitle: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginTop: 2,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  multilingualInfo: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 24,
    paddingHorizontal: 20,
    paddingVertical: 12,
    backgroundColor: COLORS.cardBackground,
    borderRadius: 20,
    borderWidth: 2,
    borderColor: COLORS.borderColor,
    gap: 10,
  },
  multilingualText: {
    fontSize: 14,
    color: COLORS.textOnDarkTeal,
    fontWeight: "500",
  },
  recordingSection: {
    alignItems: "center",
    marginBottom: 30,
  },
  micButton: {
    width: 96,
    height: 96,
    borderRadius: 48,
    marginBottom: 12,
    shadowColor: COLORS.paleAzure,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.6,
    shadowRadius: 12,
    elevation: 8,
  },
  micButtonGradient: {
    width: "100%",
    height: "100%",
    borderRadius: 48,
    justifyContent: "center",
    alignItems: "center",
  },
  micButtonLabel: {
    fontSize: 16,
    color: COLORS.textPrimary,
    fontWeight: "500",
  },
  waveformContainer: {
    width: 200,
    height: 200,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 20,
  },
  waveform: {
    width: 200,
    height: 200,
    borderRadius: 100,
    justifyContent: "center",
    alignItems: "center",
  },
  waveBar: {
    position: "absolute",
    width: 4,
    backgroundColor: COLORS.darkTeal,
    borderRadius: 2,
    opacity: 0.9,
  },
  centerMicIcon: {
    position: "absolute",
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: "rgba(17, 56, 69, 0.7)",
    justifyContent: "center",
    alignItems: "center",
  },
  stopButton: {
    paddingHorizontal: 40,
    paddingVertical: 14,
    backgroundColor: COLORS.error,
    borderRadius: 25,
    shadowColor: COLORS.error,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 6,
  },
  stopButtonText: {
    fontSize: 18,
    fontWeight: "600",
    color: "#fff",
    letterSpacing: 1,
  },
  transcriptionBox: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    borderWidth: 2,
    borderColor: COLORS.borderColor,
  },
  transcriptionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  transcriptionLabel: {
    fontSize: 16,
    fontWeight: "600",
    color: COLORS.textOnDarkTeal,
  },
  clearButton: {
    fontSize: 14,
    color: COLORS.error,
    fontWeight: "500",
  },
  transcriptionText: {
    fontSize: 16,
    color: COLORS.textOnDarkTeal,
    minHeight: 100,
    maxHeight: 200,
    textAlignVertical: "top",
  },
  partialLabel: {
    fontSize: 12,
    color: COLORS.coolSteel,
    fontStyle: "italic",
    marginTop: 8,
  },
  saveButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: COLORS.success,
    paddingVertical: 16,
    borderRadius: 16,
    marginBottom: 20,
    gap: 12,
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    fontSize: 18,
    fontWeight: "600",
    color: COLORS.textOnDarkTeal,
  },
  statusBar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: COLORS.cardBackground,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: COLORS.borderColor,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    fontSize: 12,
    color: COLORS.textPrimary,
    fontWeight: "500",
  },
  loadingOverlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0, 0, 0, 0.7)",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 1000,
  },
  loadingContainer: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 20,
    padding: 40,
    alignItems: "center",
    borderWidth: 2,
    borderColor: COLORS.borderColor,
    minWidth: 280,
  },
  loadingText: {
    fontSize: 18,
    fontWeight: "600",
    color: COLORS.textOnDarkTeal,
    marginTop: 20,
    marginBottom: 8,
  },
  loadingSubtext: {
    fontSize: 14,
    color: COLORS.textSecondary,
    textAlign: "center",
  },
});
