import * as ImagePicker from 'expo-image-picker';
import logger from './shared/logger';

// Simple function to test image picker availability
const testImagePicker = async () => {
  try {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    logger.info('Image Picker permission status:', status);
    return true;
  } catch (error) {
    logger.error('Error testing Image Picker:', error);
    return false;
  }
};

// Export the test function
export default testImagePicker;

// If this file is run directly, execute the test
if (require.main === module) {
  logger.info('Testing Image Picker...');
  testImagePicker()
    .then(result => {
      logger.info('Test completed, result:', result);
    })
    .catch(err => {
      logger.error('Test failed:', err);
    });
}
