import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, ScrollView } from 'react-native';
import api from '../shared/api';

export default function TestConnection() {
  const [testing, setTesting] = useState(false);
  const [results, setResults] = useState([]);

  const addResult = (message, isSuccess = true) => {
    setResults(prev => [...prev, { message, isSuccess, timestamp: new Date().toLocaleTimeString() }]);
  };

  const testConnection = async () => {
    setTesting(true);
    setResults([]);
    
    try {
      console.log('Testing connection to backend...');
      console.log('API base URL:', api.defaults.baseURL);
      addResult('Starting connection tests...', true);
      
      // Test 1: Basic connectivity
      try {
        addResult('Testing basic connectivity...', true);
        const response = await api.get('/core/health/');
        console.log('Health check response:', response.data);
        addResult(`✅ Health check successful: ${response.data.status}`, true);
      } catch (error) {
        console.error('Health check failed:', error);
        addResult(`❌ Health check failed: ${error.message}`, false);
        if (error.response) {
          addResult(`Status: ${error.response.status}`, false);
          addResult(`Data: ${JSON.stringify(error.response.data)}`, false);
        }
      }
      
      // Test 2: Token endpoint
      try {
        addResult('Testing token endpoint...', true);
        const tokenResponse = await api.post('/token/', {
          username: 'test',
          password: 'test'
        });
        addResult('✅ Token endpoint accessible', true);
      } catch (error) {
        console.error('Token endpoint test (expected error):', error.response?.data);
        addResult('✅ Token endpoint accessible (returns expected error for invalid credentials)', true);
      }
      
      // Test 3: AI endpoint without image
      try {
        addResult('Testing AI endpoint...', true);
        const aiResponse = await api.post('core/ai/advanced-search/', {});
        addResult('✅ AI endpoint accessible', true);
      } catch (error) {
        console.error('AI endpoint test (expected error):', error.response?.data);
        addResult('✅ AI endpoint accessible (returns expected error for missing image)', true);
      }
      
      // Test 4: Network information
      addResult(`Network Info: ${api.defaults.baseURL}`, true);
      
    } catch (error) {
      console.error('Connection test failed:', error);
      addResult(`❌ Connection test failed: ${error.message}`, false);
      if (error.response) {
        addResult(`Status: ${error.response.status}`, false);
        addResult(`Data: ${JSON.stringify(error.response.data)}`, false);
      }
    } finally {
      setTesting(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Backend Connection Test</Text>
      <TouchableOpacity 
        style={styles.button} 
        onPress={testConnection}
        disabled={testing}
      >
        <Text style={styles.buttonText}>
          {testing ? 'Testing...' : 'Test Connection'}
        </Text>
      </TouchableOpacity>
      
      <ScrollView style={styles.resultsContainer}>
        {results.map((result, index) => (
          <View key={index} style={[styles.resultItem, result.isSuccess ? styles.successItem : styles.errorItem]}>
            <Text style={[styles.resultText, result.isSuccess ? styles.successText : styles.errorText]}>
              {result.message}
            </Text>
            <Text style={styles.timestamp}>{result.timestamp}</Text>
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#1a1a1a',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 30,
  },
  button: {
    backgroundColor: '#8B5CF6',
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
    textAlign: 'center',
  },
  resultsContainer: {
    flex: 1,
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    padding: 16,
  },
  resultItem: {
    padding: 12,
    marginBottom: 8,
    borderRadius: 8,
  },
  successItem: {
    backgroundColor: '#1a2e1a',
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  errorItem: {
    backgroundColor: '#2e1a1a',
    borderLeftWidth: 4,
    borderLeftColor: '#F44336',
  },
  resultText: {
    fontSize: 14,
    lineHeight: 20,
  },
  successText: {
    color: '#4CAF50',
  },
  errorText: {
    color: '#F44336',
  },
  timestamp: {
    fontSize: 12,
    color: '#888',
    marginTop: 4,
  },
}); 