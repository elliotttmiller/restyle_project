import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, ScrollView, Image } from 'react-native';
import { useRouter } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import * as Clipboard from 'expo-clipboard';
import api from '../../shared/api';

export default function DebugCamera() {
  const router = useRouter();
  const [selectedImage, setSelectedImage] = useState(null);
  const [debugInfo, setDebugInfo] = useState([]);
  const [testing, setTesting] = useState(false);

  const addDebugInfo = (message, type = 'info') => {
    setDebugInfo(prev => [...prev, { message, type, timestamp: new Date().toLocaleTimeString() }]);
  };

  const testCameraPermissions = async () => {
    addDebugInfo('Testing camera permissions...', 'info');
    
    try {
      const { status: cameraStatus } = await ImagePicker.requestCameraPermissionsAsync();
      const { status: libraryStatus } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      
      addDebugInfo(`Camera permission: ${cameraStatus}`, cameraStatus === 'granted' ? 'success' : 'error');
      addDebugInfo(`Library permission: ${libraryStatus}`, libraryStatus === 'granted' ? 'success' : 'error');
      
      if (cameraStatus !== 'granted' || libraryStatus !== 'granted') {
        addDebugInfo('Permissions not granted - this will cause issues', 'error');
      } else {
        addDebugInfo('All permissions granted', 'success');
      }
    } catch (error) {
      addDebugInfo(`Permission test failed: ${error.message}`, 'error');
    }
  };

  const testImageCapture = async () => {
    addDebugInfo('Testing image capture...', 'info');
    
    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images', 'videos'],
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        const image = result.assets[0];
        setSelectedImage(image);
        addDebugInfo('Image captured successfully', 'success');
        addDebugInfo(`Image URI: ${image.uri}`, 'info');
        addDebugInfo(`Image type: ${image.type}`, 'info');
        addDebugInfo(`Image size: ${image.fileSize} bytes`, 'info');
        addDebugInfo(`Image dimensions: ${image.width}x${image.height}`, 'info');
      } else {
        addDebugInfo('Image capture cancelled', 'warning');
      }
    } catch (error) {
      addDebugInfo(`Image capture failed: ${error.message}`, 'error');
    }
  };

  const testImageUpload = async () => {
    if (!selectedImage) {
      addDebugInfo('No image selected for upload test', 'warning');
      return;
    }

    addDebugInfo('Testing image upload to backend...', 'info');
    setTesting(true);

    try {
      // Create FormData
      const formData = new FormData();
      const file = {
        uri: selectedImage.uri,
        type: selectedImage.type || 'image/jpeg',
        name: 'debug_image.jpg',
      };
      
      formData.append('image', file);
      formData.append('image_type', 'image/jpeg');
      
      addDebugInfo(`Sending to: ${api.defaults.baseURL}/core/ai/image-search/`, 'info');
      addDebugInfo(`File object: ${JSON.stringify(file)}`, 'info');
      
      const response = await api.post('core/ai/image-search/', formData, {
        headers: {
          // Let axios set Content-Type
        },
      });
      
      addDebugInfo('Upload successful!', 'success');
      addDebugInfo(`Response status: ${response.status}`, 'success');
      addDebugInfo(`Response data: ${JSON.stringify(response.data).substring(0, 200)}...`, 'info');
      
    } catch (error) {
      addDebugInfo(`Upload failed: ${error.message}`, 'error');
      if (error.response) {
        addDebugInfo(`Status: ${error.response.status}`, 'error');
        addDebugInfo(`Response: ${JSON.stringify(error.response.data)}`, 'error');
      }
    } finally {
      setTesting(false);
    }
  };

  const testBackendConnectivity = async () => {
    addDebugInfo('Testing backend connectivity...', 'info');
    
    try {
      const response = await api.get('/core/health/');
      addDebugInfo(`Backend health: ${response.data.status}`, 'success');
    } catch (error) {
      addDebugInfo(`Backend connectivity failed: ${error.message}`, 'error');
      if (error.response) {
        addDebugInfo(`Status: ${error.response.status}`, 'error');
      }
    }
  };

  const clearDebugInfo = () => {
    setDebugInfo([]);
  };

  const exportDebugInfo = async () => {
    const exportData = JSON.stringify(debugInfo, null, 2);
    await Clipboard.setStringAsync(exportData);
    Alert.alert('Copied!', 'Debug information copied to clipboard. Paste it here in the chat.');
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Text style={styles.backButtonText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Camera Debug</Text>
        <TouchableOpacity style={styles.clearButton} onPress={clearDebugInfo}>
          <Text style={styles.clearButtonText}>Clear</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.buttonContainer}>
          <TouchableOpacity style={styles.button} onPress={testCameraPermissions}>
            <Text style={styles.buttonText}>Test Permissions</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.button} onPress={testImageCapture}>
            <Text style={styles.buttonText}>Test Camera</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.button, !selectedImage && styles.buttonDisabled]} 
            onPress={testImageUpload}
            disabled={!selectedImage || testing}
          >
            <Text style={styles.buttonText}>
              {testing ? 'Uploading...' : 'Test Upload'}
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.button} onPress={testBackendConnectivity}>
            <Text style={styles.buttonText}>Test Backend</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.button} onPress={exportDebugInfo}>
            <Text style={styles.buttonText}>Copy Debug Info</Text>
          </TouchableOpacity>
        </View>

        {selectedImage && (
          <View style={styles.imageContainer}>
            <Text style={styles.imageTitle}>Selected Image:</Text>
            <Image source={{ uri: selectedImage.uri }} style={styles.previewImage} />
            <Text style={styles.imageInfo}>
              {selectedImage.width}x{selectedImage.height} • {selectedImage.fileSize} bytes
            </Text>
          </View>
        )}

        <View style={styles.debugContainer}>
          <Text style={styles.debugTitle}>Debug Information:</Text>
          {debugInfo.map((info, index) => (
            <View key={index} style={[styles.debugItem, styles[`debug${info.type.charAt(0).toUpperCase() + info.type.slice(1)}`]]}>
              <Text style={[styles.debugText, styles[`debugText${info.type.charAt(0).toUpperCase() + info.type.slice(1)}`]]}>
                {info.message}
              </Text>
              <Text style={styles.timestamp}>{info.timestamp}</Text>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}