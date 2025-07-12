import React, { useState, useCallback } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, TextInput, Modal, FlatList, Image, ActivityIndicator, RefreshControl } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../shared/authStore';
import * as ImagePicker from 'expo-image-picker';
import * as Linking from 'expo-linking';
import api from '../shared/api';

export default function Dashboard() {
  const router = useRouter();
  const { logout } = useAuthStore();
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
        setImageAnalysis(null);
        setQueryVariants([]);
        setHasSearched(true);
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
        setImageAnalysis(null);
        setQueryVariants([]);
        setHasSearched(true);
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
      
      const searchResponse = await api.post('/core/ai/advanced-search/', formData, {
        headers: {
          // Don't set Content-Type - let the browser set it with boundary
        },
      });
      
      const responseData = searchResponse.data;
      
      setSearchResults(responseData.results || []);
      setImageAnalysis(responseData.analysis || null);
      setQueryVariants(responseData.queries?.variants || []);
      setSelectedQueryVariant(responseData.queries?.primary || '');
      
      if (responseData.results && responseData.results.length > 0) {
        Alert.alert(
          'AI Search Complete', 
          `Found ${responseData.results.length} items!`
        );
      }
      
    } catch (error) {
      console.error('Image search failed:', error);
      Alert.alert('Error', 'Image search failed. Please try again.');
    } finally {
      setImageSearchLoading(false);
    }
  };

  const handleCameraOption = (option) => {
    setShowCameraOptions(false);
    switch (option) {
      case 'camera':
        takePhoto();
        break;
      case 'gallery':
        pickImage();
        break;
    }
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
          console.log('Navigating to item detail with item:', item);
          router.push({ pathname: '/item-detail', params: { itemId: item.itemId } });
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
      <View style={styles.header}>
        <Text style={styles.title}>Restyle</Text>
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
        <Text style={styles.searchTitle}>Search</Text>
        <View style={styles.searchContainer}>
          <TouchableOpacity 
            style={styles.cameraButton} 
            onPress={() => setShowCameraOptions(true)}
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
              {searchLoading || imageSearchLoading ? 'Searching...' : `Results (${searchResults.length})`}
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

      {/* Quick Actions - Only show when no search has been performed */}
      {!hasSearched && (
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Quick Actions</Text>
            <View style={styles.actionButtons}>
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => setShowCameraOptions(true)}
              >
                <Ionicons name="camera" size={24} color="#a259f7" />
                <Text style={styles.actionButtonText}>Camera Search</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => setShowCameraOptions(true)}
              >
                <Ionicons name="images" size={24} color="#a259f7" />
                <Text style={styles.actionButtonText}>Gallery Search</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Welcome Information */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Welcome to Restyle</Text>
            <View style={styles.infoCard}>
              <Text style={styles.infoText}>
                <Text style={styles.infoLabel}>AI-Powered Search:</Text> Use our advanced AI system to find similar items on eBay
              </Text>
              <Text style={styles.infoText}>
                <Text style={styles.infoLabel}>Multiple Search Methods:</Text> Camera, gallery, text search, and AI-powered queries
              </Text>
              <Text style={styles.infoText}>
                <Text style={styles.infoLabel}>Real-time Results:</Text> Get live eBay listings with prices and details
              </Text>
              <Text style={styles.infoText}>
                <Text style={styles.infoLabel}>Smart Analysis:</Text> Our AI analyzes images and finds the best matches
              </Text>
            </View>
          </View>
        </ScrollView>
      )}

      {/* Camera Options Modal */}
      <Modal
        visible={showCameraOptions}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setShowCameraOptions(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Choose Search Method</Text>
            
            <TouchableOpacity 
              style={styles.modalOption} 
              onPress={() => handleCameraOption('camera')}
            >
              <Ionicons name="camera" size={24} color="#a259f7" />
              <Text style={styles.modalOptionText}>Take Picture</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.modalOption} 
              onPress={() => handleCameraOption('gallery')}
            >
              <Ionicons name="images" size={24} color="#a259f7" />
              <Text style={styles.modalOptionText}>Gallery</Text>
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
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#a259f7',
  },
  headerButtons: {
    flexDirection: 'row',
    gap: 10,
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
  searchTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 12,
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
  content: {
    flex: 1,
    padding: 20,
  },
  section: {
    marginBottom: 25,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 15,
  },
  actionButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionButton: {
    backgroundColor: '#111',
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
    width: '48%',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#333',
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
    textAlign: 'center',
    marginTop: 8,
  },
  infoCard: {
    backgroundColor: '#111',
    borderRadius: 12,
    padding: 20,
    borderWidth: 1,
    borderColor: '#333',
  },
  infoText: {
    fontSize: 14,
    color: '#ccc',
    marginBottom: 12,
    lineHeight: 20,
  },
  infoLabel: {
    fontWeight: '600',
    color: '#a259f7',
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
});
