# File: backend/core/views.py

# pyright: reportAttributeAccessIssue=false

from rest_framework import generics, permissions, serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ItemSerializer, ListingSerializer, MarketAnalysisSerializer
from .models import Item, Listing, MarketAnalysis # We need MarketAnalysis for the view
from .models import Item, MarketAnalysis

# Try to import real modules, fall back to stubs if not available
try:
    from .tasks import create_ebay_listing, perform_market_analysis
except ImportError:
    from .stubs import create_ebay_listing, perform_market_analysis

try:
    from .ai_service import get_ai_service
except ImportError:
    from .stubs import get_ai_service

try:
    from .services import EbayService
except ImportError:
    from .stubs import EbayService

try:
    from .market_analysis_service import get_market_analysis_service
except ImportError:
    from .stubs import get_market_analysis_service

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
import requests
from django.conf import settings
import logging
from django.core.cache import cache
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import base64
import os
import traceback
from django.http import JsonResponse

logger = logging.getLogger(__name__)

# --- Lazy AI/ML client initialization ---
import os
import logging

# Global client instances (lazy initialization)
_vision_client = None
_rekognition_client = None
_gemini_model = None
_vertex_endpoint = None

def get_vision_client():
    """Lazy initialization of Google Vision client"""
    global _vision_client
    if _vision_client is None:
        try:
            from google.cloud import vision
            _vision_client = vision.ImageAnnotatorClient()
            logging.info("Google Vision client initialized successfully")
        except Exception as e:
            logging.warning(f"Google Vision client initialization failed: {e}")
            return None
    return _vision_client

def get_rekognition_client():
    """Lazy initialization of AWS Rekognition client"""
    global _rekognition_client
    if _rekognition_client is None:
        try:
            import boto3
            _rekognition_client = boto3.client('rekognition')
            logging.info("AWS Rekognition client initialized successfully")
        except Exception as e:
            logging.warning(f"AWS Rekognition client initialization failed: {e}")
            return None
    return _rekognition_client

def get_gemini_model():
    """Lazy initialization of Gemini model"""
    global _gemini_model
    if _gemini_model is None:
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.environ.get('GOOGLE_AI_API_KEY'))
            _gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            logging.info("Gemini model initialized successfully")
        except Exception as e:
            logging.warning(f"Gemini model initialization failed: {e}")
            return None
    return _gemini_model

# Safe import for psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not available - system metrics will be unavailable")

# Views start here
def health_check(request):
    # Test if we can import the real services or if we're using stubs
    service_status = {}
    
    try:
        from .services import EbayService
        ebay_service = EbayService()
        service_status['ebay_service'] = 'real'
    except ImportError:
        from .stubs import EbayService
        service_status['ebay_service'] = 'stub'
    except Exception as e:
        service_status['ebay_service'] = f'error: {str(e)}'
    
    try:
        from .ai_service import get_ai_service
        ai_service = get_ai_service()
        service_status['ai_service'] = 'real' if ai_service else 'null'
    except ImportError:
        service_status['ai_service'] = 'stub'
    except Exception as e:
        service_status['ai_service'] = f'error: {str(e)}'
    
    return JsonResponse({
        "status": "healthy",
        "service": "core",
        "timestamp": datetime.now().isoformat(),
        "services": service_status
    })

def ai_status(request):
    """Check AI service status with graceful degradation"""
    status = {
        "vision_client": get_vision_client() is not None,
        "rekognition_client": get_rekognition_client() is not None, 
        "gemini_model": get_gemini_model() is not None,
        "ai_service": get_ai_service() is not None
    }
    
    overall_status = "available" if any(status.values()) else "unavailable"
    
    return JsonResponse({
        "status": overall_status,
        "services": status,
        "timestamp": datetime.now().isoformat()
    })

def performance_metrics(request):
    """System performance metrics with graceful degradation"""
    metrics = {"status": "ok"}
    
    if PSUTIL_AVAILABLE:
        try:
            metrics.update({
                "cpu_usage": f"{psutil.cpu_percent()}%",
                "memory_usage": f"{psutil.virtual_memory().percent}%",
                "disk_usage": f"{psutil.disk_usage('/').percent}%"
            })
        except Exception as e:
            metrics["error"] = f"Failed to get system metrics: {str(e)}"
    else:
        metrics["note"] = "System metrics unavailable - psutil not installed"
    
    metrics["timestamp"] = datetime.now().isoformat()
    return JsonResponse(metrics)

