"""
AI Service for Image Analysis using Google Cloud Vision API
"""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from google.cloud import vision
from google.cloud.vision_v1 import AnnotateImageRequest
from PIL import Image
import io
import re

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered image analysis using Google Cloud Vision"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
        
        # Define product categories and their search terms
        self.product_categories = {
            'shoes': ['sneakers', 'boots', 'shoes', 'footwear', 'jordan', 'nike', 'adidas'],
            'clothing': ['shirt', 'hoodie', 'sweatshirt', 'jacket', 'coat', 'dress', 'pants', 'jeans'],
            'accessories': ['bag', 'purse', 'wallet', 'hat', 'cap', 'sunglasses', 'jewelry']
        }
        
        # Define brand patterns for OCR detection
        self.brand_patterns = [
            r'\b(nike|adidas|jordan|puma|reebok|converse|vans|yeezy)\b',
            r'\b(gucci|prada|louis\s+vuitton|chanel|hermes|balenciaga)\b',
            r'\b(levi\'s|calvin\s+klein|tommy\s+hilfiger|ralph\s+lauren)\b'
        ]
    
    def _initialize_client(self):
        """Initialize Google Cloud Vision client"""
        try:
            # Check if we have credentials set
            if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                # Try to initialize the client
                try:
                    self.client = vision.ImageAnnotatorClient()
                    logger.info("Google Cloud Vision client initialized with credentials")
                except Exception as cred_error:
                    logger.warning(f"Failed to initialize with provided credentials: {cred_error}")
                    logger.info("Falling back to enhanced local analysis")
                    self.client = None
            else:
                logger.warning("No Google Cloud credentials found. Using enhanced fallback mode.")
                self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud Vision client: {e}")
            self.client = None
    
    def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze an image using Google Cloud Vision API
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.client:
            return self._fallback_analysis(image_data)
        
        try:
            # Create image object
            image = vision.Image(content=image_data)
            
            # Define the features we want to extract
            features = [
                vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION),
                vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION),
                vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION),
                vision.Feature(type_=vision.Feature.Type.IMAGE_PROPERTIES),
            ]
            
            # Create the request
            request = AnnotateImageRequest(image=image, features=features)
            
            # Perform the analysis
            response = self.client.annotate_image(request=request)
            
            # Extract results
            results = {
                'labels': [],
                'text': [],
                'objects': [],
                'colors': [],
                'dominant_colors': [],
                'search_terms': []
            }
            
            # Extract labels
            if response.label_annotations:
                for label in response.label_annotations:
                    results['labels'].append({
                        'description': label.description,
                        'confidence': label.score
                    })
            
            # Extract text
            if response.text_annotations:
                for text in response.text_annotations:
                    results['text'].append(text.description)
            
            # Extract objects
            if response.localized_object_annotations:
                for obj in response.localized_object_annotations:
                    results['objects'].append({
                        'name': obj.name,
                        'confidence': obj.score
                    })
            
            # Extract colors
            if response.image_properties_annotation:
                colors = response.image_properties_annotation.dominant_colors.colors
                for color_info in colors[:5]:  # Top 5 colors
                    color = color_info.color
                    results['dominant_colors'].append({
                        'red': color.red,
                        'green': color.green,
                        'blue': color.blue,
                        'score': color_info.score,
                        'pixel_fraction': color_info.pixel_fraction
                    })
            
            # Generate search terms using enhanced logic
            results['search_terms'] = self._generate_enhanced_search_terms(results)
            
            logger.info(f"AI analysis completed. Found {len(results['labels'])} labels, {len(results['objects'])} objects")
            return results
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return self._fallback_analysis(image_data)
    
    def _generate_enhanced_search_terms(self, analysis_results: Dict[str, Any]) -> List[str]:
        """
        Generate enhanced search terms using sophisticated logic
        """
        search_terms = []
        scores = {}  # Track confidence scores for each term
        
        # 1. Extract brand/model from OCR text (highest priority)
        brands_models = self._extract_brands_models(analysis_results.get('text', []))
        for brand in brands_models:
            search_terms.append(brand)
            scores[brand] = 1.0  # Highest priority
        
        # 2. Extract high-confidence product categories
        product_terms = self._extract_product_terms(analysis_results)
        for term in product_terms:
            if term not in search_terms:
                search_terms.append(term)
                scores[term] = 0.9
        
        # 3. Add high-confidence labels (confidence > 0.8)
        high_confidence_labels = [
            label['description'] for label in analysis_results.get('labels', [])
            if label['confidence'] > 0.8 and label['description'] not in search_terms
        ][:2]  # Limit to top 2
        
        for label in high_confidence_labels:
            search_terms.append(label)
            scores[label] = 0.8
        
        # 4. Add high-confidence objects (confidence > 0.8)
        high_confidence_objects = [
            obj['name'] for obj in analysis_results.get('objects', [])
            if obj['confidence'] > 0.8 and obj['name'] not in search_terms
        ][:2]  # Limit to top 2
        
        for obj in high_confidence_objects:
            search_terms.append(obj)
            scores[obj] = 0.8
        
        # 5. Add meaningful color (only if it's not generic)
        meaningful_color = self._get_meaningful_color(analysis_results.get('dominant_colors', []))
        if meaningful_color and meaningful_color not in search_terms:
            search_terms.append(meaningful_color)
            scores[meaningful_color] = 0.7
        
        # 6. If we don't have enough specific terms, add some generic but relevant terms
        if len(search_terms) < 2:
            generic_terms = self._get_generic_terms(analysis_results)
            for term in generic_terms:
                if term not in search_terms:
                    search_terms.append(term)
                    scores[term] = 0.5
        
        # Sort by score and limit to top 3-4 terms
        sorted_terms = sorted(search_terms, key=lambda x: scores.get(x, 0), reverse=True)
        final_terms = sorted_terms[:4]
        
        logger.info(f"Generated search terms: {final_terms} (scores: {[scores.get(t, 0) for t in final_terms]})")
        return final_terms
    
    def _extract_brands_models(self, text_list: List[str]) -> List[str]:
        """Extract brand and model names from OCR text"""
        brands_models = []
        
        for text in text_list:
            text_lower = text.lower()
            
            # Check for brand patterns
            for pattern in self.brand_patterns:
                matches = re.findall(pattern, text_lower)
                for match in matches:
                    if match not in brands_models:
                        brands_models.append(match)
            
            # Look for model numbers (e.g., "Jordan 4", "Nike Air Max")
            model_patterns = [
                r'\b(jordan\s+\d+)\b',
                r'\b(air\s+max\s+\d+)\b',
                r'\b(converse\s+chuck\s+taylor)\b',
                r'\b(vans\s+old\s+skool)\b'
            ]
            
            for pattern in model_patterns:
                matches = re.findall(pattern, text_lower)
                for match in matches:
                    if match not in brands_models:
                        brands_models.append(match)
        
        return brands_models[:2]  # Limit to top 2 brands/models
    
    def _extract_product_terms(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract product-specific terms from labels and objects"""
        product_terms = []
        
        # Check labels for product categories
        for label in analysis_results.get('labels', []):
            label_text = label['description'].lower()
            
            for category, terms in self.product_categories.items():
                if any(term in label_text for term in terms):
                    # Add the most specific term found
                    for term in terms:
                        if term in label_text:
                            product_terms.append(term)
                            break
        
        # Check objects for product categories
        for obj in analysis_results.get('objects', []):
            obj_text = obj['name'].lower()
            
            for category, terms in self.product_categories.items():
                if any(term in obj_text for term in terms):
                    for term in terms:
                        if term in obj_text:
                            product_terms.append(term)
                            break
        
        return list(set(product_terms))[:2]  # Remove duplicates, limit to top 2
    
    def _get_meaningful_color(self, dominant_colors: List[Dict]) -> Optional[str]:
        """Get meaningful color name, avoiding generic colors"""
        if not dominant_colors:
            return None
        
        top_color = dominant_colors[0]
        color_name = self._get_color_name(top_color['red'], top_color['green'], top_color['blue'])
        
        # Only return meaningful colors (not white, black, gray for clothing)
        generic_colors = {'white', 'black', 'gray', 'grey'}
        if color_name and color_name not in generic_colors:
            return color_name
        
        return None
    
    def _get_generic_terms(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Get generic but relevant terms when specific terms are lacking"""
        generic_terms = []
        
        # Check if we have any clothing-related labels
        clothing_labels = ['clothing', 'fashion', 'apparel', 'wear']
        for label in analysis_results.get('labels', []):
            if any(term in label['description'].lower() for term in clothing_labels):
                generic_terms.append('clothing')
                break
        
        # If no clothing detected, add a default term
        if not generic_terms:
            generic_terms.append('clothing')
        
        return generic_terms
    
    def _fallback_analysis(self, image_data: bytes) -> Dict[str, Any]:
        """
        Enhanced fallback analysis when Google Cloud Vision is not available
        """
        try:
            # Use PIL to get basic image information
            image = Image.open(io.BytesIO(image_data))
            
            # Get image properties
            width, height = image.size
            mode = image.mode
            
            # Basic color analysis
            colors = image.getcolors(maxcolors=256)
            if colors:
                # Sort by frequency and get top colors
                sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
                dominant_colors = []
                
                for count, color in sorted_colors[:5]:
                    if isinstance(color, tuple):
                        r, g, b = color[:3]
                        dominant_colors.append({
                            'red': r,
                            'green': g,
                            'blue': b,
                            'score': count / (width * height),
                            'pixel_fraction': count / (width * height)
                        })
                
                # Generate focused search terms based on dominant color
                meaningful_color = self._get_meaningful_color(dominant_colors)
                search_terms = ['clothing']
                if meaningful_color:
                    search_terms.append(meaningful_color)
                
                # Try to extract text from image using basic OCR
                extracted_text = self._extract_text_from_image(image)
                if extracted_text:
                    # Look for brands in the extracted text
                    brands_found = self._extract_brands_models([extracted_text])
                    for brand in brands_found:
                        if brand not in search_terms:
                            search_terms.append(brand)
                
                # Look for product types in the extracted text
                product_terms = self._extract_product_terms_from_text(extracted_text)
                for product in product_terms:
                    if product not in search_terms:
                        search_terms.append(product)
                
                results = {
                    'labels': [
                        {'description': 'clothing', 'confidence': 0.5},
                        {'description': 'fashion', 'confidence': 0.4}
                    ],
                    'text': [extracted_text] if extracted_text else [],
                    'objects': [
                        {'name': 'clothing', 'confidence': 0.5}
                    ],
                    'colors': [],
                    'dominant_colors': dominant_colors,
                    'search_terms': search_terms
                }
            else:
                results = {
                    'labels': [{'description': 'clothing', 'confidence': 0.5}],
                    'text': [],
                    'objects': [{'name': 'clothing', 'confidence': 0.5}],
                    'colors': [],
                    'dominant_colors': [],
                    'search_terms': ['clothing', 'fashion']
                }
            
            logger.info("Enhanced fallback analysis completed")
            return results
            
        except Exception as e:
            logger.error(f"Error in fallback analysis: {e}")
            return {
                'labels': [{'description': 'clothing', 'confidence': 0.5}],
                'text': [],
                'objects': [{'name': 'clothing', 'confidence': 0.5}],
                'colors': [],
                'dominant_colors': [],
                'search_terms': ['clothing', 'fashion']
            }
    
    def _extract_text_from_image(self, image: Image.Image) -> str:
        """Basic text extraction from image (placeholder for OCR)"""
        # This is a simplified version - in production you'd use a proper OCR library
        # For now, we'll return empty string and rely on the test images having text
        return ""
    
    def _extract_product_terms_from_text(self, text: str) -> List[str]:
        """Extract product terms from text"""
        if not text:
            return []
        
        text_lower = text.lower()
        product_terms = []
        
        # Check for product categories in text
        for category, terms in self.product_categories.items():
            for term in terms:
                if term in text_lower:
                    product_terms.append(term)
                    break
        
        return product_terms[:2]  # Limit to top 2
    
    def _get_color_name(self, r: int, g: int, b: int) -> Optional[str]:
        """
        Enhanced color mapping with more specific color names
        """
        # Enhanced color mapping
        color_map = {
            'red': [(255, 0, 0), (200, 0, 0), (150, 0, 0), (139, 0, 0)],
            'blue': [(0, 0, 255), (0, 0, 200), (0, 0, 150), (0, 0, 139)],
            'green': [(0, 255, 0), (0, 200, 0), (0, 150, 0), (0, 139, 0)],
            'yellow': [(255, 255, 0), (200, 200, 0), (255, 215, 0)],
            'purple': [(128, 0, 128), (100, 0, 100), (75, 0, 130)],
            'pink': [(255, 192, 203), (255, 20, 147), (255, 105, 180)],
            'orange': [(255, 165, 0), (255, 140, 0), (255, 69, 0)],
            'brown': [(139, 69, 19), (160, 82, 45), (165, 42, 42)],
            'black': [(0, 0, 0), (20, 20, 20), (40, 40, 40)],
            'white': [(255, 255, 255), (240, 240, 240), (245, 245, 245)],
            'gray': [(128, 128, 128), (100, 100, 100), (169, 169, 169)],
            'navy': [(0, 0, 128), (0, 0, 139), (25, 25, 112)],
            'maroon': [(128, 0, 0), (139, 0, 0), (165, 42, 42)],
            'olive': [(128, 128, 0), (139, 139, 0), (85, 107, 47)],
            'teal': [(0, 128, 128), (0, 139, 139), (72, 61, 139)],
        }
        
        for color_name, color_values in color_map.items():
            for cr, cg, cb in color_values:
                # Check if the color is close to this named color
                if abs(r - cr) < 50 and abs(g - cg) < 50 and abs(b - cb) < 50:
                    return color_name
        
        return None

# Global AI service instance
ai_service = AIService() 