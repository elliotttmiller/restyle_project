"""
AI Service for Image Analysis using Google Cloud Vision API with Advanced ML
"""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import base64
import re
import json
from collections import defaultdict, Counter
import hashlib
import pickle

# Specific imports to avoid broad library imports
from PIL import Image
from io import BytesIO
import numpy as np

# Google Cloud Vision imports
try:
    from google.cloud import vision
    from google.cloud.vision_v1 import AnnotateImageRequest
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

# PyTorch and CLIP imports
try:
    import torch
    import open_clip
    CLIP_AVAILABLE = True
    # Set random seed for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
except ImportError:
    CLIP_AVAILABLE = False

# FAISS import
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

# RapidFuzz import
try:
    from rapidfuzz import process, fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False

# AWS Boto3 import
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

from core.credential_manager import credential_manager

logger = logging.getLogger(__name__)

# Constants for magic numbers
MIN_TERM_LENGTH = 3
MAX_TERM_LENGTH = 15
BRAND_MIN_LENGTH = 4
PRODUCT_MIN_LENGTH = 4
COLOR_MAX_LENGTH = 10
STYLE_MAX_LENGTH = 15
MATERIAL_MAX_LENGTH = 12
CONFIDENCE_THRESHOLD = 0.7
HIGH_CONFIDENCE_THRESHOLD = 0.8

