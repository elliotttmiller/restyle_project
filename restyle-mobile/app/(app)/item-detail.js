import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, Image, StyleSheet, ActivityIndicator, FlatList, TouchableOpacity, Linking, useWindowDimensions } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import axios from 'axios';
import api from '../../shared/api';

export default function ItemDetailScreen() {
  const { itemId } = useLocalSearchParams();
  const router = useRouter();
  const [analysis, setAnalysis] = useState(null);
  const [comps, setComps] = useState([]);
  const [compsToShow, setCompsToShow] = useState(20);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { width } = useWindowDimensions();
  const isTablet = width > 600;

  // Fetch analysis and all comps at once
  const fetchAnalysis = useCallback(async () => {
    if (!itemId) return;
    try {
      setLoading(true);
      const res = await axios.get(`http://192.168.0.22:8000/api/core/analysis/${itemId}/status/`, {
        withCredentials: true,
      });
      const data = res.data;
      setAnalysis(data);
      setComps(data.comps || []);
      setError('');
    } catch (err) {
      setError('Failed to load analysis data.');
    } finally {
      setLoading(false);
    }
  }, [itemId]);

  useEffect(() => {
    fetchAnalysis();
  }, [fetchAnalysis]);

  // Infinite scroll: load more comps on scroll
  const onLoadMore = useCallback(() => {
    if (compsToShow < comps.length) {
      setCompsToShow(prev => Math.min(prev + 20, comps.length));
    }
  }, [compsToShow, comps.length]);

  // Render header with all non-listing content
  const renderHeader = useCallback(() => (
    analysis && (
      <>
        <View style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>Listing Details</Text>
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
            {analysis.comps && (
              <Text style={styles.compsCount}>{analysis.comps.length} found</Text>
            )}
          </View>
        </View>
        <Text style={styles.compsHeader}>Comparable Listings</Text>
      </>
    )
  ), [analysis]);

  // Render each comparable listing as a modern card
  const renderComp = useCallback(({ item: comp }) => (
    <View style={[styles.compCard, isTablet ? styles.compCardTablet : null]}> 
      {comp.image_url ? (
        <Image source={{ uri: comp.image_url }} style={styles.compImageModern} />
      ) : (
        <View style={[styles.compImageModern, { backgroundColor: '#222', alignItems: 'center', justifyContent: 'center' }]}> 
          <Text style={{ color: '#a259f7', fontSize: 12 }}>No Image</Text>
        </View>
      )}
      <View style={styles.compCardContent}>
        <Text style={styles.compCardTitle} numberOfLines={2}>{comp.title}</Text>
        <Text style={styles.compCardPrice}>${comp.sold_price?.toFixed(2)}</Text>
        {comp.source_url ? (
          <TouchableOpacity style={styles.compCardButton} onPress={() => Linking.openURL(comp.source_url)}>
            <Text style={styles.compCardButtonText}>View on eBay</Text>
          </TouchableOpacity>
        ) : null}
      </View>
    </View>
  ), [isTablet]);

  // Render footer for loading more
  const renderFooter = useCallback(() => (
    compsToShow < comps.length ? (
      <View style={{ paddingVertical: 20, alignItems: 'center' }}>
        <ActivityIndicator size="small" color="#a259f7" />
        <Text style={{ color: '#888', marginTop: 8 }}>Loading more listings...</Text>
      </View>
    ) : null
  ), [compsToShow, comps.length]);

  // Empty state
  const renderEmpty = () => (
    <View style={{ alignItems: 'center', marginTop: 48 }}>
      <Text style={{ color: '#888', fontSize: 18, marginBottom: 8 }}>No comparable listings found.</Text>
      <Text style={{ color: '#a259f7', fontSize: 15 }}>Try analyzing a different item or check back later.</Text>
    </View>
  );

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

  // Grid layout for comps
  const numColumns = isTablet ? 2 : 1;
  const compsData = [];
  for (let i = 0; i < compsToShow; i += numColumns) {
    compsData.push(comps.slice(i, i + numColumns));
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
        data={compsData}
        keyExtractor={(_, idx) => String(idx)}
        renderItem={({ item: row }) => (
          <View style={[styles.compsRow, isTablet ? styles.compsRowTablet : null]}>
            {row.map((comp, idx) => (
              <React.Fragment key={comp.id || idx}>{renderComp({ item: comp })}</React.Fragment>
            ))}
          </View>
        )}
        ListHeaderComponent={renderHeader}
        ListFooterComponent={renderFooter}
        ListEmptyComponent={renderEmpty}
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
  compsHeader: {
    fontSize: 20,
    fontWeight: '700',
    color: '#fff',
    marginBottom: 18,
    marginTop: 8,
    alignSelf: 'flex-start',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    flexWrap: 'wrap',
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
  compsRow: {
    flexDirection: 'column',
    marginBottom: 18,
  },
  compsRowTablet: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  compCard: {
    backgroundColor: '#18181b',
    borderRadius: 14,
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    marginBottom: 12,
    marginRight: 0,
    flex: 1,
    minWidth: 0,
    maxWidth: '100%',
    shadowColor: '#000',
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 2,
  },
  compCardTablet: {
    marginRight: 18,
    maxWidth: '48%',
  },
  compImageModern: {
    width: 70,
    height: 70,
    borderRadius: 10,
    marginRight: 18,
    backgroundColor: '#222',
  },
  compCardContent: {
    flex: 1,
    flexDirection: 'column',
    justifyContent: 'center',
  },
  compCardTitle: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '600',
    marginBottom: 4,
  },
  compCardPrice: {
    color: '#a259f7',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 6,
  },
  compCardButton: {
    backgroundColor: '#a259f7',
    borderRadius: 8,
    paddingVertical: 7,
    paddingHorizontal: 18,
    alignSelf: 'flex-start',
  },
  compCardButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  error: {
    color: '#ff4d6d',
    fontSize: 18,
    marginBottom: 20,
    textAlign: 'center',
  },
}); 