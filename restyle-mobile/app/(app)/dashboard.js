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
      
      // For now, we'll create a mock analysis since the backend endpoint might not exist
      // In a real implementation, you'd call the actual API
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

  const renderComp = ({ item: comp }) => (
    <View style={styles.compRow}>
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
  );

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.modalContainer}>
        {/* Header */}
        <View style={styles.modalHeader}>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Ionicons name="close" size={24} color="#a259f7" />
          </TouchableOpacity>
          <Text style={styles.modalTitle}>Item Analysis</Text>
          <View style={{ width: 24 }} />
        </View>

        {/* Content */}
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
              {/* Item Details */}
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

              {/* Comparable Listings */}
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
  // Use a memoized selector for logout
  const logout = useAuthStore(useCallback(state => state.logout, []));
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  const isInitialized = useAuthStore(state => state.isInitialized);
  const token = useAuthStore((state) => state.token);

  useEffect(() => {
    if (isInitialized && !isAuthenticated) {
      router.replace('/(auth)/login');
    }
  }, [isInitialized, isAuthenticated, router]);

  const [searchQuery, setSearchQuery] = useState('');
  const [showCameraOptions, setShowCameraOptions] = useState(false);
  
  // Search results state
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState('');
  const [hasSearched, setHasSearched] = useState(false);
  
  // Image search state
  const [selectedImage, setSelectedImage] = useState(null);
  const [imageSearchLoading, setImageSearchLoading] = useState(false);
  const [imageAnalysis, setImageAnalysis] = useState(null);
  const [queryVariants, setQueryVariants] = useState([]);
  const [selectedQueryVariant, setSelectedQueryVariant] = useState('');
  
  // Item detail modal state
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

  // Text search functionality
  const handleTextSearch = useCallback(async () => {
    if (!searchQuery.trim()) return;
    
    setSearchLoading(true);
    setSearchError('');
    setHasSearched(true);
    
    try {
      console.log('Searching with query:', searchQuery.trim());
      const response = await api.get('/core/ebay-search/', {
        params: {
          q: searchQuery.trim(),
          limit: 20,
          offset: 0,
        },
      });
      
      console.log('API response:', response.data);
      const results = response.data.results || response.data;
      setSearchResults(results);
      
    } catch (err) {
      console.error('Search failed:', err);
      setSearchError(err.response?.data?.error || 'Search failed. Please try again.');
    } finally {
      setSearchLoading(false);
    }
  }, [searchQuery]);

  // Image search functionality
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
    console.log('takePhoto called');
    const hasPermission = await requestPermissions();
    if (!hasPermission) {
      Alert.alert('Permission Denied', 'Camera or library permission not granted.');
      return;
    }
    console.log('Launching camera...');
    console.log('ImagePicker available:', !!ImagePicker);
    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images', 'videos'],
        allowsEditing: false,
        quality: 0.8,
      });
      console.log('Camera result:', result);
      if (!result.canceled && result.assets && result.assets[0]) {
        console.log('Photo taken successfully:', result.assets[0]);
        setSelectedImage(result.assets[0]);
        setSearchResults([]);
        setImageAnalysis(null);
        setQueryVariants([]);
        setHasSearched(true);
      } else {
        console.log('Camera was canceled or no image selected');
        console.log('Result canceled:', result.canceled);
        console.log('Result assets:', result.assets);
      }
    } catch (error) {
      console.error('Error taking photo:', error);
      Alert.alert('Error', 'Failed to take photo: ' + error.message);
    }
  };

  const pickImage = async () => {
    console.log('pickImage called');
    const hasPermission = await requestPermissions();
    if (!hasPermission) {
      Alert.alert('Permission Denied', 'Camera or library permission not granted.');
      return;
    }
    console.log('Launching image library...');
    console.log('ImagePicker available:', !!ImagePicker);
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images', 'videos'],
        allowsEditing: false,
        quality: 0.8,
      });
      console.log('Gallery result:', result);
      if (!result.canceled && result.assets && result.assets[0]) {
        console.log('Image picked successfully:', result.assets[0]);
        setSelectedImage(result.assets[0]);
        setSearchResults([]);
        setImageAnalysis(null);
        setQueryVariants([]);
        setHasSearched(true);
      } else {
        console.log('Gallery was canceled or no image selected');
        console.log('Result canceled:', result.canceled);
        console.log('Result assets:', result.assets);
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Error', 'Failed to pick image: ' + error.message);
    }
  };

  const searchByImage = async (queryOverride = null) => {
    if (!selectedImage) {
      Alert.alert('No Image', 'Please select or take a photo first.');
      return;
    }
    
    setImageSearchLoading(true);
    try {
      console.log('Selected image URI:', selectedImage.uri);
      
      // Create FormData with proper file object
      const formData = new FormData();
      
      const file = {
        uri: selectedImage.uri,
        type: 'image/jpeg',
        name: 'image.jpg',
      };
      
      formData.append('image', file);
      formData.append('image_type', 'image/jpeg');
      
      const queryToSend = queryOverride !== null ? queryOverride : searchQuery;
      if (queryToSend) {
        formData.append('query', queryToSend);
      }
      
      console.log('Sending image to advanced AI backend...');
      
      // Update the endpoint to the correct backend path
      const fullUrl = api.defaults.baseURL + '/api/core/ai/advanced-search/';
      console.log('Full image search URL:', fullUrl);
      console.log('Auth token:', token);
      const searchResponse = await api.post('core/ai/advanced-search/', formData, {
        headers: {
          Authorization: token ? `Bearer ${token}` : undefined,
          // Let axios set Content-Type
        },
      });
      const responseData = searchResponse.data;
      setSearchResults(responseData.analysis_results?.visually_ranked_comps || responseData.results || []);
      setImageAnalysis(responseData.analysis_results || responseData.analysis || null);
      setQueryVariants(responseData.queries?.variants || []);
      setSelectedQueryVariant(responseData.queries?.primary || '');
      // Removed pop-up: Alert for 'AI Search Complete' with number of items found
      // if ((responseData.analysis_results?.visually_ranked_comps || responseData.results || []).length > 0) {
      //   Alert.alert('AI Search Complete', `Found ${(responseData.analysis_results?.visually_ranked_comps?.length || responseData.results?.length || 0)} items!`);
      // }

    } catch (error) {
      console.error('Image search failed:', error);
      Alert.alert('Error', 'Image search failed. Please try again.');
    } finally {
      setImageSearchLoading(false);
    }
  };

  const handleCameraOption = (option) => {
    console.log('handleCameraOption called with:', option);
    setShowCameraOptions(false);
    setTimeout(() => {
      console.log('handleCameraOption timeout fired for:', option);
      if (option === 'camera') {
        console.log('takePhoto() will be called');
        takePhoto();
      } else if (option === 'gallery') {
        console.log('pickImage() will be called');
        pickImage();
      }
    }, 800); // Increased delay for iOS modal closing
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
    setSearchError('');
    setHasSearched(false);
    setSelectedImage(null);
    setImageAnalysis(null);
    setQueryVariants([]);
  };

  const renderSearchResult = ({ item, index }) => (
    <View style={styles.searchResultItem}>
      <TouchableOpacity
        style={styles.searchResultContent}
        onPress={() => {
          console.log('Opening item detail modal for item:', item);
          setSelectedItem(item);
          setShowItemDetail(true);
        }}
      >
        {item.image?.imageUrl ? (
          <Image
            source={{ uri: item.image.imageUrl }}
            style={styles.searchResultImage}
            resizeMode="cover"
          />
        ) : (
          <View style={styles.searchResultImagePlaceholder}>
            <Text style={styles.searchResultImagePlaceholderText}>No Image</Text>
          </View>
        )}
        <View style={styles.searchResultInfo}>
          <Text style={styles.searchResultTitle} numberOfLines={2}>
            {item.title || 'No title'}
          </Text>
          {item.price?.value && (
            <Text style={styles.searchResultPrice}>
              ${item.price.value}
            </Text>
          )}
          {item.seller?.username && (
            <Text style={styles.searchResultSeller}>
              by {item.seller.username}
      </Text>
          )}
    </View>
      </TouchableOpacity>
      {(item.itemAffiliateWebUrl || item.itemWebUrl) && (
        <TouchableOpacity
          onPress={() => {
            Linking.openURL(item.itemAffiliateWebUrl || item.itemWebUrl);
          }}
          style={styles.searchResultEbayButton}
        >
          <Text style={styles.searchResultEbayButtonText}>eBay</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  const renderQueryVariant = (variant, index) => (
    <TouchableOpacity
      key={index}
      style={[
        styles.queryVariantButton,
        selectedQueryVariant === variant.query && styles.queryVariantButtonSelected
      ]}
      onPress={() => {
        setSelectedQueryVariant(variant.query);
        searchByImage(variant.query);
      }}
    >
      <Text style={[
        styles.queryVariantText,
        selectedQueryVariant === variant.query && styles.queryVariantTextSelected
      ]}>
        {variant.query}
      </Text>
      {variant.confidence && (
        <Text style={styles.queryVariantConfidence}>
          {Math.round(variant.confidence * 100)}%
        </Text>
      )}
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft} />
        <Text style={styles.headerTitle}>Restyle</Text>
        <View style={styles.headerButtons}>
          <TouchableOpacity style={styles.aiDashboardButton} onPress={() => router.push('/ai-dashboard')}>
            <Ionicons name="analytics" size={20} color="#a259f7" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Ionicons name="log-out" size={20} color="#fff" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Search Section */}
      <View style={styles.searchSection}>
        <View style={styles.searchContainer}>
          <TouchableOpacity 
            style={styles.cameraButton} 
            onPress={() => {
              console.log('Camera button pressed!');
              setShowCameraOptions(true);
            }}
          >
            <Ionicons name="camera" size={20} color="#a259f7" />
          </TouchableOpacity>
          <TextInput
            style={styles.searchInput}
            placeholder="Search for items..."
            placeholderTextColor="#666"
            value={searchQuery}
            onChangeText={setSearchQuery}
            onSubmitEditing={handleTextSearch}
            returnKeyType="search"
          />
          <TouchableOpacity style={styles.searchButton} onPress={handleTextSearch}>
            <Ionicons name="search" size={20} color="#a259f7" />
          </TouchableOpacity>
        </View>
        </View>

      {/* Selected Image Display */}
      {selectedImage && (
        <View style={styles.selectedImageContainer}>
          <Image source={{ uri: selectedImage.uri }} style={styles.selectedImage} />
          <View style={styles.selectedImageActions}>
            <TouchableOpacity 
              style={styles.searchImageButton} 
              onPress={() => searchByImage()}
              disabled={imageSearchLoading}
            >
              {imageSearchLoading ? (
                <ActivityIndicator size="small" color="#fff" />
              ) : (
                <Ionicons name="search" size={20} color="#fff" />
              )}
              <Text style={styles.searchImageButtonText}>Search Image</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.clearImageButton} 
              onPress={() => setSelectedImage(null)}
            >
              <Ionicons name="close" size={20} color="#fff" />
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* Query Variants */}
      {queryVariants.length > 0 && (
        <View style={styles.queryVariantsContainer}>
          <Text style={styles.queryVariantsTitle}>AI Suggested Queries:</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {queryVariants.map((variant, index) => renderQueryVariant(variant, index))}
          </ScrollView>
        </View>
      )}

      {/* Search Results */}
      {hasSearched && (
        <View style={styles.resultsSection}>
          <View style={styles.resultsHeader}>
            <Text style={styles.resultsTitle}>
              {selectedImage ? 'Image Search Results' : 'Text Search Results'}
              {searchLoading || imageSearchLoading ? ' (Searching...)' : ` (${searchResults.length})`}
            </Text>
            {hasSearched && (
              <TouchableOpacity style={styles.clearButton} onPress={clearSearch}>
                <Ionicons name="close" size={16} color="#888" />
                <Text style={styles.clearButtonText}>Clear</Text>
              </TouchableOpacity>
            )}
          </View>
          
          {searchLoading || imageSearchLoading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#a259f7" />
              <Text style={styles.loadingText}>
                {selectedImage ? 'Analyzing image...' : 'Searching eBay...'}
              </Text>
            </View>
          ) : searchError ? (
            <View style={styles.errorContainer}>
              <Text style={styles.errorText}>{searchError}</Text>
            </View>
          ) : searchResults.length > 0 ? (
            <FlatList
              data={searchResults}
              renderItem={renderSearchResult}
              keyExtractor={(item, index) => item.itemId || `item-${index}`}
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.resultsList}
            />
          ) : hasSearched ? (
            <View style={styles.noResultsContainer}>
              <Text style={styles.noResultsText}>No results found</Text>
            </View>
          ) : null}
        </View>
      )}

      {/* Camera Options Modal */}
      <Modal
        visible={showCameraOptions}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setShowCameraOptions(false)}
        onShow={() => console.log('Camera modal shown!')}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.cameraModalContent}>
            <Text style={styles.modalTitle}>Choose Search Method</Text>
            
            <TouchableOpacity
              style={styles.modalOption} 
              onPress={() => {
                console.log('Take Picture option selected!');
                handleCameraOption('camera');
              }}
            >
              <Ionicons name="camera" size={24} color="#a259f7" />
              <Text style={styles.modalOptionText}>Take Picture</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.modalOption} 
              onPress={() => handleCameraOption('gallery')}
            >
              <Ionicons name="images" size={24} color="#a259f7" />
              <Text style={styles.modalOptionText}>Library</Text>
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

      {/* Item Detail Modal */}
      <ItemDetailModal
        visible={showItemDetail}
        item={selectedItem}
        onClose={() => {
          setShowItemDetail(false);
          setSelectedItem(null);
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 20,
    backgroundColor: '#000',
  },
  headerLeft: {
    width: 80, // Same width as headerButtons to balance the layout
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#a259f7',
    flex: 1,
    textAlign: 'center',
  },
  headerButtons: {
    flexDirection: 'row',
    gap: 10,
  },
  debugButton: {
    padding: 10,
    backgroundColor: '#111',
    borderRadius: 8,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#333',
  },
  aiDashboardButton: {
    padding: 10,
    backgroundColor: '#111',
    borderRadius: 8,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#333',
  },
  logoutButton: {
    padding: 10,
    backgroundColor: '#F44336',
    borderRadius: 8,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchSection: {
    paddingHorizontal: 20,
    paddingBottom: 20,
    backgroundColor: '#000',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#111',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderWidth: 1,
    borderColor: '#333',
  },
  cameraButton: {
    padding: 8,
    marginRight: 12,
  },
  searchInput: {
    flex: 1,
    color: '#fff',
    fontSize: 16,
    paddingVertical: 8,
  },
  searchButton: {
    padding: 8,
    marginLeft: 12,
  },
  selectedImageContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  selectedImage: {
    width: '100%',
    height: 200,
    borderRadius: 12,
    marginBottom: 12,
  },
  selectedImageActions: {
    flexDirection: 'row',
    gap: 12,
  },
  searchImageButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#a259f7',
    paddingVertical: 12,
    borderRadius: 8,
    gap: 8,
  },
  searchImageButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  clearImageButton: {
    backgroundColor: '#333',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  queryVariantsContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  queryVariantsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 12,
  },
  queryVariantButton: {
    backgroundColor: '#111',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#333',
  },
  queryVariantButtonSelected: {
    backgroundColor: '#a259f7',
    borderColor: '#a259f7',
  },
  queryVariantText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  queryVariantTextSelected: {
    color: '#fff',
  },
  queryVariantConfidence: {
    color: '#888',
    fontSize: 12,
    marginTop: 2,
  },
  resultsSection: {
    flex: 1,
    paddingHorizontal: 20,
  },
  resultsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  resultsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  clearButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  clearButtonText: {
    color: '#888',
    fontSize: 14,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  loadingText: {
    color: '#888',
    fontSize: 16,
    marginTop: 12,
  },
  errorContainer: {
    padding: 20,
    alignItems: 'center',
  },
  errorText: {
    color: '#F44336',
    fontSize: 16,
    textAlign: 'center',
  },
  noResultsContainer: {
    padding: 40,
    alignItems: 'center',
  },
  noResultsText: {
    color: '#888',
    fontSize: 16,
  },
  resultsList: {
    paddingBottom: 20,
  },
  searchResultItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomColor: '#2a2a2a',
    borderBottomWidth: 1,
    backgroundColor: '#1a1a1a',
    marginHorizontal: 16,
    marginVertical: 4,
    borderRadius: 12,
  },
  searchResultContent: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  searchResultImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
    marginRight: 16,
    backgroundColor: '#2a2a2a',
  },
  searchResultImagePlaceholder: {
    width: 60,
    height: 60,
    borderRadius: 8,
    marginRight: 16,
    backgroundColor: '#2a2a2a',
    alignItems: 'center',
    justifyContent: 'center',
  },
  searchResultImagePlaceholderText: {
    color: '#666',
    fontSize: 10,
  },
  searchResultInfo: {
    flex: 1,
  },
  searchResultTitle: {
    fontSize: 16,
    color: '#fff',
    fontWeight: '500',
    marginBottom: 4,
    lineHeight: 20,
  },
  searchResultPrice: {
    fontSize: 18,
    color: '#8B5CF6',
    fontWeight: 'bold',
  },
  searchResultSeller: {
    fontSize: 12,
    color: '#888',
    marginTop: 2,
  },
  searchResultEbayButton: {
    marginLeft: 12,
    padding: 8,
    backgroundColor: '#8B5CF6',
    borderRadius: 6,
    minWidth: 50,
    alignItems: 'center',
  },
  searchResultEbayButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#111',
    borderRadius: 16,
    padding: 24,
    width: '80%',
    borderWidth: 1,
    borderColor: '#333',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 20,
  },
  modalOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 20,
    marginBottom: 8,
    borderRadius: 8,
    backgroundColor: '#222',
  },
  modalOptionText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '500',
    marginLeft: 12,
  },
  modalCancel: {
    marginTop: 16,
    paddingVertical: 12,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#333',
    paddingTop: 16,
  },
  modalCancelText: {
    color: '#888',
    fontSize: 16,
    fontWeight: '500',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#000',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 20,
    backgroundColor: '#000',
  },
  closeButton: {
    padding: 10,
  },
  itemDetailCard: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#333',
  },
  itemDetailTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 12,
  },
  itemDetailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  itemDetailLabel: {
    color: '#888',
    fontSize: 14,
  },
  itemDetailValue: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  compsSection: {
    marginTop: 16,
  },
  compsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 12,
  },
  compRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomColor: '#2a2a2a',
    borderBottomWidth: 1,
    backgroundColor: '#1a1a1a',
    marginHorizontal: 16,
    marginVertical: 4,
    borderRadius: 12,
  },
  compImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
    marginRight: 16,
    backgroundColor: '#2a2a2a',
  },
  compTitle: {
    fontSize: 16,
    color: '#fff',
    fontWeight: '500',
    marginBottom: 4,
  },
  compPrice: {
    fontSize: 18,
    color: '#8B5CF6',
    fontWeight: 'bold',
  },
  compButton: {
    marginLeft: 12,
    padding: 8,
    backgroundColor: '#8B5CF6',
    borderRadius: 6,
    minWidth: 50,
    alignItems: 'center',
  },
  compButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    flex: 1,
    textAlign: 'center',
  },
  cameraModalContent: {
    backgroundColor: '#111',
    borderRadius: 12,
    padding: 20,
    margin: 20,
    borderWidth: 1,
    borderColor: '#333',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  modalOptionText: {
    color: '#fff',
    fontSize: 16,
    marginLeft: 15,
  },
  modalCancel: {
    paddingVertical: 15,
    alignItems: 'center',
  },
  modalCancelText: {
    color: '#a259f7',
    fontSize: 16,
    fontWeight: '600',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#000',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 20,
    backgroundColor: '#000',
  },
  closeButton: {
    padding: 10,
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 50,
  },
  loadingText: {
    color: '#888',
    fontSize: 16,
    marginTop: 16,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 50,
  },
  errorText: {
    color: '#ff6b6b',
    fontSize: 16,
  },
}); 