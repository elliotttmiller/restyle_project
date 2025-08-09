// restyle-mobile/shared/api.js
import axios from 'axios';

// IMPORTANT: Use environment variables for this in a real app
const API_URL = 'https://restyleproject-production.up.railway.app/api/core';

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 45000, // Increased timeout for complex analysis
});

export const analyzeImageApi = async (imageAsset) => {
  const formData = new FormData();
  formData.append('image', {
    uri: imageAsset.uri,
    name: `photo.${imageAsset.uri.split('.').pop()}`,
    type: `image/${imageAsset.uri.split('.').pop()}`,
  });

  try {
    const response = await apiClient.post('/analyze-and-price/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        // 'Authorization': `Bearer YOUR_AUTH_TOKEN`,
      },
    });
    return response.data;
  } catch (error) {
    console.error("API Error in analyzeImageApi:", error.response?.data || error.message);
    throw error;
  }
};