def root_view(request):
    return JsonResponse({
        "status": "healthy",
        "message": "Core API is running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/api/core/health/",
            "ebay_search": "/api/core/ebay-search/",
            "ai_search": "/api/core/ai/advanced-search/",
            "metrics": "/api/core/metrics/"
        }
    })

# --- eBay Search Views ---
class EbaySearchView(APIView):
    logger.error('[DEBUG] EbaySearchView: class loaded')
    permission_classes = [AllowAny]  # Temporarily remove auth requirement for testing
    
    def get(self, request):
        logger.error(f"[DEBUG] EbaySearchView: HEADERS: {dict(request.headers)}")
        logger.error(f"[DEBUG] EbaySearchView: request.user={request.user}, request.auth={request.auth}")
        # Collect all supported query params
        params = {}
        for key in [
            'q', 'category_ids', 'filter', 'limit', 'offset', 'sort', 'fieldgroups', 'aspect_filter', 'compatibility_filter'
        ]:
            value = request.GET.get(key)
            if value is not None:
                params[key] = value
        
        logger.error(f"[DEBUG] EbaySearchView: Extracted params: {params}")
        
        try:
            ebay_service = EbayService()
            
            # Extract specific parameters for the search_items method
            query = params.get('q', '')
            category_ids = params.get('category_ids')
            limit = int(params.get('limit', 20))
            
            if not query:
                return Response({
                    "status": "error",
                    "message": "Query parameter 'q' is required"
                }, status=400)
            
            results = ebay_service.search_items(
                query=query, 
                category_ids=category_ids, 
                limit=limit
            )
            
            # If results is a dict with error status, it's likely from the stub
            if isinstance(results, dict) and results.get("status") == "error":
                # This is a stub response
                return Response({
                    "status": "error", 
                    "message": results.get("message", "eBay service unavailable"),
                    "results": [],
                    "debug": "eBay SDK not available - this is a placeholder response"
                }, status=503)
            
            return Response({
                "status": "success",
                "results": results,
                "params": params
            })
            
        except Exception as e:
            logger.error(f"[ERROR] EbaySearchView: Exception occurred: {str(e)}")
            logger.error(f"[ERROR] EbaySearchView: Traceback: {traceback.format_exc()}")
            return Response({
                "status": "error",
                "message": f"eBay search failed: {str(e)}",
                "debug": traceback.format_exc()
            }, status=500)

class AdvancedMultiExpertAISearchView(APIView):
    """
    Advanced multi-expert AI search endpoint with detailed debug logging.
    Accepts 'intelligent_crop' boolean flag (default: True).
    """
    permission_classes = [AllowAny]
    
    def __init__(self):
        super().__init__()
        import logging
        self.logger = logging.getLogger("advanced_ai_search_debug")

    def post(self, request):
        try:
            self.logger.info("=== Advanced Multi-Expert AI Search ===")
            
            # Get the AI service
            ai_service = get_ai_service()
            if ai_service is None:
                return Response({
                    "status": "error",
                    "message": "AI services not available - dependencies not installed",
                    "debug": "AI service initialization failed"
                }, status=503)
            
            # Extract request data
            data = request.data
            image_data = data.get('image')
            intelligent_crop = data.get('intelligent_crop', True)
            
            if not image_data:
                return Response({
                    "status": "error", 
                    "message": "No image data provided"
                }, status=400)
            
            self.logger.info(f"Processing image with intelligent_crop={intelligent_crop}")
            
            # Process the image (this would call the real AI service)
            try:
                results = ai_service.analyze_image(image_data, intelligent_crop=intelligent_crop)
                
                if isinstance(results, dict) and results.get("status") == "error":
                    # This is a stub response
                    return Response({
                        "status": "error",
                        "message": results.get("message", "AI analysis unavailable"),
                        "debug": "AI dependencies not installed - this is a placeholder response"
                    }, status=503)
                
                return Response({
                    "status": "success",
                    "results": results,
                    "intelligent_crop_used": intelligent_crop
                })
                
            except Exception as e:
                self.logger.error(f"AI analysis failed: {str(e)}")
                return Response({
                    "status": "error",
                    "message": f"AI analysis failed: {str(e)}",
                    "debug": traceback.format_exc()
                }, status=500)
                
        except Exception as e:
            self.logger.error(f"Advanced AI search failed: {str(e)}")
            return Response({
                "status": "error",
                "message": f"Search failed: {str(e)}",
                "debug": traceback.format_exc()
            }, status=500)

