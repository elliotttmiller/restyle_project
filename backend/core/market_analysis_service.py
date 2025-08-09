# backend/core/market_analysis_service.py
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from .aggregator_service import get_aggregator_service
from .services import get_ebay_service

logger = logging.getLogger(__name__)

class MarketAnalysisService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarketAnalysisService, cls).__new__(cls)
        return cls._instance
    
    def run_ai_statistical_analysis(self, image_data: bytes) -> Dict[str, Any]:
        """The main entry point for the new AI-Enhanced Statistical analysis."""
        aggregator = get_aggregator_service()
        ebay_service = get_ebay_service()

        identified_attributes = aggregator.run_full_analysis(image_data)
        if "error" in identified_attributes:
            return {"error": "AI identification failed", "identified_attributes": identified_attributes}

        query_strategy = self._build_adaptive_query_strategy(identified_attributes)
        sold_comps, query_used = self._search_marketplace(query_strategy, ebay_service.get_completed_ebay_items)

        if not sold_comps:
            return {
                "identified_attributes": identified_attributes,
                "error": "No recently sold comparable items found.", 
                "market_query_used": query_used
            }
        

        # --- Visual Similarity Integration ---
        try:
            from .encoder_service import get_encoder_service
            encoder = get_encoder_service()
            input_embedding = encoder.encode_image_from_data(image_data)
            if input_embedding is not None:
                for comp in sold_comps:
                    img_url = comp.get('galleryURL')
                    if not img_url:
                        comp['visual_similarity_score'] = 0.5  # fallback default
                        continue
                    comp_embedding = encoder.encode_image_from_url(img_url)
                    if comp_embedding is not None:
                        # Cosine similarity
                        sim = float(np.dot(input_embedding, comp_embedding) / (np.linalg.norm(input_embedding) * np.linalg.norm(comp_embedding)))
                        # Normalize to [0,1]
                        sim_norm = (sim + 1) / 2
                        comp['visual_similarity_score'] = sim_norm
                    else:
                        comp['visual_similarity_score'] = 0.5
        except Exception as e:
            logger.error(f"Visual similarity integration failed: {e}")
            for comp in sold_comps:
                comp['visual_similarity_score'] = 0.5

        statistical_analysis = self._run_statistical_analysis(sold_comps)
        final_recommendation = self._synthesize_price_recommendation(statistical_analysis, identified_attributes)

        return {
            "identified_attributes": identified_attributes,
            "market_query_used": query_used,
            "statistical_analysis": statistical_analysis,
            "final_recommendation": final_recommendation,
        }

    def _build_adaptive_query_strategy(self, attributes: Dict[str, Any]) -> List[str]:
        strategy, base_query = [], attributes.get('product_name', '')
        if not base_query: return []
        strategy.append(base_query)
        if len(base_query.split()) > 2:
            strategy.append(' '.join(base_query.split()[:2]))
        return list(dict.fromkeys(strategy))

    from typing import Tuple
    def _search_marketplace(self, query_strategy: List[str], api_func) -> Tuple[List[Dict[str, Any]], str]:
        for query in query_strategy:
            results = api_func(query=query, limit=100)
            if len(results) >= 5: return results, query
        return [], query_strategy[-1] if query_strategy else ""

    def _run_statistical_analysis(self, sold_comps: List[Dict[str, Any]]) -> Dict[str, Any]:
        comps_by_condition = {'New': [], 'Used': []}
        for comp in sold_comps:
            condition = (comp.get('condition', {}).get('conditionDisplayName') or 'Used').lower()
            price = self._extract_price(comp)
            if not price: continue
            comp_data = {'price': price, 'comp': comp}
            if 'new' in condition: comps_by_condition['New'].append(comp_data)
            else: comps_by_condition['Used'].append(comp_data)

        analysis = {'by_condition': {}}
        for condition, items in comps_by_condition.items():
            if len(items) < 3: continue
            prices = [item['price'] for item in items]
            
            Q1, Q3 = np.percentile(prices, 25), np.percentile(prices, 75)
            IQR = Q3 - Q1
            inliers_data = [item for item in items if (Q1 - 1.5 * IQR) <= item['price'] <= (Q3 + 1.5 * IQR)]
            if not inliers_data: continue
            
            inlier_prices = [item['price'] for item in inliers_data]
            # Assumes visual_similarity_score is added in a previous step
            inlier_weights = [(item['comp'].get('visual_similarity_score', 0.5)**2) + 0.01 for item in inliers_data]

            analysis['by_condition'][condition] = {
                'num_comps': len(inlier_prices),
                'price_range': (min(inlier_prices), max(inlier_prices)),
                'weighted_mean_price': round(np.average(inlier_prices, weights=inlier_weights), 2),
                'std_dev': round(np.std(inlier_prices), 2),
            }
        return analysis

    def _synthesize_price_recommendation(self, stats: Dict, attributes: Dict) -> Dict:
        ai_condition = attributes.get("item_condition", "Used").capitalize()
        primary_stats = stats.get('by_condition', {}).get(ai_condition)
        
        if not primary_stats:
            raise ValueError(f"Could not determine a reliable price due to lack of data for the item's condition: {ai_condition}")

        base_price = primary_stats['weighted_mean_price']
        adjustment_factor_raw = attributes.get('market_sentiment_score', 1.0)
        try:
            adjustment_factor = float(adjustment_factor_raw)
        except (TypeError, ValueError):
            logger.warning(f"Invalid market_sentiment_score: {adjustment_factor_raw}, defaulting to 1.0")
            adjustment_factor = 1.0
        final_price = base_price * adjustment_factor
        
        price_std_dev = primary_stats.get('std_dev', 20)
        low_end = round(final_price - price_std_dev, 2)
        high_end = round(final_price + price_std_dev, 2)
        
        summary = f"For a '{ai_condition}' item, our AI suggests a price of around ${round(final_price, 2)}. Based on market data, a realistic range is ${low_end} - ${high_end}."

        return {
            "suggested_price": round(final_price, 2),
            "suggested_price_range": (low_end, high_end),
            "summary": summary,
            "confidence": "High" if primary_stats['num_comps'] > 10 else "Medium"
        }

    def _extract_price(self, comp: Dict[str, Any]) -> Optional[float]:
        price_str = comp.get('sellingStatus', {}).get('currentPrice', {}).get('__value__')
        return float(price_str) if price_str else None

# Global getter for the service
from functools import lru_cache

@lru_cache(maxsize=1)
def get_market_analysis_service():
    return MarketAnalysisService()