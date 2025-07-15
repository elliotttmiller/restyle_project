import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Image, ActivityIndicator, TextInput, ScrollView, Dimensions, Linking } from 'react-native';
import { useRouter } from 'expo-router';
import { useLocalSearchParams } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import api from '../../shared/api';
import { useAuthStore } from '../../shared/authStore';

export default function CameraSearch() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const [selectedImage, setSelectedImage] = useState(null);
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [bestGuess, setBestGuess] = useState('');
  const [suggestedQueries, setSuggestedQueries] = useState([]);
  const [ocrText, setOcrText] = useState('');
  const [labels, setLabels] = useState([]);
  const [objects, setObjects] = useState([]);
  const [dominantColors, setDominantColors] = useState([]);
  const [searchTerms, setSearchTerms] = useState([]);
  const [textQuery, setTextQuery] = useState('');
  const [visualSimilars, setVisualSimilars] = useState([]);
  const [attributeFilter, setAttributeFilter] = useState(null);
  const [detectedObjects, setDetectedObjects] = useState([]);
  const [selectedObjectIndex, setSelectedObjectIndex] = useState(null);
  
  // Advanced AI Analysis State
  const [advancedAnalysis, setAdvancedAnalysis] = useState(null);
  const [confidenceScores, setConfidenceScores] = useState({});
  const [queryVariants, setQueryVariants] = useState([]);
  const [selectedQueryVariant, setSelectedQueryVariant] = useState(null);
  const [analysisQuality, setAnalysisQuality] = useState('medium');
  const [aiServicesStatus, setAiServicesStatus] = useState({
    vision: false,
    rekognition: false,
    gemini: false,
    vertex: false
  });

  const token = useAuthStore((state) => state.token);

  React.useEffect(() => {
    if (params.mode === 'camera') {
      takePhoto();
    } else if (params.mode === 'library') {
      pickImage();
    }
    // Only run on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const requestPermissions = async () => {
    const { status: cameraStatus } = await ImagePicker.requestCameraPermissionsAsync();
    const { status: libraryStatus } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (cameraStatus !== 'granted' || libraryStatus !== 'granted') {
      Alert.alert('Permissions Required', 'Camera and photo library permissions are needed.');
      return false;
    }
    return true;
  };

  const takePhoto = async () => {
    const hasPermission = await requestPermissions();
    if (!hasPermission) return;

    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images', 'videos'],
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setSelectedImage(result.assets[0]);
        setSearchResults([]);
        setAdvancedAnalysis(null);
        setQueryVariants([]);
      }
    } catch (error) {
      console.error('Error taking photo:', error);
      Alert.alert('Error', 'Failed to take photo. Please try again.');
    }
  };

  const pickImage = async () => {
    const hasPermission = await requestPermissions();
    if (!hasPermission) return;

    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images', 'videos'],
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setSelectedImage(result.assets[0]);
        setSearchResults([]);
        setAdvancedAnalysis(null);
        setQueryVariants([]);
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Error', 'Failed to pick image. Please try again.');
    }
  };

  const searchByImage = async (queryOverride = null) => {
    if (!selectedImage) {
      Alert.alert('No Image', 'Please select or take a photo first.');
      return;
    }
    setSearching(true);
    try {
      const formData = new FormData();
      const file = {
        uri: selectedImage.uri,
        type: selectedImage.type || 'image/jpeg',
        name: 'image.jpg',
      };
      formData.append('image', file);
      const queryToSend = queryOverride !== null ? queryOverride : textQuery;
      if (queryToSend) {
        formData.append('query', queryToSend);
      }
      if (selectedObjectIndex !== null) {
        formData.append('object_index', selectedObjectIndex);
      }
      // Use the ai-image-search endpoint for robust integration
      console.log('Posting to endpoint:', api.defaults.baseURL + '/core/ai/advanced-search/');
      console.log('Auth token:', token);
      const searchResponse = await api.post('core/ai/advanced-search/', formData, {
        headers: {
          Authorization: token ? `Bearer ${token}` : undefined,
          // Let axios set Content-Type
        },
      });
      const responseData = searchResponse.data;
      // Always use 'results' key for eBay items
      setSearchResults(responseData.analysis_results?.visually_ranked_comps || responseData.results || []);
      setAnalysis(responseData.analysis_results || responseData.analysis || null);
      
      // Set advanced AI analysis
      setAdvancedAnalysis(responseData.analysis);
      setConfidenceScores(responseData.analysis?.confidence_scores || {});
      setQueryVariants(responseData.queries?.variants || []);
      setSelectedQueryVariant(responseData.queries?.primary || '');
      setAnalysisQuality(responseData.summary?.analysis_quality || 'medium');
      
      // Set AI services status
      setAiServicesStatus({
        vision: !!responseData.analysis?.vision,
        rekognition: !!responseData.analysis?.rekognition,
        gemini: !!responseData.analysis?.gemini,
        vertex: !!responseData.analysis?.vertex
      });
      
      // Set legacy fields for backward compatibility
      setBestGuess(responseData.queries?.primary || '');
      setSuggestedQueries(responseData.queries?.variants?.map(v => v.query) || []);
      
      if ((responseData.analysis_results?.visually_ranked_comps || responseData.results || []).length > 0) {
        Alert.alert('Image Search Complete', `Found ${responseData.analysis_results?.visually_ranked_comps?.length || responseData.results?.length || 0} items!`);
      } else {
        Alert.alert('No Results', 'No items found for this image. Try a different photo.');
      }
    } catch (error) {
      console.error('Image search failed:', error);
      Alert.alert('Search Failed', error.response?.data?.error || 'Failed to search by image.');
    } finally {
      setSearching(false);
    }
  };

  const searchWithQueryVariant = async (variant) => {
    setSelectedQueryVariant(variant.query);
    await searchByImage(variant.query);
  };

  const clearImage = () => {
    setSelectedImage(null);
    setSearchResults([]);
    setAdvancedAnalysis(null);
    setQueryVariants([]);
    setConfidenceScores({});
    setAiServicesStatus({
      vision: false,
      rekognition: false,
      gemini: false,
      vertex: false
    });
  };

  // Attribute filter logic
  const filteredResults = attributeFilter
    ? searchResults.filter(item => item.attributes && Object.values(item.attributes).includes(attributeFilter))
    : searchResults;

  // For overlay scaling
  const imageWidth = 200;
  const imageHeight = 150;

  const renderConfidenceBar = (service, score) => {
    const percentage = score || 0;
    return (
      <View style={styles.confidenceBarContainer}>
        <Text style={styles.confidenceLabel}>{service}</Text>
        <View style={styles.confidenceBar}>
          <View style={[styles.confidenceFill, { width: `${percentage}%`, backgroundColor: percentage > 80 ? '#4CAF50' : percentage > 60 ? '#FF9800' : '#F44336' }]} />
        </View>
        <Text style={styles.confidenceScore}>{percentage}%</Text>
      </View>
    );
  };

  const renderQueryVariant = (variant, index) => (
    <TouchableOpacity
      key={index}
      style={[
        styles.queryVariant,
        selectedQueryVariant === variant.query && styles.selectedQueryVariant
      ]}
      onPress={() => searchWithQueryVariant(variant)}
    >
      <Text style={styles.queryVariantText}>{variant.query}</Text>
      <View style={styles.queryVariantMeta}>
        <Text style={styles.querySource}>{variant.source}</Text>
        <Text style={styles.queryConfidence}>{variant.confidence}%</Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Advanced AI Image Search</Text>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Text style={styles.backButtonText}>Back</Text>
        </TouchableOpacity>
      </View>
      <ScrollView style={styles.content} contentContainerStyle={{ flexGrow: 1, paddingBottom: 40 }}>
        <Text style={styles.subtitle}>
          Multi-Expert AI System: Google Vision, AWS Rekognition, Gemini, Vertex AI
        </Text>
        
        {/* Image Selection */}
        <View style={styles.imageSection}>
          {selectedImage ? (
            <View style={styles.selectedImageContainer}>
              <Image source={{ uri: selectedImage.uri }} style={styles.selectedImage} />
              <TouchableOpacity style={styles.clearButton} onPress={clearImage}>
                <Text style={styles.clearButtonText}>Clear</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View style={styles.imageButtons}>
              <TouchableOpacity style={styles.imageButton} onPress={takePhoto}>
                <Text style={styles.imageButtonText}>📷 Take Photo</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.imageButton} onPress={pickImage}>
                <Text style={styles.imageButtonText}>🖼️ Choose from Library</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>

        {/* Advanced AI Analysis Results */}
        {advancedAnalysis && (
          <View style={styles.analysisSection}>
            <Text style={styles.sectionTitle}>🤖 Multi-Expert AI Analysis</Text>
            
            {/* AI Services Status */}
            <View style={styles.aiServicesStatus}>
              <Text style={styles.statusTitle}>AI Services Status:</Text>
              <View style={styles.statusGrid}>
                <View style={[styles.statusItem, aiServicesStatus.vision && styles.statusActive]}>
                  <Text style={styles.statusText}>👁️ Vision</Text>
                </View>
                <View style={[styles.statusItem, aiServicesStatus.rekognition && styles.statusActive]}>
                  <Text style={styles.statusText}>🔍 Rekognition</Text>
                </View>
                <View style={[styles.statusItem, aiServicesStatus.gemini && styles.statusActive]}>
                  <Text style={styles.statusText}>🧠 Gemini</Text>
                </View>
                <View style={[styles.statusItem, aiServicesStatus.vertex && styles.statusActive]}>
                  <Text style={styles.statusText}>⚡ Vertex</Text>
                </View>
              </View>
            </View>

            {/* Confidence Scores */}
            {Object.keys(confidenceScores).length > 0 && (
              <View style={styles.confidenceSection}>
                <Text style={styles.confidenceTitle}>Confidence Scores:</Text>
                {Object.entries(confidenceScores).map(([service, score]) => 
                  renderConfidenceBar(service, score)
                )}
              </View>
            )}

            {/* Query Variants */}
            {queryVariants.length > 0 && (
              <View style={styles.queryVariantsSection}>
                <Text style={styles.queryVariantsTitle}>AI-Generated Query Variants:</Text>
                {queryVariants.map((variant, index) => renderQueryVariant(variant, index))}
              </View>
            )}

            {/* Analysis Quality */}
            <View style={styles.qualitySection}>
              <Text style={styles.qualityTitle}>Analysis Quality: </Text>
              <Text style={[
                styles.qualityValue,
                analysisQuality === 'high' && styles.qualityHigh,
                analysisQuality === 'medium' && styles.qualityMedium,
                analysisQuality === 'low' && styles.qualityLow
              ]}>
                {analysisQuality.toUpperCase()}
              </Text>
            </View>
          </View>
        )}

        {/* Search Button */}
        {selectedImage && (
          <TouchableOpacity
            style={[styles.searchButton, searching && styles.searchButtonDisabled]}
            onPress={() => searchByImage()}
            disabled={searching}
          >
            {searching ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.searchButtonText}>
                🔍 Advanced AI Search
              </Text>
            )}
          </TouchableOpacity>
        )}

        {/* Search Results */}
        {searchResults.length > 0 && (
          <View style={styles.resultsSection}>
            <Text style={styles.resultsTitle}>Found {searchResults.length} items:</Text>
            {searchResults.slice(0, 5).map((item, index) => (
              <TouchableOpacity
                key={index}
                style={styles.resultItem}
                onPress={() => {
                  // Navigate to item detail
                  router.push({
                    pathname: '/item-detail',
                    params: { itemId: item.id }
                  });
                }}
              >
                <Text style={styles.resultTitle}>{item.title}</Text>
                <Text style={styles.resultPrice}>${item.price}</Text>
                <Text style={styles.resultCondition}>{item.condition}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  backButton: {
    padding: 10,
    backgroundColor: '#007AFF',
    borderRadius: 8,
  },
  backButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
    textAlign: 'center',
  },
  imageSection: {
    marginBottom: 20,
  },
  imageButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  imageButton: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    flex: 0.45,
  },
  imageButtonText: {
    color: '#fff',
    textAlign: 'center',
    fontWeight: '600',
  },
  selectedImageContainer: {
    alignItems: 'center',
  },
  selectedImage: {
    width: 200,
    height: 150,
    borderRadius: 8,
    marginBottom: 10,
  },
  clearButton: {
    backgroundColor: '#FF3B30',
    padding: 10,
    borderRadius: 8,
  },
  clearButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  searchButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20,
  },
  searchButtonDisabled: {
    backgroundColor: '#ccc',
  },
  searchButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  analysisSection: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  aiServicesStatus: {
    marginBottom: 15,
  },
  statusTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
    color: '#666',
  },
  statusGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statusItem: {
    backgroundColor: '#f0f0f0',
    padding: 8,
    borderRadius: 6,
    marginBottom: 5,
    flex: 0.48,
  },
  statusActive: {
    backgroundColor: '#4CAF50',
  },
  statusText: {
    fontSize: 12,
    textAlign: 'center',
    color: '#333',
  },
  confidenceSection: {
    marginBottom: 15,
  },
  confidenceTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
    color: '#666',
  },
  confidenceBarContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  confidenceLabel: {
    width: 80,
    fontSize: 12,
    color: '#666',
  },
  confidenceBar: {
    flex: 1,
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    marginHorizontal: 10,
  },
  confidenceFill: {
    height: '100%',
    borderRadius: 4,
  },
  confidenceScore: {
    width: 30,
    fontSize: 12,
    color: '#666',
    textAlign: 'right',
  },
  queryVariantsSection: {
    marginBottom: 15,
  },
  queryVariantsTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
    color: '#666',
  },
  queryVariant: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 6,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  selectedQueryVariant: {
    backgroundColor: '#e3f2fd',
    borderColor: '#2196F3',
  },
  queryVariantText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 4,
  },
  queryVariantMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  querySource: {
    fontSize: 12,
    color: '#666',
  },
  queryConfidence: {
    fontSize: 12,
    color: '#4CAF50',
    fontWeight: '600',
  },
  qualitySection: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  qualityTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  qualityValue: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  qualityHigh: {
    color: '#4CAF50',
  },
  qualityMedium: {
    color: '#FF9800',
  },
  qualityLow: {
    color: '#F44336',
  },
  resultsSection: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  resultsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  resultItem: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 6,
    marginBottom: 8,
  },
  resultTitle: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 4,
  },
  resultPrice: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginBottom: 2,
  },
  resultCondition: {
    fontSize: 12,
    color: '#666',
  },
}); 