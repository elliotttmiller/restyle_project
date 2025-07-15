import React from 'react';
import { Redirect, Stack } from 'expo-router';
import { useAuthStore } from '../../shared/authStore';
import { View, ActivityIndicator, StyleSheet } from 'react-native';

// This is the gatekeeper for the main part of your app.
export default function AppLayout() {
  const { isAuthenticated, isInitialized } = useAuthStore();

  if (!isInitialized) {
    // While we wait for the auth state to load, show a spinner.
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#a259f7" />
      </View>
    );
  }

  if (!isAuthenticated) {
    // If the user is not authenticated while trying to access this group,
    // redirect them to the login page.
    return <Redirect href="/login" />;
  }
  
  // If the user IS authenticated, allow them to see the screens in this group.
  return <Stack screenOptions={{ headerShown: false }} />;
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#000',
  },
}); 