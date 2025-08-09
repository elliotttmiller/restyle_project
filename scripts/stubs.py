# Stub implementations for missing dependencies

# Stub for tasks.py
def create_ebay_listing(*args, **kwargs):
    return {"status": "error", "message": "eBay listing functionality not available - celery not installed"}

def perform_market_analysis(*args, **kwargs):
    return {"status": "error", "message": "Market analysis functionality not available - celery not installed"}


# Stub for ai_service.py  
def get_ai_service():
    return None

class MockAIService:
    def analyze_image(self, *args, **kwargs):
        return {"status": "error", "message": "AI services not available - dependencies not installed"}
    
    def search_similar(self, *args, **kwargs):
        return {"status": "error", "message": "AI services not available - dependencies not installed"}

# Stub for services.py
class EbayServiceStub:
    def __init__(self):
        pass
        
    def search(self, *args, **kwargs):
        return {"status": "error", "message": "eBay services not available - dependencies not installed"}
        
    def search_items(self, query, category_ids=None, limit=20, **kwargs):
        return {"status": "error", "message": "eBay services not available - dependencies not installed"}
        
    def get_token_info(self):
        return {"status": "error", "message": "eBay token info not available - dependencies not installed"}

# Stub for market_analysis_service.py
def get_market_analysis_service():
    return None

class MockMarketAnalysisService:
    def analyze(self, *args, **kwargs):
        return {"status": "error", "message": "Market analysis not available - dependencies not installed"}