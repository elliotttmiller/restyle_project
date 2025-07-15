import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Image } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import api from '../shared/api';

export default function SimpleImageTest() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState('');

  const pickImage = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images', 'videos'],
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setSelectedImage(result.assets[0]);
        setResult('');
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Error', 'Failed to pick image.');
    }
  };

  const testImageUpload = async () => {
    if (!selectedImage) {
      Alert.alert('No Image', 'Please select an image first.');
      return;
    }

    setTesting(true);
    setResult('');

    try {
      console.log('=== IMAGE UPLOAD TEST ===');
      console.log('Image URI:', selectedImage.uri);
      console.log('Image type:', selectedImage.type);
      console.log('Image size:', selectedImage.fileSize);
      console.log('Image dimensions:', selectedImage.width, 'x', selectedImage.height);

      // Create FormData
      const formData = new FormData();
      const file = {
        uri: selectedImage.uri,
        type: selectedImage.type || 'image/jpeg',
        name: 'test-image.jpg',
      };

      formData.append('image', file);
      console.log('FormData created with file:', file);

      // Test upload
      console.log('Sending to:', api.defaults.baseURL + '/core/ai/advanced-search/');
      
      const response = await api.post('core/ai/advanced-search/', formData, {
        headers: {
          // Let axios set the Content-Type
        },
      });

      console.log('Upload successful!');
      console.log('Response:', response.data);
      
      setResult('✅ Upload successful!\n\nResponse received from backend.');

    } catch (error) {
      console.error('Upload failed:', error);
      console.error('Error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
      });

      let errorMessage = `❌ Upload failed: ${error.message}`;
      if (error.response) {
        errorMessage += `\nStatus: ${error.response.status}`;
        errorMessage += `\nData: ${JSON.stringify(error.response.data)}`;
      }
      
      setResult(errorMessage);
    } finally {
      setTesting(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Simple Image Upload Test</Text>
      
      <TouchableOpacity style={styles.button} onPress={pickImage}>
        <Text style={styles.buttonText}>Pick Image</Text>
      </TouchableOpacity>

      {selectedImage && (
        <View style={styles.imageContainer}>
          <Image source={{ uri: selectedImage.uri }} style={styles.image} />
          <Text style={styles.imageInfo}>
            {selectedImage.width} x {selectedImage.height} ({selectedImage.fileSize} bytes)
          </Text>
        </View>
      )}

      <TouchableOpacity 
        style={[styles.button, !selectedImage && styles.buttonDisabled]} 
        onPress={testImageUpload}
        disabled={!selectedImage || testing}
      >
        <Text style={styles.buttonText}>
          {testing ? 'Testing...' : 'Test Upload'}
        </Text>
      </TouchableOpacity>

      {result ? (
        <View style={styles.resultContainer}>
          <Text style={styles.resultText}>{result}</Text>
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#1a1a1a',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 30,
  },
  button: {
    backgroundColor: '#8B5CF6',
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
  },
  buttonDisabled: {
    backgroundColor: '#666',
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
    textAlign: 'center',
  },
  imageContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  image: {
    width: 200,
    height: 150,
    borderRadius: 12,
    marginBottom: 10,
  },
  imageInfo: {
    color: '#fff',
    fontSize: 14,
  },
  resultContainer: {
    backgroundColor: '#2a2a2a',
    padding: 16,
    borderRadius: 12,
    marginTop: 20,
  },
  resultText: {
    color: '#fff',
    fontSize: 14,
    lineHeight: 20,
  },
}); 