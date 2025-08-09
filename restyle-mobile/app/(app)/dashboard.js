// restyle-mobile/app/(app)/dashboard.js
import React from 'react';
import { View, Text, StyleSheet, ActivityIndicator, ScrollView, SafeAreaView, TouchableOpacity } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import useResultsStore from '../../shared/resultsStore';
import RecommendationSummary from './components/RecommendationSummary';
import StatisticalDetails from './components/StatisticalDetails';

export default function Dashboard() {
  const { results, isLoading, error, startAnalysis, clearResults } = useResultsStore();

  const handleImagePick = async () => {
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (permissionResult.granted === false) {
      alert("You've refused to allow this app to access your photos!");
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled && result.assets && result.assets.length > 0) {
      startAnalysis(result.assets[0]);
    }
  };

  const renderContent = () => {
    if (isLoading) {
      return (
        <View style={styles.centered}>
          <ActivityIndicator size="large" color="#1A73E8" />
          <Text style={styles.loadingText}>AI is analyzing your item...</Text>
          <Text style={styles.subtleText}>This may take up to 30 seconds.</Text>
        </View>
      );
    }

    if (error) {
      return (
        <View style={styles.centered}>
          <Text style={styles.errorTitle}>Analysis Failed</Text>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.button} onPress={clearResults}>
            <Text style={styles.buttonText}>Try Again</Text>
          </TouchableOpacity>
        </View>
      );
    }

    if (results) {
      return (
        <ScrollView contentContainerStyle={{ paddingBottom: 40 }}>
          <Text style={styles.resultsTitle}>Analysis Complete</Text>
          <RecommendationSummary recommendation={results.final_recommendation} />
          <StatisticalDetails stats={results.statistical_analysis} />
          <TouchableOpacity style={styles.button} onPress={clearResults}>
            <Text style={styles.buttonText}>Analyze Another Item</Text>
          </TouchableOpacity>
        </ScrollView>
      );
    }

    return (
      <View style={styles.centered}>
        <Text style={styles.title}>Restyle.ai</Text>
        <Text style={styles.subtitle}>Get an AI-powered price analysis for your fashion items.</Text>
        <TouchableOpacity style={styles.button} onPress={handleImagePick}>
          <Text style={styles.buttonText}>Select Image to Analyze</Text>
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.innerContainer}>{renderContent()}</View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0f2f5' },
  innerContainer: { flex: 1, paddingHorizontal: 20, paddingTop: 10 },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 20 },
  title: { fontSize: 32, fontWeight: 'bold', marginBottom: 8, color: '#333' },
  subtitle: { fontSize: 16, color: '#666', marginBottom: 30, textAlign: 'center' },
  resultsTitle: { fontSize: 24, fontWeight: 'bold', marginBottom: 10, color: '#333', textAlign: 'center' },
  loadingText: { marginTop: 15, fontSize: 16, color: '#555' },
  subtleText: { marginTop: 5, fontSize: 12, color: '#888' },
  errorTitle: { fontSize: 22, fontWeight: 'bold', color: '#c00', marginBottom: 10 },
  errorText: { fontSize: 16, color: '#555', textAlign: 'center', marginBottom: 20 },
  button: { backgroundColor: '#1A73E8', paddingVertical: 15, paddingHorizontal: 30, borderRadius: 25, marginTop: 10 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
});