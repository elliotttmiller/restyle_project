import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator, ScrollView } from 'react-native';
import { useAuthStore } from '../../shared/authStore'; 
import api from '../../shared/api';
import config from '../../config.js';

export default function LoginScreen() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [debugInfo, setDebugInfo] = useState('');
  const setTokens = useAuthStore((state) => state.setTokens);

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('Error', 'Please enter both username and password');
      return;
    }
    
    setLoading(true);
    setDebugInfo('Starting login process...');
    
    try {
      console.log('🔐 Login attempt:', { username, apiUrl: config.API_BASE_URL });
      setDebugInfo(`Attempting login to: ${config.API_BASE_URL}`);
      
      const response = await api.post('/api/token/', { username, password });
      
      console.log('✅ Login successful:', response.data);
      setDebugInfo('Login successful! Setting tokens...');
      
      setTokens(response.data.access, response.data.refresh);
      setDebugInfo('Tokens set successfully!');
      
      // No navigation here! Root layout will handle redirect.
    } catch (error) {
      console.error('❌ Login error:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      console.error('Error message:', error.message);
      
      let errorMessage = 'Login failed. Please try again.';
      let debugMessage = `Error: ${error.message}`;
      
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
        debugMessage += `\nDetail: ${error.response.data.detail}`;
      }
      
      if (error.response?.status) {
        debugMessage += `\nStatus: ${error.response.status}`;
      }
      
      if (error.code === 'NETWORK_ERROR') {
        errorMessage = 'Network error. Please check your internet connection.';
        debugMessage += '\nNetwork error detected';
      }
      
      setDebugInfo(debugMessage);
      Alert.alert('Login Failed', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async () => {
    setDebugInfo('Testing connection...');
    try {
      const response = await api.get('/health');
      setDebugInfo(`Connection test successful: ${response.status}`);
      console.log('Connection test response:', response.data);
    } catch (error) {
      setDebugInfo(`Connection test failed: ${error.message}`);
      console.error('Connection test error:', error);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Restyle AI</Text>
      
      <Text style={styles.subtitle}>Login to your account</Text>
      
      <TextInput
        style={styles.input}
        placeholder="Username"
        placeholderTextColor="#888"
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
        editable={!loading}
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        placeholderTextColor="#888"
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
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Login</Text>
        )}
      </TouchableOpacity>
      
      <TouchableOpacity 
        style={styles.testButton} 
        onPress={testConnection}
        disabled={loading}
      >
        <Text style={styles.testButtonText}>Test Connection</Text>
      </TouchableOpacity>
      
      {debugInfo ? (
        <View style={styles.debugContainer}>
          <Text style={styles.debugTitle}>Debug Info:</Text>
          <Text style={styles.debugText}>{debugInfo}</Text>
          <Text style={styles.debugText}>API URL: {config.API_BASE_URL}</Text>
        </View>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { 
    flexGrow: 1, 
    justifyContent: 'center', 
    alignItems: 'center', 
    backgroundColor: '#000', 
    padding: 24, 
  },
  title: { 
    fontSize: 42, 
    fontWeight: 'bold', 
    marginBottom: 10, 
    color: '#a259f7', 
  },
  subtitle: {
    fontSize: 16,
    color: '#888',
    marginBottom: 30,
  },
  input: { 
    width: '100%', 
    maxWidth: 340, 
    height: 50, 
    borderColor: '#333', 
    borderWidth: 1, 
    borderRadius: 12, 
    paddingHorizontal: 16, 
    marginBottom: 16, 
    fontSize: 16, 
    backgroundColor: '#1a1a1a', 
    color: '#fff', 
  },
  button: { 
    width: '100%', 
    maxWidth: 340, 
    backgroundColor: '#a259f7', 
    borderRadius: 12, 
    paddingVertical: 14, 
    alignItems: 'center', 
    marginTop: 16, 
  },
  buttonDisabled: { 
    backgroundColor: '#555', 
  },
  buttonText: { 
    color: '#fff', 
    fontSize: 18, 
    fontWeight: '600', 
  },
  testButton: {
    width: '100%',
    maxWidth: 340,
    backgroundColor: '#333',
    borderRadius: 12,
    paddingVertical: 10,
    alignItems: 'center',
    marginTop: 10,
  },
  testButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  debugContainer: {
    width: '100%',
    maxWidth: 340,
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 16,
    marginTop: 20,
    borderColor: '#333',
    borderWidth: 1,
  },
  debugTitle: {
    color: '#a259f7',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  debugText: {
    color: '#ccc',
    fontSize: 12,
    marginBottom: 4,
  },
}); 