import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../shared/authStore';
import AlgorithmEbaySearchBar from './AlgorithmEbaySearchBar';
import { useActionSheet } from '@expo/react-native-action-sheet';

export default function Dashboard() {
  const router = useRouter();
  const { logout } = useAuthStore();
  const { showActionSheetWithOptions } = useActionSheet();

  const handleLogout = () => {
    logout();
    router.replace('/login');
  };

  const handleImageSearchPress = () => {
    const options = ['Take Picture', 'Choose from Library', 'Live Camera Search', 'Cancel'];
    const cancelButtonIndex = 3;
    showActionSheetWithOptions(
      {
        options,
        cancelButtonIndex,
        title: 'Image Search',
      },
      (buttonIndex) => {
        if (buttonIndex === 0) {
          // Take Picture
          router.push({ pathname: '/camera-search', params: { mode: 'camera' } });
        } else if (buttonIndex === 1) {
          // Choose from Library
          router.push({ pathname: '/camera-search', params: { mode: 'library' } });
        } else if (buttonIndex === 2) {
          // Live Camera Search
          router.push('/live-search');
        }
      }
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Restyle Dashboard</Text>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>Logout</Text>
        </TouchableOpacity>
      </View>
      <ScrollView style={styles.content} contentContainerStyle={{ flexGrow: 1 }}>
        <View style={styles.buttonContainer}>
          <TouchableOpacity 
            style={styles.cameraButton} 
            onPress={handleImageSearchPress}
          >
            <Text style={styles.cameraButtonText}>📷 AI Image Search</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.liveButton}
            onPress={() => router.push('/live-search')}
          >
            <Text style={styles.cameraButtonText}>🔴 Live Search (Real-Time)</Text>
          </TouchableOpacity>
        </View>
        <AlgorithmEbaySearchBar />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000', // black background
  },
  header: {
    backgroundColor: '#a259f7', // purple header
    padding: 20,
    paddingTop: 60,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  logoutButton: {
    backgroundColor: 'rgba(162, 89, 247, 0.2)', // semi-transparent purple
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  logoutButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  content: {
    padding: 20,
  },
  buttonContainer: {
    marginBottom: 20,
  },
  cameraButton: {
    backgroundColor: '#8B5CF6',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
  },
  cameraButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  liveButton: {
    backgroundColor: '#F87171',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
  },
}); 