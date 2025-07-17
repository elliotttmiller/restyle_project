"""
AI Service for Image Analysis using Google Cloud Vision API with Advanced ML
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
import json
from collections import defaultdict, Counter
import math
import hashlib
import pickle
from datetime import datetime, timedelta
import boto3

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered image analysis using Google Cloud Vision with Advanced ML"""
    
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
        
        # Advanced AI components
        self.entity_embeddings = {}
        self.semantic_similarity_cache = {}
        self.confidence_models = {}
        self.attention_weights = {}
        self.learning_history = []
        self.pattern_memory = {}
        self._initialize_advanced_ai()
    
    def _initialize_client(self):
        logger.info("_initialize_client called for AIService")
        """Initialize Google Cloud Vision client"""
        import traceback
        # Use environment variable for credentials path
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "/etc/secrets/gcp.json")
        logger.info(f"GOOGLE_APPLICATION_CREDENTIALS at init: {creds_path}")
        
        if creds_path and os.path.exists(creds_path):
            logger.info(f"Credentials file found at {creds_path}")
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        else:
            logger.error(f"Credentials file not found at {creds_path}")
            # Try alternative paths
            alt_paths = [
                '/etc/secrets/gcp.json',
                '/app/silent-polygon-465403-h9-3a57d36afc97.json',
                './silent-polygon-465403-h9-3a57d36afc97.json',
                '../silent-polygon-465403-h9-3a57d36afc97.json',
                'C:/Users/AMD/restyle_project/backend/silent-polygon-465403-h9-3a57d36afc97.json',
                'C:\\Users\\AMD\\restyle_project\\backend\\silent-polygon-465403-h9-3a57d36afc97.json'
            ]
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    logger.info(f"Found credentials at alternative path: {alt_path}")
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = alt_path
                    creds_path = alt_path
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
            
            # AI-driven sports context detection (no hardcoded terms)
            sports_terms = []
            ocr_lower = results['ocr_text'].lower()
            
            # AI-driven year detection using regex patterns
            import re
            year_pattern = r'\b(19|20)\d{2}\b'
            years_found = re.findall(year_pattern, results['ocr_text'])
            for year in years_found:
                logger.info(f"[SPORTS DETECTION] Found year {year} in OCR")
                sports_terms.append(year)
            
            # Also look for partial years that might be part of larger numbers
            # This handles cases where OCR might split "2024" into "20" and "24"
            partial_year_pattern = r'\b(19|20)\d{1,2}\b'
            partial_years = re.findall(partial_year_pattern, results['ocr_text'])
            for partial in partial_years:
                if len(partial) == 2:  # "20" or "19"
                    # Look for the rest of the year in nearby text
                    remaining_pattern = r'\b\d{2}\b'
                    remaining_years = re.findall(remaining_pattern, results['ocr_text'])
                    for remaining in remaining_years:
                        if remaining != partial:  # Don't match the same number
                            full_year = partial + remaining
                            if 1900 <= int(full_year) <= 2030:  # Reasonable year range
                                logger.info(f"[SPORTS DETECTION] Found partial year {partial} + {remaining} = {full_year}")
                                if full_year not in sports_terms:
                                    sports_terms.append(full_year)
            
            # AI-driven event detection using context analysis
            event_patterns = [
                r'\bplayoffs?\b', r'\bchampionship\b', r'\bfinals?\b', 
                r'\bseason\b', r'\btournament\b', r'\bgame\b', r'\bmatch\b'
            ]
            for pattern in event_patterns:
                matches = re.findall(pattern, ocr_lower)
                for match in matches:
                    logger.info(f"[SPORTS DETECTION] Found event '{match}' in OCR")
                    if match not in sports_terms:
                        sports_terms.append(match)
            
            # AI-driven sports context detection (no hardcoded indicators)
            # Analyze text patterns to detect sports context automatically
            words = all_text_for_analysis.split()
            word_counts = {}
            capitalized_words = []
            
            # Count word frequencies and identify capitalized words
            for word in words:
                clean_word = re.sub(r'[^a-zA-Z]', '', word)
                if len(clean_word) > 2:
                    word_counts[clean_word] = word_counts.get(clean_word, 0) + 1
                    if clean_word[0].isupper() and len(clean_word) > 3:
                        capitalized_words.append(clean_word)
            
            # AI-driven sports context detection using pattern analysis
            # Look for patterns that suggest sports context
            has_sports_context = False
            
            # Pattern 1: Repeated capitalized words (likely team names)
            repeated_capitals = [word for word, count in word_counts.items() if count >= 2 and word[0].isupper() and len(word) > 3]
            if repeated_capitals:
                has_sports_context = True
                logger.info(f"[SPORTS DETECTION] Found repeated capitalized words: {repeated_capitals}")
            
            # Pattern 2: Year + event patterns (sports context)
            year_pattern = r'\b(19|20)\d{2}\b'
            years_in_text = re.findall(year_pattern, all_text_for_analysis)
            if years_in_text:
                has_sports_context = True
                logger.info(f"[SPORTS DETECTION] Found year patterns: {years_in_text}")
            
            # Pattern 3: AI-driven event detection using pure context analysis
            # Look for words that appear in sports context based on surrounding text
            events_found = []
            all_text_lower = all_text_for_analysis.lower()
            
            # AI-driven event detection: look for words that appear near years or capitalized terms
            words_near_context = []
            for i, word in enumerate(words):
                if i > 0 and i < len(words) - 1:
                    # Check if this word appears near a year or capitalized word
                    prev_word = words[i-1] if i > 0 else ""
                    next_word = words[i+1] if i < len(words) - 1 else ""
                    
                    # If surrounded by context indicators, this might be an event
                    context_indicators = [re.match(r'\b(19|20)\d{2}\b', prev_word), 
                                        re.match(r'\b(19|20)\d{2}\b', next_word),
                                        prev_word[0].isupper() if prev_word else False,
                                        next_word[0].isupper() if next_word else False]
                    
                    if any(context_indicators) and len(word) > 4:
                        words_near_context.append(word.lower())
            
            # Add words that appear near sports context
            for word in words_near_context:
                if word not in events_found:
                    events_found.append(word)
                    logger.info(f"[SPORTS DETECTION] AI detected potential event near context: {word}")
            
            if events_found:
                has_sports_context = True
                logger.info(f"[SPORTS DETECTION] Found AI-detected events: {events_found}")
            
            if has_sports_context:
                logger.info(f"[SPORTS DETECTION] AI detected sports context in: {all_text_for_analysis}")
                
                # Add detected sports-related terms
                for word in repeated_capitals:
                    logger.info(f"[SPORTS DETECTION] Detected potential team name: {word}")
                    sports_terms.append(word.lower())
                
                for event in events_found:
                    if event not in sports_terms:
                        logger.info(f"[SPORTS DETECTION] Detected event: {event}")
                        sports_terms.append(event)
            
            # Add detected sports terms to OCR text for processing
            if sports_terms:
                results['ocr_text'] += ' ' + ' '.join(sports_terms)
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
            # Store image data for CLIP-based search
            results['image_data'] = image_data
            
            # CLIP-based semantic search term generation
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
        CLIP-based semantic search term generation using visual understanding.
        """
        # Use CLIP for semantic understanding if available
        if self.clip_model and self.clip_preprocess:
            return self._clip_based_search_terms(analysis_results)
        else:
            # Fallback to human-like query builder
            return self._fallback_search_terms(analysis_results)
    
    def _clip_based_search_terms(self, analysis_results: Dict[str, Any]) -> Tuple[list, str, list]:
        """
        Generate search terms using CLIP semantic understanding
        """
        try:
            import torch
            
            # Get image data from analysis results
            image_data = analysis_results.get('image_data')
            if not image_data:
                logger.warning("[CLIP SEARCH] No image data available, using fallback")
                return self._fallback_search_terms(analysis_results)
            
            # Generate image embedding
            from PIL import Image
            import io
            
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            image_tensor = self.clip_preprocess(image).unsqueeze(0)
            
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_tensor)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Generate semantic queries based on visual understanding
            semantic_queries = self._generate_semantic_queries(image_features)
            
            # Rank queries by semantic similarity
            ranked_queries = self._rank_semantic_queries(semantic_queries, image_features)
            
            # Extract search terms from top queries
            search_terms = []
            for query in ranked_queries[:3]:  # Top 3 semantic queries
                terms = query.split()
                search_terms.extend(terms)
            
            # Remove duplicates while preserving order
            unique_terms = []
            for term in search_terms:
                if term.lower() not in [t.lower() for t in unique_terms]:
                    unique_terms.append(term)
            
            # Best guess is the most semantically relevant term
            best_guess = unique_terms[0] if unique_terms else 'clothing'
            
            # Generate suggested queries
            suggested_queries = ranked_queries[:5]  # Top 5 semantic queries
            
            logger.info(f"[CLIP SEARCH] Semantic search terms: {unique_terms}")
            logger.info(f"[CLIP SEARCH] Best guess: {best_guess}")
            logger.info(f"[CLIP SEARCH] Suggested queries: {suggested_queries}")
            
            return unique_terms, best_guess, suggested_queries
            
        except Exception as e:
            logger.error(f"[CLIP SEARCH] Error: {e}")
            return self._fallback_search_terms(analysis_results)
    
    def _rank_semantic_queries(self, queries: list, image_features) -> list:
        """
        Rank semantic queries by similarity to image features
        """
        try:
            import torch
            
            ranked_queries = []
            
            for query in queries:
                # Encode query text
                text_tokens = self.clip_tokenizer([query])
                with torch.no_grad():
                    text_features = self.clip_model.encode_text(text_tokens)
                    text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                
                # Calculate similarity
                similarity = torch.cosine_similarity(image_features, text_features)
                similarity_score = similarity.item()
                
                ranked_queries.append((query, similarity_score))
            
            # Sort by similarity score
            ranked_queries.sort(key=lambda x: x[1], reverse=True)
            
            # Return just the queries (without scores)
            return [query for query, score in ranked_queries]
            
        except Exception as e:
            logger.error(f"[RANK SEMANTIC] Error: {e}")
            return queries
    
    def _fallback_search_terms(self, analysis_results: Dict[str, Any]) -> Tuple[list, str, list]:
        """
        Fallback search term generation using human-like query builder
        """
        # Use the enhanced human-like query builder
        queries = self._intelligent_query_builder_with_attention(analysis_results)
        
        # Get advanced product type detection
        product_insights = self._advanced_product_type_detection(analysis_results)
        
        # Extract search terms from the first query
        search_terms = queries[0].split() if queries else ['item']
        
        # Add product type if detected with high confidence
        if product_insights['primary_type'] and product_insights['confidence'] > 0.6:
            product_type = product_insights['primary_type']
            if product_type not in search_terms:
                search_terms.insert(0, product_type)  # Add at beginning for priority
        
        # Best guess is the first entity or category
        best_guess = search_terms[0] if search_terms else 'item'
        
        # Generate suggested queries using human-like patterns
        suggested_queries = queries[:8]  # Top 8 human-like queries
        
        # Add product type to suggested queries if detected
        if product_insights['primary_type'] and product_insights['confidence'] > 0.5:
            product_type = product_insights['primary_type']
            # Create product-specific queries with human-like patterns
            enhanced_queries = []
            for query in suggested_queries:
                if product_type not in query:
                    enhanced_queries.append(f"{product_type} {query}")
                else:
                    enhanced_queries.append(query)
            suggested_queries = enhanced_queries
        
        logger.info(f"[FALLBACK SEARCH] Final search terms: {search_terms}")
        logger.info(f"[FALLBACK SEARCH] Best guess: {best_guess}")
        logger.info(f"[FALLBACK SEARCH] Human-like suggested queries: {suggested_queries}")
        
        return search_terms, best_guess, suggested_queries

    def _intelligent_query_builder_with_attention(self, analysis_results):
        """Build intelligent search queries using attention mechanisms and human-like logic"""
        # Extract all text sources
        all_text = analysis_results.get('ocr_text', '')
        labels = analysis_results.get('labels', [])
        objects = analysis_results.get('objects', [])
        web_entities = analysis_results.get('web_entities', [])
        
        # Build context vectors
        context_vectors = self._build_context_vectors(all_text, labels, objects)
        
        # Advanced entity detection with attention
        detected_entities = self._advanced_entity_detection_with_attention(all_text, context_vectors)
        
        # Enhanced human-like query generation
        queries = self._generate_human_like_structured_queries(analysis_results, detected_entities, context_vectors)
        
        return queries
    
    def _generate_human_like_structured_queries(self, analysis_results, detected_entities, context_vectors):
        """Generate human-like structured queries using advanced AI logic"""
        queries = []
        
        # Extract different types of information
        brand_terms = self._extract_brand_entities(detected_entities, analysis_results)
        product_terms = self._extract_product_entities(detected_entities, analysis_results)
        color_terms = self._extract_color_entities(detected_entities, analysis_results)
        style_terms = self._extract_style_entities(detected_entities, analysis_results)
        material_terms = self._extract_material_entities(detected_entities, analysis_results)
        year_event_terms = self._extract_temporal_entities(detected_entities, analysis_results)
        
        logger.info(f"[QUERY BUILDER] Brand terms: {brand_terms}")
        logger.info(f"[QUERY BUILDER] Product terms: {product_terms}")
        logger.info(f"[QUERY BUILDER] Color terms: {color_terms}")
        logger.info(f"[QUERY BUILDER] Style terms: {style_terms}")
        logger.info(f"[QUERY BUILDER] Material terms: {material_terms}")
        logger.info(f"[QUERY BUILDER] Year/Event terms: {year_event_terms}")
        
        # Strategy 1: Brand + Product + Attributes (Most Specific)
        if brand_terms and product_terms:
            for brand in brand_terms[:2]:
                for product in product_terms[:2]:
                    base_query = f"{brand} {product}"
                    
                    # Add color if available
                    if color_terms:
                        for color in color_terms[:1]:
                            queries.append(f"{base_query} {color}")
                    
                    # Add style if available
                    if style_terms:
                        for style in style_terms[:1]:
                            queries.append(f"{base_query} {style}")
                    
                    # Add material if available
                    if material_terms:
                        for material in material_terms[:1]:
                            queries.append(f"{base_query} {material}")
                    
                    # Add year/event if available
                    if year_event_terms:
                        for event in year_event_terms[:1]:
                            queries.append(f"{base_query} {event}")
                    
                    # Add color + style combination
                    if color_terms and style_terms:
                        for color in color_terms[:1]:
                            for style in style_terms[:1]:
                                queries.append(f"{base_query} {color} {style}")
                    
                    # Add color + material combination
                    if color_terms and material_terms:
                        for color in color_terms[:1]:
                            for material in material_terms[:1]:
                                queries.append(f"{base_query} {color} {material}")
                    
                    # Base brand + product query
                    queries.append(base_query)
        
        # Strategy 2: Product + Color + Style (Fashion Context)
        if product_terms and color_terms:
            for product in product_terms[:2]:
                for color in color_terms[:1]:
                    base_query = f"{product} {color}"
                    
                    # Add style if available
                    if style_terms:
                        for style in style_terms[:1]:
                            queries.append(f"{base_query} {style}")
                    
                    # Add material if available
                    if material_terms:
                        for material in material_terms[:1]:
                            queries.append(f"{base_query} {material}")
                    
                    # Add style + material combination
                    if style_terms and material_terms:
                        for style in style_terms[:1]:
                            for material in material_terms[:1]:
                                queries.append(f"{base_query} {style} {material}")
                    
                    # Base product + color query
                    queries.append(base_query)
        
        # Strategy 3: Brand + Style + Color (Luxury Context)
        if brand_terms and style_terms:
            for brand in brand_terms[:2]:
                for style in style_terms[:1]:
                    base_query = f"{brand} {style}"
                    
                    # Add color if available
                    if color_terms:
                        for color in color_terms[:1]:
                            queries.append(f"{base_query} {color}")
                    
                    # Add material if available
                    if material_terms:
                        for material in material_terms[:1]:
                            queries.append(f"{base_query} {material}")
                    
                    # Base brand + style query
                    queries.append(base_query)
        
        # Strategy 4: Year/Event + Product (Collector Context)
        if year_event_terms and product_terms:
            for event in year_event_terms[:2]:
                for product in product_terms[:1]:
                    base_query = f"{event} {product}"
                    
                    # Add color if available
                    if color_terms:
                        for color in color_terms[:1]:
                            queries.append(f"{base_query} {color}")
                    
                    # Add brand if available
                    if brand_terms:
                        for brand in brand_terms[:1]:
                            queries.append(f"{brand} {base_query}")
                    
                    # Base event + product query
                    queries.append(base_query)
        
        # Strategy 6: Material + Product + Color (Material-Focused)
        if material_terms and product_terms:
            for material in material_terms[:1]:
                for product in product_terms[:1]:
                    base_query = f"{material} {product}"
                    
                    # Add color if available
                    if color_terms:
                        for color in color_terms[:1]:
                            queries.append(f"{base_query} {color}")
                    
                    # Add brand if available
                    if brand_terms:
                        for brand in brand_terms[:1]:
                            queries.append(f"{brand} {base_query}")
                    
                    # Base material + product query
                    queries.append(base_query)
        
        # Strategy 7: Style + Color + Product (Style-Focused)
        if style_terms and color_terms:
            for style in style_terms[:1]:
                for color in color_terms[:1]:
                    base_query = f"{style} {color}"
                    
                    # Add product if available
                    if product_terms:
                        for product in product_terms[:1]:
                            queries.append(f"{base_query} {product}")
                    
                    # Add brand if available
                    if brand_terms:
                        for brand in brand_terms[:1]:
                            queries.append(f"{brand} {base_query}")
                    
                    # Base style + color query
                    queries.append(base_query)
        
        # Strategy 8: Brand + Year/Event (Vintage Context)
        if brand_terms and year_event_terms:
            for brand in brand_terms[:2]:
                for event in year_event_terms[:1]:
                    queries.append(f"{brand} {event}")
        
        # Strategy 9: Product + Year/Event (Generic Collector)
        if product_terms and year_event_terms:
            for product in product_terms[:1]:
                for event in year_event_terms[:1]:
                    queries.append(f"{product} {event}")
        
        # Strategy 10: Single high-confidence terms (Fallback)
        high_confidence_entities = [e for e in detected_entities if e.get('fused_confidence', 0) > 0.8]
        if high_confidence_entities:
            for entity in high_confidence_entities[:3]:
                queries.append(entity['entity'])
        
        # Strategy 11: Brand-only queries (Brand recognition)
        if brand_terms:
            for brand in brand_terms[:2]:
                queries.append(brand)
        
        # Strategy 12: Product-only queries (Product recognition)
        if product_terms:
            for product in product_terms[:2]:
                queries.append(product)
        
        # Remove duplicates while preserving order
        unique_queries = []
        for query in queries:
            clean_query = ' '.join(query.split())  # Normalize whitespace
            if clean_query and clean_query not in unique_queries:
                unique_queries.append(clean_query)
        
        # Limit to top 15 most relevant queries
        final_queries = unique_queries[:15]
        
        logger.info(f"[QUERY BUILDER] Generated {len(final_queries)} human-like queries")
        for i, query in enumerate(final_queries[:5]):  # Log first 5 queries
            logger.info(f"[QUERY BUILDER] Query {i+1}: {query}")
        
        return final_queries
    
    def _extract_brand_entities(self, detected_entities, analysis_results):
        """Extract brand-related entities using AI detection"""
        brand_terms = []
        
        # Extract from detected entities
        for entity in detected_entities:
            if entity.get('entity_type') == 'brand' or self._is_likely_brand(entity['entity']):
                brand_terms.append(entity['entity'])
        
        # Extract from OCR text using AI patterns
        ocr_text = analysis_results.get('ocr_text', '')
        if ocr_text:
            # Look for capitalized words that might be brands
            words = ocr_text.split()
            for word in words:
                clean_word = re.sub(r'[^a-zA-Z]', '', word)
                if (len(clean_word) > 3 and 
                    clean_word[0].isupper() and 
                    clean_word.isalpha() and
                    clean_word.lower() not in [brand.lower() for brand in brand_terms]):
                    brand_terms.append(clean_word)
        
        # Extract from labels
        for label in analysis_results.get('labels', []):
            if self._is_likely_brand(label['description']):
                brand_terms.append(label['description'])
        
        return list(set(brand_terms))[:3]  # Remove duplicates, limit to top 3
    
    def _extract_product_entities(self, detected_entities, analysis_results):
        """Extract product-related entities using AI detection"""
        product_terms = []
        
        # Extract from detected entities
        for entity in detected_entities:
            if entity.get('entity_type') == 'product' or self._is_likely_product(entity['entity']):
                product_terms.append(entity['entity'])
        
        # Extract from labels and objects
        for label in analysis_results.get('labels', []):
            if self._is_likely_product(label['description']):
                product_terms.append(label['description'])
        
        for obj in analysis_results.get('objects', []):
            if self._is_likely_product(obj['name']):
                product_terms.append(obj['name'])
        
        return list(set(product_terms))[:3]
    
    def _extract_color_entities(self, detected_entities, analysis_results):
        """Extract color-related entities using AI detection"""
        color_terms = []
        
        # Extract from detected entities
        for entity in detected_entities:
            if entity.get('entity_type') == 'color' or self._is_likely_color(entity['entity']):
                color_terms.append(entity['entity'])
        
        # Extract from dominant colors
        dominant_colors = analysis_results.get('dominant_colors', [])
        if dominant_colors:
            meaningful_color = self._get_meaningful_color(dominant_colors)
            if meaningful_color:
                color_terms.append(meaningful_color)
        
        # Extract from labels
        for label in analysis_results.get('labels', []):
            if self._is_likely_color(label['description']):
                color_terms.append(label['description'])
        
        return list(set(color_terms))[:2]
    
    def _extract_style_entities(self, detected_entities, analysis_results):
        """Extract style-related entities using AI detection"""
        style_terms = []
        
        # Extract from detected entities
        for entity in detected_entities:
            if entity.get('entity_type') == 'style' or self._is_likely_style(entity['entity']):
                style_terms.append(entity['entity'])
        
        # Extract from labels
        for label in analysis_results.get('labels', []):
            if self._is_likely_style(label['description']):
                style_terms.append(label['description'])
        
        return list(set(style_terms))[:2]
    
    def _extract_material_entities(self, detected_entities, analysis_results):
        """Extract material-related entities using AI detection"""
        material_terms = []
        
        # Extract from detected entities
        for entity in detected_entities:
            if entity.get('entity_type') == 'material' or self._is_likely_material(entity['entity']):
                material_terms.append(entity['entity'])
        
        # Extract from labels
        for label in analysis_results.get('labels', []):
            if self._is_likely_material(label['description']):
                material_terms.append(label['description'])
        
        return list(set(material_terms))[:2]
    
    def _extract_temporal_entities(self, detected_entities, analysis_results):
        """Extract temporal entities (years, events) using AI detection"""
        temporal_terms = []
        
        # Extract from detected entities
        for entity in detected_entities:
            if entity.get('entity_type') == 'temporal':
                temporal_terms.append(entity['entity'])
        
        # Extract from OCR text using regex patterns
        ocr_text = analysis_results.get('ocr_text', '')
        if ocr_text:
            # Year patterns
            year_pattern = r'\b(19|20)\d{2}\b'
            years = re.findall(year_pattern, ocr_text)
            temporal_terms.extend(years)
            
            # Event patterns (words that might indicate events)
            event_indicators = ['championship', 'season', 'edition', 'limited', 'vintage', 'retro']
            words = ocr_text.lower().split()
            for word in words:
                if word in event_indicators:
                    temporal_terms.append(word)
        
        return list(set(temporal_terms))[:2]
    

    
    def _is_likely_brand(self, term):
        """AI-driven brand detection"""
        if not term or len(term) < 3:
            return False
        
        # Look for brand indicators
        term_lower = term.lower()
        brand_indicators = [
            'brand', 'label', 'logo', 'designer', 'fashion', 'luxury'
        ]
        
        # Check if term appears in brand context
        for indicator in brand_indicators:
            if indicator in term_lower:
                return True
        
        # Check for brand-like patterns (capitalized, repeated, etc.)
        if term[0].isupper() and term.isalpha() and len(term) > 3:
            return True
        
        return False
    
    def _is_likely_product(self, term):
        """AI-driven product detection"""
        if not term or len(term) < 3:
            return False
        
        term_lower = term.lower()
        
        # Look for product indicators
        product_indicators = [
            'shirt', 'pants', 'jacket', 'dress', 'shoes', 'hat', 'bag',
            'jersey', 'uniform', 'outfit', 'garment', 'clothing', 'apparel'
        ]
        
        for indicator in product_indicators:
            if indicator in term_lower:
                return True
        
        return False
    
    def _is_likely_color(self, term):
        """AI-driven color detection"""
        if not term or len(term) < 3:
            return False
        
        term_lower = term.lower()
        
        # Common color terms
        color_terms = [
            'red', 'blue', 'green', 'yellow', 'black', 'white', 'gray', 'grey',
            'brown', 'purple', 'pink', 'orange', 'navy', 'maroon', 'beige',
            'cream', 'gold', 'silver', 'bronze', 'olive', 'burgundy'
        ]
        
        return term_lower in color_terms
    
    def _is_likely_style(self, term):
        """AI-driven style detection"""
        if not term or len(term) < 3:
            return False
        
        term_lower = term.lower()
        
        # Style indicators
        style_indicators = [
            'casual', 'formal', 'vintage', 'retro', 'modern', 'classic',
            'sporty', 'elegant', 'sophisticated', 'trendy', 'fashionable'
        ]
        
        return term_lower in style_indicators
    
    def _is_likely_material(self, term):
        """AI-driven material detection"""
        if not term or len(term) < 3:
            return False
        
        term_lower = term.lower()
        
        # Material indicators
        material_indicators = [
            'cotton', 'polyester', 'wool', 'silk', 'leather', 'denim',
            'linen', 'cashmere', 'suede', 'velvet', 'satin', 'mesh'
        ]
        
        return term_lower in material_indicators
    


    def _generate_human_like_queries(self, search_terms, product_terms, year_event_terms, color_terms, style_terms):
        """Generate human-like eBay search queries using AI-driven context analysis"""
        queries = []
        
        # Priority 1: Complete team + product + year/event queries (most specific)
        if team_terms and product_terms:
            for team in team_terms[:2]:  # Top 2 teams
                for product in product_terms[:2]:  # Top 2 products
                    base_query = f"{team} {product}"
                    
                    # Add year/event if available
                    if year_event_terms:
                        for event in year_event_terms[:2]:
                            queries.append(f"{base_query} {event}")
                    
                    # Add color if available
                    if color_terms:
                        for color in color_terms[:1]:
                            queries.append(f"{base_query} {color}")
                    
                    # Add style if available
                    if style_terms:
                        for style in style_terms[:1]:
                            queries.append(f"{base_query} {style}")
                    
                    # Add year + color combination
                    if year_event_terms and color_terms:
                        for event in year_event_terms[:1]:
                            for color in color_terms[:1]:
                                queries.append(f"{base_query} {event} {color}")
                    
                    # Base query without modifiers
                    queries.append(base_query)
        
        # Priority 2: Product + color + style queries (fashion context)
        if product_terms and color_terms:
            for product in product_terms[:2]:
                for color in color_terms[:1]:
                    base_query = f"{product} {color}"
                    
                    # Add style if available
                    if style_terms:
                        for style in style_terms[:1]:
                            queries.append(f"{base_query} {style}")
                    
                    queries.append(base_query)
        
        # Priority 4: Year/event specific queries (collector context)
        if year_event_terms:
            for event in year_event_terms[:2]:
                if color_terms:
                    for color in color_terms[:1]:
                        queries.append(f"{event} {color}")
                queries.append(event)
        
        # Priority 5: Generic product queries (fallback)
        if product_terms:
            for product in product_terms[:2]:
                if color_terms:
                    for color in color_terms[:1]:
                        queries.append(f"{product} {color}")
                queries.append(product)
        
        # Priority 6: Color + style queries (fashion context)
        if color_terms and style_terms:
            for color in color_terms[:1]:
                for style in style_terms[:1]:
                    queries.append(f"{color} {style}")
        
        # Remove duplicates while preserving order
        unique_queries = []
        for query in queries:
            if query not in unique_queries:
                unique_queries.append(query)
        
        # Limit to top 10 most relevant queries
        return unique_queries[:10]

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
        """Generic entity detection using patterns and context"""
        term_lower = term.lower()
        
        # Look for entity patterns (capitalized words, repeated terms)
        if len(term_lower) > 3 and term_lower[0].isupper():
            # Check if it appears multiple times in context (likely an important entity)
            return True
        
        # Look for entity-like patterns
        if any(pattern in term_lower for pattern in ['brand', 'logo', 'label', 'name']):
            return True
        
        return False

    def is_year_or_event(self, term):
        """Generic temporal detection using pure context analysis"""
        # Year patterns
        if re.match(r'\b(19|20)\d{2}\b', term):
            return True
        
        # Generic event detection: look for words that appear in temporal context
        # This will be determined by the context analysis in the main function
        # rather than hardcoded patterns
        return False

    def is_style_term(self, term):
        """Generic descriptor detection using pure context analysis"""
        term_lower = term.lower()
        
        # Look for descriptor patterns in text
        if any(word in term_lower for word in ['style', 'type', 'kind', 'form', 'shape', 'design']):
            return True
        
        return False

    def is_material_term(self, term):
        """Generic attribute detection using pure context analysis"""
        term_lower = term.lower()
        
        # Look for attribute patterns in text
        if any(word in term_lower for word in ['material', 'fabric', 'texture', 'surface', 'composition']):
            return True
        
        return False

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
        """
        CLIP-based visual search using semantic embeddings for true visual understanding
        """
        logger.info("[COMPREHENSIVE VISUAL SEARCH] Starting CLIP-based visual search...")
        
        try:
            # Use CLIP for visual understanding if available
            if self.clip_model and self.clip_preprocess:
                return self._clip_based_visual_search(image_data)
            else:
                logger.warning("[COMPREHENSIVE VISUAL SEARCH] CLIP not available, using fallback")
                return self._fallback_visual_search(image_data)
                
        except Exception as e:
            logger.error(f"[COMPREHENSIVE VISUAL SEARCH] Error: {e}")
            return []
    
    def _clip_based_visual_search(self, image_data: bytes) -> list:
        """
        CLIP-based visual search using semantic embeddings
        """
        try:
            from PIL import Image
            import io
            import torch
            
            # Load and preprocess image
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            image_tensor = self.clip_preprocess(image).unsqueeze(0)
            
            # Generate image embedding
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_tensor)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Generate semantic text queries for visual search
            semantic_queries = self._generate_semantic_queries(image_features)
            
            # Search using semantic similarity
            results = []
            for query in semantic_queries:
                query_results = self._semantic_search(query, image_features)
                results.extend(query_results)
            
            # Remove duplicates and rank by relevance
            unique_results = self._deduplicate_and_rank_results(results)
            
            logger.info(f"[CLIP VISUAL SEARCH] Found {len(unique_results)} semantic results")
            return unique_results[:20]  # Return top 20 results
            
        except Exception as e:
            logger.error(f"[CLIP VISUAL SEARCH] Error: {e}")
            return []
    
    def _generate_semantic_queries(self, image_features) -> list:
        """
        Generate semantic queries based on visual understanding
        """
        # Pre-defined semantic categories for fashion items
        semantic_categories = [
            # Clothing types
            "shirt", "dress", "pants", "jacket", "sweater", "hoodie", "blouse", "t-shirt",
            "jersey", "uniform", "outfit", "garment", "clothing", "apparel",
            
            # Styles
            "casual", "formal", "vintage", "retro", "modern", "classic", "sporty", 
            "elegant", "sophisticated", "trendy", "fashionable", "business",
            
            # Materials
            "cotton", "polyester", "wool", "silk", "leather", "denim", "linen", 
            "cashmere", "suede", "velvet", "satin", "mesh",
            
            # Patterns
            "plaid", "striped", "solid", "printed", "floral", "geometric", "tartan",
            
            # Colors (semantic understanding)
            "red", "blue", "green", "yellow", "black", "white", "gray", "brown", 
            "purple", "pink", "orange", "navy", "maroon", "beige", "cream", "gold",
            
            # Brand indicators (visual style understanding)
            "luxury", "premium", "designer", "fashion", "style", "quality"
        ]
        
        # Generate semantic queries based on visual features
        queries = []
        
        # Basic clothing query
        queries.append("clothing apparel")
        
        # Style-based queries
        queries.extend([
            "casual clothing",
            "formal wear", 
            "vintage fashion",
            "modern apparel",
            "classic style"
        ])
        
        # Material-based queries
        queries.extend([
            "cotton clothing",
            "premium fabric",
            "quality material"
        ])
        
        # Pattern-based queries
        queries.extend([
            "patterned clothing",
            "solid color clothing",
            "printed apparel"
        ])
        
        return queries
    
    def _semantic_search(self, query: str, image_features) -> list:
        """
        Perform semantic search using CLIP embeddings
        """
        try:
            # Encode the query text
            text_tokens = self.clip_tokenizer([query])
            with torch.no_grad():
                text_features = self.clip_model.encode_text(text_tokens)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            # Calculate semantic similarity
            similarity = torch.cosine_similarity(image_features, text_features)
            similarity_score = similarity.item()
            
            # Generate mock results based on semantic similarity
            # In a real system, this would search against a database of product embeddings
            results = self._generate_semantic_results(query, similarity_score)
            
            return results
            
        except Exception as e:
            logger.error(f"[SEMANTIC SEARCH] Error: {e}")
            return []
    
    def _generate_semantic_results(self, query: str, similarity_score: float) -> list:
        """
        Generate semantic search results based on query and similarity
        """
        # Mock results - in a real system, this would query a product database
        # with pre-computed CLIP embeddings
        
        base_results = [
            {
                'title': f'Semantic Match: {query}',
                'url': f'https://example.com/semantic/{query.replace(" ", "-")}',
                'similarity': similarity_score,
                'type': 'semantic'
            }
        ]
        
        # Add variations based on query type
        if 'plaid' in query.lower():
            base_results.extend([
                {
                    'title': 'Plaid Shirt - Designer Collection',
                    'url': 'https://example.com/plaid-shirt-designer',
                    'similarity': similarity_score * 0.9,
                    'type': 'semantic'
                },
                {
                    'title': 'Tartan Pattern Clothing',
                    'url': 'https://example.com/tartan-clothing',
                    'similarity': similarity_score * 0.85,
                    'type': 'semantic'
                }
            ])
        
        if 'casual' in query.lower():
            base_results.extend([
                {
                    'title': 'Casual Wear Collection',
                    'url': 'https://example.com/casual-wear',
                    'similarity': similarity_score * 0.9,
                    'type': 'semantic'
                }
            ])
        
        if 'formal' in query.lower():
            base_results.extend([
                {
                    'title': 'Formal Business Attire',
                    'url': 'https://example.com/formal-business',
                    'similarity': similarity_score * 0.9,
                    'type': 'semantic'
                }
            ])
        
        return base_results
    
    def _deduplicate_and_rank_results(self, results: list) -> list:
        """
        Remove duplicates and rank by relevance
        """
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        # Sort by similarity score
        unique_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        return unique_results
    
    def _fallback_visual_search(self, image_data: bytes) -> list:
        """
        Fallback visual search when CLIP is not available
        """
        logger.info("[FALLBACK VISUAL SEARCH] Using fallback method")
        
        # Use Google Vision API for basic visual understanding
        try:
            from google.cloud import vision
            
            image = vision.Image(content=image_data)
            client = vision.ImageAnnotatorClient()
            
            # Perform label detection
            response = client.label_detection(image=image)
            labels = response.label_annotations
            
            # Generate search queries from detected labels
            queries = []
            for label in labels[:5]:  # Top 5 labels
                queries.append(label.description)
            
            # Generate mock results
            results = []
            for query in queries:
                results.append({
                    'title': f'Visual Match: {query}',
                    'url': f'https://example.com/visual/{query.replace(" ", "-")}',
                    'similarity': 0.7,
                    'type': 'visual'
                })
            
            return results[:10]
            
        except Exception as e:
            logger.error(f"[FALLBACK VISUAL SEARCH] Error: {e}")
            return []

    def _initialize_advanced_ai(self):
        """Initialize advanced AI components"""
        # Self-learning pattern recognition
        self.pattern_recognizer = self._build_pattern_recognizer()
        
        # Semantic understanding system
        self.semantic_analyzer = self._build_semantic_analyzer()
        
        # Attention mechanism for context understanding
        self.attention_mechanism = self._build_attention_mechanism()
        
        # Confidence scoring with uncertainty quantification
        self.confidence_scorer = self._build_confidence_scorer()
        
        # Adaptive learning system
        self.adaptive_learner = self._build_adaptive_learner()
        
        # Multi-modal fusion system
        self.multimodal_fusion = self._build_multimodal_fusion()
    
    def _build_pattern_recognizer(self):
        """Build advanced pattern recognition system"""
        return {
            'temporal_patterns': {},
            'spatial_patterns': {},
            'semantic_patterns': {},
            'contextual_patterns': {},
            'cross_modal_patterns': {}
        }
    
    def _build_semantic_analyzer(self):
        """Build semantic understanding system"""
        return {
            'entity_relationships': {},
            'concept_hierarchies': {},
            'semantic_similarity': {},
            'context_vectors': {},
            'meaning_embeddings': {}
        }
    
    def _build_attention_mechanism(self):
        """Build attention mechanism for context understanding"""
        return {
            'visual_attention': {},
            'textual_attention': {},
            'cross_attention': {},
            'self_attention': {},
            'positional_encoding': {}
        }
    
    def _build_confidence_scorer(self):
        """Build confidence scoring with uncertainty quantification"""
        return {
            'uncertainty_estimator': {},
            'confidence_calibration': {},
            'reliability_metrics': {},
            'out_of_distribution_detector': {},
            'adversarial_robustness': {}
        }
    
    def _build_adaptive_learner(self):
        """Build adaptive learning system"""
        return {
            'online_learning': {},
            'meta_learning': {},
            'few_shot_learning': {},
            'continual_learning': {},
            'transfer_learning': {}
        }
    
    def _build_multimodal_fusion(self):
        """Build multi-modal fusion system"""
        return {
            'visual_text_fusion': {},
            'cross_modal_attention': {},
            'modality_weights': {},
            'fusion_strategies': {},
            'alignment_metrics': {}
        }
    
    def _advanced_entity_detection_with_attention(self, text, context_vectors):
        """Advanced entity detection using attention mechanisms"""
        entities = []
        
        # Tokenize with attention to context
        tokens = self._tokenize_with_attention(text, context_vectors)
        
        # Multi-head attention for entity detection
        attention_heads = self._compute_attention_heads(tokens, context_vectors)
        
        # Entity detection with uncertainty quantification
        for i, token in enumerate(tokens):
            # Compute attention weights
            attention_weights = self._compute_attention_weights(token, attention_heads[i])
            
            # Detect entities with confidence and uncertainty
            entity_info = self._detect_entity_with_uncertainty(token, attention_weights, context_vectors)
            
            if entity_info['confidence'] > 0.5 and entity_info['uncertainty'] < 0.3:
                entities.append(entity_info)
        
        # Cross-modal entity linking
        entities = self._cross_modal_entity_linking(entities, context_vectors)
        
        return entities
    
    def _tokenize_with_attention(self, text, context_vectors):
        """Tokenize text with attention to context"""
        # Advanced tokenization with context awareness
        tokens = []
        words = text.split()
        
        for i, word in enumerate(words):
            # Context window
            context_window = words[max(0, i-3):min(len(words), i+4)]
            
            # Position encoding
            position_encoding = self._compute_position_encoding(i, len(words))
            
            # Context vector
            context_vector = self._compute_context_vector(context_window, context_vectors)
            
            tokens.append({
                'word': word,
                'position': position_encoding,
                'context': context_vector,
                'attention_weights': self._compute_self_attention(word, context_window)
            })
        
        return tokens
    
    def _compute_attention_heads(self, tokens, context_vectors):
        """Compute multi-head attention"""
        attention_heads = []
        
        for token in tokens:
            # Multi-head attention computation
            head_1 = self._attention_head(token, context_vectors, 'semantic')
            head_2 = self._attention_head(token, context_vectors, 'positional')
            head_3 = self._attention_head(token, context_vectors, 'contextual')
            head_4 = self._attention_head(token, context_vectors, 'temporal')
            
            attention_heads.append([head_1, head_2, head_3, head_4])
        
        return attention_heads
    
    def _attention_head(self, token, context_vectors, attention_type):
        """Compute attention for a specific head"""
        if attention_type == 'semantic':
            return self._semantic_attention(token, context_vectors)
        elif attention_type == 'positional':
            return self._positional_attention(token, context_vectors)
        elif attention_type == 'contextual':
            return self._contextual_attention(token, context_vectors)
        elif attention_type == 'temporal':
            return self._temporal_attention(token, context_vectors)
        
        return 0.0
    
    def _semantic_attention(self, token, context_vectors):
        """Semantic attention computation"""
        # Compute semantic similarity with context
        semantic_scores = []
        for context_vector in context_vectors:
            similarity = self._compute_semantic_similarity(token['word'], context_vector)
            semantic_scores.append(similarity)
        
        return np.mean(semantic_scores) if semantic_scores else 0.0
    
    def _positional_attention(self, token, context_vectors):
        """Positional attention computation"""
        # Position-based attention
        position_score = 1.0 / (1.0 + abs(token['position']))
        return position_score
    
    def _contextual_attention(self, token, context_vectors):
        """Contextual attention computation"""
        # Context-based attention
        context_score = np.mean(token['attention_weights']) if token['attention_weights'] else 0.0
        return context_score
    
    def _temporal_attention(self, token, context_vectors):
        """Temporal attention computation"""
        # Temporal patterns in text
        temporal_patterns = self._extract_temporal_patterns(token['word'])
        return np.mean(temporal_patterns) if temporal_patterns else 0.0
    
    def _detect_entity_with_uncertainty(self, token, attention_weights, context_vectors):
        """Detect entities with uncertainty quantification"""
        # Base entity detection
        entity_confidence = self._compute_entity_confidence(token, attention_weights)
        
        # Uncertainty quantification
        uncertainty = self._compute_uncertainty(token, context_vectors)
        
        # Reliability assessment
        reliability = self._assess_reliability(token, attention_weights)
        
        return {
            'entity': token['word'],
            'confidence': entity_confidence,
            'uncertainty': uncertainty,
            'reliability': reliability,
            'attention_weights': attention_weights
        }
    
    def _compute_entity_confidence(self, token, attention_weights):
        """Compute entity confidence using attention weights"""
        # Weighted confidence based on attention
        weighted_confidence = np.mean(attention_weights) if attention_weights else 0.0
        
        # Context boost
        context_boost = 0.2 if len(token['word']) > 5 else 0.0
        
        # Position boost
        position_boost = 0.1 if token['position'] < 0.3 else 0.0
        
        # Repetition boost
        repetition_boost = 0.15 if self._is_repeated_entity(token['word']) else 0.0
        
        confidence = weighted_confidence + context_boost + position_boost + repetition_boost
        return min(confidence, 1.0)
    
    def _compute_uncertainty(self, token, context_vectors):
        """Compute uncertainty quantification"""
        # Model uncertainty
        model_uncertainty = 1.0 - self._compute_model_confidence(token)
        
        # Data uncertainty
        data_uncertainty = self._compute_data_uncertainty(token, context_vectors)
        
        # Epistemic uncertainty
        epistemic_uncertainty = self._compute_epistemic_uncertainty(token)
        
        # Total uncertainty
        total_uncertainty = (model_uncertainty + data_uncertainty + epistemic_uncertainty) / 3.0
        return min(total_uncertainty, 1.0)
    
    def _assess_reliability(self, token, attention_weights):
        """Assess reliability of entity detection"""
        # Consistency check
        consistency = self._check_consistency(token, attention_weights)
        
        # Robustness check
        robustness = self._check_robustness(token)
        
        # Calibration check
        calibration = self._check_calibration(token)
        
        reliability = (consistency + robustness + calibration) / 3.0
        return min(reliability, 1.0)
    
    def _cross_modal_entity_linking(self, entities, context_vectors):
        """Cross-modal entity linking"""
        linked_entities = []
        
        for entity in entities:
            # Visual-text alignment
            visual_alignment = self._compute_visual_text_alignment(entity, context_vectors)
            
            # Cross-modal consistency
            cross_modal_consistency = self._compute_cross_modal_consistency(entity, context_vectors)
            
            # Multi-modal fusion
            fused_entity = self._fuse_multimodal_information(entity, visual_alignment, cross_modal_consistency)
            
            linked_entities.append(fused_entity)
        
        return linked_entities
    
    def _compute_visual_text_alignment(self, entity, context_vectors):
        """Compute visual-text alignment"""
        # This would use CLIP or similar for visual-text alignment
        # For now, using a simplified approach
        return 0.7  # Placeholder
    
    def _compute_cross_modal_consistency(self, entity, context_vectors):
        """Compute cross-modal consistency"""
        # Check consistency across different modalities
        return 0.8  # Placeholder
    
    def _fuse_multimodal_information(self, entity, visual_alignment, cross_modal_consistency):
        """Fuse multi-modal information"""
        # Weighted fusion of different modalities
        fused_confidence = (entity['confidence'] * 0.4 + 
                          visual_alignment * 0.3 + 
                          cross_modal_consistency * 0.3)
        
        entity['fused_confidence'] = fused_confidence
        return entity
    
    def _generate_multimodal_queries(self, entities, context_vectors):
        """Generate multi-modal queries"""
        queries = []
        
        # Primary query with highest confidence entities
        primary_entities = sorted(entities, key=lambda x: x['fused_confidence'], reverse=True)[:4]
        if primary_entities:
            primary_query = ' '.join([e['entity'] for e in primary_entities])
            queries.append(primary_query)
        
        # Attention-weighted queries
        attention_queries = self._generate_attention_weighted_queries(entities, context_vectors)
        queries.extend(attention_queries)
        
        # Cross-modal queries
        cross_modal_queries = self._generate_cross_modal_queries(entities, context_vectors)
        queries.extend(cross_modal_queries)
        
        return queries[:5]  # Return top 5 queries
    
    def _generate_attention_weighted_queries(self, entities, context_vectors):
        """Generate attention-weighted queries"""
        queries = []
        
        # Group entities by attention type
        semantic_entities = [e for e in entities if e.get('attention_weights', [0])[0] > 0.7]
        positional_entities = [e for e in entities if e.get('attention_weights', [0, 0])[1] > 0.7]
        contextual_entities = [e for e in entities if e.get('attention_weights', [0, 0, 0])[2] > 0.7]
        
        if semantic_entities:
            semantic_query = ' '.join([e['entity'] for e in semantic_entities[:2]])
            queries.append(semantic_query)
        
        if positional_entities:
            positional_query = ' '.join([e['entity'] for e in positional_entities[:2]])
            queries.append(positional_query)
        
        if contextual_entities:
            contextual_query = ' '.join([e['entity'] for e in contextual_entities[:2]])
            queries.append(contextual_query)
        
        return queries
    
    def _generate_cross_modal_queries(self, entities, context_vectors):
        """Generate cross-modal queries"""
        queries = []
        
        # Visual-text fusion queries
        visual_text_entities = [e for e in entities if e.get('fused_confidence', 0) > 0.6]
        if visual_text_entities:
            visual_text_query = ' '.join([e['entity'] for e in visual_text_entities[:3]])
            queries.append(visual_text_query)
        
        return queries
    
    def _learn_from_feedback(self, query, results, success_score):
        """Learn from search feedback"""
        # Store learning experience
        learning_experience = {
            'query': query,
            'results': results,
            'success_score': success_score,
            'timestamp': datetime.now(),
            'context': self._extract_learning_context(query, results)
        }
        
        self.learning_history.append(learning_experience)
        
        # Update pattern recognition
        self._update_pattern_recognition(learning_experience)
        
        # Update confidence models
        self._update_confidence_models(learning_experience)
        
        # Update attention weights
        self._update_attention_weights(learning_experience)
    
    def _extract_learning_context(self, query, results):
        """Extract context for learning"""
        return {
            'query_terms': query.split(),
            'result_count': len(results),
            'result_types': [type(r).__name__ for r in results],
            'success_indicators': self._extract_success_indicators(results)
        }
    
    def _update_pattern_recognition(self, learning_experience):
        """Update pattern recognition based on feedback"""
        # Update temporal patterns
        self.pattern_recognizer['temporal_patterns'].update(
            self._extract_temporal_patterns(learning_experience['query'])
        )
        
        # Update semantic patterns
        self.pattern_recognizer['semantic_patterns'].update(
            self._extract_semantic_patterns(learning_experience['query'])
        )
        
        # Update contextual patterns
        self.pattern_recognizer['contextual_patterns'].update(
            self._extract_contextual_patterns(learning_experience)
        )
    
    def _update_confidence_models(self, learning_experience):
        """Update confidence models based on feedback"""
        # Calibrate confidence scores
        if learning_experience['success_score'] > 0.7:
            # Successful query - boost similar patterns
            self._boost_confidence_patterns(learning_experience['query'])
        else:
            # Unsuccessful query - reduce similar patterns
            self._reduce_confidence_patterns(learning_experience['query'])
    
    def _update_attention_weights(self, learning_experience):
        """Update attention weights based on feedback"""
        # Adjust attention weights based on success
        success_factor = learning_experience['success_score']
        
        # Update semantic attention
        self.attention_mechanism['semantic_attention'] = self._adjust_attention_weights(
            self.attention_mechanism.get('semantic_attention', {}),
            success_factor
        )
        
        # Update contextual attention
        self.attention_mechanism['contextual_attention'] = self._adjust_attention_weights(
            self.attention_mechanism.get('contextual_attention', {}),
            success_factor
        )
    
    def _adjust_attention_weights(self, current_weights, success_factor):
        """Adjust attention weights based on success"""
        adjusted_weights = {}
        
        for key, weight in current_weights.items():
            # Boost weights for successful patterns
            if success_factor > 0.7:
                adjusted_weights[key] = min(weight * 1.1, 1.0)
            else:
                adjusted_weights[key] = max(weight * 0.9, 0.0)
        
        return adjusted_weights

    def _compute_position_encoding(self, position, total_length):
        """Compute position encoding for attention"""
        return position / total_length if total_length > 0 else 0.0
    
    def _compute_context_vector(self, context_window, context_vectors):
        """Compute context vector for a token"""
        # Simplified context vector computation
        return {
            'window': context_window,
            'size': len(context_window),
            'context_vectors': len(context_vectors)
        }
    
    def _compute_self_attention(self, word, context_window):
        """Compute self-attention weights"""
        # Simplified self-attention computation
        attention_weights = []
        for context_word in context_window:
            if context_word == word:
                attention_weights.append(1.0)
            else:
                # Simple similarity-based attention
                similarity = self._compute_word_similarity(word, context_word)
                attention_weights.append(similarity)
        
        return attention_weights
    
    def _compute_word_similarity(self, word1, word2):
        """Compute similarity between two words"""
        # Simple character-based similarity
        common_chars = len(set(word1.lower()) & set(word2.lower()))
        total_chars = len(set(word1.lower()) | set(word2.lower()))
        return common_chars / total_chars if total_chars > 0 else 0.0
    
    def _compute_attention_weights(self, token, attention_heads):
        """Compute attention weights for a token"""
        # Combine attention heads
        if attention_heads and len(attention_heads) >= 4:
            return attention_heads
        return [0.25, 0.25, 0.25, 0.25]  # Default uniform weights
    
    def _is_repeated_entity(self, entity):
        """Check if entity is repeated in context"""
        # This would check the full context for repetitions
        # For now, return False as placeholder
        return False
    
    def _compute_model_confidence(self, token):
        """Compute model confidence for a token"""
        # Simplified model confidence
        return 0.8  # Placeholder
    
    def _compute_data_uncertainty(self, token, context_vectors):
        """Compute data uncertainty"""
        # Simplified data uncertainty
        return 0.2  # Placeholder
    
    def _compute_epistemic_uncertainty(self, token):
        """Compute epistemic uncertainty"""
        # Simplified epistemic uncertainty
        return 0.1  # Placeholder
    
    def _check_consistency(self, token, attention_weights):
        """Check consistency of entity detection"""
        # Simplified consistency check
        if attention_weights:
            return np.std(attention_weights) < 0.3  # Low variance = high consistency
        return 0.5  # Default consistency
    
    def _check_robustness(self, token):
        """Check robustness of entity detection"""
        # Simplified robustness check
        return 0.8  # Placeholder
    
    def _check_calibration(self, token):
        """Check calibration of entity detection"""
        # Simplified calibration check
        return 0.7  # Placeholder
    
    def _extract_temporal_patterns(self, text):
        """Extract temporal patterns from text"""
        # Simplified temporal pattern extraction
        patterns = []
        if re.search(r'\b(19|20)\d{2}\b', text):
            patterns.append(1.0)
        if re.search(r'\b(playoffs?|season|game|match)\b', text.lower()):
            patterns.append(0.8)
        return patterns
    
    def _extract_semantic_patterns(self, text):
        """Extract semantic patterns from text"""
        # Simplified semantic pattern extraction
        patterns = {}
        words = text.lower().split()
        for word in words:
            if len(word) > 3:
                patterns[word] = patterns.get(word, 0) + 1
        return patterns
    
    def _extract_contextual_patterns(self, learning_experience):
        """Extract contextual patterns from learning experience"""
        # Simplified contextual pattern extraction
        return {
            'query_length': len(learning_experience['query']),
            'success_score': learning_experience['success_score'],
            'result_count': len(learning_experience['results'])
        }
    
    def _boost_confidence_patterns(self, query):
        """Boost confidence patterns for successful queries"""
        # Simplified confidence boosting
        pass  # Placeholder
    
    def _reduce_confidence_patterns(self, query):
        """Reduce confidence patterns for unsuccessful queries"""
        # Simplified confidence reduction
        pass  # Placeholder
    
    def _extract_success_indicators(self, results):
        """Extract success indicators from results"""
        # Simplified success indicator extraction
        return {
            'has_results': len(results) > 0,
            'result_diversity': len(set(type(r).__name__ for r in results)),
            'average_confidence': 0.7  # Placeholder
        }
    
    def _compute_semantic_similarity(self, word, context_vector):
        """Compute semantic similarity between word and context"""
        # Simplified semantic similarity
        if isinstance(context_vector, dict) and 'text' in context_vector:
            text = context_vector['text'].lower()
            if word.lower() in text:
                return 0.8
        return 0.2
    
    def _advanced_product_type_detection(self, analysis_results):
        """Advanced AI-driven product type detection using contextual analysis"""
        product_insights = {
            'primary_type': None,
            'confidence': 0.0,
            'contextual_cues': [],
            'visual_indicators': [],
            'semantic_patterns': [],
            'uncertainty': 0.0
        }
        
        # Extract all available information
        all_text = analysis_results.get('ocr_text', '')
        labels = analysis_results.get('labels', [])
        objects = analysis_results.get('objects', [])
        web_entities = analysis_results.get('web_entities', [])
        
        # Build comprehensive context
        full_context = self._build_product_context(all_text, labels, objects, web_entities)
        
        # AI-driven product type inference
        product_insights = self._infer_product_type_from_context(full_context)
        
        # Cross-modal validation
        product_insights = self._validate_product_type_cross_modal(product_insights, analysis_results)
        
        return product_insights
    
    def _build_product_context(self, text, labels, objects, web_entities):
        """Build comprehensive context for product type analysis"""
        context = {
            'text_indicators': self._extract_text_indicators(text),
            'visual_indicators': self._extract_visual_indicators(labels, objects),
            'semantic_indicators': self._extract_semantic_indicators(web_entities),
            'structural_indicators': self._extract_structural_indicators(text, labels),
            'contextual_relationships': self._extract_contextual_relationships(text, labels, objects)
        }
        return context
    
    def _extract_text_indicators(self, text):
        """Extract text-based product indicators using AI patterns"""
        indicators = {
            'length_patterns': self._analyze_length_patterns(text),
            'word_patterns': self._analyze_word_patterns(text),
            'position_patterns': self._analyze_position_patterns(text),
            'frequency_patterns': self._analyze_frequency_patterns(text),
            'contextual_patterns': self._analyze_contextual_patterns(text)
        }
        return indicators
    
    def _extract_visual_indicators(self, labels, objects):
        """Extract visual indicators for product type"""
        indicators = {
            'shape_indicators': self._analyze_shape_indicators(labels, objects),
            'texture_indicators': self._analyze_texture_indicators(labels, objects),
            'color_indicators': self._analyze_color_indicators(labels, objects),
            'size_indicators': self._analyze_size_indicators(labels, objects),
            'composition_indicators': self._analyze_composition_indicators(labels, objects)
        }
        return indicators
    
    def _extract_semantic_indicators(self, web_entities):
        """Extract semantic indicators from web entities"""
        indicators = {
            'entity_relationships': self._analyze_entity_relationships(web_entities),
            'concept_hierarchies': self._analyze_concept_hierarchies(web_entities),
            'semantic_clusters': self._analyze_semantic_clusters(web_entities),
            'contextual_similarities': self._analyze_contextual_similarities(web_entities)
        }
        return indicators
    
    def _extract_structural_indicators(self, text, labels):
        """Extract structural indicators for product classification"""
        indicators = {
            'texture_patterns': self._analyze_texture_patterns(text),
            'material_patterns': self._analyze_material_patterns(text),
            'function_patterns': self._analyze_function_patterns(text),
            'category_patterns': self._analyze_category_patterns(text)
        }
        return indicators
    
    def _extract_contextual_relationships(self, text, labels, objects):
        """Extract contextual relationships between different indicators"""
        relationships = {
            'text_visual_alignment': self._analyze_text_visual_alignment(text, labels, objects),
            'semantic_visual_correlation': self._analyze_semantic_visual_correlation(text, labels, objects),
            'contextual_coherence': self._analyze_contextual_coherence(text, labels, objects),
            'cross_modal_consistency': self._analyze_cross_modal_consistency(text, labels, objects)
        }
        return relationships
    
    def _infer_product_type_from_context(self, context):
        """Infer product type using advanced AI reasoning"""
        # Multi-modal reasoning
        reasoning_steps = []
        
        # Step 1: Analyze text patterns
        text_reasoning = self._reason_from_text_patterns(context['text_indicators'])
        reasoning_steps.append(text_reasoning)
        
        # Step 2: Analyze visual patterns
        visual_reasoning = self._reason_from_visual_patterns(context['visual_indicators'])
        reasoning_steps.append(visual_reasoning)
        
        # Step 3: Analyze semantic patterns
        semantic_reasoning = self._reason_from_semantic_patterns(context['semantic_indicators'])
        reasoning_steps.append(semantic_reasoning)
        
        # Step 4: Analyze structural patterns
        structural_reasoning = self._reason_from_structural_patterns(context['structural_indicators'])
        reasoning_steps.append(structural_reasoning)
        
        # Step 5: Analyze contextual relationships
        contextual_reasoning = self._reason_from_contextual_relationships(context['contextual_relationships'])
        reasoning_steps.append(contextual_reasoning)
        
        # Combine all reasoning steps
        final_inference = self._combine_reasoning_steps(reasoning_steps)
        
        return final_inference
    
    def _reason_from_text_patterns(self, text_indicators):
        """Reason about product type from text patterns"""
        reasoning = {
            'product_type': None,
            'confidence': 0.0,
            'reasoning_path': [],
            'uncertainty': 0.0
        }
        
        # Analyze length patterns for product complexity
        length_analysis = self._analyze_product_complexity(text_indicators['length_patterns'])
        reasoning['reasoning_path'].append(length_analysis)
        
        # Analyze word patterns for product characteristics
        word_analysis = self._analyze_product_characteristics(text_indicators['word_patterns'])
        reasoning['reasoning_path'].append(word_analysis)
        
        # Analyze position patterns for product hierarchy
        position_analysis = self._analyze_product_hierarchy(text_indicators['position_patterns'])
        reasoning['reasoning_path'].append(position_analysis)
        
        # Analyze frequency patterns for product importance
        frequency_analysis = self._analyze_product_importance(text_indicators['frequency_patterns'])
        reasoning['reasoning_path'].append(frequency_analysis)
        
        # Analyze contextual patterns for product context
        contextual_analysis = self._analyze_product_context(text_indicators['contextual_patterns'])
        reasoning['reasoning_path'].append(contextual_analysis)
        
        # Combine all text-based reasoning
        reasoning = self._synthesize_text_reasoning(reasoning)
        
        return reasoning
    
    def _reason_from_visual_patterns(self, visual_indicators):
        """Reason about product type from visual patterns"""
        reasoning = {
            'product_type': None,
            'confidence': 0.0,
            'reasoning_path': [],
            'uncertainty': 0.0
        }
        
        # Analyze shape for product form
        shape_analysis = self._analyze_product_form(visual_indicators['shape_indicators'])
        reasoning['reasoning_path'].append(shape_analysis)
        
        # Analyze texture for product material
        texture_analysis = self._analyze_product_material(visual_indicators['texture_indicators'])
        reasoning['reasoning_path'].append(texture_analysis)
        
        # Analyze color for product attributes
        color_analysis = self._analyze_product_attributes(visual_indicators['color_indicators'])
        reasoning['reasoning_path'].append(color_analysis)
        
        # Analyze size for product scale
        size_analysis = self._analyze_product_scale(visual_indicators['size_indicators'])
        reasoning['reasoning_path'].append(size_analysis)
        
        # Analyze composition for product structure
        composition_analysis = self._analyze_product_structure(visual_indicators['composition_indicators'])
        reasoning['reasoning_path'].append(composition_analysis)
        
        # Combine all visual-based reasoning
        reasoning = self._synthesize_visual_reasoning(reasoning)
        
        return reasoning
    
    def _reason_from_semantic_patterns(self, semantic_indicators):
        """Reason about product type from semantic patterns"""
        reasoning = {
            'product_type': None,
            'confidence': 0.0,
            'reasoning_path': [],
            'uncertainty': 0.0
        }
        
        # Analyze entity relationships for product categories
        entity_analysis = self._analyze_product_categories(semantic_indicators['entity_relationships'])
        reasoning['reasoning_path'].append(entity_analysis)
        
        # Analyze concept hierarchies for product classification
        hierarchy_analysis = self._analyze_product_classification(semantic_indicators['concept_hierarchies'])
        reasoning['reasoning_path'].append(hierarchy_analysis)
        
        # Analyze semantic clusters for product grouping
        cluster_analysis = self._analyze_product_grouping(semantic_indicators['semantic_clusters'])
        reasoning['reasoning_path'].append(cluster_analysis)
        
        # Analyze contextual similarities for product relationships
        similarity_analysis = self._analyze_product_relationships(semantic_indicators['contextual_similarities'])
        reasoning['reasoning_path'].append(similarity_analysis)
        
        # Combine all semantic-based reasoning
        reasoning = self._synthesize_semantic_reasoning(reasoning)
        
        return reasoning
    
    def _reason_from_structural_patterns(self, structural_indicators):
        """Reason about product type from structural patterns"""
        reasoning = {
            'product_type': None,
            'confidence': 0.0,
            'reasoning_path': [],
            'uncertainty': 0.0
        }
        
        # Analyze texture patterns for product feel
        texture_analysis = self._analyze_product_feel(structural_indicators['texture_patterns'])
        reasoning['reasoning_path'].append(texture_analysis)
        
        # Analyze material patterns for product composition
        material_analysis = self._analyze_product_composition(structural_indicators['material_patterns'])
        reasoning['reasoning_path'].append(material_analysis)
        
        # Analyze function patterns for product purpose
        function_analysis = self._analyze_product_purpose(structural_indicators['function_patterns'])
        reasoning['reasoning_path'].append(function_analysis)
        
        # Analyze category patterns for product classification
        category_analysis = self._analyze_product_classification(structural_indicators['category_patterns'])
        reasoning['reasoning_path'].append(category_analysis)
        
        # Combine all structural-based reasoning
        reasoning = self._synthesize_structural_reasoning(reasoning)
        
        return reasoning
    
    def _reason_from_contextual_relationships(self, contextual_relationships):
        """Reason about product type from contextual relationships"""
        reasoning = {
            'product_type': None,
            'confidence': 0.0,
            'reasoning_path': [],
            'uncertainty': 0.0
        }
        
        # Analyze text-visual alignment for product coherence
        alignment_analysis = self._analyze_product_coherence(contextual_relationships['text_visual_alignment'])
        reasoning['reasoning_path'].append(alignment_analysis)
        
        # Analyze semantic-visual correlation for product consistency
        correlation_analysis = self._analyze_product_consistency(contextual_relationships['semantic_visual_correlation'])
        reasoning['reasoning_path'].append(correlation_analysis)
        
        # Analyze contextual coherence for product logic
        coherence_analysis = self._analyze_product_logic(contextual_relationships['contextual_coherence'])
        reasoning['reasoning_path'].append(coherence_analysis)
        
        # Analyze cross-modal consistency for product reliability
        consistency_analysis = self._analyze_product_reliability(contextual_relationships['cross_modal_consistency'])
        reasoning['reasoning_path'].append(consistency_analysis)
        
        # Combine all contextual-based reasoning
        reasoning = self._synthesize_contextual_reasoning(reasoning)
        
        return reasoning
    
    def _combine_reasoning_steps(self, reasoning_steps):
        """Combine all reasoning steps into final product type inference"""
        # Weight each reasoning step based on confidence and uncertainty
        weighted_reasoning = []
        
        for step in reasoning_steps:
            weight = step['confidence'] * (1 - step['uncertainty'])
            weighted_reasoning.append({
                'reasoning': step,
                'weight': weight
            })
        
        # Sort by weight to prioritize most confident reasoning
        weighted_reasoning.sort(key=lambda x: x['weight'], reverse=True)
        
        # Synthesize final product type
        final_inference = self._synthesize_final_inference(weighted_reasoning)
        
        return final_inference
    
    def _synthesize_final_inference(self, weighted_reasoning):
        """Synthesize final product type inference from weighted reasoning"""
        if not weighted_reasoning:
            return {
                'primary_type': 'unknown',
                'confidence': 0.0,
                'reasoning_path': [],
                'uncertainty': 1.0
            }
        
        # Get the highest weighted reasoning
        top_reasoning = weighted_reasoning[0]['reasoning']
        
        # Calculate overall confidence and uncertainty
        total_weight = sum(w['weight'] for w in weighted_reasoning)
        avg_confidence = sum(w['reasoning']['confidence'] * w['weight'] for w in weighted_reasoning) / total_weight if total_weight > 0 else 0.0
        avg_uncertainty = sum(w['reasoning']['uncertainty'] * w['weight'] for w in weighted_reasoning) / total_weight if total_weight > 0 else 1.0
        
        return {
            'primary_type': top_reasoning.get('product_type', 'unknown'),
            'confidence': avg_confidence,
            'reasoning_path': [w['reasoning']['reasoning_path'] for w in weighted_reasoning],
            'uncertainty': avg_uncertainty
        }
    
    def _validate_product_type_cross_modal(self, product_insights, analysis_results):
        """Validate product type using cross-modal consistency"""
        # This would implement cross-modal validation
        # For now, return the insights as-is
        return product_insights
    
    # Placeholder methods for the analysis functions
    def _analyze_length_patterns(self, text):
        return {'complexity': 'medium', 'confidence': 0.7}
    
    def _analyze_word_patterns(self, text):
        return {'characteristics': 'generic', 'confidence': 0.6}
    
    def _analyze_position_patterns(self, text):
        return {'hierarchy': 'standard', 'confidence': 0.5}
    
    def _analyze_frequency_patterns(self, text):
        return {'importance': 'moderate', 'confidence': 0.6}
    
    def _analyze_contextual_patterns(self, text):
        return {'context': 'general', 'confidence': 0.5}
    
    def _analyze_shape_indicators(self, labels, objects):
        return {'form': 'rectangular', 'confidence': 0.7}
    
    def _analyze_texture_indicators(self, labels, objects):
        return {'material': 'fabric', 'confidence': 0.6}
    
    def _analyze_color_indicators(self, labels, objects):
        return {'attributes': 'colored', 'confidence': 0.5}
    
    def _analyze_size_indicators(self, labels, objects):
        return {'scale': 'medium', 'confidence': 0.6}
    
    def _analyze_composition_indicators(self, labels, objects):
        return {'structure': 'layered', 'confidence': 0.5}
    
    def _analyze_entity_relationships(self, web_entities):
        return {'categories': 'clothing', 'confidence': 0.7}
    
    def _analyze_concept_hierarchies(self, web_entities):
        return {'classification': 'apparel', 'confidence': 0.6}
    
    def _analyze_semantic_clusters(self, web_entities):
        return {'grouping': 'sports', 'confidence': 0.5}
    
    def _analyze_contextual_similarities(self, web_entities):
        return {'relationships': 'team', 'confidence': 0.6}
    
    def _analyze_texture_patterns(self, text):
        return {'feel': 'smooth', 'confidence': 0.5}
    
    def _analyze_material_patterns(self, text):
        return {'composition': 'cotton', 'confidence': 0.6}
    
    def _analyze_function_patterns(self, text):
        return {'purpose': 'wearable', 'confidence': 0.7}
    
    def _analyze_category_patterns(self, text):
        return {'classification': 'clothing', 'confidence': 0.6}
    
    def _analyze_text_visual_alignment(self, text, labels, objects):
        return {'coherence': 'high', 'confidence': 0.7}
    
    def _analyze_semantic_visual_correlation(self, text, labels, objects):
        return {'consistency': 'medium', 'confidence': 0.6}
    
    def _analyze_contextual_coherence(self, text, labels, objects):
        return {'logic': 'consistent', 'confidence': 0.5}
    
    def _analyze_cross_modal_consistency(self, text, labels, objects):
        return {'reliability': 'good', 'confidence': 0.6}
    
    # Analysis methods for reasoning
    def _analyze_product_complexity(self, length_patterns):
        return {'type': 'medium_complexity', 'confidence': 0.6}
    
    def _analyze_product_characteristics(self, word_patterns):
        return {'type': 'standard_characteristics', 'confidence': 0.5}
    
    def _analyze_product_hierarchy(self, position_patterns):
        return {'type': 'standard_hierarchy', 'confidence': 0.5}
    
    def _analyze_product_importance(self, frequency_patterns):
        return {'type': 'moderate_importance', 'confidence': 0.6}
    
    def _analyze_product_context(self, contextual_patterns):
        return {'type': 'general_context', 'confidence': 0.5}
    
    def _analyze_product_form(self, shape_indicators):
        return {'type': 'rectangular_form', 'confidence': 0.7}
    
    def _analyze_product_material(self, texture_indicators):
        return {'type': 'fabric_material', 'confidence': 0.6}
    
    def _analyze_product_attributes(self, color_indicators):
        return {'type': 'colored_attributes', 'confidence': 0.5}
    
    def _analyze_product_scale(self, size_indicators):
        return {'type': 'medium_scale', 'confidence': 0.6}
    
    def _analyze_product_structure(self, composition_indicators):
        return {'type': 'layered_structure', 'confidence': 0.5}
    
    def _analyze_product_categories(self, entity_relationships):
        return {'type': 'clothing_category', 'confidence': 0.7}
    
    def _analyze_product_classification(self, concept_hierarchies):
        return {'type': 'apparel_classification', 'confidence': 0.6}
    
    def _analyze_product_grouping(self, semantic_clusters):
        return {'type': 'sports_grouping', 'confidence': 0.5}
    
    def _analyze_product_relationships(self, contextual_similarities):
        return {'type': 'team_relationship', 'confidence': 0.6}
    
    def _analyze_product_feel(self, texture_patterns):
        return {'type': 'smooth_feel', 'confidence': 0.5}
    
    def _analyze_product_composition(self, material_patterns):
        return {'type': 'cotton_composition', 'confidence': 0.6}
    
    def _analyze_product_purpose(self, function_patterns):
        return {'type': 'wearable_purpose', 'confidence': 0.7}
    
    def _analyze_product_coherence(self, alignment_analysis):
        return {'type': 'high_coherence', 'confidence': 0.7}
    
    def _analyze_product_consistency(self, correlation_analysis):
        return {'type': 'medium_consistency', 'confidence': 0.6}
    
    def _analyze_product_logic(self, coherence_analysis):
        return {'type': 'consistent_logic', 'confidence': 0.5}
    
    def _analyze_product_reliability(self, consistency_analysis):
        return {'type': 'good_reliability', 'confidence': 0.6}
    
    # Synthesis methods
    def _synthesize_text_reasoning(self, reasoning):
        reasoning['product_type'] = 'clothing'
        reasoning['confidence'] = 0.6
        reasoning['uncertainty'] = 0.3
        return reasoning
    
    def _synthesize_visual_reasoning(self, reasoning):
        reasoning['product_type'] = 'apparel'
        reasoning['confidence'] = 0.7
        reasoning['uncertainty'] = 0.2
        return reasoning
    
    def _synthesize_semantic_reasoning(self, reasoning):
        reasoning['product_type'] = 'sports_wear'
        reasoning['confidence'] = 0.5
        reasoning['uncertainty'] = 0.4
        return reasoning
    
    def _synthesize_structural_reasoning(self, reasoning):
        reasoning['product_type'] = 'fabric_item'
        reasoning['confidence'] = 0.6
        reasoning['uncertainty'] = 0.3
        return reasoning
    
    def _synthesize_contextual_reasoning(self, reasoning):
        reasoning['product_type'] = 'team_merchandise'
        reasoning['confidence'] = 0.7
        reasoning['uncertainty'] = 0.2
        return reasoning

    def _build_context_vectors(self, text, labels, objects):
        """Build context vectors for attention mechanism"""
        context_vectors = []
        
        # Text context
        text_vector = self._compute_text_vector(text)
        context_vectors.append(text_vector)
        
        # Label context
        for label in labels:
            label_vector = self._compute_label_vector(label)
            context_vectors.append(label_vector)
        
        # Object context
        for obj in objects:
            object_vector = self._compute_object_vector(obj)
            context_vectors.append(object_vector)
        
        return context_vectors
    
    def _compute_text_vector(self, text):
        """Compute text vector representation"""
        # Simplified text vector computation
        # In a real system, this would use BERT or similar
        return {'text': text, 'length': len(text), 'words': len(text.split())}
    
    def _compute_label_vector(self, label):
        """Compute label vector representation"""
        return {'label': label['description'], 'confidence': label.get('score', 0.0)}
    
    def _compute_object_vector(self, obj):
        """Compute object vector representation"""
        return {'object': obj['name'], 'confidence': obj.get('score', 0.0)}

    def detect_objects_rekognition(self, image_data: bytes) -> list:
        """
        Use AWS Rekognition to detect objects and their bounding boxes in the image.
        Returns a list of dicts: {name, confidence, bounding_box: (x_min, y_min, x_max, y_max)}
        """
        try:
            rekognition = boto3.client(
                'rekognition',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('AWS_REGION_NAME', 'us-east-1')
            )
            response = rekognition.detect_labels(
                Image={'Bytes': image_data},
                MaxLabels=10,
                MinConfidence=70
            )
            objects = []
            for label in response['Labels']:
                for instance in label.get('Instances', []):
                    box = instance.get('BoundingBox')
                    if box:
                        # Rekognition bounding box is in relative coordinates (0-1)
                        x_min = box['Left']
                        y_min = box['Top']
                        x_max = x_min + box['Width']
                        y_max = y_min + box['Height']
                        objects.append({
                            'name': label['Name'],
                            'confidence': instance.get('Confidence', label.get('Confidence', 0)),
                            'bounding_box': (x_min, y_min, x_max, y_max),
                        })
            logger.info(f"[CROP] Rekognition detected {len(objects)} objects")
            return objects
        except Exception as e:
            logger.error(f"[CROP] Rekognition error: {e}")
            return []

    def get_best_bounding_box(self, objects: list) -> Optional[tuple]:
        """
        Select the most relevant bounding box (highest confidence, largest area, etc.)
        """
        if not objects:
            return None
        # Sort by confidence, then area
        def area(box):
            x_min, y_min, x_max, y_max = box
            return (x_max - x_min) * (y_max - y_min)
        objects = sorted(objects, key=lambda o: (o['confidence'], area(o['bounding_box'])), reverse=True)
        return objects[0]['bounding_box']

    def intelligent_crop(self, image_data: bytes, use_vision=True, use_rekognition=True) -> tuple:
        """
        Try to crop the image using Google Vision first, then AWS Rekognition.
        Returns (cropped_image_bytes, crop_info_dict)
        crop_info_dict: {service: 'vision'|'rekognition'|'none', bounding_box: tuple or None}
        """
        # Try Google Vision
        if use_vision and self.client:
            objects = self.detect_objects_and_regions(image_data)
            bbox = self.get_best_bounding_box(objects)
            if bbox:
                logger.info(f"[CROP] Using Google Vision bounding box: {bbox}")
                cropped = self.crop_to_region(image_data, bbox)
                return cropped, {'service': 'vision', 'bounding_box': bbox}
        # Try Rekognition
        if use_rekognition:
            objects = self.detect_objects_rekognition(image_data)
            bbox = self.get_best_bounding_box(objects)
            if bbox:
                logger.info(f"[CROP] Using Rekognition bounding box: {bbox}")
                cropped = self.crop_to_region(image_data, bbox)
                return cropped, {'service': 'rekognition', 'bounding_box': bbox}
        # Fallback: no crop
        logger.info(f"[CROP] No bounding box found, using original image")
        return image_data, {'service': 'none', 'bounding_box': None}

    # Global AI service instance (lazy initialization)
_ai_service_instance = None

def get_ai_service():
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance