"""
Vertex AI Service for Advanced ML Capabilities
Provides enhanced AI features using Google Cloud Vertex AI while maintaining
compatibility with the existing Gemini API approach.
"""
import logging
import os
from typing import Dict, Any, Optional, List
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
import google.generativeai as genai
import json

logger = logging.getLogger(__name__)

class VertexAIService:
    """
    Enhanced AI service using Google Cloud Vertex AI for advanced capabilities.
    Provides both Vertex AI and Gemini API options for maximum flexibility.
    """
    
    def __init__(self):
        self.project_id = "silent-polygon-465403-h9"  # From your service account
        self.location = "us-central1"  # Vertex AI region
        self.vertex_ai_available = False
        self.gemini_available = False
        
        # Initialize Vertex AI using existing Google Cloud credentials
        try:
            aiplatform.init(
                project=self.project_id,
                location=self.location,
            )
            self.vertex_ai_available = True
            logger.info("Vertex AI initialized successfully using existing Google Cloud credentials")
        except Exception as e:
            logger.warning(f"Vertex AI initialization failed: {e}")
        
        # Initialize Gemini API using existing Google Cloud credentials
        try:
            # Use the same service account for Gemini API
            genai.configure(
                ***REMOVED***=None,  # Will use service account credentials
                transport="rest"
            )
            generation_config = genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
            self.gemini_model = genai.GenerativeModel(
                'gemini-1.5-pro-latest',
                generation_config=generation_config
            )
            self.gemini_available = True
            logger.info("Gemini API initialized successfully using existing Google Cloud credentials")
        except Exception as e:
            logger.warning(f"Gemini API initialization failed: {e}")
    
    def synthesize_expert_opinions(self, expert_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize expert opinions using the best available AI service.
        Prioritizes Vertex AI if available, falls back to Gemini API.
        """
        if self.vertex_ai_available:
            return self._synthesize_with_vertex_ai(expert_outputs)
        elif self.gemini_available:
            return self._synthesize_with_gemini(expert_outputs)
        else:
            logger.error("No AI synthesis service available")
            return self._fallback_synthesis(expert_outputs)
    
    def _synthesize_with_vertex_ai(self, expert_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Vertex AI for advanced synthesis with custom model capabilities.
        """
        try:
            # For now, we'll use Vertex AI's text generation endpoint
            # In the future, you could deploy custom models here
            
            # Create a prompt for Vertex AI
            prompt = self._build_vertex_ai_prompt(expert_outputs)
            
            # Use Vertex AI's text generation
            # Note: This is a simplified implementation
            # In production, you'd deploy a custom model for this task
            
            # For now, fall back to Gemini API if available
            if self.gemini_available:
                logger.info("Using Gemini API for synthesis (Vertex AI custom model not deployed)")
                return self._synthesize_with_gemini(expert_outputs)
            else:
                logger.warning("Vertex AI custom model not available, using fallback")
                return self._fallback_synthesis(expert_outputs)
                
        except Exception as e:
            logger.error(f"Vertex AI synthesis failed: {e}")
            # Fall back to Gemini API
            if self.gemini_available:
                return self._synthesize_with_gemini(expert_outputs)
            else:
                return self._fallback_synthesis(expert_outputs)
    
    def _synthesize_with_gemini(self, expert_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Gemini API for synthesis (current implementation).
        """
        try:
            prompt = self._build_gemini_prompt(expert_outputs)
            response = self.gemini_model.generate_content(prompt)
            synthesized_attributes = json.loads(response.text)
            logger.info(f"Gemini synthesis successful: {synthesized_attributes}")
            return synthesized_attributes
        except Exception as e:
            logger.error(f"Gemini synthesis failed: {e}")
            return self._fallback_synthesis(expert_outputs)
    
    def _build_vertex_ai_prompt(self, expert_outputs: Dict[str, Any]) -> str:
        """
        Build a prompt optimized for Vertex AI's capabilities.
        """
        google_data = expert_outputs.get('google_vision', {})
        aws_data = expert_outputs.get('aws_rekognition', {})
        
        prompt = f"""
You are an advanced AI expert for fashion resale and product identification, powered by Google Cloud Vertex AI. Your task is to analyze the following raw JSON data from multiple AI vision services and synthesize all available information into a single, high-confidence set of attributes for the item.

**Advanced Analysis Instructions:**
1. **Multi-Modal Synthesis**: Combine visual, textual, and semantic information from all sources
2. **Confidence Calibration**: Use advanced statistical methods to calculate confidence scores
3. **Attribute Hierarchy**: Prioritize specific, branded information over generic labels
4. **Cross-Validation**: Verify information across multiple AI services
5. **Market Context**: Consider current fashion trends and market dynamics
6. **Output Format**: Return ONLY a single, valid JSON object with the specified schema

**AI Data Sources:**
```json
{json.dumps(expert_outputs, indent=2)}
```

**Required JSON Output Schema:**
{{
  "product_name": "String | null",
  "brand": "String | null", 
  "category": "String | null",
  "sub_category": "String | null",
  "attributes": ["String", ...],
  "colors": ["String", ...],
  "confidence_score": "Float (0.0-1.0)",
  "ai_summary": "A brief, one-sentence summary for the user.",
  "expert_agreement": {{
    "google_vision_confidence": "Float (0.0-1.0)",
    "aws_rekognition_confidence": "Float (0.0-1.0)",
    "overall_agreement": "Float (0.0-1.0)"
  }},
  "market_insights": {{
    "trending": "Boolean",
    "seasonality": "String | null",
    "price_category": "String | null"
  }}
}}

**Advanced Analysis Guidelines:**
- Use Vertex AI's advanced reasoning capabilities for complex synthesis
- Apply statistical confidence intervals for reliability assessment
- Consider temporal market dynamics and seasonal trends
- Leverage cross-modal information fusion for higher accuracy
- Implement uncertainty quantification for robust decision making
"""
        
        return prompt
    
    def _build_gemini_prompt(self, expert_outputs: Dict[str, Any]) -> str:
        """
        Build a prompt for Gemini API (current implementation).
        """
        google_data = expert_outputs.get('google_vision', {})
        aws_data = expert_outputs.get('aws_rekognition', {})
        
        prompt = f"""
You are a world-class AI expert for fashion resale. Your task is to analyze the following raw JSON data from two separate AI vision services (Google Vision and AWS Rekognition) and synthesize all available information into a single, high-confidence set of attributes for the item.

**Instructions:**
1. **Prioritize Google's `web_entities`**: This is your most reliable signal for the specific `product_name` and `brand`.
2. **Use AWS `labels` and Google `objects`**: These confirm the general `category` (e.g., "Sneakers", "Hoodie").
3. **Analyze text from both services**: Extract brand names, model numbers, and other specific details from OCR results.
4. **Infer secondary attributes**: Based on all data, infer attributes like `style`, `sport`, `material`, `era`, etc.
5. **Calculate confidence scores**: Provide confidence scores based on agreement between services and data quality.
6. **Output Format**: You must return ONLY a single, valid JSON object with the specified schema and nothing else.

**AI Data:**
```json
{json.dumps(expert_outputs, indent=2)}
```

**Your Required JSON Output Schema:**
{{
  "product_name": "String | null",
  "brand": "String | null", 
  "category": "String | null",
  "sub_category": "String | null",
  "attributes": ["String", ...],
  "colors": ["String", ...],
  "confidence_score": "Float (0.0-1.0)",
  "ai_summary": "A brief, one-sentence summary for the user.",
  "expert_agreement": {{
    "google_vision_confidence": "Float (0.0-1.0)",
    "aws_rekognition_confidence": "Float (0.0-1.0)",
    "overall_agreement": "Float (0.0-1.0)"
  }}
}}

**Analysis Guidelines:**
- If Google web entities suggest a specific product (e.g., "Nike Air Jordan 1"), use that as the primary product_name
- If AWS labels confirm the category (e.g., "Shoe" from AWS + "Sneaker" from Google), use the more specific one
- Extract brand names from text annotations and web entities
- Use dominant colors to identify color attributes
- Calculate confidence based on agreement between services and data quality
- If services disagree significantly, lower the confidence score
- Always prioritize specific, branded information over generic labels
"""
        
        return prompt
    
    def _fallback_synthesis(self, expert_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback synthesis when no AI service is available.
        """
        logger.warning("Using fallback synthesis (no AI service available)")
        
        google_data = expert_outputs.get('google_vision', {})
        aws_data = expert_outputs.get('aws_rekognition', {})
        
        # Simple heuristic-based synthesis
        product_name = None
        brand = None
        if google_data.get('success') and google_data.get('web_entities'):
            top_entity = google_data['web_entities'][0]
            product_name = top_entity.get('description', '')
            
            if product_name:
                words = product_name.split()
                if len(words) > 1:
                    brand = words[0]
        
        category = None
        if google_data.get('success') and google_data.get('objects'):
            category = google_data['objects'][0].get('name', '')
        
        confidence = 0.5
        if google_data.get('success'):
            confidence += 0.3
        if aws_data.get('success'):
            confidence += 0.2
        
        return {
            "product_name": product_name,
            "brand": brand,
            "category": category,
            "sub_category": None,
            "attributes": [],
            "colors": [],
            "confidence_score": min(confidence, 1.0),
            "ai_summary": f"Identified as {product_name or 'item'} in {category or 'unknown'} category",
            "expert_agreement": {
                "google_vision_confidence": 0.8 if google_data.get('success') else 0.0,
                "aws_rekognition_confidence": 0.7 if aws_data.get('success') else 0.0,
                "overall_agreement": confidence
            }
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get the status of available AI services.
        """
        return {
            "vertex_ai_available": self.vertex_ai_available,
            "gemini_available": self.gemini_available,
            "project_id": self.project_id,
            "location": self.location,
            "recommended_service": "vertex_ai" if self.vertex_ai_available else "gemini" if self.gemini_available else "fallback"
        }

def get_vertex_ai_service():
    """Global getter for easy, safe access to the service instance."""
    return VertexAIService() 