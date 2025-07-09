import React, { useEffect, useState } from 'react';
import { View, Text, Image, Button, ScrollView, StyleSheet, ActivityIndicator, FlatList, TouchableOpacity } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import * as Linking from 'expo-linking';
import api from '../shared/api';

export default function ItemDetailScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const item = params && params.item ? JSON.parse(params.item) : null;

  // Price analysis state
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Only re-run effect if itemId changes
  useEffect(() => {
    if (!item) return;
    setLoading(true);
    setError('');
    // Compose request body from item details
    const body = {
      title: item.title,
      brand: item.brand || '',
      category: item.categoryId || item.category || '',
      size: item.size || '',
      color: item.color || '',
      condition: item.condition || '',
    };
    api.post('/core/price-analysis/', body)
      .then(res => {
        setAnalysis(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.response?.data?.error || 'Failed to fetch price analysis.');
        setLoading(false);
      });
  }, [item?.itemId]);

  if (!item) {
    return (
      <View style={styles.container}>
        <Text style={styles.error}>No item data found.</Text>
        <Button title="Back" onPress={() => router.back()} />
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      {/* Back Button at Top Left */}
      <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
        <Text style={styles.backButtonText}>← Back</Text>
      </TouchableOpacity>

      {/* Listing Details Section */}
      <View style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>Listing Details</Text>
        {item.image?.imageUrl && (
          <Image source={{ uri: item.image.imageUrl }} style={styles.image} resizeMode="contain" />
        )}
        <Text style={styles.title}>{item.title || 'No title'}</Text>
        <View style={styles.row}>
          <Text style={styles.label}>Item ID:</Text>
          <Text style={styles.value}>{item.itemId}</Text>
        </View>
        {item.price && (
          <View style={styles.row}>
            <Text style={styles.label}>Price:</Text>
            <Text style={styles.value}>${item.price.value} {item.price.currency}</Text>
          </View>
        )}
        {item.condition && (
          <View style={styles.row}>
            <Text style={styles.label}>Condition:</Text>
            <Text style={styles.value}>{item.condition}</Text>
          </View>
        )}
        {item.seller && (
          <View style={styles.row}>
            <Text style={styles.label}>Seller:</Text>
            <Text style={styles.value}>{item.seller.username} ({item.seller.feedbackScore} | {item.seller.feedbackPercentage}%)</Text>
          </View>
        )}
        {(item.itemWebUrl || item.itemAffiliateWebUrl) && (
          <TouchableOpacity style={styles.button} onPress={() => Linking.openURL(item.itemAffiliateWebUrl || item.itemWebUrl)}>
            <Text style={styles.buttonText}>View on eBay</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Price Analysis Section */}
      <View style={styles.analysisCard}>
        <Text style={styles.sectionTitle}>Price Analysis</Text>
        {loading && <ActivityIndicator size="large" color="#a259f7" style={{ marginVertical: 16 }} />}
        {error ? <Text style={styles.error}>{error}</Text> : null}
        {analysis && (
          <>
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
              {/* Extract count from confidence_score, e.g. (10 comparable listings) */}
              {analysis.confidence_score && analysis.confidence_score.match(/\((\d+) comparable listings\)/) && (
                <Text style={styles.compsCount}>
                  {analysis.confidence_score.match(/\((\d+) comparable listings\)/)[0]}
                </Text>
              )}
            </View>
            <FlatList
              data={analysis.comps}
              keyExtractor={(comp, idx) => comp.id ? String(comp.id) : String(idx)}
              renderItem={({ item: comp }) => (
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
              )}
              style={{ marginTop: 8, width: '100%' }}
              horizontal={true}
              showsHorizontalScrollIndicator={false}
            />
          </>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    alignItems: 'center',
    padding: 24,
    backgroundColor: '#000', // black background
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