import * as ImagePicker from 'expo-image-picker';

// Simple function to test image picker availability
const testImagePicker = async () => {
  try {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    console.log('Image Picker permission status:', status);
    return true;
  } catch (error) {
    console.error('Error testing Image Picker:', error);
    return false;
  }
};

// Export the test function
export default testImagePicker;

// If this file is run directly, execute the test
if (require.main === module) {
  console.log('Testing Image Picker...');
  testImagePicker()
    .then(result => {
      console.log('Test completed, result:', result);
    })
    .catch(err => {
      console.error('Test failed:', err);
    });
}
