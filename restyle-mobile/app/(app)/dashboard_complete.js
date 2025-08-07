import React, { useState, useCallback, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, TextInput, Modal, FlatList, Image, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../shared/authStore';
import * as ImagePicker from 'expo-image-picker';
import * as Linking from 'expo-linking';
import api from '../../shared/api';

// Item Detail Modal Component
const ItemDetailModal = ({ visible, item, onClose }) => {
  const [analysis, setAnalysis] = useState(null);
  const [comps, setComps] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchAnalysis = useCallback(async () => {
    if (!item?.itemId) return;
    
    try {
      setLoading(true);
      setError('');
      
      const mockAnalysis = {
        suggested_price: parseFloat(item.price?.value || 0),
        price_range_low: parseFloat(item.price?.value || 0) * 0.8,
        price_range_high: parseFloat(item.price?.value || 0) * 1.2,
        confidence_score: 'High (5 comparable listings)',
        comps: [
          {
            id: 1,
            title: 'Similar Item 1',
            sold_price: parseFloat(item.price?.value || 0) * 0.9,
            image_url: item.image?.imageUrl,
            source_url: item.itemWebUrl
          },
          {
            id: 2,
            title: 'Similar Item 2',
            sold_price: parseFloat(item.price?.value || 0) * 1.1,
            image_url: item.image?.imageUrl,
            source_url: item.itemWebUrl
          }
        ]
      };
      
      setAnalysis(mockAnalysis);
      setComps(mockAnalysis.comps);
      
    } catch (err) {
      setError('Failed to load analysis data.');
    } finally {
      setLoading(false);
    }
  }, [item]);

  React.useEffect(() => {
    if (visible && item) {
      fetchAnalysis();
    }
  }, [visible, item, fetchAnalysis]);

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Ionicons name="close" size={24} color="#a259f7" />
          </TouchableOpacity>
          <Text style={styles.modalTitle}>Item Analysis</Text>
          <View style={{ width: 24 }} />
        </View>

        <ScrollView style={styles.modalContent} showsVerticalScrollIndicator={false}>
          {loading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#a259f7" />
              <Text style={styles.loadingText}>Loading analysis...</Text>
            </View>
          ) : error ? (
            <View style={styles.errorContainer}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          ) : analysis ? (
            <>
              <View style={styles.itemDetailCard}>
                <Text style={styles.itemDetailTitle}>Listing Details</Text>
                <View style={styles.itemDetailRow}>
                  <Text style={styles.itemDetailLabel}>Suggested Price:</Text>
                  <Text style={styles.itemDetailValue}>${analysis.suggested_price?.toFixed(2)}</Text>
                </View>
                <View style={styles.itemDetailRow}>
                  <Text style={styles.itemDetailLabel}>Price Range:</Text>
                  <Text style={styles.itemDetailValue}>${analysis.price_range_low?.toFixed(2)} - ${analysis.price_range_high?.toFixed(2)}</Text>
                </View>
                <View style={styles.itemDetailRow}>
                  <Text style={styles.itemDetailLabel}>Confidence:</Text>
                  <Text style={styles.itemDetailValue}>{analysis.confidence_score?.replace(/\s*\(.+\)/, '')}</Text>
                </View>
              </View>

              <View style={styles.compsSection}>
                <Text style={styles.compsTitle}>Comparable Listings</Text>
                {comps.map((comp, index) => (
                  <View key={comp.id || index} style={styles.compRow}>
                    {comp.image_url ? (
                      <Image source={{ uri: comp.image_url }} style={styles.compImage} />
                    ) : (
                      <View style={[styles.compImage, { backgroundColor: '#222', alignItems: 'center', justifyContent: 'center' }]}> 
                        <Text style={{ color: '#a259f7', fontSize: 10 }}>No Image</Text>
                      </View>
                    )}
                    <View style={{ flex: 1 }}>
                      <Text style={styles.compTitle} numberOfLines={1}>{comp.title}</Text>
                      <Text style={styles.compPrice}>${comp.sold_price?.toFixed(2)}</Text>
                    </View>
                    {comp.source_url ? (
                      <TouchableOpacity style={styles.compButton} onPress={() => Linking.openURL(comp.source_url)}>
                        <Text style={styles.compButtonText}>View</Text>
                      </TouchableOpacity>
                    ) : null}
                  </View>
                ))}
              </View>
            </>
          ) : null}
        </ScrollView>
      </View>
    </Modal>
  );
};

