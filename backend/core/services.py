# backend/core/services.py
import requests
import logging
from django.conf import settings
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class EbayService:
    """
    Centralized service for eBay API interactions.
    This version focuses on the Finding API for sold item searches.
    """
    def get_completed_ebay_items(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetches recently SOLD listings from eBay for accurate price analysis."""
        logger.info(f"Searching for COMPLETED items on eBay with query: {query}")
        try:
            from ebaysdk.finding import Connection as Finding
            
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
            
            error_message = "Unknown Error"
            if hasattr(response.reply, 'errorMessage') and hasattr(response.reply.errorMessage, 'error'):
                error_message = response.reply.errorMessage.error.message
            logger.error(f"eBay findCompletedItems call failed: {error_message}")
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
            except (AttributeError, KeyError):
                continue
        return parsed_items

# Global getter for the service
_ebay_service_instance = None
def get_ebay_service():
    global _ebay_service_instance
    if _ebay_service_instance is None:
        _ebay_service_instance = EbayService()
    return _ebay_service_instance