import requests
import logging
from .ebay_auth import get_ebay_oauth_token, token_manager
from django.conf import settings
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class EbayService:
    """
    Centralized service for all eBay API interactions.
    Handles authentication, error handling, and logging.
    Easily extensible for new endpoints and features.
    """
    BASE_URL = "https://api.ebay.com/buy/browse/v1"
    DEFAULT_TIMEOUT = 15

    def __init__(self):
        self.auth_token = self._get_valid_token()
        if not self.auth_token:
            logger.warning("[EbayService] No valid eBay OAuth token available. eBay search will be disabled.")
            self.auth_token = None

    def get_completed_ebay_items(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetches recently SOLD listings from eBay for accurate price analysis.
        """
        logger.info(f"Searching for COMPLETED items on eBay with query: {query}")
        try:
            from ebaysdk.finding import Connection as Finding
            from django.conf import settings
            
            api = Finding(
                appid=settings.EBAY_PRODUCTION_APP_ID, 
                config_file=None,
                siteid='EBAY-US'
            )
            
            response = api.execute('findCompletedItems', {
                'keywords': query,
                'sortOrder': 'EndTimeSoonest',
                'paginationInput': {'entriesPerPage': str(limit)},
                'itemFilter': [{'name': 'SoldItemsOnly', 'value': 'true'}],
                'outputSelector': ['SellerInfo', 'PictureURLSuperSize', 'Condition']
            })

            if response.reply.ack == 'Success' and hasattr(response.reply.searchResult, 'item'):
                return self._parse_ebay_response(response.reply.searchResult.item)
            
            logger.error(f"eBay findCompletedItems call failed: {getattr(response.reply.errorMessage.error, 'message', 'Unknown Error')}")
            return []
        except Exception as e:
            logger.error(f"Exception during eBay findCompletedItems call: {e}", exc_info=True)
            return []

    def _parse_ebay_response(self, items: List[Any]) -> List[Dict[str, Any]]:
        """A helper to convert the raw SDK response into a clean list of dictionaries."""
        parsed_items = []
        for item in items:
            try:
                parsed_items.append({
                    'itemId': item.itemId,
                    'title': item.title,
                    'galleryURL': getattr(item, 'galleryURL', None),
                    'sellingStatus': {
                        'currentPrice': {
                            '__value__': item.sellingStatus.currentPrice.value
                        }
                    },
                    'condition': {
                        'conditionDisplayName': getattr(item.condition, 'conditionDisplayName', 'Not Specified')
                    } if hasattr(item, 'condition') else {'conditionDisplayName': 'Not Specified'},
                })
            except AttributeError:
                # Skip item if it's missing essential fields
                continue
        return parsed_items

# Global getter for the service
_ebay_service_instance = None
def get_ebay_service():
    global _ebay_service_instance
    if _ebay_service_instance is None:
        _ebay_service_instance = EbayService()
    return _ebay_service_instance
    """
    Centralized service for all eBay API interactions.
    Handles authentication, error handling, and logging.
    Easily extensible for new endpoints and features.
    """
    BASE_URL = "https://api.ebay.com/buy/browse/v1"
    DEFAULT_TIMEOUT = 15

    def __init__(self):
        self.auth_token = self._get_valid_token()
        if not self.auth_token:
            logger.warning("[EbayService] No valid eBay OAuth token available. eBay search will be disabled.")
            # Don't raise exception - just log warning and continue without eBay functionality
            self.auth_token = None

    def _get_valid_token(self) -> Optional[str]:
        # Use token_manager for auto-refresh
        try:
            token = token_manager.get_valid_token()
            if not token:
                logger.warning("[EbayService] Token manager returned no token, attempting manual refresh.")
                token_manager.force_refresh()
                token = token_manager.get_valid_token()
            return token
        except Exception as e:
            logger.error(f"[EbayService] Error getting eBay token: {e}")
            return None

    def get_headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            'Accept': 'application/json',
            'Content-Language': 'en-US',
        }
        
        # Only add Authorization header if we have a valid token
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
            headers['X-EBAY-C-MARKETPLACE-ID'] = 'EBAY_US'
        
        if extra:
            headers.update(extra)
        return headers

    def search_items(self, query: str, category_ids: Optional[str] = None, limit: int = 20, affiliate: bool = True, localization: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for item summaries on eBay. Handles affiliate links and localization if requested.
        """
        # If no auth token, return empty results
        if not self.auth_token:
            logger.warning(f"[EbayService] Cannot search eBay - no valid token available for query: '{query}'")
            return []
            
        endpoint = f"{self.BASE_URL}/item_summary/search"
        params = {'q': query, 'limit': limit}
        if category_ids:
            params['category_ids'] = category_ids
        headers = self.get_headers()
        if localization:
            headers['X-EBAY-C-ENDUSERCTX'] = f"contextualLocation=country={localization}"
        logger.info(f"[EbayService] Searching eBay with query: '{query}' params={params}")
        try:
            response = requests.get(endpoint, headers=headers, params=params, timeout=self.DEFAULT_TIMEOUT)
            if response.status_code == 401:
                logger.warning("[EbayService] Token expired, attempting refresh and retry.")
                self.auth_token = self._get_valid_token()
                if not self.auth_token:
                    logger.warning("[EbayService] Token refresh failed, returning empty results.")
                    return []
                headers = self.get_headers()
                response = requests.get(endpoint, headers=headers, params=params, timeout=self.DEFAULT_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            items = data.get('itemSummaries', [])
            logger.info(f"[EbayService] Found {len(items)} items for query: '{query}'")
            
            # Process items to extract imageUrl and add affiliate links
            processed_items = []
            for item in items:
                # Extract imageUrl from image object if it exists
                if item.get('image') and item['image'].get('imageUrl'):
                    item['imageUrl'] = item['image']['imageUrl']
                
                # Add affiliate link fallback if requested
                if affiliate and 'itemAffiliateWebUrl' not in item and 'itemWebUrl' in item:
                    item['itemAffiliateWebUrl'] = item['itemWebUrl']
                
                processed_items.append(item)
            
            return processed_items
        except requests.exceptions.RequestException as e:
            logger.error(f"[EbayService] Search request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"[EbayService] Unexpected error during search: {e}")
            return []

    # Example for future extensibility
    def get_item_details(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch details for a specific eBay item by item_id.
        """
        endpoint = f"{self.BASE_URL}/item/{item_id}"
        headers = self.get_headers()
        try:
            response = requests.get(endpoint, headers=headers, timeout=self.DEFAULT_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"[EbayService] Failed to fetch item details for {item_id}: {e}")
            return None 