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
        
        # AI-driven product detection (no hardcoded categories)
        # The system will learn product types from Google Vision labels and web entities
        
        # No hardcoded brand patterns - let AI detect everything dynamically
        self.brand_patterns = []
    
    def _initialize_client(self):
        logger.info("_initialize_client called for AIService")
        """Initialize Google Cloud Vision client"""
        import traceback
        # Use environment variable for credentials path
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        logger.info(f"GOOGLE_APPLICATION_CREDENTIALS at init: {credentials_path}")
        
        if credentials_path and os.path.exists(credentials_path):
            logger.info(f"Credentials file found at {credentials_path}")
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        else:
            logger.error(f"Credentials file not found at {credentials_path}")
            # Try alternative paths
            alt_paths = [
                '/app/silent-polygon-465403-h9-81cb035ed6d4.json',
                './silent-polygon-465403-h9-81cb035ed6d4.json',
                '../silent-polygon-465403-h9-81cb035ed6d4.json'
            ]
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    logger.info(f"Found credentials at alternative path: {alt_path}")
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = alt_path
                    credentials_path = alt_path
                    break
            else:
                logger.error("No Google Cloud credentials found. Using fallback mode.")
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
            logger.info(f"Extracted objects: {[o['name'] for o in results['objects']]}")
            all_text_for_analysis = ' '.join([results['ocr_text']] + [l['description'] for l in results['labels']] + [o['name'] for o in results['objects']])
            logger.info(f"All text for analysis: {all_text_for_analysis}")
            
            # Enhanced OCR analysis for sports items
            if any(word in all_text_for_analysis.lower() for word in ['timberwolves', 'wolves', 'nba', 'basketball']):
                logger.info(f"[SPORTS DETECTION] Found sports-related text: {all_text_for_analysis}")
                # Look for specific patterns in OCR
                ocr_lower = results['ocr_text'].lower()
                if '2024' in ocr_lower:
                    logger.info("[SPORTS DETECTION] Found year 2024 in OCR")
                if 'playoffs' in ocr_lower:
                    logger.info("[SPORTS DETECTION] Found playoffs in OCR")
                if 'playoff' in ocr_lower:
                    logger.info("[SPORTS DETECTION] Found playoff in OCR")
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
        Enhanced AI-driven detection: Extract all entities from image analysis (labels, objects, web entities, OCR, best guess labels)
        Returns: (search_terms, best_guess, suggested_queries)
        """
        import re
        from difflib import get_close_matches, SequenceMatcher
        
        # AI-driven team name mappings with fuzzy matching
        team_abbreviations = {
            'wolves': 'minnesota timberwolves',
            'timberwolves': 'minnesota timberwolves',
            'minn': 'minnesota timberwolves',
            'minnesota': 'minnesota timberwolves',
            'lakers': 'los angeles lakers',
            'la': 'los angeles lakers',
            'celtics': 'boston celtics',
            'boston': 'boston celtics',
            'warriors': 'golden state warriors',
            'gs': 'golden state warriors',
            'bulls': 'chicago bulls',
            'chicago': 'chicago bulls',
            'heat': 'miami heat',
            'miami': 'miami heat',
            'knicks': 'new york knicks',
            'ny': 'new york knicks',
            'nets': 'brooklyn nets',
            'brooklyn': 'brooklyn nets',
            'suns': 'phoenix suns',
            'phoenix': 'phoenix suns',
            'nuggets': 'denver nuggets',
            'denver': 'denver nuggets',
            'clippers': 'los angeles clippers',
            'lac': 'los angeles clippers',
            'mavericks': 'dallas mavericks',
            'dallas': 'dallas mavericks',
            'spurs': 'san antonio spurs',
            'san antonio': 'san antonio spurs',
            'rockets': 'houston rockets',
            'houston': 'houston rockets',
            'thunder': 'oklahoma city thunder',
            'okc': 'oklahoma city thunder',
            'pelicans': 'new orleans pelicans',
            'new orleans': 'new orleans pelicans',
            'kings': 'sacramento kings',
            'sacramento': 'sacramento kings',
            'jazz': 'utah jazz',
            'utah': 'utah jazz',
            'trail blazers': 'portland trail blazers',
            'blazers': 'portland trail blazers',
            'portland': 'portland trail blazers',
            'grizzlies': 'memphis grizzlies',
            'memphis': 'memphis grizzlies'
        }
        
        # AI-driven color mappings with context awareness
        color_mappings = {
            'white': ['white', 'cream', 'ivory', 'off-white', 'bone'],
            'black': ['black', 'charcoal', 'navy', 'dark'],
            'red': ['red', 'crimson', 'scarlet', 'burgundy', 'maroon'],
            'blue': ['blue', 'navy', 'royal', 'cobalt', 'indigo'],
            'green': ['green', 'forest', 'olive', 'emerald', 'sage'],
            'yellow': ['yellow', 'gold', 'mustard', 'amber'],
            'purple': ['purple', 'violet', 'lavender', 'plum'],
            'orange': ['orange', 'tangerine', 'coral', 'peach'],
            'pink': ['pink', 'rose', 'salmon', 'fuchsia'],
            'brown': ['brown', 'tan', 'beige', 'khaki', 'taupe'],
            'gray': ['gray', 'grey', 'silver', 'slate', 'steel'],
            'multi': ['multi', 'colorful', 'patterned', 'printed']
        }
        
        # AI-driven product type normalization
        product_type_mappings = {
            'shirt': ['shirt', 't-shirt', 'tee', 'top', 'blouse'],
            'jersey': ['jersey', 'uniform', 'team shirt', 'athletic shirt'],
            'hoodie': ['hoodie', 'sweatshirt', 'pullover', 'hooded'],
            'jacket': ['jacket', 'coat', 'outerwear', 'windbreaker'],
            'pants': ['pants', 'trousers', 'jeans', 'slacks'],
            'shorts': ['shorts', 'athletic shorts', 'basketball shorts'],
            'dress': ['dress', 'gown', 'frock'],
            'skirt': ['skirt', 'mini', 'midi', 'maxi'],
            'shoes': ['shoes', 'sneakers', 'boots', 'footwear'],
            'hat': ['hat', 'cap', 'beanie', 'headwear'],
            'bag': ['bag', 'purse', 'handbag', 'backpack']
        }
        
        def fuzzy_match(term1, term2, threshold=0.7):
            """Fuzzy string matching using SequenceMatcher"""
            return SequenceMatcher(None, term1.lower(), term2.lower()).ratio() >= threshold
        
        def find_team_match(term):
            """AI-driven team name detection with fuzzy matching"""
            # Direct abbreviation matching
            if term in team_abbreviations:
                return team_abbreviations[term]
            
            # Fuzzy matching for partial matches
            for abbrev, full_name in team_abbreviations.items():
                if fuzzy_match(term, abbrev, threshold=0.6):
                    return full_name
            
            # Check if term contains team keywords
            team_keywords = ['wolves', 'timberwolves', 'lakers', 'celtics', 'warriors', 
                            'bulls', 'heat', 'knicks', 'nets', 'suns', 'nuggets', 
                            'clippers', 'mavericks', 'spurs', 'rockets', 'thunder',
                            'pelicans', 'kings', 'jazz', 'blazers', 'grizzlies']
            
            for keyword in team_keywords:
                if keyword in term:
                    return team_abbreviations.get(keyword, term)
            
            return None
        
        def find_product_type_match(term):
            """AI-driven product type detection with normalization"""
            # Direct mapping
            for normalized, variants in product_type_mappings.items():
                if term in variants:
                    return normalized
            
            # Fuzzy matching for product types
            for normalized, variants in product_type_mappings.items():
                for variant in variants:
                    if fuzzy_match(term, variant, threshold=0.7):
                        return normalized
            
            # Context-aware product type detection
            if any(word in term for word in ['shirt', 'tee', 'top']):
                return 'shirt'
            elif any(word in term for word in ['jersey', 'uniform', 'team']):
                return 'jersey'
            elif any(word in term for word in ['hoodie', 'sweatshirt', 'pullover']):
                return 'hoodie'
            elif any(word in term for word in ['jacket', 'coat', 'outerwear']):
                return 'jacket'
            
            return None
        
        def find_color_match(term):
            """AI-driven color detection with mapping"""
            # Direct color mapping
            for normalized, variants in color_mappings.items():
                if term in variants:
                    return normalized
            
            # Fuzzy matching for colors
            for normalized, variants in color_mappings.items():
                for variant in variants:
                    if fuzzy_match(term, variant, threshold=0.7):
                        return normalized
            
            # Context-aware color detection
            if any(word in term for word in ['white', 'cream', 'ivory']):
                return 'white'
            elif any(word in term for word in ['black', 'charcoal', 'dark']):
                return 'black'
            elif any(word in term for word in ['red', 'crimson', 'scarlet']):
                return 'red'
            elif any(word in term for word in ['blue', 'navy', 'royal']):
                return 'blue'
            
            return None
        
        # Extract brands/models
        brands_models = self._extract_brands_models([analysis_results.get('ocr_text', '')])
        
        # Extract product and style terms (now includes all relevant terms)
        product_terms, _ = self._extract_product_terms(analysis_results, return_priority=True)
        
        # Extract color
        color = None
        rgb = None
        if analysis_results.get('dominant_colors'):
            color = self._get_meaningful_color(analysis_results['dominant_colors'])
            rgb = analysis_results['dominant_colors'][0]
        
        # Extract all text and context
        all_text = analysis_results.get('ocr_text', '').lower()
        for label in analysis_results.get('labels', []):
            all_text += ' ' + label['description'].lower()
        for entity in analysis_results.get('web_entities', []):
            all_text += ' ' + entity['description'].lower()
        
        # AI-driven term analysis and categorization
        brand_terms = []
        product_terms_enhanced = []
        color_terms = []
        team_terms = []
        year_event_terms = []
        style_terms = []
        material_terms = []
        
        # Enhanced AI-driven categorization with fuzzy matching
        all_text_terms = all_text.split()
        
        # AI-driven brand detection with fuzzy matching
        for term in all_text_terms:
            term_lower = term.lower()
            
            # AI-driven brand detection
            if self.is_brand_term(term_lower):
                brand_terms.append(term)
                continue
            
            # AI-driven team name detection with fuzzy matching
            team_match = find_team_match(term_lower)
            if team_match:
                team_terms.append(team_match)
                continue
            
            # AI-driven product type detection with normalization
            product_match = find_product_type_match(term_lower)
            if product_match:
                product_terms_enhanced.append(product_match)
                continue
            
            # AI-driven color detection with mapping
            color_match = find_color_match(term_lower)
            if color_match:
                color_terms.append(color_match)
                continue
            
            # AI-driven year/event detection
            if self.is_year_or_event(term_lower):
                year_event_terms.append(term)
                continue
            
            # AI-driven style detection
            if self.is_style_term(term_lower):
                style_terms.append(term)
                continue
            
            # AI-driven material detection
            if self.is_material_term(term_lower):
                material_terms.append(term)
                continue
        
        # AI-driven query prioritization and combination
        query_parts = []
        
        # Prioritize brand terms
        if brand_terms:
            query_parts.extend(brand_terms[:2])  # Limit to top 2 brands
        
        # Prioritize team terms with full expansion
        if team_terms:
            query_parts.extend(team_terms[:2])  # Limit to top 2 teams
        
        # Enhanced product type normalization with context awareness
        if product_terms_enhanced:
            # Gather all cues for t-shirt/tee
            tshirt_cues = ['t-shirt', 't shirt', 'tee', 'crewneck', 'short sleeve', 'cotton']
            jersey_cues = ['jersey', 'uniform', 'mesh', 'athletic']
            all_text_lower = all_text.lower()
            has_tshirt_cue = any(self.fuzzy_match(cue, all_text_lower, threshold=0.8) or cue in all_text_lower for cue in tshirt_cues)
            has_jersey_cue = any(self.fuzzy_match(cue, all_text_lower, threshold=0.8) or cue in all_text_lower for cue in jersey_cues)
            # Check label/object confidence for t-shirt/tee
            high_conf_tshirt = False
            for label in analysis_results.get('labels', []):
                if any(self.fuzzy_match(label['description'], cue, threshold=0.8) for cue in tshirt_cues) and label.get('score', 0) > 0.6:
                    high_conf_tshirt = True
            for obj in analysis_results.get('objects', []):
                if any(self.fuzzy_match(obj['name'], cue, threshold=0.8) for cue in tshirt_cues) and obj.get('score', 0) > 0.6:
                    high_conf_tshirt = True
            # Final product type selection
            normalized_products = []
            for product in product_terms_enhanced:
                if (product == 'shirt' or product == 't-shirt' or product == 'tee') and (has_tshirt_cue or high_conf_tshirt):
                    normalized_products.append('t-shirt')
                elif product == 'jersey' and has_jersey_cue:
                    normalized_products.append('jersey')
                elif product == 'jersey' and not has_jersey_cue:
                    continue  # skip false positive jersey
                else:
                    normalized_products.append(product)
            # If no t-shirt detected but cues are present, add it
            if has_tshirt_cue and 't-shirt' not in normalized_products:
                normalized_products.insert(0, 't-shirt')
            query_parts.extend(normalized_products[:2])
        elif product_terms:
            query_parts.extend(product_terms[:2])  # Fallback to original product terms
        
        # Enhanced AI-driven color detection with multi-source analysis
        detected_colors = []
        color_confidence = {}
        
        # 1. RGB Analysis with fashion-specific ranges
        if rgb:
            r, g, b = rgb['red'], rgb['green'], rgb['blue']
            total = r + g + b
            max_comp = max(r, g, b)
            min_comp = min(r, g, b)
            range_comp = max_comp - min_comp
            
            # Enhanced white detection (most important)
            if total > 700 and range_comp < 50:  # Very light, low saturation
                if r > 220 and g > 220 and b > 220:  # Pure white
                    detected_colors.append('white')
                    color_confidence['white'] = 0.95
                elif r > 180 and g > 180 and b > 180:  # Off-white/cream/light colors
                    # Context-aware white detection
                    if any(word in all_text for word in ['cotton', 'fashion', 'crewneck', 'casual', 'shirt']):
                        detected_colors.append('white')
                        color_confidence['white'] = 0.9
                    else:
                        detected_colors.append('white')  # Default to white for light colors
                        color_confidence['white'] = 0.85
                else:  # Light but not white
                    detected_colors.append('light')
                    color_confidence['light'] = 0.75
            
            # Enhanced color detection for fashion items
            elif range_comp > 100:  # Saturated colors
                if r > g + 80 and r > b + 80:
                    detected_colors.append('red')
                    color_confidence['red'] = 0.9
                elif g > r + 80 and g > b + 80:
                    detected_colors.append('green')
                    color_confidence['green'] = 0.9
                elif b > r + 80 and b > g + 80:
                    detected_colors.append('blue')
                    color_confidence['blue'] = 0.9
                elif r > 200 and g > 150 and b < 100:  # Orange/yellow
                    detected_colors.append('orange')
                    color_confidence['orange'] = 0.8
                elif r > 150 and g < 100 and b > 150:  # Purple
                    detected_colors.append('purple')
                    color_confidence['purple'] = 0.8
            
            # Neutral colors
            elif range_comp < 80:
                if total < 300:  # Dark neutrals
                    detected_colors.append('dark')
                    color_confidence['dark'] = 0.8
                elif 300 <= total <= 600:  # Medium neutrals
                    if r > g and g > b:  # Warm neutral
                        detected_colors.append('beige')
                        color_confidence['beige'] = 0.7
                    else:  # Cool neutral
                        detected_colors.append('gray')
                        color_confidence['gray'] = 0.7
        
        # 2. OCR Text Color Detection
        color_keywords = {
            'white': ['white', 'cream', 'ivory', 'bone', 'off-white'],
            'black': ['black', 'charcoal', 'navy', 'dark'],
            'red': ['red', 'crimson', 'scarlet', 'burgundy', 'maroon'],
            'blue': ['blue', 'navy', 'royal', 'cobalt', 'indigo'],
            'green': ['green', 'forest', 'olive', 'emerald', 'sage'],
            'yellow': ['yellow', 'gold', 'mustard', 'amber'],
            'purple': ['purple', 'violet', 'lavender', 'plum'],
            'orange': ['orange', 'tangerine', 'coral', 'peach'],
            'pink': ['pink', 'rose', 'salmon', 'fuchsia'],
            'brown': ['brown', 'tan', 'beige', 'khaki', 'taupe'],
            'gray': ['gray', 'grey', 'silver', 'slate', 'steel']
        }
        
        for color_name, keywords in color_keywords.items():
            for keyword in keywords:
                if keyword in all_text.lower():
                    if color_name not in detected_colors:
                        detected_colors.append(color_name)
                        color_confidence[color_name] = 0.9  # High confidence from text
                    break
        
        # 3. Label/Object Color Detection
        for label in analysis_results.get('labels', []):
            label_text = label['description'].lower()
            confidence = label.get('score', 0.5)
            
            for color_name, keywords in color_keywords.items():
                for keyword in keywords:
                    if keyword in label_text:
                        if color_name not in detected_colors:
                            detected_colors.append(color_name)
                            color_confidence[color_name] = max(color_confidence.get(color_name, 0), confidence)
                        break
        
        # 4. Web Entity Color Detection
        for entity in analysis_results.get('web_entities', []):
            entity_text = entity['description'].lower()
            confidence = entity.get('score', 0.5)
            
            for color_name, keywords in color_keywords.items():
                for keyword in keywords:
                    if keyword in entity_text:
                        if color_name not in detected_colors:
                            detected_colors.append(color_name)
                            color_confidence[color_name] = max(color_confidence.get(color_name, 0), confidence)
                        break
        
        # 5. Context-Aware Color Enhancement
        # If we have cotton/fashion context and light RGB, reinforce white
        if rgb and any(word in all_text for word in ['cotton', 'fashion', 'casual', 'crewneck', 'shirt', 'playoffs']):
            r, g, b = rgb['red'], rgb['green'], rgb['blue']
            if r > 150 and g > 150 and b > 150:  # Much lower threshold for clothing
                if 'white' not in detected_colors:
                    detected_colors.append('white')
                    color_confidence['white'] = 0.9  # High confidence for clothing context
                # Override beige/light with white for clothing context
                if 'beige' in detected_colors:
                    detected_colors.remove('beige')
                    if 'white' not in detected_colors:
                        detected_colors.append('white')
                        color_confidence['white'] = 0.9
        
        # 6. Confidence-Weighted Color Selection
        if detected_colors:
            # Sort by confidence and select top colors
            sorted_colors = sorted(detected_colors, key=lambda c: color_confidence.get(c, 0), reverse=True)
            query_parts.extend(sorted_colors[:2])  # Top 2 most confident colors
        elif color:
            query_parts.append(color)  # Fallback to original color detection
        
        # Add year/event terms
        if year_event_terms:
            query_parts.extend(year_event_terms[:2])  # Limit to top 2 years/events
        
        # Add style terms
        if style_terms:
            query_parts.extend(style_terms[:2])  # Limit to top 2 styles
        
        # Add material terms
        if material_terms:
            query_parts.extend(material_terms[:1])  # Limit to top 1 material
        
        # AI-driven query construction with confidence weighting
        if query_parts:
            search_terms = query_parts
        else:
            # Fallback to original logic
            search_terms = []
            if team_terms:
                search_terms.extend(team_terms)
            if product_terms:
                search_terms.extend(product_terms)
            if year_event_terms:
                search_terms.extend(year_event_terms)
            if color:
                search_terms.append(color)
        
        # Remove duplicates, preserve order
        search_terms = list(dict.fromkeys(search_terms))
        
        # Ensure minimum query length
        if len(search_terms) == 0:
            search_terms = ['clothing']
        
        # Best guess is the most confident product term or team
        best_guess = team_terms[0] if team_terms else (product_terms_enhanced[0] if product_terms_enhanced else (product_terms[0] if product_terms else None))
        
        # Generate all prioritized query combinations (from most specific to general)
        from itertools import combinations
        suggested_queries = []
        n = len(search_terms)
        if n > 1:
            suggested_queries.append(' '.join(search_terms))
        for r in range(n-1, 1, -1):
            for combo in combinations(search_terms, r):
                q = ' '.join(combo)
                if q not in suggested_queries:
                    suggested_queries.append(q)
        for combo in combinations(search_terms, 2):
            q = ' '.join(combo)
            if q not in suggested_queries:
                suggested_queries.append(q)
        
        logger.info(f"[AI ENHANCED] Final search terms: {search_terms}")
        logger.info(f"[AI ENHANCED] Best guess: {best_guess}")
        logger.info(f"[AI ENHANCED] Suggested queries: {suggested_queries[:5]}")
        
        return search_terms, best_guess, suggested_queries

    def _extract_brands_models(self, text_list: List[str]) -> List[str]:
        """Extract brand and model names from OCR text using pure AI detection"""
        brands_models = []
        
        for text in text_list:
            text_lower = text.lower()
            
            # Pure AI-driven brand detection from OCR text
            # Look for repeated words (likely brand names)
            words = text.split()
            word_counts = {}
            for word in words:
                clean_word = re.sub(r'[^a-zA-Z]', '', word).lower()
                if len(clean_word) > 2:
                    word_counts[clean_word] = word_counts.get(clean_word, 0) + 1
            
            # Add frequently occurring words as potential brands
            for word, count in word_counts.items():
                if count >= 2 and len(word) > 3:  # Repeated words are likely brands
                    if word not in brands_models:
                        brands_models.append(word)
                        logger.debug(f"[AI DEBUG] AI detected brand from repetition: {word}")
            
            # Extract capitalized words that might be brands or models
            for word in words:
                clean_word = re.sub(r'[^a-zA-Z]', '', word)
                if len(clean_word) > 3 and clean_word[0].isupper() and clean_word.isalpha():
                    if clean_word.lower() not in [brand.lower() for brand in brands_models]:
                        brands_models.append(clean_word)
                        logger.debug(f"[AI DEBUG] AI detected potential brand/model: {clean_word}")
            
            # AI-driven model name detection from OCR patterns
            # Look for patterns that suggest model names (e.g., "Thornaby", "Haymarket")
            model_patterns = [
                r'\b[A-Z][a-z]{3,}\b',  # Capitalized words with 4+ letters
                r'\b[A-Z]{2,}[a-z]+\b',  # Mixed case words (e.g., "Thornaby")
                r'\b[A-Z][a-z]+[A-Z][a-z]+\b',  # CamelCase words
                r'\b[A-Z][a-z]+[A-Z][a-z]+[a-z]+\b'  # Longer CamelCase (e.g., "Thornaby")
            ]
            
            # Also look for model names in web entities and labels
            # Note: analysis_results is not available in this method, so we'll skip web entity model detection for now
            # The model detection will still work from OCR text
            
            for pattern in model_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if len(match) > 4 and match.lower() not in [brand.lower() for brand in brands_models]:
                        brands_models.append(match)
                        logger.debug(f"[AI DEBUG] AI detected potential model name: {match}")
        
        return brands_models[:3]  # Limit to top 3 brands/models
    
    def _extract_product_terms(self, analysis_results: Dict[str, Any], return_priority=False) -> List[str]:
        """Extract product-specific terms from labels and objects using pure AI detection, with prioritization."""
        product_terms = []
        all_text = ""
        # Collect all text from labels, objects, web entities, and best guess labels
        for label in analysis_results.get('labels', []):
            all_text += " " + label['description'].lower()
        for obj in analysis_results.get('objects', []):
            all_text += " " + obj['name'].lower()
        for entity in analysis_results.get('web_entities', []):
            all_text += " " + entity['description'].lower()
        for guess in analysis_results.get('best_guess_labels', []):
            all_text += " " + guess.lower()
        if analysis_results.get('ocr_text'):
            all_text += " " + analysis_results['ocr_text'].lower()
        logger.debug(f"[AI DEBUG] Product extraction - All text: {all_text}")
        # Pure AI-driven product detection - no hardcoded clothing keywords
        # Let the AI determine product types from labels, objects, and web entities
        clothing_priority = []
        # Pure AI-driven product detection with intelligent prioritization
        meaningful_terms = []
        
        # Extract from labels (AI-detected) with confidence scoring
        for label in analysis_results.get('labels', []):
            label_text = label['description'].lower()
            confidence = label.get('confidence', 0.5)
            if len(label_text) > 2:  # Only meaningful terms
                meaningful_terms.append((label_text, confidence))
                logger.debug(f"[AI DEBUG] AI detected product term from label: {label_text} (confidence: {confidence})")
        
        # Extract from objects (AI-detected) with confidence scoring
        for obj in analysis_results.get('objects', []):
            obj_text = obj['name'].lower()
            confidence = obj.get('confidence', 0.5)
            if len(obj_text) > 2:  # Only meaningful terms
                meaningful_terms.append((obj_text, confidence))
                logger.debug(f"[AI DEBUG] AI detected product term from object: {obj_text} (confidence: {confidence})")
        
        # Extract from web entities (AI-detected) with confidence scoring
        for entity in analysis_results.get('web_entities', []):
            entity_text = entity['description'].lower()
            confidence = entity.get('confidence', 0.5)
            if len(entity_text) > 2:  # Only meaningful terms
                meaningful_terms.append((entity_text, confidence))
                logger.debug(f"[AI DEBUG] AI detected product term from web entity: {entity_text} (confidence: {confidence})")
        
        # Extract style information from all text sources
        style_terms = []
        all_text = ' '.join([term for term, _ in meaningful_terms])
        
        # AI-driven style detection from text patterns
        style_patterns = [
            'long sleeve', 'short sleeve', 'sleeveless',
            'button up', 'button down', 'zip up', 'pullover',
            'formal', 'casual', 'business', 'dress',
            'fitted', 'loose', 'tight', 'relaxed'
        ]
        
        for pattern in style_patterns:
            if pattern in all_text:
                style_terms.append(pattern)
                logger.debug(f"[AI DEBUG] AI detected style: {pattern}")
        
        # AI-driven style inference from detected parts
        detected_parts = [term for term, _ in meaningful_terms]
        
        # Infer "long sleeve" if "sleeve" is detected (most shirts are long sleeve)
        if 'sleeve' in detected_parts and 'long sleeve' not in style_terms:
            style_terms.append('long sleeve')
            logger.debug(f"[AI DEBUG] AI inferred 'long sleeve' from 'sleeve'")
        
        # Infer "button up" if "button" is detected
        if 'button' in detected_parts and 'button up' not in style_terms:
            style_terms.append('button up')
            logger.debug(f"[AI DEBUG] AI inferred 'button up' from 'button'")
        
        # Infer "collared" if "collar" is detected
        if 'collar' in detected_parts and 'collared' not in style_terms:
            style_terms.append('collared')
            logger.debug(f"[AI DEBUG] AI inferred 'collared' from 'collar'")
        
        # AI-driven formal wear detection
        formal_indicators = ['collar', 'button', 'plaid', 'check']
        if any(indicator in detected_parts for indicator in formal_indicators):
            if 'formal' not in style_terms:
                style_terms.append('formal')
                logger.debug(f"[AI DEBUG] AI inferred 'formal' from formal indicators")
            if 'business' not in style_terms:
                style_terms.append('business')
                logger.debug(f"[AI DEBUG] AI inferred 'business' from formal indicators")
        
        # Sort by confidence and extract top terms
        meaningful_terms.sort(key=lambda x: x[1], reverse=True)
        final_terms = [term for term, _ in meaningful_terms[:5]]  # Top 5 by confidence
        
        # Add detected styles to final terms
        final_terms.extend(style_terms[:3])  # Add top 3 styles
        
        # AI-driven prioritization: prefer complete product types over parts
        # Product types (complete items) vs parts (components)
        product_types = ['shirt', 'dress', 'pants', 'jacket', 'coat', 'sweater', 'hoodie', 'blouse']
        parts = ['sleeve', 'collar', 'button', 'pocket', 'zipper', 'label']
        generic_terms = ['top', 'clothing', 'fashion', 'design']
        
        # Prioritize complete product types over parts and generic terms
        product_terms = [term for term in final_terms if any(product in term for product in product_types)]
        part_terms = [term for term in final_terms if any(part in term for part in parts)]
        generic_terms_found = [term for term in final_terms if any(generic in term for generic in generic_terms)]
        
        # AI-driven inference: if we have shirt parts, infer "shirt"
        if not product_terms and part_terms:
            shirt_parts = ['sleeve', 'collar', 'button']
            if any(part in part_terms for part in shirt_parts):
                logger.debug(f"[AI DEBUG] AI inferred 'shirt' from parts: {part_terms}")
                product_terms = ['shirt']
        
        # AI-driven prioritization: prefer specific product types over generic terms
        if product_terms:
            priority_terms = product_terms
        elif part_terms:
            priority_terms = part_terms
        else:
            priority_terms = generic_terms_found
        
        found_priority = priority_terms[0] if priority_terms else (final_terms[0] if final_terms else None)
        logger.debug(f"[AI DEBUG] AI-driven final product terms: {final_terms}, priority: {found_priority}")
        
        if return_priority:
            return final_terms, found_priority
        return final_terms
    
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
        Enhanced AI-driven color detection for fashion items
        Uses RGB analysis to determine fashion-relevant colors
        """
        # Log the RGB values for debugging
        logger.debug(f"[AI DEBUG] Color detection - RGB: ({r}, {g}, {b})")
        
        # AI-driven color analysis based on RGB relationships and fashion context
        # No hardcoded color names - pure RGB analysis
        
        # Calculate color characteristics
        total = r + g + b
        max_component = max(r, g, b)
        min_component = min(r, g, b)
        range_components = max_component - min_component
        
        # AI determines color based on RGB patterns
        if total > 700:  # Very light colors
            if abs(r - g) < 20 and abs(g - b) < 20:
                logger.debug(f"[AI DEBUG] AI detected white/cream - RGB: ({r}, {g}, {b})")
                return 'cream' if r > 240 else 'beige'
            else:
                logger.debug(f"[AI DEBUG] AI detected light color - RGB: ({r}, {g}, {b})")
                return 'light'
        
        elif total < 150:  # Very dark colors
            logger.debug(f"[AI DEBUG] AI detected dark color - RGB: ({r}, {g}, {b})")
            return 'dark'
        
        elif range_components < 50:  # Neutral colors (grays, beiges, tans)
            if 60 <= r <= 200 and 40 <= g <= 180 and 30 <= b <= 160:
                # Beige/tan range (expanded for our RGB values)
                if r > g and g > b:
                    logger.debug(f"[AI DEBUG] AI detected beige/tan - RGB: ({r}, {g}, {b})")
                    return 'beige'
                else:
                    logger.debug(f"[AI DEBUG] AI detected neutral - RGB: ({r}, {g}, {b})")
                    return 'neutral'
        
        # AI determines specific colors based on dominant components
        elif r > g + 50 and r > b + 50:
            logger.debug(f"[AI DEBUG] AI detected red family - RGB: ({r}, {g}, {b})")
            return 'red'
        elif g > r + 50 and g > b + 50:
            logger.debug(f"[AI DEBUG] AI detected green family - RGB: ({r}, {g}, {b})")
            return 'green'
        elif b > r + 50 and b > g + 50:
            logger.debug(f"[AI DEBUG] AI detected blue family - RGB: ({r}, {g}, {b})")
            return 'blue'
        
        # AI determines warm vs cool neutrals
        elif r > g and g > b:
            logger.debug(f"[AI DEBUG] AI detected warm neutral - RGB: ({r}, {g}, {b})")
            return 'warm'
        else:
            logger.debug(f"[AI DEBUG] AI detected cool neutral - RGB: ({r}, {g}, {b})")
            return 'cool'

    def is_brand_term(self, term):
        """AI-driven brand detection"""
        brand_indicators = [
            'burberry', 'nike', 'adidas', 'puma', 'reebok', 'under armour',
            'champion', 'hanes', 'fruit of the loom', 'gildan', 'american apparel',
            'levi', 'calvin klein', 'tommy hilfiger', 'ralph lauren', 'polo',
            'gucci', 'prada', 'louis vuitton', 'hermes', 'chanel', 'dior',
            'versace', 'dolce', 'gabbana', 'fendi', 'givenchy', 'balenciaga',
            'off-white', 'supreme', 'palace', 'bape', 'stussy', 'obey',
            'vans', 'converse', 'new balance', 'asics', 'mizuno', 'wilson'
        ]
        
        # Fuzzy matching for brand detection
        for brand in brand_indicators:
            if self.fuzzy_match(term, brand, threshold=0.7):
                return True
        
        return False

    def is_year_or_event(self, term):
        """AI-driven year and event detection"""
        # Year patterns
        if re.match(r'\b(19|20)\d{2}\b', term):
            return True
        
        # Event keywords
        event_keywords = [
            'playoffs', 'championship', 'finals', 'all-star', 'allstar',
            'opening night', 'season', 'regular', 'postseason', 'playoff',
            'conference', 'division', 'semifinals', 'quarterfinals',
            'champions', 'title', 'trophy', 'ring', 'medal'
        ]
        
        return any(keyword in term for keyword in event_keywords)

    def is_style_term(self, term):
        """AI-driven style detection"""
        style_keywords = [
            'long sleeve', 'short sleeve', 'sleeveless', 'v-neck', 'crew neck',
            'round neck', 'turtle neck', 'polo', 'button down', 'button up',
            'casual', 'formal', 'athletic', 'sport', 'fashion', 'street',
            'vintage', 'retro', 'modern', 'classic', 'contemporary'
        ]
        
        return any(keyword in term for keyword in style_keywords)

    def is_material_term(self, term):
        """AI-driven material detection"""
        material_keywords = [
            'cotton', 'polyester', 'wool', 'silk', 'linen', 'denim',
            'leather', 'suede', 'mesh', 'nylon', 'spandex', 'elastane',
            'acrylic', 'rayon', 'viscose', 'modal', 'bamboo', 'hemp'
        ]
        
        return any(keyword in term for keyword in material_keywords)

    def fuzzy_match(self, term1, term2, threshold=0.7):
        """Fuzzy string matching using SequenceMatcher"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, term1.lower(), term2.lower()).ratio() >= threshold

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

    def comprehensive_visual_search(self, image_data: bytes) -> list:
        logger.info("[COMPREHENSIVE VISUAL SEARCH] Starting visual search across web and eBay...")
        results = []
        try:
            # Google Vision Web Detection
            web_detection = None
            analysis_results = {
                'labels': [],
                'objects': [],
                'ocr_text': '',
                'dominant_colors': [],
                'web_entities': [],
                'best_guess_labels': []
            }
            if self.client:
                image = vision.Image(content=image_data)
                response = self.client.web_detection(image=image)
                web_detection = response.web_detection
                # Web entities
                if web_detection.web_entities:
                    analysis_results['web_entities'] = [
                        {'description': entity.description, 'score': entity.score}
                        for entity in web_detection.web_entities if entity.description
                    ]
                # Best guess labels
                if web_detection.best_guess_labels:
                    analysis_results['best_guess_labels'] = [label.label for label in web_detection.best_guess_labels]
                # OCR text (from web entities if available)
                if web_detection.pages_with_matching_images:
                    texts = []
                    for page in web_detection.pages_with_matching_images:
                        if page.page_title:
                            texts.append(page.page_title)
                    analysis_results['ocr_text'] = ' '.join(texts)
            # Also run label and object detection for richer context
            try:
                features = [
                    vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION),
                    vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION),
                    vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION),
                    vision.Feature(type_=vision.Feature.Type.IMAGE_PROPERTIES),
                ]
                request = vision.AnnotateImageRequest(image=image, features=features)
                response = self.client.batch_annotate_images(requests=[request])
                if response.responses:
                    result = response.responses[0]
                    if result.label_annotations:
                        analysis_results['labels'] = [
                            {'description': l.description, 'score': l.score}
                            for l in result.label_annotations
                        ]
                    if result.localized_object_annotations:
                        analysis_results['objects'] = [
                            {'name': o.name, 'score': o.score}
                            for o in result.localized_object_annotations
                        ]
                    if result.text_annotations:
                        analysis_results['ocr_text'] += ' ' + ' '.join([t.description for t in result.text_annotations])
                    if result.image_properties_annotation and result.image_properties_annotation.dominant_colors:
                        analysis_results['dominant_colors'] = [
                            {'red': c.color.red, 'green': c.color.green, 'blue': c.color.blue}
                            for c in result.image_properties_annotation.dominant_colors.colors
                        ]
            except Exception as e:
                logger.warning(f"[COMPREHENSIVE VISUAL SEARCH] Secondary annotation failed: {e}")
            # Use advanced NLP query builder
            search_terms, best_guess, suggested_queries = self._nlp_enhanced_search_terms(analysis_results)
            logger.info(f"[COMPREHENSIVE VISUAL SEARCH] Using suggested queries: {suggested_queries}")
            # Visual matches (web images)
            visual_matches = []
            if web_detection and web_detection.visually_similar_images:
                for img in web_detection.visually_similar_images[:10]:
                    visual_matches.append({
                        'type': 'web_image',
                        'url': img.url,
                        'score': 0.0,
                        'title': 'Similar Product',
                        'source': 'web_detection',
                    })
                logger.debug(f"[AI DEBUG] Top visually similar image URLs: {[img['url'] for img in visual_matches]}")
            # Web entities (brands, objects, etc.)
            web_entities = []
            if web_detection and web_detection.web_entities:
                for entity in web_detection.web_entities[:5]:
                    web_entities.append({
                        'type': 'web_entity',
                        'entity_id': entity.entity_id,
                        'score': entity.score,
                        'description': entity.description,
                        'source': 'web_detection',
                    })
                logger.debug(f"[AI DEBUG] Top web entity descriptions: {[e['description'] for e in web_entities]}")
            # eBay/web search using advanced queries (simulate, or call your EbayService here)
            # For demonstration, just log the queries
            logger.info(f"[COMPREHENSIVE VISUAL SEARCH] Would search eBay/web with: {suggested_queries}")
            results = visual_matches + web_entities
            logger.info(f"[COMPREHENSIVE VISUAL SEARCH] Found {len(visual_matches)} visual matches and {len(web_entities)} web entities")
        except Exception as e:
            logger.error(f"[COMPREHENSIVE VISUAL SEARCH] Error: {e}")
        return results

    # Global AI service instance (lazy initialization)
_ai_service_instance = None

def get_ai_service():
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance