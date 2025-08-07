"""
Image Encoder Service
This service is responsible for encoding images into vector embeddings for visual similarity search.
"""
import logging
logger = logging.getLogger(__name__)


import numpy as np
from PIL import Image
import requests
from io import BytesIO
from typing import Optional

# Placeholder for a real image model
# In a real application, this would be a more sophisticated model like CLIP, ResNet, etc.
# For now, we'll simulate it with a very simple "model"
class SimpleImageEncoder:
    def __init__(self):
        logger.info("Initializing SimpleImageEncoder")
        # In a real scenario, you would load model weights here
        self.model = "simple_placeholder"

    def encode(self, image: Image.Image) -> np.ndarray:
        """
        Encodes a single image into a vector embedding.
        """
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be a PIL Image")

        # Simulate a complex encoding process by creating a feature vector
        # based on the image's average color and size.
        image = image.resize((128, 128)).convert("RGB")
        
        # Get average color
        avg_color = np.array(image).mean(axis=(0, 1))
        
        # Get size features
        width, height = image.size
        size_features = np.array([width, height])
        
        # Combine into a single feature vector (and normalize)
        feature_vector = np.concatenate([avg_color, size_features])
        normalized_vector = feature_vector / np.linalg.norm(feature_vector)
        
        return normalized_vector.astype(np.float32)

class EncoderService:
    """
    Service to handle image encoding using a trained model.
    """
    def __init__(self):
        self.model = SimpleImageEncoder()
        logger.info("EncoderService initialized.")

    def encode_image_from_data(self, image_data: bytes) -> Optional[np.ndarray]:
        """
        Encodes an image from raw bytes.
        """
        try:
            image = Image.open(BytesIO(image_data))
            return self.model.encode(image)
        except Exception as e:
            logger.error(f"Failed to encode image from data: {e}")
            return None

    def encode_image_from_url(self, image_url: str) -> Optional[np.ndarray]:
        """
        Encodes an image from a URL.
        """
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            return self.model.encode(image)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download image from URL {image_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to encode image from URL {image_url}: {e}")
            return None

_encoder_service_instance = None

def get_encoder_service() -> EncoderService:
    """
    Singleton accessor for the EncoderService.
    """
    global _encoder_service_instance
    if _encoder_service_instance is None:
        _encoder_service_instance = EncoderService()
    return _encoder_service_instance

if __name__ == '__main__':
    # Example usage
    logging.basicConfig(level=logging.INFO)
    service = get_encoder_service()
    
    # Create a dummy image for testing
    dummy_image = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = BytesIO()
    dummy_image.save(img_byte_arr, format='PNG')
    image_data = img_byte_arr.getvalue()
    
    embedding = service.encode_image_from_data(image_data)
    logger.info(f"Generated embedding: {embedding}")
    logger.info(f"Embedding shape: {embedding.shape}")