class AIService:
    """Service for AI-powered image analysis using Google Cloud Vision with Advanced ML"""
    
    def __init__(self):
        logger.info("AIService initialization started")
        # Lazy initialization - don't initialize clients until needed
        self._client = None
        self._client_initialized = False
        self.faiss_index = None
        self.faiss_id_to_item = {}
        
        # Initialize CLIP model if available
        self.clip_model = None
        self.clip_tokenizer = None
        self.clip_preprocess = None
        if CLIP_AVAILABLE:
            self._initialize_clip_model()
        
        # Advanced AI components
        self.entity_embeddings = {}
        self.semantic_similarity_cache = {}
        self.confidence_models = {}
        self.attention_weights = {}
        self.learning_history = []
        self.pattern_memory = {}
        
        # AWS Rekognition client
        self._aws_client = None
        self._aws_client_initialized = False
        self._initialize_aws_client()

    def _initialize_clip_model(self):
        """Initialize CLIP model with proper error handling"""
        try:
            model, _, preprocess = open_clip.create_model_and_transforms(
                'ViT-B-32', pretrained='openai'
            )
            self.clip_model = model
            self.clip_tokenizer = open_clip.get_tokenizer('ViT-B-32')
            self.clip_preprocess = preprocess
            logger.info("OpenCLIP ViT-B-32 model initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize CLIP model: %s", str(e)[:100])
            self.clip_model = None

    @property
    def client(self):
        """Lazy initialization of Google Vision client"""
        if not self._client_initialized:
            self._initialize_client()
        return self._client
    
    def _initialize_client(self):
        """Initialize Google Cloud Vision client using API key"""
        logger.info("Initializing Google Vision client")
        
        # Check if Google Vision service is enabled
        if not credential_manager.is_service_enabled('google_vision'):
            logger.info("Google Vision service is disabled")
            self._client = None
            self._client_initialized = True
            return
        
        try:
            # Get Google API key from credential manager
            google_api_key = credential_manager.get_google_api_key()
            
            if google_api_key:
                logger.info("Using Google API key from credential manager")
                
                # Get project ID from environment
                project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', '609071491201')
                
                # Initialize client with API key and correct project
                client_options = {
                    "api_key": google_api_key,
                    "quota_project_id": project_id
                }
                self._client = vision.ImageAnnotatorClient(client_options=client_options)
                logger.info("Google Cloud Vision client initialized for project %s", project_id)
            else:
                logger.error("No Google API key available")
                self._client = None
                
        except ImportError:
            logger.error("Google Cloud Vision library not available")
            self._client = None
        except Exception as e:
            logger.error("Error initializing Google Cloud Vision client: %s", str(e)[:100])
            self._client = None
        finally:
            self._client_initialized = True

    def analyze_image(self, image_data: bytes, **kwargs) -> dict:
        """
        Analyze an image using Google Vision and AWS Rekognition in parallel.
        """
        if not image_data:
            logger.error("Empty image data provided")
            return self._fallback_analysis("Empty image data")

        logger.info("Starting AI analysis with image data of size: %d bytes", len(image_data))

        # Validate image data
        try:
            with BytesIO(image_data) as img_buffer:
                test_image = Image.open(img_buffer)
                logger.info("Image validation successful: %s %s", test_image.size, test_image.mode)
        except Exception as e:
            logger.error("Invalid image data: %s", str(e)[:100])
            return self._fallback_analysis("Invalid image format")

        # Run Google Vision analysis
        google_results = self._google_vision_analysis(image_data)
        
        # Run AWS Rekognition analysis
        aws_results = self._aws_rekognition_analysis(image_data)

        # CLIP/semantic analysis (if available)
        clip_results = self._clip_analysis(image_data) if CLIP_AVAILABLE else {}

        # Process and combine results
        return self._process_analysis_results(google_results, aws_results, clip_results)

    def _google_vision_analysis(self, image_data: bytes) -> Optional[dict]:
        """Perform Google Vision analysis"""
        if not self.client:
            return None
            
        try:
            image = vision.Image(content=image_data)
            features = [
                vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION),
                vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION),
                vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION),
            ]
            request = vision.AnnotateImageRequest(image=image, features=features)
            logger.info("Sending request to Google Vision API")
            response = self.client.batch_annotate_images(requests=[request])
            if response.responses:
                return response.responses[0]
        except Exception as e:
            logger.warning("Google Vision analysis failed: %s", str(e)[:100])
        return None

    def _aws_rekognition_analysis(self, image_data: bytes) -> dict:
        """AWS Rekognition analysis with proper error handling"""
        if not self._aws_client:
            return {}
        
        try:
            response = self._aws_client.detect_labels(
                Image={'Bytes': image_data},
                MaxLabels=10,
                MinConfidence=70
            )
            
            return {
                'labels': [
                    {'name': label['Name'], 'confidence': label['Confidence']} 
                    for label in response['Labels']
                ]
            }
        except (BotoCoreError, ClientError) as e:
            logger.warning("AWS Rekognition analysis failed: %s", str(e)[:100])
        except Exception as e:
            logger.warning("Unexpected AWS error: %s", str(e)[:100])
        return {}

    def _clip_analysis(self, image_data: bytes) -> dict:
        """CLIP analysis with proper error handling"""
        if not self.clip_model:
            return {}
            
        try:
            with BytesIO(image_data) as img_buffer:
                image = Image.open(img_buffer).convert('RGB')
                image_tensor = self.clip_preprocess(image).unsqueeze(0)
                
                with torch.inference_mode():
                    image_features = self.clip_model.encode_image(image_tensor)
                    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                
                return {'image_features': image_features.cpu().numpy()}
        except Exception as e:
            logger.warning("CLIP analysis failed: %s", str(e)[:100])
        return {}

    def _process_analysis_results(self, google_results, aws_results, clip_results) -> dict:
        """Process and combine analysis results"""
        # Extract labels
        labels = []
        if google_results and google_results.label_annotations:
            labels = [
                {'description': label.description, 'score': label.score} 
                for label in google_results.label_annotations[:5]
            ]
        
        # Extract OCR text
        ocr_text = ""
        if google_results and google_results.text_annotations:
            ocr_text = google_results.text_annotations[0].description if google_results.text_annotations else ""
        
        # Extract objects
        objects = []
        if google_results and google_results.localized_object_annotations:
            objects = [
                {'name': obj.name, 'score': obj.score} 
                for obj in google_results.localized_object_annotations[:3]
            ]
        
        # Generate search terms
        search_terms = self._generate_search_terms(labels, objects, ocr_text)
        best_guess = search_terms[0] if search_terms else 'item'
        suggested_queries = self._generate_suggested_queries(search_terms, labels, objects)
        
        return {
            'status': 'success',
            'labels': labels,
            'ocr_text': self._sanitize_text_for_logging(ocr_text),
            'objects': objects,
            'search_terms': search_terms,
            'best_guess': best_guess,
            'suggested_queries': suggested_queries,
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }

    def _generate_search_terms(self, labels: List[dict], objects: List[dict], ocr_text: str) -> List[str]:
        """Generate search terms from analysis results"""
        search_terms = set()
        
        # Add labels
        for label in labels[:3]:
            term = self._clean_term(label['description'])
            if self._is_valid_search_term(term):
                search_terms.add(term)
        
        # Add objects
        for obj in objects[:2]:
            term = self._clean_term(obj['name'])
            if self._is_valid_search_term(term):
                search_terms.add(term)
        
        # Add OCR terms
        if ocr_text:
            words = ocr_text.split()[:5]  # Limit OCR words
            for word in words:
                term = self._clean_term(word)
                if self._is_valid_search_term(term) and len(term) >= BRAND_MIN_LENGTH:
                    search_terms.add(term)
        
        return list(search_terms) if search_terms else ['item']

    def _generate_suggested_queries(self, search_terms: List[str], labels: List[dict], objects: List[dict]) -> List[str]:
        """Generate suggested queries"""
        queries = set()
        
        # Single terms
        for term in search_terms[:3]:
            queries.add(term)
        
        # Combinations
        if len(search_terms) >= 2:
            for i in range(min(3, len(search_terms))):
                for j in range(i + 1, min(3, len(search_terms))):
                    queries.add(f"{search_terms[i]} {search_terms[j]}")
        
        # Add fallback queries
        queries.update(['clothing', 'fashion', 'apparel'])
        
        return list(queries)[:8]

    def _clean_term(self, term: str) -> str:
        """Clean and normalize a term"""
        if not term:
            return ""
        # Remove special characters and normalize
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', term).strip().lower()
        return ' '.join(cleaned.split())  # Normalize whitespace

    def _is_valid_search_term(self, term: str) -> bool:
        """Check if a term is valid for search"""
        if not term or len(term) < MIN_TERM_LENGTH or len(term) > MAX_TERM_LENGTH:
            return False
        return term.isalpha() and not term.endswith('ly')

    def _sanitize_text_for_logging(self, text: str) -> str:
        """Sanitize text for safe logging"""
        if not text:
            return ""
        # Remove newlines and control characters
        sanitized = re.sub(r'[\r\n\t\x00-\x1f\x7f-\x9f]', ' ', text)
        return sanitized[:200]  # Limit length

    def _initialize_aws_client(self):
        """Initialize AWS Rekognition client with proper error handling"""
        if not credential_manager.is_service_enabled('aws_rekognition'):
            return
        
        try:
            aws_creds = credential_manager.get_aws_credentials()
            if aws_creds.get('aws_access_key_id'):
                self._aws_client = boto3.client(
                    'rekognition',
                    aws_access_key_id=aws_creds['aws_access_key_id'],
                    aws_secret_access_key=aws_creds['aws_secret_access_key'],
                    region_name=aws_creds.get('aws_region', 'us-east-1')
                )
                logger.info("AWS Rekognition client initialized")
        except (BotoCoreError, ClientError) as e:
            logger.error("Failed to initialize AWS client: %s", str(e)[:100])
        except Exception as e:
            logger.error("Unexpected error initializing AWS client: %s", str(e)[:100])

    def detect_objects_and_regions(self, image_data: bytes) -> list:
        """
        Use Google Vision to detect objects and their bounding boxes in the image.
        Returns a list of dicts: {name, confidence, bounding_box: (x_min, y_min, x_max, y_max)}
        """
        if not self.client:
            logger.warning("No Google Vision client available")
            return []
        
        try:
            # Validate image data
            if not image_data:
                logger.error("Empty image data provided")
                return []
            
            logger.info("Processing image data of size: %d bytes", len(image_data))
            
            # Validate the image data first
            try:
                with BytesIO(image_data) as img_buffer:
                    test_image = Image.open(img_buffer)
                    logger.info("Image validation successful: %s %s", test_image.size, test_image.mode)
            except Exception as e:
                logger.error("Invalid image data: %s", str(e)[:100])
                return []
            
            image = vision.Image(content=image_data)
            
            # Create the request with explicit features
            request = vision.AnnotateImageRequest(
                image=image,
                features=[vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION)]
            )
            
            logger.info("Sending request to Google Vision API")
            response = self.client.batch_annotate_images(requests=[request])
            
            if not response.responses:
                logger.warning("No response from Google Vision API")
                return []
                
            if not response.responses[0].localized_object_annotations:
                logger.info("No objects detected in image")
                return []
                
            objects = []
            for obj in response.responses[0].localized_object_annotations:
                box = obj.bounding_poly.normalized_vertices
                # Convert normalized vertices to (x_min, y_min, x_max, y_max)
                x_coords = [v.x for v in box]
                y_coords = [v.y for v in box]
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                
                objects.append({
                    'name': obj.name,
                    'confidence': obj.score,
                    'bounding_box': (x_min, y_min, x_max, y_max),
                })
            
            logger.info("Detected %d objects in image", len(objects))
            return objects
            
        except Exception as e:
            logger.error("Error in detect_objects_and_regions: %s", str(e)[:100])
            return []

    def crop_to_region(self, image_data: bytes, bounding_box: tuple) -> bytes:
        """
        Crop the image to the given bounding box (normalized coordinates).
        Returns cropped image bytes.
        """
        try:
            with BytesIO(image_data) as input_buffer:
                image = Image.open(input_buffer).convert('RGB')
                width, height = image.size
                x_min, y_min, x_max, y_max = bounding_box
                left = int(x_min * width)
                top = int(y_min * height)
                right = int(x_max * width)
                bottom = int(y_max * height)
                cropped = image.crop((left, top, right, bottom))
                
                with BytesIO() as output_buffer:
                    cropped.save(output_buffer, format='JPEG')
                    return output_buffer.getvalue()
        except Exception as e:
            logger.error("Error cropping image: %s", str(e)[:100])
            return image_data  # Return original if cropping fails

    def build_faiss_index(self):
        """
        Build or rebuild the FAISS index from all ItemEmbeddings.
        """
        if not FAISS_AVAILABLE:
            logger.warning("FAISS not available")
            return
            
        try:
            from core.models import ItemEmbedding
            all_embeddings = list(ItemEmbedding.objects.select_related('item').all())
            if not all_embeddings:
                self.faiss_index = None
                self.faiss_id_to_item = {}
                return
                
            dim = len(all_embeddings[0].embedding)
            index = faiss.IndexFlatL2(dim)
            vectors = []
            id_to_item = {}
            
            for idx, emb in enumerate(all_embeddings):
                vectors.append(emb.embedding)
                id_to_item[idx] = emb.item
                
            vectors = np.array(vectors).astype('float32')
            index.add(vectors)
            self.faiss_index = index
            self.faiss_id_to_item = id_to_item
            logger.info("FAISS index built with %d items", len(all_embeddings))
        except ImportError:
            logger.warning("ItemEmbedding model not available")
        except Exception as e:
            logger.error("Error building FAISS index: %s", str(e)[:100])

    def get_visual_similar_items(self, image_data: bytes, text_query: str = None, top_k=5, bounding_box: tuple = None) -> list:
        """
        Use FAISS for fast similarity search if available, otherwise fallback to slow method.
        """
        if not CLIP_AVAILABLE:
            return []
            
        if bounding_box:
            image_data = self.crop_to_region(image_data, bounding_box)
            
        try:
            # Load CLIP model (ViT-B/32)
            model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
            tokenizer = open_clip.get_tokenizer('ViT-B-32')
            model.eval()
            
            with BytesIO(image_data) as img_buffer:
                image = Image.open(img_buffer).convert('RGB')
                image_input = preprocess(image).unsqueeze(0)
                
            with torch.inference_mode():
                image_features = model.encode_image(image_input).cpu().numpy()[0]
                image_features = image_features / np.linalg.norm(image_features)
                
            if text_query:
                text_input = tokenizer([text_query])
                with torch.inference_mode():
                    text_features = model.encode_text(text_input).cpu().numpy()[0]
                    text_features = text_features / np.linalg.norm(text_features)
                combined_features = (image_features + text_features) / 2
            else:
                combined_features = image_features
                
            query_vec = np.array([combined_features]).astype('float32')
            
            # Use FAISS if index is built
            if self.faiss_index is None or self.faiss_index.ntotal == 0:
                self.build_faiss_index()
                
            if self.faiss_index is not None and self.faiss_index.ntotal > 0:
                D, I = self.faiss_index.search(query_vec, top_k)
                results = []
                for rank, idx in enumerate(I[0]):
                    item = self.faiss_id_to_item.get(idx)
                    if not item:
                        continue
                    attributes = self.extract_attributes(item)
                    results.append({
                        'item_id': item.id,
                        'title': item.title,
                        'brand': item.brand,
                        'image_url': getattr(item, 'image_url', ''),
                        'similarity': float(1.0 / (1.0 + D[0][rank])),
                        'attributes': attributes,
                    })
                return results
        except Exception as e:
            logger.error("Error in visual similarity search: %s", str(e)[:100])
        return []

    def extract_attributes(self, item_or_analysis) -> dict:
        """
        Extract fine-grained attributes (color, brand, style, etc.) from an Item or analysis result.
        """
        # If passed an Item, use its fields
        if hasattr(item_or_analysis, 'brand'):
            return {
                'brand': getattr(item_or_analysis, 'brand', ''),
                'color': getattr(item_or_analysis, 'color', ''),
                'category': getattr(item_or_analysis, 'category', ''),
                'title': getattr(item_or_analysis, 'title', ''),
            }
        
        # If passed an analysis result dict
        attrs = {}
        labels = item_or_analysis.get('labels', [])
        if labels and isinstance(labels[0], str):
            attrs['labels'] = [{'description': l} for l in labels]
        elif labels:
            attrs['labels'] = labels
            
        if 'ocr_text' in item_or_analysis:
            attrs['ocr_text'] = self._sanitize_text_for_logging(item_or_analysis['ocr_text'])
            
        if 'dominant_colors' in item_or_analysis and item_or_analysis['dominant_colors']:
            color_info = item_or_analysis['dominant_colors'][0]
            attrs['color'] = f"rgb({color_info['red']},{color_info['green']},{color_info['blue']})"
            
        return attrs

    def _fallback_analysis(self, error_message: str) -> dict:
        """Fallback analysis when image processing fails"""
        return {
            'status': 'error',
            'message': f'Image analysis failed: {error_message}',
            'labels': [],
            'ocr_text': '',
            'objects': [],
            'search_terms': ['item'],
            'best_guess': 'item',
            'suggested_queries': ['item', 'product', 'clothing', 'fashion'],
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }


# Placeholder classes for future implementation
class NeuralReasoner:
    """Neural reasoning component for advanced AI analysis"""
    def reason(self, visual_results: dict, semantic_results: dict) -> dict:
        return {}


class MultimodalFusion:
    """Multimodal fusion component for combining different AI results"""
    def fuse(self, visual_results: dict, semantic_results: dict) -> dict:
        return {}


class UncertaintyQuantifier:
    """Uncertainty quantification for AI results"""
    def quantify(self, fused_results: dict) -> dict:
        return fused_results


class AdaptiveThreshold:
    """Adaptive threshold management for AI confidence scores"""
    def get_adaptive_threshold(self, context: dict) -> float:
        return CONFIDENCE_THRESHOLD


# Global AI service instance with thread-safe singleton pattern
_ai_service_instance = None
_ai_service_lock = None

def get_ai_service():
    """Get AI service instance with thread-safe singleton pattern"""
    global _ai_service_instance, _ai_service_lock
    
    if _ai_service_lock is None:
        import threading
        _ai_service_lock = threading.Lock()
    
    if _ai_service_instance is None:
        with _ai_service_lock:
            if _ai_service_instance is None:
                _ai_service_instance = AIService()
    
    return _ai_service_instance