export default function Dashboard() {
  const router = useRouter();
  const logout = useAuthStore(useCallback(state => state.logout, []));
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  const isInitialized = useAuthStore(state => state.isInitialized);

  useEffect(() => {
    if (isInitialized && !isAuthenticated) {
      router.replace('/(auth)/login');
    }
  }, [isInitialized, isAuthenticated, router]);

  const [searchQuery, setSearchQuery] = useState('');
  const [showCameraOptions, setShowCameraOptions] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState('');
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imageSearchLoading, setImageSearchLoading] = useState(false);
  const [imageAnalysis, setImageAnalysis] = useState(null);
  const [queryVariants, setQueryVariants] = useState([]);
  const [selectedQueryVariant, setSelectedQueryVariant] = useState('');
  const [showItemDetail, setShowItemDetail] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);

  const handleLogout = async () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Logout', 
          style: 'destructive',
          onPress: async () => {
            await logout();
            router.replace('/login');
          }
        }
      ]
    );
  };

  const handleTextSearch = useCallback(async () => {
    if (!searchQuery.trim()) {
      setSearchError('Please enter a search query');
      return;
    }
    
    setSearchLoading(true);
    setSearchError('');
    setHasSearched(true);
    
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 30000);
      
      const response = await api.get('/core/ebay-search/', {
        params: {
          q: searchQuery.trim(),
          limit: 20
        },
        signal: controller.signal
      });
      
      clearTimeout(timeout);
      
      let results = [];
      if (response.data) {
        if (Array.isArray(response.data)) {
          results = response.data;
        } else if (response.data.results && Array.isArray(response.data.results)) {
          results = response.data.results;
        }
      }
      
      setSearchResults(results);
      
    } catch (error) {
      if (error.name === 'AbortError') {
        setSearchError('Search timed out');
      } else {
        setSearchError(error.response?.data?.message || 'Search failed');
      }
    } finally {
      setSearchLoading(false);
    }
  }, [searchQuery]);

  const handleImageSearch = useCallback(async (imageUri) => {
    setImageSearchLoading(true);
    setImageAnalysis(null);
    setQueryVariants([]);
    
    try {
      const formData = new FormData();
      formData.append('image', {
        uri: imageUri,
        type: 'image/jpeg',
        name: 'image.jpg'
      });
      formData.append('use_advanced_ai', 'true');
      
      const response = await api.post('/core/ai/advanced-search/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 45000
      });
      
      if (response.data.status === 'success') {
        setImageAnalysis(response.data.results);
        setQueryVariants(response.data.results.search_queries || []);
      } else {
        Alert.alert('Analysis Failed', response.data.message || 'Failed to analyze image');
      }
    } catch (error) {
      Alert.alert('Error', error.response?.data?.message || 'Image analysis failed');
    } finally {
      setImageSearchLoading(false);
    }
  }, []);

  const openCamera = useCallback(async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Camera permission is required');
      return;
    }
    
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8
    });
    
    if (!result.canceled) {
      setSelectedImage(result.assets[0].uri);
      handleImageSearch(result.assets[0].uri);
    }
    setShowCameraOptions(false);
  }, [handleImageSearch]);

  const openGallery = useCallback(async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Gallery permission is required');
      return;
    }
    
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8
    });
    
    if (!result.canceled) {
      setSelectedImage(result.assets[0].uri);
      handleImageSearch(result.assets[0].uri);
    }
    setShowCameraOptions(false);
  }, [handleImageSearch]);

  const searchWithVariant = useCallback(async (query) => {
    setSelectedQueryVariant(query);
    setSearchQuery(query);
    setSearchLoading(true);
    setSearchError('');
    setHasSearched(true);
    
    try {
      const response = await api.get('/core/ebay-search/', {
        params: {
          q: query,
          limit: 20
        }
      });
      
      let results = [];
      if (response.data?.results) {
        results = response.data.results;
      }
      
      setSearchResults(results);
    } catch (error) {
      setSearchError(error.response?.data?.message || 'Search failed');
    } finally {
      setSearchLoading(false);
    }
  }, []);

  const showItemDetailFunc = useCallback((item) => {
    setSelectedItem(item);
    setShowItemDetail(true);
  }, []);

  if (!isInitialized) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#a259f7" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Restyle AI</Text>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Ionicons name="log-out-outline" size={24} color="#a259f7" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.searchSection}>
          <View style={styles.searchInputContainer}>
            <TextInput
              style={styles.searchInput}
              placeholder="Search for items..."
              placeholderTextColor="#666"
              value={searchQuery}
              onChangeText={setSearchQuery}
              onSubmitEditing={handleTextSearch}
            />
            <TouchableOpacity style={styles.searchButton} onPress={handleTextSearch}>
              <Ionicons name="search" size={20} color="white" />
            </TouchableOpacity>
          </View>
          
          <TouchableOpacity 
            style={styles.cameraButton} 
            onPress={() => setShowCameraOptions(true)}
          >
            <Ionicons name="camera" size={20} color="white" />
            <Text style={styles.cameraButtonText}>AI Search</Text>
          </TouchableOpacity>
        </View>

        {selectedImage && (
          <View style={styles.imageSection}>
            <Image source={{ uri: selectedImage }} style={styles.selectedImage} />
            {imageSearchLoading && (
              <View style={styles.imageOverlay}>
                <ActivityIndicator size="large" color="#a259f7" />
                <Text style={styles.overlayText}>Analyzing...</Text>
              </View>
            )}
          </View>
        )}

        {queryVariants.length > 0 && (
          <View style={styles.variantsSection}>
            <Text style={styles.variantsTitle}>Suggested Searches:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {queryVariants.map((variant, index) => (
                <TouchableOpacity
                  key={index}
                  style={[
                    styles.variantChip,
                    selectedQueryVariant === variant && styles.selectedVariant
                  ]}
                  onPress={() => searchWithVariant(variant)}
                >
                  <Text style={[
                    styles.variantText,
                    selectedQueryVariant === variant && styles.selectedVariantText
                  ]}>
                    {variant}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}

        {searchLoading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#a259f7" />
            <Text style={styles.loadingText}>Searching...</Text>
          </View>
        )}

        {searchError && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{searchError}</Text>
          </View>
        )}

        {hasSearched && !searchLoading && searchResults.length === 0 && !searchError && (
          <View style={styles.noResultsContainer}>
            <Text style={styles.noResultsText}>No results found</Text>
          </View>
        )}

        {searchResults.length > 0 && (
          <View style={styles.resultsSection}>
            <Text style={styles.resultsTitle}>Search Results ({searchResults.length})</Text>
            {searchResults.map((item, index) => (
              <TouchableOpacity
                key={index}
                style={styles.resultItem}
                onPress={() => showItemDetailFunc(item)}
              >
                {item.image?.imageUrl && (
                  <Image source={{ uri: item.image.imageUrl }} style={styles.resultImage} />
                )}
                <View style={styles.resultContent}>
                  <Text style={styles.resultTitle} numberOfLines={2}>
                    {item.title}
                  </Text>
                  {item.price?.value && (
                    <Text style={styles.resultPrice}>
                      ${parseFloat(item.price.value).toFixed(2)}
                    </Text>
                  )}
                  {item.condition && (
                    <Text style={styles.resultCondition}>{item.condition}</Text>
                  )}
                </View>
                <Ionicons name="chevron-forward" size={20} color="#666" />
              </TouchableOpacity>
            ))}
          </View>
        )}
      </ScrollView>

      <Modal
        visible={showCameraOptions}
        transparent
        animationType="fade"
        onRequestClose={() => setShowCameraOptions(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.cameraOptionsModal}>
            <Text style={styles.modalTitle}>Choose Image Source</Text>
            <TouchableOpacity style={styles.modalOption} onPress={openCamera}>
              <Ionicons name="camera" size={24} color="#a259f7" />
              <Text style={styles.modalOptionText}>Take Photo</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.modalOption} onPress={openGallery}>
              <Ionicons name="images" size={24} color="#a259f7" />
              <Text style={styles.modalOptionText}>Choose from Gallery</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.modalCancel} 
              onPress={() => setShowCameraOptions(false)}
            >
              <Text style={styles.modalCancelText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      <ItemDetailModal
        visible={showItemDetail}
        item={selectedItem}
        onClose={() => setShowItemDetail(false)}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000'
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 20,
    backgroundColor: '#111'
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#a259f7'
  },
  logoutButton: {
    padding: 8
  },
  content: {
    flex: 1,
    paddingHorizontal: 20
  },
  searchSection: {
    marginVertical: 20
  },
  searchInputContainer: {
    flexDirection: 'row',
    marginBottom: 15
  },
  searchInput: {
    flex: 1,
    backgroundColor: '#222',
    color: 'white',
    paddingHorizontal: 15,
    paddingVertical: 12,
    borderRadius: 8,
    marginRight: 10
  },
  searchButton: {
    backgroundColor: '#a259f7',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    justifyContent: 'center'
  },
  cameraButton: {
    backgroundColor: '#a259f7',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 15,
    borderRadius: 8
  },
  cameraButtonText: {
    color: 'white',
    fontWeight: 'bold',
    marginLeft: 8
  },
  imageSection: {
    marginBottom: 20,
    position: 'relative'
  },
  selectedImage: {
    width: '100%',
    height: 200,
    borderRadius: 8
  },
  imageOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 8
  },
  overlayText: {
    color: 'white',
    marginTop: 10
  },
  variantsSection: {
    marginBottom: 20
  },
  variantsTitle: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10
  },
  variantChip: {
    backgroundColor: '#333',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 10
  },
  selectedVariant: {
    backgroundColor: '#a259f7'
  },
  variantText: {
    color: 'white',
    fontSize: 14
  },
  selectedVariantText: {
    color: 'white',
    fontWeight: 'bold'
  },
  loadingContainer: {
    alignItems: 'center',
    paddingVertical: 40
  },
  loadingText: {
    color: '#666',
    marginTop: 10
  },
  errorContainer: {
    backgroundColor: '#ff4444',
    padding: 15,
    borderRadius: 8,
    marginVertical: 10
  },
  errorText: {
    color: 'white',
    textAlign: 'center'
  },
  noResultsContainer: {
    alignItems: 'center',
    paddingVertical: 40
  },
  noResultsText: {
    color: '#666',
    fontSize: 16
  },
  resultsSection: {
    marginBottom: 20
  },
  resultsTitle: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15
  },
  resultItem: {
    flexDirection: 'row',
    backgroundColor: '#222',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    alignItems: 'center'
  },
  resultImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
    marginRight: 15
  },
  resultContent: {
    flex: 1
  },
  resultTitle: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5
  },
  resultPrice: {
    color: '#a259f7',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 2
  },
  resultCondition: {
    color: '#666',
    fontSize: 14
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  cameraOptionsModal: {
    backgroundColor: '#222',
    borderRadius: 15,
    padding: 20,
    width: '80%',
    maxWidth: 300
  },
  modalTitle: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20
  },
  modalOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 15,
    paddingHorizontal: 10
  },
  modalOptionText: {
    color: 'white',
    fontSize: 16,
    marginLeft: 15
  },
  modalCancel: {
    marginTop: 10,
    paddingVertical: 15,
    alignItems: 'center'
  },
  modalCancelText: {
    color: '#666',
    fontSize: 16
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#000'
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 20,
    backgroundColor: '#111'
  },
  closeButton: {
    padding: 8
  },
  modalContent: {
    flex: 1,
    paddingHorizontal: 20
  },
  itemDetailCard: {
    backgroundColor: '#222',
    padding: 20,
    borderRadius: 12,
    marginVertical: 15
  },
  itemDetailTitle: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15
  },
  itemDetailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10
  },
  itemDetailLabel: {
    color: '#666',
    fontSize: 14
  },
  itemDetailValue: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold'
  },
  compsSection: {
    marginBottom: 20
  },
  compsTitle: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15
  },
  compRow: {
    flexDirection: 'row',
    backgroundColor: '#222',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    alignItems: 'center'
  },
  compImage: {
    width: 50,
    height: 50,
    borderRadius: 8,
    marginRight: 15
  },
  compTitle: {
    color: 'white',
    fontSize: 14,
    marginBottom: 5
  },
  compPrice: {
    color: '#a259f7',
    fontSize: 14,
    fontWeight: 'bold'
  },
  compButton: {
    backgroundColor: '#a259f7',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6
  },
  compButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold'
  }
});