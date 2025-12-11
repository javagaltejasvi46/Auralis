/**
 * Connection Status Component
 * Shows the current connection status and allows manual server configuration
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Modal,
  TextInput,
  Alert,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';
import { COLORS } from '../config';
import ConnectionManager from '../services/ConnectionManager';

interface ConnectionStatusProps {
  showDetails?: boolean;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ showDetails = false }) => {
  const [connectionState, setConnectionState] = useState(ConnectionManager.getInstance().getConnectionState());
  const [showModal, setShowModal] = useState(false);
  const [manualIP, setManualIP] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const [isDiscovering, setIsDiscovering] = useState(false);

  const connectionManager = ConnectionManager.getInstance();

  useEffect(() => {
    // Listen for connection state changes
    const handleStateChange = (state: any) => {
      setConnectionState(state);
    };

    connectionManager.addListener(handleStateChange);

    // Initialize connection if not connected
    if (!connectionState.isConnected) {
      initializeConnection();
    }

    return () => {
      connectionManager.removeListener(handleStateChange);
    };
  }, []);

  const initializeConnection = async () => {
    setIsConnecting(true);
    try {
      await connectionManager.initialize();
    } catch (error) {
      console.log('Connection initialization failed:', error);
    } finally {
      setIsConnecting(false);
    }
  };

  const handleManualConnect = async () => {
    if (!manualIP.trim()) {
      Alert.alert('Error', 'Please enter a valid IP address');
      return;
    }

    setIsConnecting(true);
    try {
      const success = await connectionManager.setServerIP(manualIP.trim());
      if (success) {
        setShowModal(false);
        setManualIP('');
        Alert.alert('Success', 'Connected to server successfully!');
      } else {
        Alert.alert('Error', 'Could not connect to the specified server');
      }
    } catch (error) {
      Alert.alert('Error', 'Connection failed');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleAutoDiscover = async () => {
    setIsDiscovering(true);
    try {
      const success = await connectionManager.retry();
      if (success) {
        Alert.alert('Success', 'Server discovered and connected!');
      } else {
        Alert.alert('No Server Found', 'Could not find any Auralis server on the network. Please ensure the backend is running and try manual connection.');
      }
    } catch (error) {
      Alert.alert('Error', 'Auto-discovery failed');
    } finally {
      setIsDiscovering(false);
    }
  };

  const getStatusColor = () => {
    if (isConnecting || isDiscovering) return COLORS.warning;
    return connectionState.isConnected ? COLORS.success : COLORS.error;
  };

  const getStatusText = () => {
    if (isConnecting) return 'Connecting...';
    if (isDiscovering) return 'Discovering...';
    if (connectionState.isConnected) {
      return showDetails ? `Connected to ${connectionState.serverIP}` : 'Connected';
    }
    return 'Disconnected';
  };

  if (!showDetails && connectionState.isConnected) {
    // Simple status indicator when connected
    return (
      <View style={styles.simpleStatus}>
        <View style={[styles.statusDot, { backgroundColor: getStatusColor() }]} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={[styles.statusButton, { borderColor: getStatusColor() }]}
        onPress={() => setShowModal(true)}
      >
        <View style={[styles.statusDot, { backgroundColor: getStatusColor() }]} />
        <Text style={[styles.statusText, { color: getStatusColor() }]}>
          {getStatusText()}
        </Text>
        {(isConnecting || isDiscovering) && (
          <ActivityIndicator size="small" color={getStatusColor()} style={styles.spinner} />
        )}
      </TouchableOpacity>

      <Modal
        visible={showModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Server Connection</Text>
            
            <View style={styles.statusInfo}>
              <Text style={styles.infoLabel}>Status:</Text>
              <Text style={[styles.infoValue, { color: getStatusColor() }]}>
                {getStatusText()}
              </Text>
            </View>

            {connectionState.serverIP && (
              <View style={styles.statusInfo}>
                <Text style={styles.infoLabel}>Server IP:</Text>
                <Text style={styles.infoValue}>{connectionState.serverIP}</Text>
              </View>
            )}

            {connectionState.error && (
              <View style={styles.statusInfo}>
                <Text style={styles.infoLabel}>Error:</Text>
                <Text style={[styles.infoValue, { color: COLORS.error }]}>
                  {connectionState.error}
                </Text>
              </View>
            )}

            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Quick Connection</Text>
              <TouchableOpacity
                style={[styles.button, styles.primaryButton]}
                onPress={handleAutoDiscover}
                disabled={isDiscovering || isConnecting}
              >
                {isDiscovering ? (
                  <ActivityIndicator size="small" color="white" />
                ) : (
                  <Text style={styles.buttonText}>Quick Discovery (5s)</Text>
                )}
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[styles.button, styles.qrButton]}
                onPress={() => Alert.alert('QR Code', 'QR code scanning will be available in the next update. For now, use manual connection with the IP shown on your computer screen.')}
                disabled={isConnecting}
              >
                <Text style={styles.buttonText}>📱 Scan QR Code</Text>
              </TouchableOpacity>
            </View>

            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Manual Connection</Text>
              <TextInput
                style={styles.input}
                placeholder="Enter server IP (e.g., 192.168.1.100)"
                placeholderTextColor={COLORS.textSecondary}
                value={manualIP}
                onChangeText={setManualIP}
                autoCapitalize="none"
                autoCorrect={false}
              />
              <TouchableOpacity
                style={[styles.button, styles.secondaryButton]}
                onPress={handleManualConnect}
                disabled={isConnecting || isDiscovering}
              >
                {isConnecting ? (
                  <ActivityIndicator size="small" color={COLORS.textPrimary} />
                ) : (
                  <Text style={[styles.buttonText, { color: COLORS.textPrimary }]}>
                    Connect Manually
                  </Text>
                )}
              </TouchableOpacity>
            </View>

            <TouchableOpacity
              style={[styles.button, styles.closeButton]}
              onPress={() => setShowModal(false)}
            >
              <Text style={styles.buttonText}>Close</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
  },
  simpleStatus: {
    padding: 4,
  },
  statusButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '500',
  },
  spinner: {
    marginLeft: 6,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: COLORS.parchment,
    borderRadius: 16,
    padding: 24,
    width: '90%',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.darkTeal,
    textAlign: 'center',
    marginBottom: 20,
  },
  statusInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  infoLabel: {
    fontSize: 14,
    color: COLORS.textSecondary,
    fontWeight: '500',
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '600',
    flex: 1,
    textAlign: 'right',
  },
  section: {
    marginTop: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.darkTeal,
    marginBottom: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: COLORS.borderColor,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    color: COLORS.textPrimary,
    backgroundColor: 'white',
    marginBottom: 12,
  },
  button: {
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 44,
  },
  primaryButton: {
    backgroundColor: COLORS.success,
    marginBottom: 8,
  },
  qrButton: {
    backgroundColor: COLORS.darkTeal,
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: COLORS.coolSteel,
  },
  closeButton: {
    backgroundColor: COLORS.coolSteel,
    marginTop: 20,
  },
  buttonText: {
    fontSize: 14,
    fontWeight: '600',
    color: 'white',
  },
});

export default ConnectionStatus;