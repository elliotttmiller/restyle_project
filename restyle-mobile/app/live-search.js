import React, { useRef, useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Image, ScrollView } from 'react-native';
import { Camera } from 'expo-camera';
import api from '../shared/api';

export default function LiveSearch() {
  const [hasPermission, setHasPermission] = useState(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState('');
  const cameraRef = useRef(null);
  const [intervalId, setIntervalId] = useState(null);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, []);

  const startLiveSearch = () => {
    if (intervalId) return;
    setError('');
    setResults([]);
    setSearching(true);
    // Capture a frame every 1.5 seconds
    const id = setInterval(async () => {
      if (!cameraRef.current || !cameraReady) return;
      try {
        const photo = await cameraRef.current.takePictureAsync({ base64: true, quality: 0.5 });
        const formData = new FormData();
        formData.append('image', {
          uri: photo.uri,
          name: 'frame.jpg',
          type: 'image/jpeg',
        });
        formData.append('image_type', 'image/jpeg');
        const response = await api.post('/core/ai/image-search/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setResults(response.data.ensemble_results || response.data.results || []);
        setError('');
      } catch (err) {
        setError('Live search failed.');
      }
    }, 1500);
    setIntervalId(id);
  };

  const stopLiveSearch = () => {
    if (intervalId) clearInterval(intervalId);
    setIntervalId(null);
    setSearching(false);
  };

  if (hasPermission === null) {
    return <View style={styles.center}><ActivityIndicator size="large" color="#8B5CF6" /></View>;
  }
  if (hasPermission === false) {
    return <View style={styles.center}><Text>No access to camera</Text></View>;
  }

  return (
    <View style={styles.container}>
      <Camera
        ref={cameraRef}
        style={styles.camera}
        type={Camera.Constants.Type.back}
        onCameraReady={() => setCameraReady(true)}
        ratio="4:3"
      />
      <View style={styles.controls}>
        {searching ? (
          <TouchableOpacity style={styles.stopButton} onPress={stopLiveSearch}>
            <Text style={styles.buttonText}>Stop Live Search</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity style={styles.startButton} onPress={startLiveSearch}>
            <Text style={styles.buttonText}>Start Live Search</Text>
          </TouchableOpacity>
        )}
      </View>
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <ScrollView style={styles.resultsContainer}>
        {results.length > 0 && <Text style={styles.resultsTitle}>Live Results</Text>}
        <View style={styles.grid}>
          {results.map((item, idx) => (
            <View key={idx} style={styles.resultCard}>
              {item.image_url && (
                <Image source={{ uri: item.image_url }} style={styles.resultImage} />
              )}
              <Text style={styles.resultTitle} numberOfLines={2}>{item.title || 'No title'}</Text>
              {item.similarity && (
                <Text style={styles.resultScore}>Score: {item.similarity.toFixed(2)}</Text>
              )}
              {item.attributes && (
                <Text style={styles.resultAttrs} numberOfLines={2}>
                  {Object.entries(item.attributes).map(([k, v]) => `${k}: ${v}`).join(', ')}
                </Text>
              )}
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  camera: { width: '100%', height: 320, borderRadius: 12, marginTop: 20 },
  controls: { flexDirection: 'row', justifyContent: 'center', marginVertical: 16 },
  startButton: { backgroundColor: '#8B5CF6', padding: 16, borderRadius: 12 },
  stopButton: { backgroundColor: '#F87171', padding: 16, borderRadius: 12 },
  buttonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  error: { color: '#F87171', textAlign: 'center', marginVertical: 8 },
  resultsContainer: { flex: 1, marginTop: 8 },
  resultsTitle: { color: '#fff', fontWeight: 'bold', fontSize: 18, marginBottom: 8, marginLeft: 8 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  resultCard: { width: '48%', backgroundColor: '#1a1a1a', borderRadius: 12, marginBottom: 12, overflow: 'hidden', padding: 8 },
  resultImage: { width: '100%', height: 100, borderRadius: 8, marginBottom: 6 },
  resultTitle: { color: '#fff', fontWeight: '600', fontSize: 14, marginBottom: 2 },
  resultScore: { color: '#8B5CF6', fontSize: 12, marginBottom: 2 },
  resultAttrs: { color: '#bbb', fontSize: 11, marginTop: 2 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
}); 