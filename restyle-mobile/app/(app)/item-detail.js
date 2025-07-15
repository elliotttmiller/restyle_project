import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, Image, StyleSheet, ActivityIndicator, FlatList, TouchableOpacity, Linking } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import axios from 'axios';
import api from '../../shared/api';

export default function ItemDetailScreen() {
  const { itemId } = useLocalSearchParams();
  const router = useRouter();
  const [analysis, setAnalysis] = useState(null);
  const [comps, setComps] = useState([]);
  const [pagination, setPagination] = useState({ page: 1, page_size: 10, has_more: false });
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState('');

  // Fetch analysis and comps (paginated)
  const fetchAnalysis = useCallback(async (page = 1) => {
    if (!itemId) return;
    try {
      if (page === 1) setLoading(true);
      else setLoadingMore(true);
      const res = await axios.get(`http://192.168.0.22:8000/api/core/analysis/${itemId}/status/`, {
        params: { page, page_size: 10 },
        withCredentials: true,
      });
      const data = res.data;
      setAnalysis(data);
      if (page === 1) {
        setComps(data.comps || []);
      } else {
        setComps(prev => [...prev, ...(data.comps || [])]);
      }
      setPagination(data.pagination || { page, page_size: 10, has_more: false });
      setError('');
    } catch (err) {
      setError('Failed to load analysis data.');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [itemId]);

  useEffect(() => {
    fetchAnalysis(1);
  }, [fetchAnalysis]);

  // Load more comps when user scrolls to bottom
  const onLoadMore = useCallback(() => {
    if (loadingMore || !pagination.has_more) return;
    fetchAnalysis(pagination.page + 1);
  }, [loadingMore, pagination, fetchAnalysis]);

  // Render header with all non-listing content
  const renderHeader = useCallback(() => (
    analysis && (
      <>
        <View style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>Listing Details</Text>
          {/* Add your item details here, e.g. image, title, etc. */}
          <View style={styles.row}>
            <Text style={styles.analysisLabel}>Suggested Price:</Text>
            <Text style={styles.analysisValue}>${analysis.suggested_price?.toFixed(2)}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.analysisLabel}>Price Range:</Text>
            <Text style={styles.analysisValue}>${analysis.price_range_low?.toFixed(2)} - ${analysis.price_range_high?.toFixed(2)}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.analysisLabel}>Confidence:</Text>
            <Text style={styles.analysisValue}>{analysis.confidence_score?.replace(/\s*\(.+\)/, '')}</Text>
          </View>
          <View style={[styles.row, { alignItems: 'flex-end', flexWrap: 'wrap' }]}> 
            <Text style={[styles.analysisLabel, { marginTop: 16 }]}>Comparable Listings:</Text>
            {analysis.confidence_score && analysis.confidence_score.match(/\((\d+) comparable listings\)/) && (
              <Text style={styles.compsCount}>
                {analysis.confidence_score.match(/\((\d+) comparable listings\)/)[0]}
              </Text>
            )}
          </View>
        </View>
      </>
    )
  ), [analysis]);

  // Render each comparable listing
  const renderComp = useCallback(({ item: comp }) => (
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
  ), []);

  // Render footer for loading more
  const renderFooter = useCallback(() => (
    loadingMore ? (
      <View style={{ paddingVertical: 20, alignItems: 'center' }}>
        <ActivityIndicator size="small" color="#a259f7" />
        <Text style={{ color: '#888', marginTop: 8 }}>Loading more listings...</Text>
      </View>
    ) : null
  ), [loadingMore]);

  if (loading && comps.length === 0) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}> 
        <ActivityIndicator size="large" color="#a259f7" />
        <Text style={{ color: '#888', marginTop: 16 }}>Loading analysis...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}> 
        <Text style={{ color: '#ff6b6b', fontSize: 16 }}>{error}</Text>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: '#000' }}>
      <TouchableOpacity 
        style={styles.backButton} 
        onPress={() => router.back()}
      >
        <Text style={styles.backButtonText}>← Back</Text>
      </TouchableOpacity>
      <FlatList
        data={comps}
        keyExtractor={(comp, idx) => comp.id ? String(comp.id) : String(idx)}
        renderItem={renderComp}
        ListHeaderComponent={renderHeader}
        ListFooterComponent={renderFooter}
        onEndReached={onLoadMore}
        onEndReachedThreshold={0.2}
        style={{ flex: 1 }}
        contentContainerStyle={{ padding: 24, backgroundColor: '#000' }}
        showsVerticalScrollIndicator={true}
        scrollEnabled={true}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  backButton: {
    position: 'absolute',
    top: 18,
    left: 18,
    zIndex: 10,
    backgroundColor: 'transparent',
    padding: 4,
  },
  backButtonText: {
    color: '#a259f7',
    fontSize: 18,
    fontWeight: 'bold',
  },
  sectionCard: {
    width: '100%',
    backgroundColor: '#111',
    borderRadius: 16,
    padding: 20,
    marginBottom: 28,
    shadowColor: '#a259f7',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.18,
    shadowRadius: 8,
    elevation: 3,
    alignItems: 'flex-start',
    marginTop: 48, // to make space for back button
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#a259f7',
    marginBottom: 16,
    alignSelf: 'flex-start',
  },
  image: {
    width: '100%',
    height: 220,
    borderRadius: 12,
    marginBottom: 18,
    backgroundColor: '#222',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'left',
    color: '#fff',
    alignSelf: 'flex-start',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    flexWrap: 'wrap',
  },
  label: {
    fontWeight: '600',
    color: '#a259f7',
    marginRight: 8,
    fontSize: 15,
  },
  value: {
    color: '#fff',
    fontSize: 15,
    flexShrink: 1,
  },
  button: {
    backgroundColor: '#a259f7',
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 28,
    alignItems: 'center',
    marginTop: 18,
    alignSelf: 'flex-start',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  analysisCard: {
    marginTop: 0,
    width: '100%',
    backgroundColor: '#111',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#a259f7',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.18,
    shadowRadius: 8,
    elevation: 3,
    alignItems: 'flex-start',
    marginBottom: 32,
  },
  analysisLabel: {
    color: '#a259f7',
    fontWeight: '600',
    fontSize: 15,
    marginRight: 8,
  },
  analysisValue: {
    color: '#fff',
    fontSize: 17,
    fontWeight: 'bold',
  },
  compsCount: {
    color: '#a259f7',
    fontSize: 13,
    fontWeight: '500',
    marginLeft: 6,
    marginBottom: 2,
  },
  compRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#222',
    borderRadius: 8,
    padding: 8,
    marginRight: 12,
    minWidth: 180,
    maxWidth: 220,
  },
  compImage: {
    width: 48,
    height: 48,
    borderRadius: 6,
    marginRight: 10,
    backgroundColor: '#222',
  },
  compTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 2,
  },
  compPrice: {
    color: '#a259f7',
    fontSize: 14,
    fontWeight: 'bold',
  },
  compButton: {
    backgroundColor: '#a259f7',
    borderRadius: 6,
    paddingVertical: 6,
    paddingHorizontal: 14,
    marginLeft: 8,
  },
  compButtonText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: 'bold',
  },
  error: {
    color: '#ff4d6d',
    fontSize: 18,
    marginBottom: 20,
    textAlign: 'center',
  },
}); 