# Placeholder views for other endpoints that were in original
class ItemListCreateView(APIView):
    def get(self, request):
        return Response({"message": "Items endpoint working - full functionality not yet restored"})

class ItemDetailView(APIView):  
    def get(self, request, pk):
        return Response({"message": f"Item {pk} endpoint working - full functionality not yet restored"})

class ListingListCreateView(APIView):
    def get(self, request, item_pk):
        return Response({"message": f"Listings for item {item_pk} endpoint working - full functionality not yet restored"})

class ListingDetailView(APIView):
    def get(self, request, pk):
        return Response({"message": f"Listing {pk} endpoint working - full functionality not yet restored"})

class TriggerAnalysisView(APIView):
    def post(self, request, pk):
        try:
            # Try to trigger analysis
            result = perform_market_analysis(pk)
            
            if isinstance(result, dict) and result.get("status") == "error":
                return Response({
                    "status": "error",
                    "message": result.get("message", "Analysis unavailable"),
                    "debug": "Analysis dependencies not installed"
                }, status=503)
            
            return Response({
                "status": "success",
                "message": f"Analysis triggered for item {pk}",
                "result": result
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Analysis trigger failed: {str(e)}"
            }, status=500)

class AnalysisStatusView(APIView):
    def get(self, request, pk):
        return Response({
            "status": "pending", 
            "message": f"Analysis status for item {pk} - full functionality not yet restored"
        })

class EbayTokenHealthView(APIView):
    def get(self, request):
        try:
            ebay_service = EbayService()
            token_info = ebay_service.get_token_info()
            
            if isinstance(token_info, dict) and token_info.get("status") == "error":
                return Response({
                    "status": "error",
                    "message": token_info.get("message", "eBay token check unavailable"),
                    "debug": "eBay SDK not installed"
                }, status=503)
            
            return Response(token_info)
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Token health check failed: {str(e)}"
            }, status=500)

class EbayTokenActionView(APIView):
    def post(self, request):
        return Response({"message": "eBay token action endpoint working - full functionality not yet restored"})

class SetEbayRefreshTokenView(APIView):
    def post(self, request):
        return Response({"message": "Set eBay refresh token endpoint working - full functionality not yet restored"})

class EbayOAuthCallbackView(APIView):
    def get(self, request):
        return Response({"message": "eBay OAuth callback endpoint working - full functionality not yet restored"})

class EbayOAuthDeclinedView(APIView):
    def get(self, request):
        return Response({"message": "eBay OAuth declined endpoint working - full functionality not yet restored"})

class EbayOAuthView(APIView):
    def get(self, request):
        return Response({"message": "eBay OAuth endpoint working - full functionality not yet restored"})

class PriceAnalysisView(APIView):
    def post(self, request):
        try:
            analysis_service = get_market_analysis_service()
            if analysis_service is None:
                return Response({
                    "status": "error",
                    "message": "Market analysis service not available - dependencies not installed",
                    "debug": "Analysis service initialization failed"
                }, status=503)
            
            # This would call the real analysis service
            result = analysis_service.analyze(request.data)
            
            return Response({
                "status": "success",
                "result": result
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Price analysis failed: {str(e)}"
            }, status=500)

class AIImageSearchView(APIView):
    def post(self, request):
        try:
            ai_service = get_ai_service()
            if ai_service is None:
                return Response({
                    "status": "error",
                    "message": "AI image search not available - dependencies not installed",
                    "debug": "AI service initialization failed"
                }, status=503)
                
            # Extract image data
            image_data = request.data.get('image')
            if not image_data:
                return Response({
                    "status": "error",
                    "message": "No image data provided"
                }, status=400)
            
            # This would call the real AI search
            results = ai_service.search_similar(image_data)
            
            return Response({
                "status": "success",
                "results": results
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"AI image search failed: {str(e)}"
            }, status=500)

class PrivacyPolicyView(APIView):
    def get(self, request):
        return Response({
            "message": "Privacy policy endpoint working",
            "content": "Privacy policy content would be here"
        })

class CropPreviewView(APIView):
    def post(self, request):
        return Response({"message": "Crop preview endpoint working - full functionality not yet restored"})