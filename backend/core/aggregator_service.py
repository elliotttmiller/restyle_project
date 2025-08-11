"""
Multi-Expert AI Aggregator Service
Coordinates Google Vision API, Amazon Rekognition, and Google Gemini for superior image analysis.
This service implements a "panel of experts" approach with LLM synthesis for maximum accuracy.
"""
import logging
import boto3
import json
import os
from threading import Thread
from typing import Dict, Any, Optional, List
from google.cloud import vision
import google.generativeai as genai
from django.conf import settings
import numpy as np

logger = logging.getLogger(__name__)

class AggregatorService:
    """
    Multi-expert AI service that coordinates Google Vision, Amazon Rekognition, and Google Gemini.
    Implements a "panel of experts" approach with LLM synthesis for maximum accuracy.
    """
    _instance = None
    
    def __new__(cls):
        # Singleton pattern for this service
        if cls._instance is None:
            cls._instance = super(AggregatorService, cls).__new__(cls)
            # Lazy initialization - don't initialize clients until needed
            cls._instance._google_vision_client = None
            cls._instance._aws_rekognition_client = None
            cls._instance._gemini_model = None
            cls._instance._initialized = False
        return cls._instance
    
    def _initialize_clients(self):
        """Lazy initialization of AI clients"""
        if self._initialized:
            return
        
        try:
            # Initialize Google Vision client with API key
            google_api_key = os.environ.get('GOOGLE_API_KEY')
            if google_api_key:
                # Get project ID from environment
                project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', '609071491201')
                
                client_options = {
                    "api_key": google_api_key,
                    "quota_project_id": project_id
                }
                self._google_vision_client = vision.ImageAnnotatorClient(client_options=client_options)
                logger.info(f"Google Vision client initialized with API key for project {project_id}")
            else:
                logger.warning("No GOOGLE_API_KEY found, Google Vision client not initialized")
                self._google_vision_client = None
            
            # Initialize AWS Rekognition client
            self._aws_rekognition_client = boto3.client(
                'rekognition',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('AWS_REGION_NAME', 'us-east-1')
            )
            
            # Initialize Google Gemini
            gemini_api_key = os.environ.get('GEMINI_API_KEY')
            if gemini_api_key:
                genai.configure(api_key=gemini_api_key)
                generation_config = genai.types.GenerationConfig(
                    response_mime_type="application/json"
                )
                self._gemini_model = genai.GenerativeModel(
                    'gemini-1.5-pro-latest',
                    generation_config=generation_config
                )
                logger.info("AggregatorService initialized with all AI clients.")
            else:
                logger.warning("GEMINI_API_KEY not found. Gemini synthesis will be disabled.")
                self._gemini_model = None
                
            self._initialized = True
                
        except Exception as e:
            logger.error(f"CRITICAL: Failed to initialize AggregatorService clients. Error: {e}")
            raise
    
    @property
    def google_vision_client(self):
        """Lazy initialization of Google Vision client"""
        if not self._initialized:
            self._initialize_clients()
        return self._google_vision_client
    
    @property
    def aws_rekognition_client(self):
        """Lazy initialization of AWS Rekognition client"""
        if not self._initialized:
            self._initialize_clients()
        return self._aws_rekognition_client
    
    @property
    def gemini_model(self):
        """Lazy initialization of Google Gemini model"""
        if not self._initialized:
            self._initialize_clients()
        return self._gemini_model

    def run_full_analysis(self, image_data: bytes) -> Dict[str, Any]:
        """
        Runs the full multi-expert analysis pipeline.
        """
        logger.info("Starting multi-expert AI analysis pipeline...")
        expert_outputs = {}
        threads = [
            Thread(target=self._call_google_vision, args=(image_data, expert_outputs)),
            Thread(target=self._call_aws_rekognition, args=(image_data, expert_outputs)),
            Thread(target=self._call_clip_encoder, args=(image_data, expert_outputs)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        logger.info(f"Expert outputs collected: {list(expert_outputs.keys())}")
        # Add user-facing error messages for missing/failed services
        errors = {}
        for key in ["google_vision", "aws_rekognition", "clip_encoder"]:
            if key not in expert_outputs or not expert_outputs.get(key, {}).get("success", False):
                err = expert_outputs.get(key, {}).get("error", f"{key} did not return a successful result.")
                errors[key] = err
        if errors:
            expert_outputs["service_errors"] = errors
        if self.gemini_model:
            return self._synthesize_with_gemini(expert_outputs)
        else:
            logger.error("Gemini model is not available. AI-driven synthesis required.")
            return {"error": "Gemini model is not available. AI-driven synthesis required.", "identified_attributes": {}, "service_errors": errors}

    def _call_google_vision(self, image_data: bytes, output: Dict[str, Any]):
        """Calls Google Vision API for its expert opinion."""
        try:
            image = vision.Image(content=image_data)
            response = self.google_vision_client.annotate_image({
                'image': image,
                'features': [
                    {'type_': vision.Feature.Type.WEB_DETECTION},
                    {'type_': vision.Feature.Type.OBJECT_LOCALIZATION},
                    {'type_': vision.Feature.Type.TEXT_DETECTION},
                    {'type_': vision.Feature.Type.IMAGE_PROPERTIES},
                ],
            })
            # DEBUG: Log raw Google Vision response
            logger.info(f"[DEBUG] Raw Google Vision response: {response}")
            
            # Extract web entities (most powerful for product identification)

    def _call_clip_encoder(self, image_data: bytes, output: Dict[str, Any]):
        """Calls the CLIP/encoder service for semantic description and embedding."""
        try:
            from backend.core.encoder_service import get_encoder_service
            encoder = get_encoder_service()
            description_result = encoder.describe(image_data)
            embedding_result = encoder.encode(image_data)
            output['clip_encoder'] = {
                'description': description_result.get('description'),
                'confidence': description_result.get('confidence'),
                'top_labels': description_result.get('top_labels'),
                'embedding': embedding_result,
                'success': True
            }
            logger.info(f"CLIP/encoder analysis completed: {description_result.get('description')}")
        except Exception as e:
            logger.error(f"CLIP/encoder error: {e}")
            output['clip_encoder'] = {
                'error': str(e),
                'success': False
            }
            web_entities = []
            if response.web_detection.web_entities:
                web_entities = [
                    {
                        'description': entity.description,
                        'score': entity.score,
                        'entity_id': entity.entity_id
                    }
                    for entity in response.web_detection.web_entities[:10]
                ]
            
            # Extract localized objects
            objects = []
            if response.localized_object_annotations:
                objects = [
                    {
                        'name': obj.name,
                        'confidence': obj.score,
                        'bounding_poly': {
                            'vertices': [
                                {'x': vertex.x, 'y': vertex.y}
                                for vertex in obj.bounding_poly.vertices
                            ]
                        }
                    }
                    for obj in response.localized_object_annotations[:5]
                ]
            
            # Extract text (OCR)
            text_annotations = []
            if response.text_annotations:
                text_annotations = [
                    {
                        'description': text.description,
                        'bounding_poly': {
                            'vertices': [
                                {'x': vertex.x, 'y': vertex.y}
                                for vertex in text.bounding_poly.vertices
                            ]
                        }
                    }
                    for text in response.text_annotations[:10]
                ]
            
            # Extract dominant colors
            dominant_colors = []
            if response.image_properties_annotation.dominant_colors.colors:
                dominant_colors = [
                    {
                        'color': {
                            'red': color.color.red,
                            'green': color.color.green,
                            'blue': color.color.blue
                        },
                        'score': color.score,
                        'pixel_fraction': color.pixel_fraction
                    }
                    for color in response.image_properties_annotation.dominant_colors.colors[:5]
                ]
            
            output['google_vision'] = {
                'web_entities': web_entities,
                'objects': objects,
                'text_annotations': text_annotations,
                'dominant_colors': dominant_colors,
                'success': True
            }
            
            logger.info(f"Google Vision analysis completed: {len(web_entities)} web entities, {len(objects)} objects")
            
        except Exception as e:
            logger.error(f"Google Vision API error: {e}")
            output['google_vision'] = {
                'error': str(e),
                'success': False
            }

    def _call_aws_rekognition(self, image_data: bytes, output: Dict[str, Any]):
        """Calls AWS Rekognition for its expert opinion."""
        try:
            labels_response = self.aws_rekognition_client.detect_labels(
                Image={'Bytes': image_data},
                MaxLabels=20,
                MinConfidence=50.0
            )
            # DEBUG: Log raw AWS Rekognition labels response
            logger.info(f"[DEBUG] Raw AWS Rekognition labels response: {labels_response}")
            
            # Extract labels with confidence scores
            labels = []
            if 'Labels' in labels_response:
                for label in labels_response['Labels']:
                    label_info = {
                        'name': label['Name'],
                        'confidence': label['Confidence'],
                        'instances': len(label.get('Instances', [])),
                        'parents': [parent['Name'] for parent in label.get('Parents', [])]
                    }
                    labels.append(label_info)
            
            # Detect text (OCR)
            text_response = self.aws_rekognition_client.detect_text(
                Image={'Bytes': image_data}
            )
            # DEBUG: Log raw AWS Rekognition text response
            logger.info(f"[DEBUG] Raw AWS Rekognition text response: {text_response}")
            
            detected_text = []
            if 'TextDetections' in text_response:
                for text_detection in text_response['TextDetections']:
                    if text_detection['Type'] == 'LINE':
                        detected_text.append({
                            'text': text_detection['DetectedText'],
                            'confidence': text_detection['Confidence'],
                            'geometry': text_detection.get('Geometry', {})
                        })
            
            output['aws_rekognition'] = {
                'labels': labels,
                'detected_text': detected_text,
                'success': True
            }
            
            logger.info(f"AWS Rekognition analysis completed: {len(labels)} labels, {len(detected_text)} text elements")
            
        except Exception as e:
            logger.error(f"AWS Rekognition error: {e}")
            output['aws_rekognition'] = {
                'error': str(e),
                'success': False
            }

    def _build_gemini_prompt(self, expert_outputs: Dict[str, Any]) -> str:
        """
        Builds an advanced prompt for Gemini to synthesize expert opinions and generate a human-like, optimized search query for eBay.
        """
        google_data = expert_outputs.get('google_vision', {})
        aws_data = expert_outputs.get('aws_rekognition', {})
        # Extract all candidate terms from web entities, objects, and detected text
        web_entities = [e['description'] for e in google_data.get('web_entities', []) if e.get('description')]
        objects = [o['name'] for o in google_data.get('objects', []) if o.get('name')]
        detected_text = [t['text'] for t in aws_data.get('detected_text', []) if t.get('text')]
        all_terms = web_entities + objects + detected_text
        prompt = f'''
You are a world-class AI expert for fashion resale and product identification. Your task is to analyze raw JSON data from Google Vision and AWS Rekognition, extract all key item terms (objects, web entities, detected text), and then act as a cutting-edge query builder. Your goal is to generate the most accurate, human-like search query for eBay to find this item, as if you were a top-tier eBay power user.

**Step 1: Extract Key Terms**
- List all possible product names, brands, categories, and any relevant text or object labels from the AI outputs.

**Step 2: Build Search Query**
- Using the extracted terms, synthesize a single, highly accurate, human-like search query string that would maximize the chance of finding this exact item on eBay. Use natural language, include only the most relevant terms, and avoid generic or irrelevant words. If the item is a sports jersey, for example, include team, player, year, and "jersey".

**Step 3: Output**
- Return a single, valid JSON object with the following schema:
{{
  "product_name": "String | null",
  "brand": "String | null",
  "category": "String | null",
  "item_condition": "String ('New', 'Used', 'Unknown')",
  "colors": ["String", ...],
  "market_sentiment_score": "Float (e.g., 1.15)",
  "ai_summary": "A brief, one-sentence summary for the user.",
  "confidence_score": "Float (0.0-1.0)",
  "ebay_search_query": "String (the optimized search query)"
}}

**Google Vision Data:**
```json
{json.dumps(google_data, indent=2)}
```

**AWS Rekognition Data:**
```json
{json.dumps(aws_data, indent=2)}
```

**Extracted Terms:** {all_terms}
'''
        return prompt

    def _synthesize_with_gemini(self, expert_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses Gemini to intelligently synthesize expert outputs and generate an optimized eBay search query.
        """
        try:
            if self._gemini_model:
                prompt = self._build_gemini_prompt(expert_outputs)
                response = self._gemini_model.generate_content(prompt)
                try:
                    synthesized_attributes = json.loads(response.text)
                    required_keys = ["product_name", "brand", "category", "colors", "confidence_score", "ebay_search_query"]
                    if all(k in synthesized_attributes for k in required_keys):
                        logger.info(f"Gemini AI synthesis successful: {synthesized_attributes}")
                        return synthesized_attributes
                    else:
                        logger.error(f"Gemini output missing required keys: {synthesized_attributes}")
                        return {"error": "Gemini output missing required keys", "identified_attributes": synthesized_attributes}
                except json.JSONDecodeError:
                    logger.warning("Failed to parse Gemini response as JSON")
                    return {"error": "Gemini response not valid JSON", "identified_attributes": {}}
            else:
                logger.error("Gemini model not available, cannot synthesize.")
                return {"error": "Gemini model not available", "identified_attributes": {}}
        except Exception as e:
            logger.error(f"AI synthesis failed: {e}")
            return {"error": f"Gemini synthesis failed: {e}", "identified_attributes": {}}

    def _synthesize_with_fallback(self, expert_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback synthesis when Gemini is not available.
        Uses simple heuristics to combine expert opinions.
        """
        logger.info("Using fallback synthesis (Gemini not available)")
        
        google_data = expert_outputs.get('google_vision', {})
        aws_data = expert_outputs.get('aws_rekognition', {})
        
        # Extract product name from Google web entities
        product_name = None
        brand = None
        if google_data.get('success') and google_data.get('web_entities'):
            top_entity = google_data['web_entities'][0]
            product_name = top_entity.get('description', '')
            
            # Try to extract brand from product name
            if product_name:
                words = product_name.split()
                if len(words) > 1:
                    brand = words[0]  # Simple heuristic
        
        # Extract category from objects
        category = None
        if google_data.get('success') and google_data.get('objects'):
            category = google_data['objects'][0].get('name', '')
        
        # Extract colors
        colors = []
        if google_data.get('success') and google_data.get('dominant_colors'):
            for color_info in google_data['dominant_colors'][:3]:
                color = color_info.get('color', {})
                if color:
                    # Simple color name mapping
                    r, g, b = color.get('red', 0), color.get('green', 0), color.get('blue', 0)
                    color_name = self._get_color_name(r, g, b)
                    if color_name:
                        colors.append(color_name)
        
        # Calculate confidence
        confidence = 0.5  # Base confidence
        if google_data.get('success'):
            confidence += 0.3
        if aws_data.get('success'):
            confidence += 0.2

        # Integrate CLIP/encoder description if available
        clip_data = expert_outputs.get('clip_encoder', {})
        clip_description = clip_data.get('description')
        if clip_description and isinstance(clip_description, str):
            if not product_name:
                product_name = clip_description

        return {
            "product_name": product_name,
            "brand": brand,
            "category": category,
            "sub_category": None,
            "attributes": [],
            "colors": colors,
            "confidence_score": min(confidence, 1.0),
            "ai_summary": f"Identified as {product_name or 'item'} in {category or 'unknown'} category",
            "expert_agreement": {
                "google_vision_confidence": 0.8 if google_data.get('success') else 0.0,
                "aws_rekognition_confidence": 0.7 if aws_data.get('success') else 0.0,
                "clip_encoder_confidence": clip_data.get('confidence', 0.0) if clip_data.get('success') else 0.0,
                "overall_agreement": confidence
            }
        }

        """Simple color name mapping."""
        # Basic color detection
        if r > 200 and g < 100 and b < 100:
            return "Red"
        elif r < 100 and g > 200 and b < 100:
            return "Green"
        elif r < 100 and g < 100 and b > 200:
            return "Blue"
        elif r > 200 and g > 200 and b < 100:
            return "Yellow"
        elif r > 200 and g < 100 and b > 200:
            return "Magenta"
        elif r < 100 and g > 200 and b > 200:
            return "Cyan"
        elif r > 200 and g > 200 and b > 200:
            return "White"
        elif r < 50 and g < 50 and b < 50:
            return "Black"
        elif r > 150 and g > 150 and b > 150:
            return "Gray"
        else:
            return None

def get_aggregator_service():
    """Global getter for easy, safe access to the service instance."""
    return AggregatorService()