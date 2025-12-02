import React, { useState, useEffect } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  TouchableOpacity, 
  FlatList, 
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, CARD_GLOW_STYLE } from '../config';
import { patientAPI } from '../services/api';
import { Patient } from '../types';
import { useFocusEffect } from '@react-navigation/native';

export default function PatientListScreen({ navigation }: any) {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Fetch patients when screen comes into focus
  useFocusEffect(
    React.useCallback(() => {
      fetchPatients();
    }, [])
  );

  const fetchPatients = async () => {
    try {
      const { patients: fetchedPatients } = await patientAPI.getAll(true);
      setPatients(fetchedPatients);
    } catch (error) {
      console.error('Fetch patients error:', error);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    fetchPatients();
  };

  const renderPatientCard = ({ item }: { item: Patient }) => (
    <TouchableOpacity 
      style={styles.patientCard}
      onPress={() => navigation.navigate('PatientProfile', { patientId: item.id })}
    >
      <View style={styles.patientIconContainer}>
        <Ionicons name="person" size={28} color={COLORS.raisinBlack} />
      </View>
      <View style={styles.patientInfo}>
        <View style={styles.patientNameRow}>
          <Text style={styles.patientName}>{item.full_name}</Text>
          <Text style={styles.patientId}>ID: {item.patient_id}</Text>
        </View>
        {item.phone && (
          <Text style={styles.patientDetail}>
            <Ionicons name="call" size={12} /> {item.phone}
          </Text>
        )}
      </View>
      <Ionicons name="chevron-forward" size={24} color={COLORS.paleAzure} />
    </TouchableOpacity>
  );

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
        <Text style={styles.title}>Patient List</Text>
        <TouchableOpacity 
          onPress={() => navigation.navigate('CreatePatient')} 
          style={styles.addButton}
        >
          <Ionicons name="add" size={24} color={COLORS.paleAzure} />
        </TouchableOpacity>
      </View>

      {isLoading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={COLORS.paleAzure} />
        </View>
      ) : patients.length === 0 ? (
        <View style={styles.content}>
          <Ionicons name="people-outline" size={80} color={COLORS.paleAzure} />
          <Text style={styles.emptyText}>No patients yet</Text>
          <Text style={styles.emptySubtext}>Create your first patient to get started</Text>
          
          <TouchableOpacity
            style={styles.createButton}
            onPress={() => navigation.navigate('CreatePatient')}
          >
            <Ionicons name="add" size={24} color={COLORS.raisinBlack} />
            <Text style={styles.createButtonText}>Create Patient</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={patients}
          renderItem={renderPatientCard}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl
              refreshing={isRefreshing}
              onRefresh={handleRefresh}
              tintColor={COLORS.paleAzure}
            />
          }
        />
      )}
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
    borderWidth: 1,
    borderColor: COLORS.borderColor,
    ...CARD_GLOW_STYLE,
  },
  addButton: {
    padding: 10,
    backgroundColor: COLORS.cardBackground,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.borderColor,
    ...CARD_GLOW_STYLE,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.paleAzure,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyText: {
    fontSize: 20,
    fontWeight: '600',
    color: COLORS.paleAzure,
    marginTop: 20,
  },
  emptySubtext: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginTop: 8,
    textAlign: 'center',
  },
  createButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.buttonBackground,
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
    marginTop: 30,
    ...CARD_GLOW_STYLE,
  },
  createButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.buttonText,
    marginLeft: 8,
  },
  listContent: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  patientCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.cardBackground,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.borderColor,
    ...CARD_GLOW_STYLE,
  },
  patientIconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: COLORS.buttonBackground,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  patientInfo: {
    flex: 1,
  },
  patientNameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  patientName: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.paleAzure,
  },
  patientId: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginLeft: 10,
  },
  patientDetail: {
    fontSize: 12,
    color: COLORS.textSecondary,
    marginTop: 2,
  },
});
