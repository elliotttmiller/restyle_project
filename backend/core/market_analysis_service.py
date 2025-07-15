"""
Enhanced Market Analysis Service
Uses synthesized attributes from the AggregatorService to build intelligent search queries
and perform visual re-ranking of marketplace results.
"""
import logging
logger = logging.getLogger(__name__)

import requests
import numpy as np
from typing import Dict, Any, List, Optional
from .aggregator_service import get_aggregator_service

# Try to import encoder_service, but make it optional
try:
    from .encoder_service import get_encoder_service
    ENCODER_AVAILABLE = True
except ImportError:
    ENCODER_AVAILABLE = False
    logger.warning("EncoderService not available - visual similarity ranking will be disabled")


class MarketAnalysisService:
    """
    Enhanced market analysis service that builds intelligent search queries
    and performs visual re-ranking of marketplace results.
    """
    
    def __init__(self):
        self.aggregator = get_aggregator_service()
        if ENCODER_AVAILABLE:
            self.encoder = get_encoder_service()
        else:
            self.encoder = None
        
    def run_complete_analysis(self, image_data: bytes, marketplace_api_func) -> Dict[str, Any]:
        """
        Complete market analysis pipeline: AI identification + market search + visual re-ranking.
        
        Args:
            image_data: Raw image bytes
            marketplace_api_func: Function that takes a query and returns marketplace results
            
        Returns:
            Complete analysis with identified attributes, market query, and ranked comps
        """
        logger.info("Starting complete market analysis pipeline...")
        
        # Step 1: Multi-expert AI identification
        identified_attributes = self.aggregator.run_full_analysis(image_data)
        
        if "error" in identified_attributes:
            logger.error(f"AI identification failed: {identified_attributes['error']}")
            return {
                "error": "Failed to identify item from image",
                "identified_attributes": identified_attributes
            }
        
        # Step 2: Build intelligent market query
        market_query = self._build_intelligent_query(identified_attributes)
        logger.info(f"Built market query: '{market_query}'")
        
        # Step 3: Search marketplace
        initial_comps = marketplace_api_func(market_query)
        if not initial_comps:
            logger.warning(f"No marketplace results found for query: {market_query}")
            return {
                "identified_attributes": identified_attributes,
                "market_query_used": market_query,
                "visually_ranked_comps": [],
                "search_success": False
            }
        
        # Step 4: Visual re-ranking
        logger.info(f"Visually re-ranking {len(initial_comps)} marketplace results...")
        ranked_comps = self._find_visual_comps(image_data, initial_comps)
        
        # Step 5: Compile final results
        return {
            "identified_attributes": identified_attributes,
            "market_query_used": market_query,
            "visually_ranked_comps": ranked_comps,
            "search_success": True,
            "analysis_summary": {
                "total_comps_found": len(initial_comps),
                "comps_with_visual_scores": len([c for c in ranked_comps if 'visual_similarity_score' in c]),
                "confidence_score": identified_attributes.get('confidence_score', 0.0),
                "expert_agreement": identified_attributes.get('expert_agreement', {})
            }
        }
    
    def _build_intelligent_query(self, attributes: Dict[str, Any]) -> str:
        """
        Builds an intelligent search query from synthesized attributes.
        Prioritizes the most specific and high-confidence attributes.
        """
        query_parts = []
        
        # Priority 1: Brand (highest confidence)
        brand = attributes.get('brand')
        if brand and brand != 'Unknown':
            query_parts.append(brand)
        
        # Priority 2: Product name (specific model)
        product_name = attributes.get('product_name')
        if product_name and product_name != 'Unknown':
            # Clean up product name (remove brand if already included)
            if brand and brand in product_name:
                clean_product = product_name.replace(brand, '').strip()
                if clean_product:
                    query_parts.append(clean_product)
            else:
                query_parts.append(product_name)
        
        # Priority 3: Category
        category = attributes.get('category')
        if category and category != 'Unknown':
            query_parts.append(category)
        
        # Priority 4: Colors (if available)
        colors = attributes.get('colors', [])
        if colors:
            # Use the most prominent color
            primary_color = colors[0] if colors else None
            if primary_color:
                query_parts.append(primary_color)
        
        # Priority 5: Key attributes
        key_attributes = attributes.get('attributes', [])
        if key_attributes:
            # Add the most relevant attributes (limit to 2)
            relevant_attrs = [attr for attr in key_attributes if len(attr) > 2][:2]
            query_parts.extend(relevant_attrs)
        
        # Build final query
        query = ' '.join(query_parts)
        
        # Clean up the query
        query = ' '.join(query.split())  # Remove extra spaces
        query = query.strip()
        
        logger.info(f"Built query from attributes: {query_parts} -> '{query}'")
        return query
    
    def _find_visual_comps(self, user_image_data: bytes, initial_comps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Re-ranks marketplace results by visual similarity to the user's image.
        This is the "secret sauce" that ensures results actually look like the user's item.
        """
        if not self.encoder:
            logger.warning("Encoder not available; returning comps without visual ranking.")
            return initial_comps
            
        user_image_vector = self.encoder.encode_image(user_image_data)
        if user_image_vector is None:
            logger.warning("Could not encode user image; returning comps without visual ranking.")
            return initial_comps
        
        ranked_results = []
        processed_count = 0
        
        for comp in initial_comps:
            try:
                # Extract image URL from comp
                image_url = self._extract_image_url(comp)
                if not image_url:
                    logger.debug(f"No image URL found for comp {comp.get('itemId', 'unknown')}")
                    continue
                
                # Download and encode the marketplace item's image
                comp_image_vector = self._download_and_encode_image(image_url)
                if comp_image_vector is not None:
                    # Calculate cosine similarity
                    similarity = np.dot(user_image_vector, comp_image_vector)
                    comp['visual_similarity_score'] = round(float(similarity), 4)
                    ranked_results.append(comp)
                    processed_count += 1
                else:
                    logger.debug(f"Could not encode comp image for {comp.get('itemId', 'unknown')}")
                    
            except Exception as e:
                logger.warning(f"Error processing comp image for item {comp.get('itemId', 'unknown')}: {e}")
                continue
        
        logger.info(f"Successfully processed {processed_count}/{len(initial_comps)} comp images for visual ranking")
        
        # Sort by visual similarity score (highest first)
        ranked_results.sort(key=lambda x: x.get('visual_similarity_score', 0), reverse=True)
        
        return ranked_results
    
    def _extract_image_url(self, comp: Dict[str, Any]) -> Optional[str]:
        """Extracts image URL from various marketplace result formats."""
        # Try different possible image URL fields
        image_fields = ['image', 'imageUrl', 'pictureURLSuperSize', 'galleryURL']
        
        for field in image_fields:
            if field in comp:
                image_data = comp[field]
                if isinstance(image_data, dict):
                    # Handle nested image objects
                    for url_field in ['imageUrl', 'url', 'link']:
                        if url_field in image_data:
                            return image_data[url_field]
                elif isinstance(image_data, str):
                    return image_data
        
        return None
    
    def _download_and_encode_image(self, image_url: str) -> Optional[np.ndarray]:
        """Downloads and encodes an image from URL."""
        try:
            response = requests.get(image_url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Read image data
            image_data = response.content
            
            # Encode using our CLIP model
            return self.encoder.encode_image(image_data)
            
        except Exception as e:
            logger.debug(f"Failed to download/encode image from {image_url}: {e}")
            return None
    
    def analyze_price_trends(self, ranked_comps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes price trends from the ranked comps.
        """
        if not ranked_comps:
            return {
                "price_analysis": "No comparable items found",
                "price_range": None,
                "suggested_price": None,
                "confidence": "low"
            }
        
        # Extract prices
        prices = []
        for comp in ranked_comps:
            price = self._extract_price(comp)
            if price and price > 0:
                prices.append(price)
        
        if not prices:
            return {
                "price_analysis": "No valid prices found in comparable items",
                "price_range": None,
                "suggested_price": None,
                "confidence": "low"
            }
        
        # Calculate price statistics
        prices.sort()
        min_price = prices[0]
        max_price = prices[-1]
        median_price = prices[len(prices) // 2]
        avg_price = sum(prices) / len(prices)
        
        # Calculate confidence based on number of comps and price consistency
        price_variance = np.var(prices) if len(prices) > 1 else 0
        price_consistency = 1.0 / (1.0 + price_variance / (avg_price ** 2)) if avg_price > 0 else 0
        
        confidence = min(0.9, 0.3 + 0.4 * price_consistency + 0.2 * min(len(prices) / 10, 1.0))
        
        return {
            "price_analysis": f"Based on {len(prices)} comparable items",
            "price_range": {
                "min": min_price,
                "max": max_price,
                "median": median_price,
                "average": avg_price
            },
            "suggested_price": median_price,  # Use median as suggested price
            "confidence": confidence,
            "num_comps": len(prices),
            "price_consistency": price_consistency
        }
    
    def _extract_price(self, comp: Dict[str, Any]) -> Optional[float]:
        """Extracts price from various marketplace result formats."""
        # Try different price fields
        price_fields = ['price', 'currentPrice', 'sellingStatus', 'convertedCurrentPrice']
        
        for field in price_fields:
            if field in comp:
                price_data = comp[field]
                if isinstance(price_data, dict):
                    # Handle nested price objects
                    for price_key in ['value', 'amount', 'price']:
                        if price_key in price_data:
                            try:
                                return float(price_data[price_key])
                            except (ValueError, TypeError):
                                continue
                elif isinstance(price_data, (int, float)):
                    return float(price_data)
                elif isinstance(price_data, str):
                    try:
                        # Remove currency symbols and convert
                        clean_price = ''.join(c for c in price_data if c.isdigit() or c == '.')
                        return float(clean_price)
                    except ValueError:
                        continue
        
        return None

def get_market_analysis_service():
    """Global getter for easy, safe access to the service instance."""
    return MarketAnalysisService() 