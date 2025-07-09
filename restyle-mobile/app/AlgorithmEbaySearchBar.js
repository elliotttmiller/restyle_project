import React, { useState, useCallback } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList, Image, ActivityIndicator, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import api from '../shared/api';
import { useRouter } from 'expo-router';
import * as Linking from 'expo-linking';

export default function AlgorithmEbaySearchBar() {
  console.log('AlgorithmEbaySearchBar: render called');
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const router = useRouter();

  const searchItems = async (searchQuery, searchOffset = 0, append = false) => {
    if (searchOffset === 0) {
      setLoading(true);
    } else {
      setLoadingMore(true);
    }
    
    setError('');
    
    try {
      console.log('Searching with query:', searchQuery, 'offset:', searchOffset);
      const response = await api.get('/core/ebay-search/', {
        params: {
          q: searchQuery.trim(),
          limit: 20,
          offset: searchOffset,
        },
      });
      
      console.log('API response:', response.data);
      const newResults = response.data.results || response.data;
      
      if (append) {
        setResults(prev => [...prev, ...newResults]);
      } else {
        setResults(newResults);
      }
      
      // Check if there are more results
      setHasMore(newResults.length === 20);
      setOffset(searchOffset + newResults.length);
      
    } catch (err) {
      console.error('Search failed:', err);
      if (err.response) {
        console.error('Error response data:', err.response.data);
      }
      setError(err.response?.data?.error || 'Search failed. Please try again.');
    } finally {
      setLoading(false);
      setLoadingMore(false);
      setRefreshing(false);
    }
  };

  const handleSearch = useCallback(() => {
    if (!query.trim()) return;
    
    setOffset(0);
    setHasMore(true);
    searchItems(query, 0, false);
  }, [query]);

  const handleLoadMore = useCallback(() => {
    if (!loadingMore && hasMore && query.trim()) {
      searchItems(query, offset, true);
    }
  }, [loadingMore, hasMore, query, offset]);

  const handleRefresh = useCallback(() => {
    setRefreshing(true);
    setOffset(0);
    setHasMore(true);
    searchItems(query, 0, false);
  }, [query]);

  const handleCameraSearch = useCallback(() => {
    // Navigate to camera search screen
    router.push('/camera-search');
  }, [router]);

  const renderItem = ({ item, index }) => (
    <View style={{
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
    }}>
      <TouchableOpacity
        style={{ flex: 1, flexDirection: 'row', alignItems: 'center' }}
        onPress={() => {
          router.push({ pathname: '/item-detail', params: { item: JSON.stringify(item) } });
        }}
      >
        {item.image?.imageUrl ? (
          <Image
            source={{ uri: item.image.imageUrl }}
            style={{ 
              width: 60, 
              height: 60, 
              borderRadius: 8, 
              marginRight: 16, 
              backgroundColor: '#2a2a2a' 
            }}
            resizeMode="cover"
          />
        ) : (
          <View style={{ 
            width: 60, 
            height: 60, 
            borderRadius: 8, 
            marginRight: 16, 
            backgroundColor: '#2a2a2a', 
            alignItems: 'center', 
            justifyContent: 'center' 
          }}>
            <Text style={{ color: '#666', fontSize: 10 }}>No Image</Text>
          </View>
        )}
        <View style={{ flex: 1 }}>
          <Text style={{ 
            fontSize: 16, 
            color: '#fff', 
            fontWeight: '500',
            marginBottom: 4,
            lineHeight: 20
          }} numberOfLines={2}>
            {item.title || 'No title'}
          </Text>
          {item.price?.value && (
            <Text style={{ 
              fontSize: 18, 
              color: '#8B5CF6', 
              fontWeight: 'bold' 
            }}>
              ${item.price.value}
            </Text>
          )}
          {item.seller?.username && (
            <Text style={{ 
              fontSize: 12, 
              color: '#888', 
              marginTop: 2 
            }}>
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
          style={{ 
            marginLeft: 12, 
            padding: 8,
            backgroundColor: '#8B5CF6',
            borderRadius: 6,
            minWidth: 50,
            alignItems: 'center'
          }}
        >
          <Text style={{ color: '#fff', fontSize: 12, fontWeight: '600' }}>eBay</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  const renderFooter = () => {
    if (!loadingMore) return null;
    return (
      <View style={{ paddingVertical: 20, alignItems: 'center' }}>
        <ActivityIndicator size="small" color="#8B5CF6" />
        <Text style={{ color: '#888', marginTop: 8 }}>Loading more items...</Text>
      </View>
    );
  };

  return (
    <View style={{ 
      flex: 1, 
      backgroundColor: '#000',
      paddingTop: 20
    }}>
      <View style={{ paddingHorizontal: 20, paddingBottom: 20 }}>
        <Text style={{ 
          fontSize: 32, 
          fontWeight: '700', 
          marginBottom: 24, 
          color: '#fff',
          textAlign: 'center'
        }}>
          Search
        </Text>
        
        <View style={{ 
          flexDirection: 'row', 
          alignItems: 'center', 
          marginBottom: 16 
        }}>
          <TouchableOpacity
            onPress={handleCameraSearch}
            style={{
              backgroundColor: '#8B5CF6',
              width: 50,
              height: 50,
              borderRadius: 12,
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: 12,
            }}
          >
            <Ionicons name="camera" size={24} color="#fff" />
          </TouchableOpacity>
          <TextInput
            style={{
              flex: 1,
              height: 50,
              borderColor: '#333',
              borderWidth: 1,
              borderRadius: 12,
              paddingHorizontal: 16,
              fontSize: 16,
              backgroundColor: '#1a1a1a',
              color: '#fff',
              marginRight: 12,
            }}
            placeholder="Search for items..."
            placeholderTextColor="#666"
            value={query}
            onChangeText={setQuery}
            onSubmitEditing={handleSearch}
            returnKeyType="search"
          />
          <TouchableOpacity
            onPress={handleSearch}
            style={{
              backgroundColor: '#8B5CF6',
              paddingHorizontal: 20,
              paddingVertical: 12,
              borderRadius: 12,
              minWidth: 80,
              alignItems: 'center'
            }}
          >
            <Text style={{ color: '#fff', fontSize: 16, fontWeight: '600' }}>
              Search
            </Text>
          </TouchableOpacity>
        </View>
        
        {error ? (
          <Text style={{ 
            color: '#ff6b6b', 
            marginTop: 8, 
            textAlign: 'center',
            backgroundColor: '#2a1a1a',
            padding: 12,
            borderRadius: 8
          }}>
            {error}
          </Text>
        ) : null}
      </View>

      {loading && results.length === 0 ? (
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
          <ActivityIndicator size="large" color="#8B5CF6" />
          <Text style={{ color: '#888', marginTop: 16 }}>Searching...</Text>
        </View>
      ) : (
        <FlatList
          data={results}
          keyExtractor={(item, idx) => (item.itemId ? String(item.itemId) : String(idx))}
          renderItem={renderItem}
          onEndReached={handleLoadMore}
          onEndReachedThreshold={0.1}
          ListFooterComponent={renderFooter}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
              tintColor="#8B5CF6"
              colors={["#8B5CF6"]}
            />
          }
          ListEmptyComponent={
            !loading && (
              <View style={{ 
                flex: 1, 
                justifyContent: 'center', 
                alignItems: 'center',
                paddingVertical: 60
              }}>
                <Text style={{ color: '#666', fontSize: 16, textAlign: 'center' }}>
                  {query.trim() ? 'No results found' : 'Search for items to get started'}
                </Text>
              </View>
            )
          }
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{ paddingBottom: 20 }}
        />
      )}
    </View>
  );
} 