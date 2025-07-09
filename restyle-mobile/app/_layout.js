import { Stack } from 'expo-router';
import { useAuthStore } from '../shared/authStore';
import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'expo-router';
import { View, Text, StyleSheet } from 'react-native';

export default function RootLayout() {
  const router = useRouter();
  const pathname = usePathname();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    console.log('RootLayout useEffect: starting navigation effect');
    // Add a small delay to ensure the store is initialized
    const timer = setTimeout(() => {
      try {
        if (isAuthenticated) {
          // Only redirect to dashboard if currently on login
          if (pathname === '/login') {
            console.log('RootLayout useEffect: user authenticated, navigating to /dashboard');
            router.replace('/dashboard');
          } else {
            console.log('RootLayout useEffect: already authenticated and not on login, not navigating');
          }
        } else {
          // Only redirect to login if not already on login or item-detail
          if (pathname !== '/login' && pathname !== '/item-detail') {
            console.log('RootLayout useEffect: user not authenticated, navigating to /login');
            router.replace('/login');
          } else {
            console.log('RootLayout useEffect: already on /login or /item-detail, not navigating');
          }
        }
      } catch (error) {
        console.error('Navigation error:', error);
        // Fallback to login if there's an error and not on /login or /item-detail
        if (pathname !== '/login' && pathname !== '/item-detail') {
          router.replace('/login');
          console.log('RootLayout useEffect: fallback navigation to /login called');
        }
      } finally {
        setIsLoading(false);
        console.log('RootLayout useEffect: setIsLoading(false) called');
      }
    }, 1000);
  
    return () => clearTimeout(timer);
  }, [isAuthenticated, pathname]); // Re-run when auth or path changes

  // Show loading screen while checking auth
  if (isLoading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return (
    <Stack>
      <Stack.Screen 
        name="index" 
        options={{ 
          headerShown: false,
          gestureEnabled: false 
        }} 
      />
      <Stack.Screen 
        name="login" 
        options={{ 
          headerShown: false,
          gestureEnabled: false 
        }} 
      />
      <Stack.Screen 
        name="dashboard" 
        options={{ 
          headerShown: false,
          gestureEnabled: false 
        }} 
      />
      <Stack.Screen 
        name="test-connection" 
        options={{ 
          title: "Test Connection",
          headerShown: true 
        }} 
      />
    </Stack>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000', // black background
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    fontSize: 18,
    color: '#a259f7', // purple text
  },
}); 