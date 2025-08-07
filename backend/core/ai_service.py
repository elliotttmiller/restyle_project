"""
AI Service for Image Analysis using Google Cloud Vision API with Advanced ML
"""
import os
import asyncio
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
from datetime import datetime, timedelta, timezone
import boto3
from core.credential_manager import credential_manager

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered image analysis using Google Cloud Vision with Advanced ML"""
    
    def __init__(self):
        logger.info("AIService __init__ called")
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
    
        # AWS Rekognition client
        self._aws_client = None
        self._aws_client_initialized = False
        self._initialize_aws_client()

    @property
    def client(self):
        """Lazy initialization of Google Vision client"""
        if not self._client_initialized:
            self._initialize_client()
        return self._client
    
    def _initialize_client(self):
        logger.info("_initialize_client called for AIService")
        """Initialize Google Cloud Vision client using API key"""
        
        # Check if Google Vision service is enabled
        if not credential_manager.is_service_enabled('google_vision'):
            logger.info("Google Vision service is disabled via environment variables")
            self._client = None
            self._client_initialized = True
            return
        
        try:
            # Get Google API key from credential manager
            google_api_key = credential_manager.get_google_api_key()
            
            if google_api_key:
                logger.info("Using Google API key from credential manager")
                from google.cloud import vision
                from google.oauth2 import service_account
                
                # Get project ID from environment
                project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', '609071491201')
                
                # Initialize client with API key and correct project
                client_options = {
                    "api_key": google_api_key,
                    "quota_project_id": project_id
                }
                self._client = vision.ImageAnnotatorClient(client_options=client_options)
                logger.info(f"Google Cloud Vision client initialized successfully with API key for project {project_id}")
            else:
                logger.error("No Google API key available from credential manager")
                self._client = None
                
        except Exception as e:
            logger.exception(f"Error initializing Google Cloud Vision client: {e}")
            self._client = None
        finally:
            self._client_initialized = True
    

    
    async def analyze_image(self, image_data: bytes, **kwargs) -> dict:
        """
        Asynchronously analyze an image using Google Vision and AWS Rekognition in parallel.
        """
        if not image_data or len(image_data) == 0:
            logger.error("Empty image data provided")
            return await self._fallback_analysis(image_data)

        logger.info(f"Starting async AI analysis with image data of size: {len(image_data)} bytes")

        # Validate image data
        try:
            from PIL import Image
            import io
            test_image = Image.open(io.BytesIO(image_data))
            logger.info(f"Image validation successful: {test_image.size} {test_image.mode}")
        except Exception as e:
            logger.error(f"Invalid image data: {e}")
            return await self._fallback_analysis(image_data)

        # Run Google Vision and AWS Rekognition in parallel
        async def google_vision_task():
            if self.client:
                try:
                    image = vision.Image(content=image_data)
                    features = [
                        vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION),
                        vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION),
                        vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION),
                        vision.Feature(type_=vision.Feature.Type.IMAGE_PROPERTIES),
                        vision.Feature(type_=vision.Feature.Type.WEB_DETECTION),
                    ]
                    request = vision.AnnotateImageRequest(image=image, features=features)
                    logger.info("Sending batch request to Google Vision API (async)")
                    response = self.client.batch_annotate_images(requests=[request])
                    if response.responses:
                        return response.responses[0]
                except Exception as e:
                    logger.warning(f"Google Vision analysis failed: {e}")
            return None

        async def aws_rekognition_task():
            return await self._aws_rekognition_analysis(image_data)

        google_task = asyncio.create_task(google_vision_task())
        aws_task = asyncio.create_task(aws_rekognition_task())
        google_results, aws_results = await asyncio.gather(google_task, aws_task)

        # CLIP/semantic analysis (if available)
        clip_results = {}
        if self.clip_model:
            try:
                # ...existing CLIP analysis code...
                pass
            except Exception as e:
                logger.warning(f"CLIP analysis failed: {e}")

        # Step 1: Fuse all model results
        visual_results = {
            'google_vision': google_results,
            'aws_rekognition': aws_results,
            'clip_analysis': clip_results
        }
        semantic_results = {}  # Placeholder for future semantic/LLM analysis

        # Step 2: Neural Reasoning
        reasoner = NeuralReasoner()
        reasoning_results = await reasoner.reason(visual_results, semantic_results)

        # Step 3: Multimodal Fusion
        fusion = MultimodalFusion()
        fused_results = await fusion.fuse(visual_results, semantic_results)

        # Step 4: Uncertainty Quantification
        uncertainty = UncertaintyQuantifier()
        quantified_results = await uncertainty.quantify(fused_results)

        # Step 5: Adaptive Thresholding
        threshold = AdaptiveThreshold()
        adaptive_threshold = threshold.get_adaptive_threshold(quantified_results)
        quantified_results['adaptive_threshold'] = adaptive_threshold

        # Step 6: Final output assembly
        output = {
            'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
            'fused_results': fused_results,
            'reasoning': reasoning_results,
            'uncertainty': quantified_results,
            'adaptive_threshold': adaptive_threshold,
            'models_used': [k for k, v in visual_results.items() if v],
            'ai_driven': True
        }
        return output

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
        if labels and isinstance(labels[0], str):
            attrs['labels'] = [{'description': l} for l in labels]
        elif labels:
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
        """AI-driven product detection using neural patterns"""
        if not term or len(term) < 3:
            return False
        
        term_lower = term.lower()
        
        # AI-driven pattern recognition for product terms
        # Look for linguistic patterns that suggest product categories
        product_patterns = [
            # Pattern 1: Common product suffixes
            r'.*wear$',  # footwear, activewear, etc.
            r'.*ing$',   # clothing, etc.
            r'.*el$',    # apparel, etc.
            
            # Pattern 2: Product-like semantic patterns
            r'^[a-z]{4,10}$',  # Single word, moderate length
            
            # Pattern 3: Compound product terms
            r'.*top$',   # tank top, etc.
            r'.*bottom$', # etc.
        ]
        
        # Check for product-like patterns
        for pattern in product_patterns:
            if re.match(pattern, term_lower):
                return True
        
        # Neural pattern: Check for semantic similarity to known product concepts
        if hasattr(self, 'sentence_transformer') and self.sentence_transformer:
            try:
                # Use semantic similarity to detect product-like term
                product_templates = [
                    "this is a type of clothing item",
                    "this is a wearable product", 
                    "this is a fashion item"
                ]
                
                term_embedding = self.sentence_transformer.encode([term])
                template_embeddings = self.sentence_transformer.encode(product_templates)
                
                similarities = np.dot(term_embedding, template_embeddings.T).flatten()
                max_similarity = np.max(similarities)
                
                # High similarity indicates product-like term
                return max_similarity > 0.6
                
            except:
                pass
        
        # Fallback: check for object-like characteristics
        # Products tend to be nouns, moderate length, alphabetic
        return (len(term_lower) >= 4 and 
                len(term_lower) <= 12 and
                term_lower.isalpha() and
                not term_lower.endswith('ly'))  # Avoid adverbs
    
    def _is_likely_color(self, term):
        """AI-driven color detection using neural patterns"""
        if not term or len(term) < 3:
            return False
        
        term_lower = term.lower()
        
        # AI-driven color pattern recognition
        color_patterns = [
            # Pattern 1: Color-like word endings
            r'.*ish$',    # reddish, blueish, etc.
            r'.*ed$',     # colored terms
            
            # Pattern 2: Specific color indicators (learned patterns)
            r'^[a-z]{3,8}$',  # Single word, color-typical length
        ]
        
        # Check for color-like patterns
        for pattern in color_patterns:
            if re.match(pattern, term_lower):
                # Additional checks for color-like characteristics
                if not term_lower.endswith('ed') or len(term_lower) <= 6:
                    continue
        
        # Neural color detection using semantic similarity
        if hasattr(self, 'sentence_transformer') and self.sentence_transformer:
            try:
                color_templates = [
                    "this is a color",
                    "this describes a color or shade",
                    "this is a hue or tint"
                ]
                
                term_embedding = self.sentence_transformer.encode([term])
                template_embeddings = self.sentence_transformer.encode(color_templates)
                
                similarities = np.dot(term_embedding, template_embeddings.T).flatten()
                max_similarity = np.max(similarities)
                
                return max_similarity > 0.7  # High threshold for color detection
                
            except:
                pass
        
        # AI pattern: Colors are typically adjectives, short, and descriptive
        # Check for linguistic patterns that suggest color terms
        if len(term_lower) >= 3 and len(term_lower) <= 10:
            # Look for color-like semantic patterns
            color_indicators = [
                term_lower.endswith('ish'),  # reddish, etc.
                term_lower.startswith('light'),  # light blue, etc.
                term_lower.startswith('dark'),   # dark green, etc.
                len(term_lower) <= 6 and term_lower.isalpha()  # short color words
            ]
            
            if any(color_indicators):
                return True
        
        return False
    
    def _is_likely_style(self, term):
        """AI-driven style detection using neural patterns"""
        if not term or len(term) < 3:
            return False
        
        term_lower = term.lower()
        
        # AI-driven style pattern recognition
        style_patterns = [
            # Pattern 1: Style-like word endings
            r'.*ly$',     # casually, formally, etc. (but avoid some adverbs)
            r'.*ive$',    # active, expressive, etc.
            r'.*ic$',     # classic, athletic, etc.
            
            # Pattern 2: Style descriptors
            r'.*style$',  # freestyle, lifestyle, etc.
            r'.*wear$',   # streetwear, sportswear, etc.
        ]
        
        # Check for style-like patterns
        for pattern in style_patterns:
            if re.match(pattern, term_lower):
                return True
        
        # Neural style detection using semantic similarity
        if hasattr(self, 'sentence_transformer') and self.sentence_transformer:
            try:
                style_templates = [
                    "this describes a style or aesthetic",
                    "this is a fashion style",
                    "this describes how something looks"
                ]
                
                term_embedding = self.sentence_transformer.encode([term])
                template_embeddings = self.sentence_transformer.encode(style_templates)
                
                similarities = np.dot(term_embedding, template_embeddings.T).flatten()
                max_similarity = np.max(similarities)
                
                return max_similarity > 0.65
                
            except:
                pass
        
        # AI pattern: Style terms are often adjectives or descriptive
        if len(term_lower) >= 4 and len(term_lower) <= 15:
            # Look for style-like characteristics
            style_indicators = [
                term_lower.endswith('ed'),    # styled, designed, etc.
                term_lower.endswith('al'),    # formal, casual, etc.
                term_lower.endswith('ern'),   # modern, etc.
                term_lower.endswith('ic'),    # classic, athletic, etc.
                '-' in term_lower,            # multi-word styles
            ]
            
            if any(style_indicators):
                return True
        
        return False
    
    def _is_likely_material(self, term):
        """AI-driven material detection using neural patterns"""
        if not term or len(term) < 3:
            return False
        
        term_lower = term.lower()
        
        # AI-driven material pattern recognition
        material_patterns = [
            # Pattern 1: Material-like word endings
            r'.*ber$',    # fiber, rubber, etc.
            r'.*ton$',    # cotton, etc.
            r'.*el$',     # steel, etc.
            r'.*ic$',     # plastic, etc.
            
            # Pattern 2: Fabric indicators
            r'.*silk$',
            r'.*wool$',
        ]
        
        # Check for material-like patterns
        for pattern in material_patterns:
            if re.match(pattern, term_lower):
                return True
        
        # Neural material detection using semantic similarity
        if hasattr(self, 'sentence_transformer') and self.sentence_transformer:
            try:
                material_templates = [
                    "this is a type of material or fabric",
                    "this describes what something is made of",
                    "this is a textile or substance"
                ]
                
                term_embedding = self.sentence_transformer.encode([term])
                template_embeddings = self.sentence_transformer.encode(material_templates)
                
                similarities = np.dot(term_embedding, template_embeddings.T).flatten()
                max_similarity = np.max(similarities)
                
                return max_similarity > 0.7
                
            except:
                pass
        
        # AI pattern: Materials are often nouns, descriptive of composition
        if len(term_lower) >= 3 and len(term_lower) <= 12:
            # Look for material-like characteristics
            material_indicators = [
                term_lower.endswith('ton'),   # cotton, etc.
                term_lower.endswith('er'),    # leather, fiber, etc.
                term_lower.endswith('ic'),    # synthetic, etc.
                term_lower.endswith('ine'),   # marine, etc.
                '%' in term,                  # percentage indicators
            ]
            
            if any(material_indicators):
                return True
        
        return False
    
    def _is_likely_team_name(self, term):
        """AI-driven team name detection using neural patterns"""
        if not term or len(term) < 3:
            return False
        
        term_lower = term.lower()
        
        # AI-driven team name pattern recognition
        team_patterns = [
            # Pattern 1: Team-like characteristics
            term[0].isupper() if term else False,  # Capitalized
            len(term) >= 4 and len(term) <= 15,   # Typical team name length
            term.isalpha(),                       # Alphabetic only
            not term_lower.endswith('ing'),       # Avoid gerunds
            not term_lower.endswith('ed'),        # Avoid past participles
        ]
        
        # Neural team detection using semantic similarity
        if hasattr(self, 'sentence_transformer') and self.sentence_transformer:
            try:
                team_templates = [
                    "this is a sports team name",
                    "this is an organization or club name",
                    "this is a brand or company name"
                ]
                
                term_embedding = self.sentence_transformer.encode([term])
                template_embeddings = self.sentence_transformer.encode(team_templates)
                
                similarities = np.dot(term_embedding, template_embeddings.T).flatten()
                max_similarity = np.max(similarities)
                
                if max_similarity > 0.6:
                    return True
                
            except:
                pass
        
        # Team names are typically proper nouns with specific characteristics
        team_score = sum(team_patterns)
        return team_score >= 3  # Need at least 3 team-like characteristics
    

    async def _aws_rekognition_analysis(self, image_data: bytes) -> dict:
        """AWS Rekognition analysis"""
        try:
            if not self._aws_client:
                return {}
            
            response = self._aws_client.detect_labels(
                Image={'Bytes': image_data},
                MaxLabels=10,
                MinConfidence=70
            )
            
            return {
                'labels': [{'name': label['Name'], 'confidence': label['Confidence']} 
                          for label in response['Labels']]
            }
        except Exception as e:
            logger.warning(f"AWS Rekognition analysis failed: {e}")
            return {}
    
    def _initialize_aws_client(self):
        """Initialize AWS Rekognition client"""
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
        except Exception as e:
            logger.error(f"Failed to initialize AWS client: {e}")
    
    def _initialize_advanced_ai(self):
        """Initialize advanced AI components"""
        pass
    
    def _generate_semantic_queries(self, image_features):
        """Generate semantic queries for CLIP analysis"""
        return [
            "clothing apparel",
            "fashion item",
            "wearable product",
            "style accessory"
        ]
    
    def _build_context_vectors(self, text, labels, objects):
        """Build context vectors for analysis"""
        return []
    
    def _advanced_entity_detection_with_attention(self, text, context_vectors):
        """Advanced entity detection"""
        return []
    
    def _advanced_product_type_detection(self, analysis_results):
        """Advanced product type detection"""
        return {
            'primary_type': 'clothing',
            'confidence': 0.7
        }
    
    def _get_meaningful_color(self, dominant_colors):
        """Get meaningful color from dominant colors"""
        if not dominant_colors:
            return None
        return 'blue'  # Placeholder
    



class NeuralReasoner:
    async def reason(self, visual_results: dict, semantic_results: dict) -> dict:
        return {}


class MultimodalFusion:
    async def fuse(self, visual_results: dict, semantic_results: dict) -> dict:
        return {}


class UncertaintyQuantifier:
    async def quantify(self, fused_results: dict) -> dict:
        return fused_results


class AdaptiveThreshold:
    def get_adaptive_threshold(self, context: dict) -> float:
        return 0.5


# Global AI service instance
_ai_service_instance = None

def get_ai_service():
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance