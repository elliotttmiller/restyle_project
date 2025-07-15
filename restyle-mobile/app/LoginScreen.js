import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../shared/authStore';
import api from '../shared/api';

export default function LoginScreen() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const setTokens = useAuthStore((state) => state.setTokens);
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  const isInitialized = useAuthStore(state => state.isInitialized);

  useEffect(() => {
    if (isInitialized && isAuthenticated) {
      router.replace('/dashboard');
    }
  }, [isInitialized, isAuthenticated, router]);

  const handleLogin = async () => {
    console.log('LoginScreen: handleLogin called');
    if (!username || !password) {
      Alert.alert('Error', 'Please enter both username and password');
      return;
    }

    setLoading(true);
    console.log('LoginScreen: setLoading(true)');
    try {
      console.log('Attempting login to:', api.defaults.baseURL);
      const response = await api.post('/token/', { username, password });
      console.log('Login successful:', response.data);
      
      // Store both access and refresh tokens
      setTokens(response.data.access, response.data.refresh);
      
      // Debug: print the tokens after storing
      console.log('Stored tokens in auth store:', {
        token: useAuthStore.getState().token,
        refreshToken: useAuthStore.getState().refreshToken
      });
      
      router.replace('/dashboard');
      console.log('LoginScreen: navigation to /dashboard called');
    } catch (error) {
      console.error('Login error:', error);
      if (error.response) {
        console.error('Error response:', error.response.data);
        Alert.alert('Login Failed', error.response.data?.detail || 'Invalid credentials');
      } else if (error.request) {
        console.error('Network error:', error.request);
        Alert.alert('Connection Error', 'Unable to connect to server. Please check your network connection.');
      } else {
        Alert.alert('Login Failed', 'An unexpected error occurred');
      }
    } finally {
      setLoading(false);
      console.log('LoginScreen: setLoading(false)');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Login to Restyle</Text>
      <TextInput
        style={styles.input}
        placeholder="Username"
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
        editable={!loading}
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        editable={!loading}
      />
      <TouchableOpacity 
        style={[styles.button, loading && styles.buttonDisabled]} 
        onPress={handleLogin}
        disabled={loading}
      >
        <Text style={styles.buttonText}>
          {loading ? 'Logging in...' : 'Login'}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#000', // black background
    padding: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: '600',
    marginBottom: 32,
    color: '#a259f7', // purple title
  },
  input: {
    width: '100%',
    maxWidth: 320,
    height: 48,
    borderColor: '#a259f7', // purple border
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 16,
    marginBottom: 16,
    fontSize: 16,
    backgroundColor: '#222', // dark input background
    color: '#fff', // white text
  },
  button: {
    backgroundColor: '#a259f7', // purple button
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 32,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonDisabled: {
    backgroundColor: '#444', // dark disabled
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '500',
  },
}); 