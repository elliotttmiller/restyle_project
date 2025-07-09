import React from 'react';
import { StyleSheet, Text, View, Platform } from "react-native";

export default function Page() {
  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Restyle</Text>
        <Text style={styles.subtitle}>Loading...</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 32,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  title: {
    fontSize: 48,
    fontWeight: Platform.OS === 'ios' ? '600' : 'bold',
    color: '#222',
    marginBottom: 12,
    fontFamily: Platform.OS === 'ios' ? 'San Francisco' : 'Roboto',
  },
  subtitle: {
    fontSize: 20,
    color: '#555',
    marginBottom: 32,
    textAlign: 'center',
  },
});
