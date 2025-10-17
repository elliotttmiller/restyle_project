// restyle-mobile/app/(app)/dashboard.js
import React from 'react';
import { View, Text, StyleSheet, ActivityIndicator, ScrollView, SafeAreaView, TouchableOpacity, StatusBar } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
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

  const handleCameraLaunch = async () => {
    const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
    if (permissionResult.granted === false) {
      alert("You've refused to allow this app to access your camera!");
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
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
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#667eea" />
            <Text style={styles.loadingText}>✨ AI is analyzing your item...</Text>
            <Text style={styles.subtleText}>This may take up to 30 seconds.</Text>
          </View>
        </View>
      );
    }

    if (error) {
      return (
        <View style={styles.centered}>
          <View style={styles.errorContainer}>
            <Text style={styles.errorIcon}>⚠️</Text>
            <Text style={styles.errorTitle}>Analysis Failed</Text>
            <Text style={styles.errorText}>{error}</Text>
            <TouchableOpacity 
              style={styles.button} 
              onPress={clearResults}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={['#667eea', '#764ba2']}
                start={{x: 0, y: 0}}
                end={{x: 1, y: 1}}
                style={styles.buttonGradient}
              >
                <Text style={styles.buttonText}>Try Again</Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </View>
      );
    }

    if (results) {
      return (
        <ScrollView 
          contentContainerStyle={styles.resultsScroll}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.resultsContainer}>
            <Text style={styles.resultsTitle}>✅ Analysis Complete</Text>
            <RecommendationSummary recommendation={results.final_recommendation} />
            <StatisticalDetails stats={results.statistical_analysis} />
            <TouchableOpacity 
              style={[styles.button, styles.buttonSecondary]} 
              onPress={clearResults}
              activeOpacity={0.8}
            >
              <Text style={styles.buttonTextSecondary}>Analyze Another Item</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      );
    }

    return (
      <View style={styles.centered}>
        <View style={styles.heroContainer}>
          <Text style={styles.heroIcon}>✨</Text>
          <Text style={styles.title}>Restyle.ai</Text>
          <View style={styles.betaBadge}>
            <Text style={styles.betaText}>BETA</Text>
          </View>
          <Text style={styles.subtitle}>
            Get AI-powered price analysis for your fashion items in seconds.
          </Text>
          
          <View style={styles.statsContainer}>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>AI</Text>
              <Text style={styles.statLabel}>Powered</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>< 30s</Text>
              <Text style={styles.statLabel}>Analysis</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>99%</Text>
              <Text style={styles.statLabel}>Accuracy</Text>
            </View>
          </View>
          
          <View style={styles.actionButtons}>
            <TouchableOpacity 
              style={styles.button} 
              onPress={handleCameraLaunch}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={['#667eea', '#764ba2']}
                start={{x: 0, y: 0}}
                end={{x: 1, y: 1}}
                style={styles.buttonGradient}
              >
                <Text style={styles.buttonIcon}>📸</Text>
                <Text style={styles.buttonText}>Take Photo</Text>
              </LinearGradient>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={[styles.button, styles.buttonOutline]} 
              onPress={handleImagePick}
              activeOpacity={0.8}
            >
              <Text style={styles.buttonIconSecondary}>🖼️</Text>
              <Text style={styles.buttonTextOutline}>Choose from Gallery</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      <View style={styles.innerContainer}>{renderContent()}</View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: '#0f0f23',
  },
  innerContainer: { 
    flex: 1,
  },
  centered: { 
    flex: 1, 
    justifyContent: 'center', 
    alignItems: 'center', 
    paddingHorizontal: 24,
  },
  heroContainer: {
    alignItems: 'center',
    width: '100%',
    maxWidth: 500,
  },
  heroIcon: {
    fontSize: 64,
    marginBottom: 16,
    textShadowColor: 'rgba(102, 126, 234, 0.5)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 20,
  },
  title: { 
    fontSize: 40, 
    fontWeight: '900', 
    marginBottom: 12, 
    color: '#fff',
    letterSpacing: -1,
  },
  betaBadge: {
    backgroundColor: '#667eea',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 20,
    marginBottom: 16,
  },
  betaText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 1,
  },
  subtitle: { 
    fontSize: 17, 
    color: '#b8c5d6', 
    marginBottom: 32, 
    textAlign: 'center',
    lineHeight: 26,
    fontWeight: '400',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginBottom: 40,
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'rgba(22, 33, 62, 0.6)',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(184, 197, 214, 0.1)',
  },
  statNumber: {
    fontSize: 20,
    fontWeight: '800',
    color: '#667eea',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 11,
    color: '#7989a3',
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  actionButtons: {
    width: '100%',
    gap: 16,
  },
  button: { 
    borderRadius: 16,
    overflow: 'hidden',
    elevation: 4,
    shadowColor: '#667eea',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
  },
  buttonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 18,
    paddingHorizontal: 32,
    gap: 8,
  },
  buttonIcon: {
    fontSize: 20,
  },
  buttonText: { 
    color: '#fff', 
    fontSize: 17, 
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  buttonOutline: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: 'rgba(102, 126, 234, 0.4)',
    shadowOpacity: 0,
  },
  buttonIconSecondary: {
    fontSize: 20,
  },
  buttonTextOutline: {
    color: '#667eea',
    fontSize: 17,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  buttonSecondary: {
    backgroundColor: 'rgba(22, 33, 62, 0.8)',
    borderWidth: 1,
    borderColor: 'rgba(184, 197, 214, 0.2)',
    marginTop: 16,
  },
  buttonTextSecondary: {
    color: '#b8c5d6',
    fontSize: 17,
    fontWeight: '700',
    textAlign: 'center',
    paddingVertical: 16,
  },
  loadingContainer: {
    alignItems: 'center',
    backgroundColor: 'rgba(22, 33, 62, 0.6)',
    borderRadius: 24,
    padding: 40,
    borderWidth: 1,
    borderColor: 'rgba(184, 197, 214, 0.1)',
  },
  loadingText: { 
    marginTop: 20, 
    fontSize: 18, 
    color: '#fff',
    fontWeight: '600',
  },
  subtleText: { 
    marginTop: 8, 
    fontSize: 14, 
    color: '#7989a3',
  },
  errorContainer: {
    alignItems: 'center',
    backgroundColor: 'rgba(22, 33, 62, 0.6)',
    borderRadius: 24,
    padding: 32,
    borderWidth: 1,
    borderColor: 'rgba(239, 68, 68, 0.3)',
    maxWidth: 400,
  },
  errorIcon: {
    fontSize: 56,
    marginBottom: 16,
  },
  errorTitle: { 
    fontSize: 24, 
    fontWeight: '800', 
    color: '#ef4444', 
    marginBottom: 12,
  },
  errorText: { 
    fontSize: 16, 
    color: '#b8c5d6', 
    textAlign: 'center', 
    marginBottom: 24,
    lineHeight: 24,
  },
  resultsScroll: {
    paddingBottom: 40,
  },
  resultsContainer: {
    padding: 24,
  },
  resultsTitle: { 
    fontSize: 28, 
    fontWeight: '800', 
    marginBottom: 24, 
    color: '#fff', 
    textAlign: 'center',
  },
});