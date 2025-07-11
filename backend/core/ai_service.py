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
from rapidfuzz import process, fuzz

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered image analysis using Google Cloud Vision"""
    
    def __init__(self):
        logger.info("AIService __init__ called")
        self.client = None
        self._initialize_client()
        self.faiss_index = None
        self.faiss_id_to_item = {}
        
        # Initialize CLIP model if available
        self.clip_model = None
        self.clip_tokenizer = None
        self.clip_preprocess = None
        if CLIP_AVAILABLE:
            try:
                model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
                self.clip_model = model
                self.clip_tokenizer = open_clip.get_tokenizer('ViT-B-32')
                self.clip_preprocess = preprocess
                logger.info("OpenCLIP ViT-B-32 (openai) model initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize CLIP model: {e}")
                self.clip_model = None
                self.clip_tokenizer = None
                self.clip_preprocess = None
        else:
            logger.warning("CLIP not available, visual similarity features will be disabled")
        
        # Define product categories and their search terms
        self.product_categories = {
            'shoes': [
                'sneakers', 'boots', 'shoes', 'footwear', 'jordan', 'nike', 'adidas', 'loafers', 'sandals', 'heels', 'flats', 'slippers', 'cleats', 'oxfords', 'converse', 'vans', 'yeezy', 'puma', 'reebok', 'crocs', 'asics', 'new balance', 'under armour', 'fila', 'skechers', 'brooks', 'saucony', 'hoka', 'on running', 'timberland', 'dr martens', 'ugg'
            ],
            'clothing': [
                'shirt', 't-shirt', 'tee', 'hoodie', 'sweatshirt', 'jacket', 'coat', 'dress', 'pants', 'jeans', 'shorts', 'skirt', 'blouse', 'sweater', 'cardigan', 'tank', 'top', 'suit', 'blazer', 'trousers', 'leggings', 'activewear', 'polo', 'jersey', 'vest', 'overalls', 'swimsuit', 'bodysuit', 'kimono', 'robe', 'anorak', 'windbreaker', 'parka', 'raincoat',
                'button up', 'button-down', 'long sleeve', 'short sleeve', 'oxford', 'dress shirt', 'henley', 'tunic', 'crop top', 'tube top', 'halter', 'peacoat', 'bomber', 'parka', 'field jacket', 'military jacket', 'fleece', 'thermal', 'undershirt', 'base layer', 'cami', 'camisole', 'tank top', 'mock neck', 'turtleneck', 'zip up', 'pullover', 'crewneck', 'v-neck'
            ],
            'accessories': [
                'bag', 'purse', 'wallet', 'hat', 'cap', 'sunglasses', 'jewelry', 'belt', 'scarf', 'gloves', 'watch', 'bracelet', 'necklace', 'ring', 'earrings', 'backpack', 'beanie', 'headband', 'tie', 'cufflinks', 'umbrella', 'luggage', 'duffel', 'fanny pack', 'satchel', 'tote', 'clutch', 'crossbody', 'messenger', 'briefcase', 'keychain', 'brooch', 'hairpin'
            ]
        }
        
        # Define brand patterns for OCR detection
        self.brand_patterns = [
            r'\b(nike|adidas|jordan|puma|reebok|converse|vans|yeezy|asics|new balance|under armour|fila|skechers|brooks|saucony|hoka|on running|timberland|dr martens|ugg|crocs)\b',
            r'\b(gucci|prada|louis\s+vuitton|chanel|hermes|balenciaga|burberry|versace|fendi|dior|givenchy|celine|coach|kate spade|michael kors|tory burch|marc jacobs|longchamp|fossil|dooney|gabbana|dolce)\b',
            r'\b(levi\'s|calvin\s+klein|tommy\s+hilfiger|ralph\s+lauren|lacoste|armani|diesel|guess|hugo boss|zara|uniqlo|gap|banana republic|old navy|express|abercrombie|hollister|aeropostale|patagonia|columbia|north face|canada goose|moncler)\b'
        ]
        
        # Large list of known brands for fuzzy matching
        self.known_brands = [
            'nike', 'adidas', 'jordan', 'puma', 'reebok', 'levi\'s', 'wrangler', 'lee', 'patagonia', 'the north face', 'columbia',
            'gucci', 'prada', 'louis vuitton', 'burberry', 'versace', 'hermes', 'fendi', 'balenciaga', 'givenchy', 'dior', 'celine',
            'tommy hilfiger', 'ralph lauren', 'lacoste', 'armani', 'calvin klein', 'coach', 'kate spade', 'michael kors', 'tory burch',
            'under armour', 'asics', 'fila', 'skechers', 'brooks', 'saucony', 'hoka', 'on running', 'timberland', 'dr martens', 'ugg',
            'vans', 'converse', 'yeezy', 'new balance', 'supreme', 'off-white', 'bape', 'stone island', 'moncler', 'canada goose',
            'zara', 'uniqlo', 'h&m', 'gap', 'banana republic', 'abercrombie', 'fitch', 'aeropostale', 'express', 'guess', 'diesel',
            'balmain', 'moschino', 'kenzo', 'valentino', 'loewe', 'marc jacobs', 'dsquared2', 'fear of god', 'palm angels', 'ami',
            'fred perry', 'g-star', 'allsaints', 'rag & bone', 'reiss', 'topman', 'river island', 'jack & jones', 'superdry', 'barbour',
            'carhartt', 'stussy', 'obey', 'rvca', 'volcom', 'billabong', 'quiksilver', 'roxy', 'oakley', 'spyder', 'columbia', 'mammut',
            'salomon', 'merrell', 'keen', 'teva', 'chaco', 'birkenstock', 'crocs', 'hunter', 'sorel', 'blundstone', 'clarks', 'geox',
            'ecco', 'rockport', 'mephisto', 'sebago', 'dockers', 'florsheim', 'allen edmonds', 'johnston & murphy', 'cole haan',
            'steve madden', 'aldo', 'sam edelman', 'vince camuto', 'nine west', 'clarks', 'naturalizer', 'franco sarto', 'lucky brand',
            'toms', 'keds', 'sperry', 'havaianas', 'reef', 'sanuk', 'teva', 'rainbow', 'ugg', 'emu', 'bearpaw', 'minnetonka', 'muk luks',
            'ugg', 'emu', 'bearpaw', 'minnetonka', 'muk luks', 'ugg', 'emu', 'bearpaw', 'minnetonka', 'muk luks', 'ugg', 'emu', 'bearpaw',
            'minnetonka', 'muk luks', 'ugg', 'emu', 'bearpaw', 'minnetonka', 'muk luks', 'ugg', 'emu', 'bearpaw', 'minnetonka', 'muk luks'
        ]
    
    def _initialize_client(self):
        logger.info("_initialize_client called for AIService")
        """Initialize Google Cloud Vision client"""
        import traceback
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        logger.info(f"GOOGLE_APPLICATION_CREDENTIALS at init: {credentials_path}")
        if credentials_path and os.path.exists(credentials_path):
            logger.info(f"Credentials file found at {credentials_path}")
        else:
            logger.error(f"Credentials file not found at {credentials_path}")
        try:
            from google.cloud import vision
            self.client = vision.ImageAnnotatorClient()
            logger.info("Google Cloud Vision client initialized successfully.")
        except Exception as e:
            logger.exception(f"Error initializing Google Cloud Vision client: {e}")
            self.client = None
    
    def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze an image using Google Cloud Vision API and return a rich, precise response
        """
        if not self.client:
            logger.warning("No Google Vision client available, using fallback analysis")
            return self._fallback_analysis(image_data)
        
        try:
            # Validate image data
            if not image_data or len(image_data) == 0:
                logger.error("Empty image data provided")
                return self._fallback_analysis(image_data)
            
            logger.info(f"Starting AI analysis with image data of size: {len(image_data)} bytes")
            
            # Try to validate the image data first
            try:
                from PIL import Image
                import io
                test_image = Image.open(io.BytesIO(image_data))
                logger.info(f"Image validation successful: {test_image.size} {test_image.mode}")
            except Exception as e:
                logger.error(f"Invalid image data: {e}")
                return self._fallback_analysis(image_data)
            
            image = vision.Image(content=image_data)
            features = [
                vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION),
                vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION),
                vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION),
                vision.Feature(type_=vision.Feature.Type.IMAGE_PROPERTIES),
                vision.Feature(type_=vision.Feature.Type.WEB_DETECTION),  # Added Web Entities
            ]
            request = vision.AnnotateImageRequest(image=image, features=features)
            
            logger.info("Sending batch request to Google Vision API")
            response = self.client.batch_annotate_images(requests=[request])
            
            if not response.responses:
                logger.warning("No response from Google Vision API, using fallback")
                return self._fallback_analysis(image_data)
                
            result_response = response.responses[0]
            
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
            if result_response.label_annotations:
                for label in result_response.label_annotations:
                    results['labels'].append({
                        'description': label.description,
                        'confidence': label.score
                    })
            # Text (OCR)
            if result_response.text_annotations:
                ocr_texts = [text.description for text in result_response.text_annotations]
                results['text'] = ocr_texts
                results['ocr_text'] = ' '.join(ocr_texts)
            # Debug: Log raw OCR text and labels
            logger.info(f"Raw OCR text: {results['ocr_text']}")
            logger.info(f"Extracted labels: {[l['description'] for l in results['labels']]}")
            # Objects
            if result_response.localized_object_annotations:
                for obj in result_response.localized_object_annotations:
                    results['objects'].append({
                        'name': obj.name,
                        'confidence': obj.score
                    })
            # Colors
            if result_response.image_properties_annotation:
                colors = result_response.image_properties_annotation.dominant_colors.colors
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
            logger.warning("No Google Vision client available")
            return []
        
        try:
            from PIL import Image
            import io
            
            # Validate image data
            if not image_data or len(image_data) == 0:
                logger.error("Empty image data provided")
                return []
            
            logger.info(f"Processing image data of size: {len(image_data)} bytes")
            
            # Try to validate the image data first
            try:
                test_image = Image.open(io.BytesIO(image_data))
                logger.info(f"Image validation successful: {test_image.size} {test_image.mode}")
            except Exception as e:
                logger.error(f"Invalid image data: {e}")
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
                x_min = min([v.x for v in box])
                y_min = min([v.y for v in box])
                x_max = max([v.x for v in box])
                y_max = max([v.y for v in box])
                objects.append({
                    'name': obj.name,
                    'confidence': obj.score,
                    'bounding_box': (x_min, y_min, x_max, y_max),
                })
            
            logger.info(f"Detected {len(objects)} objects in image")
            return objects
            
        except Exception as e:
            logger.error(f"Error in detect_objects_and_regions: {e}")
            return []

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
            # Convert to list of dicts with 'description' key if it's not already
            if labels and isinstance(labels[0], str):
                attrs['labels'] = [{'description': l} for l in labels]
            else:
                attrs['labels'] = labels
        if 'ocr_text' in item_or_analysis:
            attrs['ocr_text'] = item_or_analysis['ocr_text']
        if 'dominant_colors' in item_or_analysis and item_or_analysis['dominant_colors']:
            attrs['color'] = f"rgb({item_or_analysis['dominant_colors'][0]['red']},{item_or_analysis['dominant_colors'][0]['green']},{item_or_analysis['dominant_colors'][0]['blue']})"
        return attrs
    
    def _nlp_enhanced_search_terms(self, analysis_results: Dict[str, Any]) -> Tuple[list, str, list]:
        """
        Use NLP to generate ranked search terms, a best guess phrase, and suggested queries.
        Always prioritize detected brand and product type at the front of the search_terms list.
        """
        spacy_spec = importlib.util.find_spec("spacy")
        if spacy_spec is not None:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            text_blob = ' '.join([
                analysis_results.get('ocr_text', ''),
                ' '.join([l['description'] for l in analysis_results.get('labels', [])]),
                ' '.join([o['name'] for o in analysis_results.get('objects', [])])
            ])
            doc = nlp(text_blob)
            noun_chunks = [chunk.text for chunk in doc.noun_chunks]
            entities = [ent.text for ent in doc.ents]
            best_guess = ''
            if entities:
                best_guess = entities[0]
            elif noun_chunks:
                best_guess = noun_chunks[0]
            else:
                best_guess = analysis_results['labels'][0]['description'] if analysis_results['labels'] else ''
            # Build search terms: combine brand, color, product type
            search_terms = []
            # Brand from OCR
            brands = self._extract_brands_models([analysis_results.get('ocr_text', '')])
            # Product type from labels/objects
            product_terms = self._extract_product_terms(analysis_results)
            # Always prioritize brand and product type
            prioritized = []
            if brands:
                prioritized.extend(brands)
            if product_terms:
                for pt in product_terms:
                    if pt not in prioritized:
                        prioritized.append(pt)
            # Color
            color = self._get_meaningful_color(analysis_results.get('dominant_colors', []))
            if color and color not in prioritized:
                prioritized.append(color)
            # Add best guess if not present
            if best_guess and best_guess.lower() not in [t.lower() for t in prioritized]:
                prioritized.append(best_guess)
            # Remove duplicates, keep order
            seen = set()
            search_terms = [x for x in prioritized if not (x.lower() in seen or seen.add(x.lower()))]
            # Suggested queries: combine top 2-3 terms in different ways
            suggested_queries = []
            if len(search_terms) >= 2:
                suggested_queries.append(' '.join(search_terms[:2]))
            if len(search_terms) >= 3:
                suggested_queries.append(' '.join(search_terms[:3]))
            suggested_queries.append(' '.join(search_terms))
            if best_guess and best_guess not in suggested_queries:
                suggested_queries.insert(0, best_guess)
            return search_terms[:4], best_guess, suggested_queries[:4]
        else:
            # Fallback to simple logic without spaCy
            search_terms = []
            best_guess = ''
            brands = self._extract_brands_models([analysis_results.get('ocr_text', '')])
            product_terms = self._extract_product_terms(analysis_results)
            prioritized = []
            if brands:
                prioritized.extend(brands)
            if product_terms:
                for pt in product_terms:
                    if pt not in prioritized:
                        prioritized.append(pt)
            color = self._get_meaningful_color(analysis_results.get('dominant_colors', []))
            if color and color not in prioritized:
                prioritized.append(color)
            if not best_guess and analysis_results.get('labels'):
                best_guess = analysis_results['labels'][0]['description']
                if best_guess.lower() not in [t.lower() for t in prioritized]:
                    prioritized.insert(0, best_guess)
            if not prioritized:
                prioritized = self._get_generic_terms(analysis_results)
                best_guess = prioritized[0] if prioritized else 'clothing'
            suggested_queries = []
            if len(prioritized) >= 2:
                suggested_queries.append(' '.join(prioritized[:2]))
            if len(prioritized) >= 3:
                suggested_queries.append(' '.join(prioritized[:3]))
            suggested_queries.append(' '.join(prioritized))
            return prioritized[:4], best_guess, suggested_queries[:4]
    
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

    def fuzzy_find_brand(self, ocr_text):
        if not ocr_text:
            return ""
        match, score, _ = process.extractOne(ocr_text, self.known_brands, scorer=fuzz.partial_ratio)
        logger.info(f"[FUZZY BRAND] OCR: '{ocr_text}' | Match: '{match}' | Score: {score}")
        return match.title() if score and score > 80 else ""

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

    def hybrid_image_search(self, image_data: bytes, ebay_search_func, top_k=10) -> list:
        """
        Hybrid search: Use Google Vision for search terms, fetch eBay results, then re-rank with CLIP similarity.
        ebay_search_func: function that takes a list of queries and returns eBay items (dicts with 'title', etc.)
        """
        logger.info("[HYBRID] Starting hybrid image search...")
        # Step 1: Google Vision extraction
        analysis_results = self.analyze_image(image_data)
        # Print only the most relevant fields for debugging
        debug_labels = analysis_results.get('labels', [])
        debug_objects = analysis_results.get('objects', [])
        debug_ocr = analysis_results.get('ocr_text', '')
        debug_web = analysis_results.get('web_entities', []) if 'web_entities' in analysis_results else []
        print(f"[DEBUG] (ai_service) Vision summary: labels={debug_labels}, objects={debug_objects}, ocr_text='{debug_ocr}', web_entities={debug_web}")
        attributes = self.extract_attributes(analysis_results)
        logger.info(f"[HYBRID] Vision attributes: {attributes}")
        # --- Generalized Apparel/Footwear Search Term Extraction ---
        # 1. Mappings for brands, product types, and sports teams/events
        BRAND_MAPPINGS = {
            'nike': 'nike', 'adidas': 'adidas', 'puma': 'puma', 'reebok': 'reebok', 'asics': 'asics',
            'new balance': 'new balance', 'under armour': 'under armour', 'converse': 'converse',
            'vans': 'vans', 'fila': 'fila', 'skechers': 'skechers', 'levis': "levi's", 'levi': "levi's",
            'gucci': 'gucci', 'prada': 'prada', 'zara': 'zara', 'h&m': 'h&m', 'uniqlo': 'uniqlo',
            'gap': 'gap', 'ralph lauren': 'ralph lauren', 'lacoste': 'lacoste', 'tommy hilfiger': 'tommy hilfiger',
            'calvin klein': 'calvin klein', 'columbia': 'columbia', 'patagonia': 'patagonia', 'north face': 'the north face',
            'timberland': 'timberland', 'dr martens': 'dr martens', 'birkenstock': 'birkenstock', 'ugg': 'ugg',
            'balenciaga': 'balenciaga', 'off-white': 'off-white', 'supreme': 'supreme', 'bape': 'bape',
            'armani': 'armani', 'versace': 'versace', 'burberry': 'burberry', 'moncler': 'moncler',
            'canada goose': 'canada goose', 'stone island': 'stone island', 'crocs': 'crocs',
        }
        PRODUCT_TYPE_MAPPINGS = {
            'shirt': 'shirt', 't-shirt': 't-shirt', 'tee': 't-shirt', 'jersey': 'jersey', 'dress': 'dress',
            'jeans': 'jeans', 'pants': 'pants', 'shorts': 'shorts', 'skirt': 'skirt', 'jacket': 'jacket',
            'coat': 'coat', 'hoodie': 'hoodie', 'sweatshirt': 'sweatshirt', 'sweater': 'sweater',
            'blazer': 'blazer', 'suit': 'suit', 'vest': 'vest', 'tank': 'tank top', 'top': 'top',
            'sneakers': 'sneakers', 'shoes': 'shoes', 'boots': 'boots', 'heels': 'heels', 'sandals': 'sandals',
            'flip flops': 'flip flops', 'loafer': 'loafers', 'slipper': 'slippers', 'cleats': 'cleats',
            'slides': 'slides', 'moccasin': 'moccasins', 'oxford': 'oxfords', 'derby': 'derby shoes',
            'brogue': 'brogues', 'wingtip': 'wingtips', 'espadrille': 'espadrilles', 'pump': 'pumps',
            'platform': 'platform shoes', 'wedge': 'wedges', 'clog': 'clogs',
        }
        COLOR_WORDS = {'white','black','red','blue','green','yellow','orange','purple','pink','brown','grey','gray','beige','tan','navy','maroon','burgundy','gold','silver','ivory','teal','olive','mint','peach','coral','mustard','aqua','turquoise','lavender','violet','charcoal','cream'}
        # Sports mappings (NBA, NFL, MLB, NHL, events, cities) from previous code
        TEAM_MAPPINGS = {
            # NBA
            'wolves': 'minnesota timberwolves',
            'lakers': 'los angeles lakers',
            'warriors': 'golden state warriors',
            'celtics': 'boston celtics',
            'knicks': 'new york knicks',
            'bucks': 'milwaukee bucks',
            'suns': 'phoenix suns',
            'heat': 'miami heat',
            'bulls': 'chicago bulls',
            'mavs': 'dallas mavericks',
            'mavericks': 'dallas mavericks',
            'spurs': 'san antonio spurs',
            'raptors': 'toronto raptors',
            'hawks': 'atlanta hawks',
            'nuggets': 'denver nuggets',
            'sixers': 'philadelphia 76ers',
            '76ers': 'philadelphia 76ers',
            'clippers': 'los angeles clippers',
            'jazz': 'utah jazz',
            'magic': 'orlando magic',
            'kings': 'sacramento kings',
            'nets': 'brooklyn nets',
            'pelicans': 'new orleans pelicans',
            'pistons': 'detroit pistons',
            'rockets': 'houston rockets',
            'thunder': 'oklahoma city thunder',
            'trail blazers': 'portland trail blazers',
            'blazers': 'portland trail blazers',
            'wizards': 'washington wizards',
            'hornets': 'charlotte hornets',
            'grizzlies': 'memphis grizzlies',
            'pacers': 'indiana pacers',
            'cavaliers': 'cleveland cavaliers',
            # NFL (sample)
            'patriots': 'new england patriots',
            'packers': 'green bay packers',
            'cowboys': 'dallas cowboys',
            'giants': 'new york giants',
            'jets': 'new york jets',
            'bears': 'chicago bears',
            'chiefs': 'kansas city chiefs',
            # MLB (sample)
            'yankees': 'new york yankees',
            'dodgers': 'los angeles dodgers',
            'red sox': 'boston red sox',
            'cubs': 'chicago cubs',
            # NHL (sample)
            'bruins': 'boston bruins',
            'rangers': 'new york rangers',
            'canadiens': 'montreal canadiens',
            # Events/Cities
            'playoffs': 'playoffs',
            'finals': 'finals',
            'super bowl': 'super bowl',
            'world series': 'world series',
            'stanley cup': 'stanley cup',
            'nba': 'nba',
            'mlb': 'mlb',
            'nfl': 'nfl',
            'nhl': 'nhl',
            'minnesota': 'minnesota',
            'boston': 'boston',
            'los angeles': 'los angeles',
            'new york': 'new york',
            'chicago': 'chicago',
            'dallas': 'dallas',
            'miami': 'miami',
            'houston': 'houston',
            'philadelphia': 'philadelphia',
            'phoenix': 'phoenix',
            'san antonio': 'san antonio',
            'toronto': 'toronto',
            'atlanta': 'atlanta',
            'denver': 'denver',
            'utah': 'utah',
            'orlando': 'orlando',
            'sacramento': 'sacramento',
            'brooklyn': 'brooklyn',
            'new orleans': 'new orleans',
            'detroit': 'detroit',
            'oklahoma city': 'oklahoma city',
            'portland': 'portland',
            'washington': 'washington',
            'charlotte': 'charlotte',
            'memphis': 'memphis',
            'indiana': 'indiana',
            'cleveland': 'cleveland',
        }
        GENERIC_TERMS = {'clothing','apparel','wear','gear','sportswear','activewear','outfit','garment','outerwear','footwear','accessory','sleeve','top','bottom','item','thing'}
        # 2. Gather all detected words
        all_words = set()
        if debug_ocr:
            for word in debug_ocr.replace('\n', ' ').split():
                w = word.strip().lower()
                if len(w) > 2 and w not in {'the','and','for','with','new','tags'}:
                    all_words.add(w)
        all_words.update(l['description'].lower() for l in debug_labels if l.get('description'))
        all_words.update(o['name'].lower() for o in debug_objects if o.get('name'))
        print(f"[DEBUG] (ai_service) all_words: {all_words}")
        # 3. Extract brand, product type, color, team/event/city, year
        brand = next((BRAND_MAPPINGS[w] for w in all_words if w in BRAND_MAPPINGS), None)
        product_type = next((PRODUCT_TYPE_MAPPINGS[w] for w in all_words if w in PRODUCT_TYPE_MAPPINGS), None)
        color = next((w for w in all_words if w in COLOR_WORDS), None)
        team = next((TEAM_MAPPINGS[w] for w in all_words if w in TEAM_MAPPINGS), None)
        year = next((w for w in all_words if w.isdigit() and len(w) == 4), None)
        # 4. Build distinguishing features (other non-generic, non-brand, non-type, non-color, non-team words)
        used = set(filter(None, [brand, product_type, color, team, year]))
        features = [w for w in all_words if w not in GENERIC_TERMS and w not in used and not w.isdigit() and w not in BRAND_MAPPINGS and w not in PRODUCT_TYPE_MAPPINGS and w not in COLOR_WORDS and w not in TEAM_MAPPINGS]
        print(f"[DEBUG] (ai_service) brand: {brand}, product_type: {product_type}, color: {color}, team: {team}, year: {year}, features: {features}")
        # 5. Build final query: [team] [brand] [color] [year] [product_type] [features...]
        query_parts = []
        if team: query_parts.append(team)
        if brand: query_parts.append(brand)
        if color: query_parts.append(color)
        if year: query_parts.append(year)
        if product_type: query_parts.append(product_type)
        query_parts.extend(features)
        # If nothing specific, fallback to mapped_terms or all_words
        if not query_parts:
            query_parts = list(all_words - GENERIC_TERMS)
        final_query = ' '.join(query_parts)
        print(f"[DEBUG] (ai_service) FINAL EBAY QUERY: '{final_query}' (from: {query_parts})")
        search_terms = [final_query]
        suggested_queries = [final_query]
        # Use improved search_terms for eBay
        best_guess = search_terms[0] if search_terms else ''
        logger.info(f"[HYBRID] Generated search_terms: {search_terms}, best_guess: {best_guess}, suggested_queries: {suggested_queries}")
        if not search_terms:
            logger.warning("[HYBRID] No queries generated from image.")
            return []
        # Step 2: Fetch eBay results
        logger.info(f"[HYBRID] Querying eBay with search_terms: {search_terms}")
        ebay_items = ebay_search_func(search_terms)
        logger.info(f"[HYBRID] Got {len(ebay_items)} eBay items. Titles: {[item.get('title','') for item in ebay_items[:5]]}")
        if not ebay_items:
            logger.warning("[HYBRID] No eBay items found for search_terms: {search_terms}")
            return []
        # Step 3: Check if CLIP is available for re-ranking
        if not self.clip_model or not self.clip_tokenizer:
            logger.warning("[HYBRID] CLIP model not available, returning eBay results without re-ranking")
            return ebay_items[:top_k]
        # Step 4: CLIP encode query image
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        preprocess = self.clip_preprocess
        image_input = preprocess(image).unsqueeze(0)
        with torch.no_grad():
            image_features = self.clip_model.encode_image(image_input).cpu().numpy()[0]
        image_features = image_features / np.linalg.norm(image_features)
        # Step 5: CLIP encode eBay titles
        titles = [item.get('title', '') for item in ebay_items]
        text_inputs = self.clip_tokenizer(titles)
        with torch.no_grad():
            text_features = self.clip_model.encode_text(text_inputs).cpu().numpy()
        text_features = text_features / np.linalg.norm(text_features, axis=1, keepdims=True)
        # Step 6: Compute similarity
        sims = np.dot(text_features, image_features)
        ranked_indices = np.argsort(sims)[::-1][:top_k]
        ranked_items = [ebay_items[i] for i in ranked_indices]
        logger.info(f"[HYBRID] Top ranked item titles: {[ebay_items[i]['title'] for i in ranked_indices]}")
        return ranked_items

# Global AI service instance (lazy initialization)
_ai_service_instance = None

def get_ai_service():
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance 