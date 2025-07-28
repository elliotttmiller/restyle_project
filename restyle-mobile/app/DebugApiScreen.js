import React, { useState } from 'react';
import { View, Text, TextInput, Button, ScrollView, StyleSheet } from 'react-native';
import api from '../shared/api';
import config from '../config.js';

export default function DebugApiScreen() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [debugLog, setDebugLog] = useState('');
  const [loading, setLoading] = useState(false);

  const handleDebugLogin = async () => {
    let log = `API Base URL: ${api.defaults.baseURL}\nPayload: ${JSON.stringify({ username, password })}\n`;
    setDebugLog(log);
    setLoading(true);
    try {
      const response = await api.post('/api/token/', { username, password });
      log += `Status: ${response.status}\nResponse: ${JSON.stringify(response.data, null, 2)}\n`;
      setDebugLog(log);
    } catch (error) {
      log += `Error: ${error.message}\n`;
      if (error.response) {
        log += `Response status: ${error.response.status}\nResponse data: ${JSON.stringify(error.response.data, null, 2)}\n`;
      } else if (error.request) {
        log += `No response received. Request: ${JSON.stringify(error.request, null, 2)}\n`;
      }
      setDebugLog(log);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.header}>Debug API Screen</Text>
      <Text style={styles.label}>API Base URL:</Text>
      <Text style={styles.value}>{api.defaults.baseURL}</Text>
      <Text style={styles.label}>Username:</Text>
      <TextInput value={username} onChangeText={setUsername} autoCapitalize="none" style={styles.input} />
      <Text style={styles.label}>Password:</Text>
      <TextInput value={password} onChangeText={setPassword} secureTextEntry style={styles.input} />
      <Button title={loading ? 'Testing...' : 'Debug Login'} onPress={handleDebugLogin} disabled={loading} />
      <Text style={styles.label}>Debug Log:</Text>
      <Text style={styles.log}>{debugLog}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, backgroundColor: '#fff', flex: 1 },
  header: { fontSize: 22, fontWeight: 'bold', marginBottom: 20 },
  label: { fontWeight: 'bold', marginTop: 15 },
  value: { marginBottom: 10, color: '#333' },
  input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 5, padding: 8, marginBottom: 10 },
  log: { marginTop: 10, fontFamily: 'monospace', color: '#444' },
}); 