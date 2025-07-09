import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Image, ActivityIndicator, TextInput, ScrollView, Dimensions } from 'react-native';
import { useRouter } from 'expo-router';
import { useLocalSearchParams } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import api from '../shared/api';

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
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setSelectedImage(result.assets[0]);
        setSearchResults([]);
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
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setSelectedImage(result.assets[0]);
        setSearchResults([]);
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
      const response = await fetch(selectedImage.uri);
      const blob = await response.blob();
      const formData = new FormData();
      formData.append('image', blob, 'image.jpg');
      formData.append('image_type', 'image/jpeg');
      const queryToSend = queryOverride !== null ? queryOverride : textQuery;
      if (queryToSend) {
        formData.append('query', queryToSend);
      }
      if (selectedObjectIndex !== null) {
        formData.append('object_index', selectedObjectIndex);
      }
      const searchResponse = await api.post('/core/ai/image-search/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setSearchResults(searchResponse.data.results || []);
      setAnalysis(searchResponse.data.analysis || null);
      setBestGuess(searchResponse.data.best_guess || '');
      setSuggestedQueries(searchResponse.data.suggested_queries || []);
      setOcrText(searchResponse.data.ocr_text || '');
      setLabels(searchResponse.data.labels || []);
      setObjects(searchResponse.data.objects || []);
      setDominantColors(searchResponse.data.dominant_colors || []);
      setSearchTerms(searchResponse.data.search_terms || []);
      setVisualSimilars(searchResponse.data.visual_similar_results || []);
      setDetectedObjects(searchResponse.data.detected_objects || []);
      if (searchResponse.data.results && searchResponse.data.results.length > 0) {
        Alert.alert('Success', `Found ${searchResponse.data.results.length} items!`);
      } else {
        Alert.alert('No Results', 'No items found for this image. Try a different photo.');
      }
    } catch (error) {
      console.error('AI search failed:', error);
      Alert.alert('Search Failed', error.response?.data?.error || 'Failed to search by image.');
    } finally {
      setSearching(false);
    }
  };

  const clearImage = () => {
    setSelectedImage(null);
    setSearchResults([]);
  };

  // Attribute filter logic
  const filteredResults = attributeFilter
    ? searchResults.filter(item => item.attributes && Object.values(item.attributes).includes(attributeFilter))
    : searchResults;

  // For overlay scaling
  const imageWidth = 200;
  const imageHeight = 150;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>AI Image Search</Text>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Text style={styles.backButtonText}>Back</Text>
        </TouchableOpacity>
      </View>
      <View style={styles.content}>
        <Text style={styles.subtitle}>
          Take a photo or select an image to search for similar items on eBay
        </Text>
        <TextInput
          style={styles.textInput}
          placeholder="Add keywords (e.g. 'red Nike', 'leather')"
          placeholderTextColor="#888"
          value={textQuery}
          onChangeText={setTextQuery}
          onSubmitEditing={() => searchByImage()}
          returnKeyType="search"
        />
        <View style={styles.buttonContainer}>
          <TouchableOpacity style={styles.button} onPress={takePhoto}>
            <Text style={styles.buttonText}>📷 Take Photo</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.button} onPress={pickImage}>
            <Text style={styles.buttonText}>🖼️ Choose from Gallery</Text>
          </TouchableOpacity>
        </View>
        {selectedImage && (
          <View style={styles.imageContainer}>
            <View style={{ position: 'relative' }}>
              <Image source={{ uri: selectedImage.uri }} style={styles.selectedImage} />
              {/* Object overlays */}
              {detectedObjects.map((obj, idx) => {
                const [x_min, y_min, x_max, y_max] = obj.bounding_box;
                const left = x_min * imageWidth;
                const top = y_min * imageHeight;
                const width = (x_max - x_min) * imageWidth;
                const height = (y_max - y_min) * imageHeight;
                return (
                  <TouchableOpacity
                    key={idx}
                    style={[
                      styles.objectBox,
                      {
                        left,
                        top,
                        width,
                        height,
                        borderColor: selectedObjectIndex === idx ? '#8B5CF6' : '#fff',
                        zIndex: 10,
                      },
                    ]}
                    onPress={() => setSelectedObjectIndex(idx)}
                    activeOpacity={0.7}
                  >
                    <Text style={styles.objectLabel}>{obj.name} ({Math.round(obj.confidence * 100)}%)</Text>
                  </TouchableOpacity>
                );
              })}
            </View>
            <View style={styles.imageActions}>
              <TouchableOpacity style={styles.searchButton} onPress={() => searchByImage()}>
                {searching ? (
                  <ActivityIndicator color="#fff" size="small" />
                ) : (
                  <Text style={styles.searchButtonText}>🔍 Search by Image</Text>
                )}
              </TouchableOpacity>
              <TouchableOpacity style={styles.clearButton} onPress={clearImage}>
                <Text style={styles.clearButtonText}>Clear</Text>
              </TouchableOpacity>
              {selectedObjectIndex !== null && (
                <TouchableOpacity style={styles.clearButton} onPress={() => setSelectedObjectIndex(null)}>
                  <Text style={styles.clearButtonText}>Clear Region</Text>
                </TouchableOpacity>
              )}
            </View>
          </View>
        )}
        {/* Advanced AI Analysis UI */}
        {analysis && (
          <View style={styles.analysisContainer}>
            {bestGuess ? (
              <Text style={styles.bestGuess}>Best Guess: <Text style={{fontWeight:'bold'}}>{bestGuess}</Text></Text>
            ) : null}
            {ocrText ? (
              <Text style={styles.ocrText}>OCR: "{ocrText}"</Text>
            ) : null}
            {labels.length > 0 && (
              <View style={styles.chipRow}><Text style={styles.chipLabel}>Labels:</Text>{labels.map((l, i) => (
                <Text key={i} style={styles.chip}>{l.description} ({(l.confidence*100).toFixed(0)}%)</Text>
              ))}</View>
            )}
            {objects.length > 0 && (
              <View style={styles.chipRow}><Text style={styles.chipLabel}>Objects:</Text>{objects.map((o, i) => (
                <Text key={i} style={styles.chip}>{o.name} ({(o.confidence*100).toFixed(0)}%)</Text>
              ))}</View>
            )}
            {dominantColors.length > 0 && (
              <View style={styles.chipRow}><Text style={styles.chipLabel}>Colors:</Text>{dominantColors.map((c, i) => (
                <Text key={i} style={styles.chip}>{`rgb(${c.red},${c.green},${c.blue})`}</Text>
              ))}</View>
            )}
            {suggestedQueries.length > 0 && (
              <View style={styles.chipRow}><Text style={styles.chipLabel}>Suggested Queries:</Text>{suggestedQueries.map((q, i) => (
                <TouchableOpacity key={i} style={styles.suggestedChip} onPress={() => searchByImage(q)}>
                  <Text style={styles.suggestedChipText}>{q}</Text>
                </TouchableOpacity>
              ))}</View>
            )}
          </View>
        )}
        {/* Attribute Filter Chips */}
        {searchResults.length > 0 && (
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{marginBottom: 10}}>
            {[...new Set(searchResults.flatMap(item => Object.values(item.attributes || {})))].map((attr, i) => (
              <TouchableOpacity
                key={i}
                style={[styles.chip, attributeFilter === attr && {backgroundColor: '#8B5CF6'}]}
                onPress={() => setAttributeFilter(attributeFilter === attr ? null : attr)}
              >
                <Text style={{color: '#fff'}}>{attr}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        )}
        {/* Results Grid */}
        {filteredResults.length > 0 && (
          <View style={styles.resultsContainer}>
            <Text style={styles.resultsTitle}>Search Results ({filteredResults.length})</Text>
            <View style={styles.grid}>
              {filteredResults.map((item, index) => (
                <TouchableOpacity
                  key={`${item.itemId || index}-${Date.now()}`}
                  style={styles.resultCard}
                  onPress={() => {
                    router.push({ 
                      pathname: '/item-detail', 
                      params: { item: JSON.stringify(item) } 
                    });
                  }}
                >
                  {item.image?.imageUrl && (
                    <Image source={{ uri: item.image.imageUrl }} style={styles.resultImage} />
                  )}
                  <Text style={styles.resultTitle} numberOfLines={2}>{item.title || 'No title'}</Text>
                  {item.price?.value && (
                    <Text style={styles.resultPrice}>${item.price.value}</Text>
                  )}
                  {/* Show attributes */}
                  {item.attributes && (
                    <Text style={styles.resultAttrs} numberOfLines={2}>
                      {Object.entries(item.attributes).map(([k, v]) => `${k}: ${v}`).join(', ')}
                    </Text>
                  )}
                  {/* Show matched_on */}
                  {item.matched_on && item.matched_on.length > 0 && (
                    <Text style={styles.resultMatchedOn} numberOfLines={1}>
                      Matched on: {item.matched_on.join(', ')}
                    </Text>
                  )}
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}
        {/* Visually Similar Results */}
        {visualSimilars.length > 0 && (
          <View style={styles.similarContainer}>
            <Text style={styles.similarTitle}>Visually Similar Items</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {visualSimilars.map((sim, i) => (
                <View key={i} style={styles.similarCard}>
                  {sim.image_url && (
                    <Image source={{ uri: sim.image_url }} style={styles.similarImage} />
                  )}
                  <Text style={styles.similarTitleText} numberOfLines={1}>{sim.title}</Text>
                  <Text style={styles.similarBrand}>{sim.brand}</Text>
                  <Text style={styles.similarScore}>Score: {sim.similarity.toFixed(2)}</Text>
                  {sim.attributes && (
                    <Text style={styles.similarAttrs} numberOfLines={2}>
                      {Object.entries(sim.attributes).map(([k, v]) => `${k}: ${v}`).join(', ')}
                    </Text>
                  )}
                </View>
              ))}
            </ScrollView>
          </View>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  header: {
    backgroundColor: '#a259f7',
    padding: 20,
    paddingTop: 60,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  backButton: {
    backgroundColor: 'rgba(162, 89, 247, 0.2)',
    paddingHorizontal: 16,
    paddingVertical: 8,
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
    color: '#ccc',
    textAlign: 'center',
    marginBottom: 30,
    lineHeight: 22,
  },
  buttonContainer: {
    gap: 16,
    marginBottom: 30,
  },
  button: {
    backgroundColor: '#a259f7',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  imageContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  selectedImage: {
    width: 200,
    height: 150,
    borderRadius: 12,
    marginBottom: 16,
  },
  imageActions: {
    flexDirection: 'row',
    gap: 12,
  },
  searchButton: {
    backgroundColor: '#8B5CF6',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  searchButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  clearButton: {
    backgroundColor: '#666',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
  },
  clearButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  resultsContainer: {
    marginTop: 20,
  },
  resultsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 12,
  },
  resultItem: {
    backgroundColor: '#1a1a1a',
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
  },
  resultTitle: {
    fontSize: 16,
    color: '#fff',
    fontWeight: '500',
    marginBottom: 4,
  },
  resultPrice: {
    fontSize: 18,
    color: '#8B5CF6',
    fontWeight: 'bold',
  },
  // New styles for advanced analysis and grid
  analysisContainer: {
    backgroundColor: '#1a1a1a',
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
  },
  bestGuess: {
    fontSize: 16,
    color: '#ccc',
    marginBottom: 8,
  },
  ocrText: {
    fontSize: 16,
    color: '#ccc',
    marginBottom: 12,
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 12,
  },
  chipLabel: {
    fontSize: 14,
    color: '#888',
    fontWeight: '600',
  },
  chip: {
    backgroundColor: '#2a2a2a',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 16,
    fontSize: 13,
    color: '#fff',
  },
  suggestedChip: {
    backgroundColor: '#8B5CF6',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 16,
    fontSize: 13,
    color: '#fff',
  },
  suggestedChipText: {
    fontWeight: '600',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  resultCard: {
    width: '48%', // Two items per row
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    marginBottom: 12,
    overflow: 'hidden',
  },
  resultImage: {
    width: '100%',
    height: 120,
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
  },
  textInput: {
    backgroundColor: '#181818',
    color: '#fff',
    fontSize: 16,
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#333',
  },
  resultAttrs: {
    color: '#bbb',
    fontSize: 12,
    marginTop: 2,
  },
  resultMatchedOn: {
    color: '#8B5CF6',
    fontSize: 12,
    marginTop: 2,
  },
  similarContainer: {
    marginTop: 24,
  },
  similarTitle: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
    marginBottom: 8,
  },
  similarCard: {
    backgroundColor: '#181818',
    borderRadius: 12,
    padding: 12,
    marginRight: 12,
    width: 140,
    alignItems: 'center',
  },
  similarImage: {
    width: 100,
    height: 80,
    borderRadius: 8,
    marginBottom: 8,
  },
  similarTitleText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
    marginBottom: 2,
  },
  similarBrand: {
    color: '#bbb',
    fontSize: 12,
    marginBottom: 2,
  },
  similarScore: {
    color: '#8B5CF6',
    fontSize: 12,
    marginBottom: 2,
  },
  similarAttrs: {
    color: '#bbb',
    fontSize: 11,
    marginTop: 2,
    textAlign: 'center',
  },
  objectBox: {
    position: 'absolute',
    borderWidth: 2,
    borderRadius: 6,
    backgroundColor: 'rgba(138,89,246,0.15)',
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
  },
  objectLabel: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
    backgroundColor: 'rgba(0,0,0,0.5)',
    paddingHorizontal: 4,
    borderRadius: 4,
    marginTop: 2,
  },
}); 