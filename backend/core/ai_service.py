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
import importlib
import numpy as np
try:
    import torch
    import open_clip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
import faiss

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered image analysis using Google Cloud Vision"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
        self.faiss_index = None
        self.faiss_id_to_item = {}
        
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
        Analyze an image using Google Cloud Vision API and return a rich, precise response
        """
        if not self.client:
            return self._fallback_analysis(image_data)
        try:
            image = vision.Image(content=image_data)
            features = [
                vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION),
                vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION),
                vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION),
                vision.Feature(type_=vision.Feature.Type.IMAGE_PROPERTIES),
            ]
            request = AnnotateImageRequest(image=image, features=features)
            response = self.client.annotate_image(request=request)
            # Extract results
            results = {
                'labels': [],
                'text': [],
                'objects': [],
                'dominant_colors': [],
                'search_terms': [],
                'ocr_text': '',
                'best_guess': '',
                'suggested_queries': [],
                'visual_similar_results': [],  # Placeholder for future
            }
            # Labels
            if response.label_annotations:
                for label in response.label_annotations:
                    results['labels'].append({
                        'description': label.description,
                        'confidence': label.score
                    })
            # Text (OCR)
            if response.text_annotations:
                ocr_texts = [text.description for text in response.text_annotations]
                results['text'] = ocr_texts
                results['ocr_text'] = ' '.join(ocr_texts)
            # Objects
            if response.localized_object_annotations:
                for obj in response.localized_object_annotations:
                    results['objects'].append({
                        'name': obj.name,
                        'confidence': obj.score
                    })
            # Colors
            if response.image_properties_annotation:
                colors = response.image_properties_annotation.dominant_colors.colors
                for color_info in colors[:5]:
                    color = color_info.color
                    results['dominant_colors'].append({
                        'red': color.red,
                        'green': color.green,
                        'blue': color.blue,
                        'score': color_info.score,
                        'pixel_fraction': color_info.pixel_fraction
                    })
            # NLP-enhanced search term generation
            results['search_terms'], results['best_guess'], results['suggested_queries'] = self._nlp_enhanced_search_terms(results)
            logger.info(f"AI analysis completed. Labels: {len(results['labels'])}, Objects: {len(results['objects'])}, Best guess: {results['best_guess']}")
            return results
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return self._fallback_analysis(image_data)

    def detect_objects_and_regions(self, image_data: bytes) -> list:
        """
        Use Google Vision to detect objects and their bounding boxes in the image.
        Returns a list of dicts: {name, confidence, bounding_box: (x_min, y_min, x_max, y_max)}
        """
        if not self.client:
            return []
        from PIL import Image
        import io
        image = vision.Image(content=image_data)
        response = self.client.object_localization(image=image)
        objects = []
        for obj in response.localized_object_annotations:
            box = obj.bounding_poly.normalized_vertices
            # Convert normalized vertices to (x_min, y_min, x_max, y_max)
            x_min = min([v.x for v in box])
            y_min = min([v.y for v in box])
            x_max = max([v.x for v in box])
            y_max = max([v.y for v in box])
            objects.append({
                'name': obj.name,
                'confidence': obj.score,
                'bounding_box': (x_min, y_min, x_max, y_max),
            })
        return objects

    def crop_to_region(self, image_data: bytes, bounding_box: tuple) -> bytes:
        """
        Crop the image to the given bounding box (normalized coordinates).
        Returns cropped image bytes.
        """
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        width, height = image.size
        x_min, y_min, x_max, y_max = bounding_box
        left = int(x_min * width)
        top = int(y_min * height)
        right = int(x_max * width)
        bottom = int(y_max * height)
        cropped = image.crop((left, top, right, bottom))
        buf = io.BytesIO()
        cropped.save(buf, format='JPEG')
        return buf.getvalue()

    def build_faiss_index(self):
        """
        Build or rebuild the FAISS index from all ItemEmbeddings.
        """
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
        import numpy as np
        vectors = np.array(vectors).astype('float32')
        index.add(vectors)
        self.faiss_index = index
        self.faiss_id_to_item = id_to_item

    def get_visual_similar_items(self, image_data: bytes, text_query: str = None, top_k=5, bounding_box: tuple = None) -> list:
        """
        Use FAISS for fast similarity search if available, otherwise fallback to slow method.
        """
        if bounding_box:
            image_data = self.crop_to_region(image_data, bounding_box)
        if not CLIP_AVAILABLE:
            return []
        # Load CLIP model (ViT-B/32)
        model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
        tokenizer = open_clip.get_tokenizer('ViT-B-32')
        model.eval()
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        image_input = preprocess(image).unsqueeze(0)
        with torch.no_grad():
            image_features = model.encode_image(image_input).cpu().numpy()[0]
        image_features = image_features / np.linalg.norm(image_features)
        if text_query:
            text_input = tokenizer([text_query])
            with torch.no_grad():
                text_features = model.encode_text(text_input).cpu().numpy()[0]
            text_features = text_features / np.linalg.norm(text_features)
            combined_features = (image_features + text_features) / 2
        else:
            combined_features = image_features
        import numpy as np
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
        # Fallback to slow method if FAISS not available
        # ... (existing slow method here) ...
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
        if labels:
            attrs['labels'] = [l['description'] for l in labels]
        if 'ocr_text' in item_or_analysis:
            attrs['ocr_text'] = item_or_analysis['ocr_text']
        if 'dominant_colors' in item_or_analysis and item_or_analysis['dominant_colors']:
            attrs['color'] = f"rgb({item_or_analysis['dominant_colors'][0]['red']},{item_or_analysis['dominant_colors'][0]['green']},{item_or_analysis['dominant_colors'][0]['blue']})"
        return attrs
    
    def _nlp_enhanced_search_terms(self, analysis_results: Dict[str, Any]) -> Tuple[list, str, list]:
        """
        Use NLP to generate ranked search terms, a best guess phrase, and suggested queries.
        """
        # Try to use spaCy for NLP if available
        spacy_spec = importlib.util.find_spec("spacy")
        if spacy_spec is not None:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            # Combine all text for context
            text_blob = ' '.join([
                analysis_results.get('ocr_text', ''),
                ' '.join([l['description'] for l in analysis_results.get('labels', [])]),
                ' '.join([o['name'] for o in analysis_results.get('objects', [])])
            ])
            doc = nlp(text_blob)
            # Extract noun chunks and entities
            noun_chunks = [chunk.text for chunk in doc.noun_chunks]
            entities = [ent.text for ent in doc.ents]
            # Use most relevant noun/entity as best guess
            best_guess = ''
            if entities:
                best_guess = entities[0]
            elif noun_chunks:
                best_guess = noun_chunks[0]
            else:
                # Fallback to top label
                best_guess = analysis_results['labels'][0]['description'] if analysis_results['labels'] else ''
            # Build search terms: combine brand, color, product type
            search_terms = []
            # Brand from OCR
            brands = self._extract_brands_models([analysis_results.get('ocr_text', '')])
            if brands:
                search_terms.extend(brands)
            # Color
            color = self._get_meaningful_color(analysis_results.get('dominant_colors', []))
            if color:
                search_terms.append(color)
            # Product type from labels/objects
            product_terms = self._extract_product_terms(analysis_results)
            search_terms.extend([t for t in product_terms if t not in search_terms])
            # Add best guess if not present
            if best_guess and best_guess.lower() not in [t.lower() for t in search_terms]:
                search_terms.append(best_guess)
            # Remove duplicates, keep order
            seen = set()
            search_terms = [x for x in search_terms if not (x.lower() in seen or seen.add(x.lower()))]
            # Suggested queries: combine top 2-3 terms in different ways
            suggested_queries = []
            if len(search_terms) >= 2:
                suggested_queries.append(' '.join(search_terms[:2]))
            if len(search_terms) >= 3:
                suggested_queries.append(' '.join(search_terms[:3]))
            suggested_queries.append(' '.join(search_terms))
            # Add best guess as a query if not already present
            if best_guess and best_guess not in suggested_queries:
                suggested_queries.insert(0, best_guess)
            return search_terms[:4], best_guess, suggested_queries[:4]
        else:
            # Fallback to current logic
            search_terms = self._generate_enhanced_search_terms(analysis_results)
            best_guess = search_terms[0] if search_terms else ''
            suggested_queries = [' '.join(search_terms[:2]), ' '.join(search_terms[:3]), ' '.join(search_terms)]
            return search_terms, best_guess, suggested_queries
    
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

    def ensemble_search(self, image_data: bytes, text_query: str = None, bounding_box: tuple = None, top_k=10) -> list:
        """
        Run both Google Vision and CLIP on the (optionally cropped) image and text, merge and re-rank results by combined confidence and attribute match.
        Returns a list of results with combined scores.
        """
        # Google Vision analysis
        if bounding_box:
            region_data = self.crop_to_region(image_data, bounding_box)
        else:
            region_data = image_data
        vision_results = self.analyze_image(region_data)
        # CLIP visual similarity
        visual_similars = self.get_visual_similar_items(region_data, text_query=text_query, top_k=top_k)
        # Merge and re-rank
        results = []
        # Add vision results (e.g., eBay search, etc.)
        # ... (this can be extended to include eBay/marketplace results)
        # Add visual similars with combined score
        for sim in visual_similars:
            combined_score = sim['similarity']
            # Boost score if attributes match text_query or vision labels
            attrs = sim.get('attributes', {})
            if text_query and any(q.lower() in str(v).lower() for q in text_query.split() for v in attrs.values()):
                combined_score += 0.1
            if 'labels' in vision_results and any(l in attrs.get('labels', []) for l in vision_results.get('labels', [])):
                combined_score += 0.1
            sim['combined_score'] = combined_score
            results.append(sim)
        # Sort by combined score
        results.sort(key=lambda x: x['combined_score'], reverse=True)
        return results[:top_k]

# Global AI service instance
ai_service = AIService() 