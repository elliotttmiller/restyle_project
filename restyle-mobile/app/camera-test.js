import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Image } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

export default function CameraTest() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [testing, setTesting] = useState(false);

  const testCameraPermissions = async () => {
    console.log('Testing camera permissions...');
    
    try {
      const { status: cameraStatus } = await ImagePicker.requestCameraPermissionsAsync();
      const { status: libraryStatus } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      
      console.log('Camera permission status:', cameraStatus);
      console.log('Library permission status:', libraryStatus);
      
      Alert.alert(
        'Permission Status',
        `Camera: ${cameraStatus}\nLibrary: ${libraryStatus}`,
        [{ text: 'OK' }]
      );
      
      return cameraStatus === 'granted' && libraryStatus === 'granted';
    } catch (error) {
      console.error('Error checking permissions:', error);
      Alert.alert('Error', 'Failed to check permissions');
      return false;
    }
  };

  const testCamera = async () => {
    setTesting(true);
    console.log('Testing camera...');
    
    try {
      const hasPermission = await testCameraPermissions();
      if (!hasPermission) {
        Alert.alert('Permissions Required', 'Camera and photo library permissions are needed.');
        setTesting(false);
        return;
      }

      console.log('Launching camera...');
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images', 'videos'],
        allowsEditing: false,
        quality: 0.8,
      });

      console.log('Camera result:', result);
      
      if (!result.canceled && result.assets && result.assets[0]) {
        console.log('Photo taken successfully:', result.assets[0]);
        setSelectedImage(result.assets[0]);
        Alert.alert('Success', 'Photo taken successfully!');
      } else {
        console.log('Camera was canceled or no image selected');
        Alert.alert('Info', 'Camera was canceled or no image selected');
      }
    } catch (error) {
      console.error('Error taking photo:', error);
      Alert.alert('Error', `Failed to take photo: ${error.message}`);
    } finally {
      setTesting(false);
    }
  };

  const testGallery = async () => {
    setTesting(true);
    console.log('Testing gallery...');
    
    try {
      const hasPermission = await testCameraPermissions();
      if (!hasPermission) {
        Alert.alert('Permissions Required', 'Camera and photo library permissions are needed.');
        setTesting(false);
        return;
      }

      console.log('Launching image library...');
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images', 'videos'],
        allowsEditing: false,
        quality: 0.8,
      });

      console.log('Gallery result:', result);
      
      if (!result.canceled && result.assets && result.assets[0]) {
        console.log('Image picked successfully:', result.assets[0]);
        setSelectedImage(result.assets[0]);
        Alert.alert('Success', 'Image picked successfully!');
      } else {
        console.log('Gallery was canceled or no image selected');
        Alert.alert('Info', 'Gallery was canceled or no image selected');
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Error', `Failed to pick image: ${error.message}`);
    } finally {
      setTesting(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Camera Test</Text>
      
      <TouchableOpacity 
        style={styles.button} 
        onPress={testCamera}
        disabled={testing}
      >
        <Text style={styles.buttonText}>
          {testing ? 'Testing...' : 'Test Camera'}
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity 
        style={styles.button} 
        onPress={testGallery}
        disabled={testing}
      >
        <Text style={styles.buttonText}>
          {testing ? 'Testing...' : 'Test Gallery'}
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity 
        style={styles.button} 
        onPress={testCameraPermissions}
        disabled={testing}
      >
        <Text style={styles.buttonText}>Test Permissions</Text>
      </TouchableOpacity>
      
      {selectedImage && (
        <View style={styles.imageContainer}>
          <Text style={styles.imageTitle}>Selected Image:</Text>
          <Image source={{ uri: selectedImage.uri }} style={styles.image} />
          <Text style={styles.imageInfo}>
            URI: {selectedImage.uri}
          </Text>
          <Text style={styles.imageInfo}>
            Type: {selectedImage.type || 'unknown'}
          </Text>
          <Text style={styles.imageInfo}>
            Size: {selectedImage.fileSize || 'unknown'} bytes
          </Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    padding: 20,
    justifyContent: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#a259f7',
    textAlign: 'center',
    marginBottom: 30,
  },
  button: {
    backgroundColor: '#a259f7',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  imageContainer: {
    marginTop: 20,
    alignItems: 'center',
  },
  imageTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 10,
  },
  image: {
    width: 200,
    height: 200,
    borderRadius: 8,
    marginBottom: 10,
  },
  imageInfo: {
    color: '#888',
    fontSize: 12,
    textAlign: 'center',
    marginBottom: 5,
  },
}); 