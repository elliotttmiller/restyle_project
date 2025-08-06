# File: backend/core/views.py

# pyright: reportAttributeAccessIssue=false

from rest_framework import generics, permissions, serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ItemSerializer, ListingSerializer, MarketAnalysisSerializer
from .models import Item, Listing, MarketAnalysis # We need MarketAnalysis for the view
from .models import Item, MarketAnalysis
from .tasks import create_ebay_listing, perform_market_analysis # Import the analysis task
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
import requests
from django.conf import settings
import logging
from django.core.cache import cache
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .ai_service import get_ai_service  # Import the AI service getter
import base64
import psutil
import os
from .services import EbayService
import traceback
from .market_analysis_service import get_market_analysis_service
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
            _vision_client = None
            logging.error(f"Failed to initialize Google Vision client: {e}")
    return _vision_client

def get_rekognition_client():
    """Lazy initialization of AWS Rekognition client"""
    global _rekognition_client
    if _rekognition_client is None:
        try:
            import boto3
            _rekognition_client = boto3.client(
                'rekognition',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('AWS_REGION_NAME', 'us-east-1')
            )
            logging.info("AWS Rekognition client initialized successfully")
        except Exception as e:
            _rekognition_client = None
            logging.error(f"Failed to initialize AWS Rekognition client: {e}")
    return _rekognition_client

def get_gemini_model():
    """Lazy initialization of Google Gemini model"""
    global _gemini_model
    if _gemini_model is None:
        try:
            import google.generativeai as genai
            genai.configure(
                api_key=os.environ.get("GOOGLE_API_KEY"),
                transport="rest"
            )
            _gemini_model = genai.GenerativeModel('gemini-1.5-pro-latest')
            logging.info("Google Gemini model initialized successfully")
        except Exception as e:
            _gemini_model = None
            logging.error(f"Failed to initialize Google Gemini model: {e}")
    return _gemini_model

def get_vertex_endpoint():
    """Lazy initialization of Google Vertex AI endpoint"""
    global _vertex_endpoint
    if _vertex_endpoint is None:
        try:
            from google.cloud import aiplatform
            aiplatform.init(
                project=os.environ.get('GOOGLE_CLOUD_PROJECT'),
                location=os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
            )
            _vertex_endpoint = aiplatform.Endpoint(
                endpoint_name="projects/silent-polygon-465403/locations/us-central1/endpoints/1234567890123456789"
            )
            logging.info("Google Vertex AI endpoint initialized successfully")
        except Exception as e:
            _vertex_endpoint = None
            logging.error(f"Failed to initialize Vertex AI endpoint: {e}")
    return _vertex_endpoint

# --- eBay Token Monitoring Views ---
class EbayTokenHealthView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get eBay token health status and metrics"""
        try:
            from .ebay_auth import token_manager, validate_ebay_token
            
            # Get current token status
            token = token_manager.get_valid_token()
            token_available = bool(token)
            token_valid = validate_ebay_token(token) if token else False
            
            # Get cached metrics
            health_metrics = cache.get('ebay_token_health_metrics', {})
            alerts = cache.get('ebay_token_alerts', [])
            validation_status = cache.get('ebay_token_validation_status', 'unknown')
            
            # Calculate uptime
            last_refresh = cache.get('ebay_token_last_refresh')
            last_validation = cache.get('ebay_token_last_validation')
            
            uptime_info = {
                'last_refresh': last_refresh.isoformat() if last_refresh else None,
                'last_validation': last_validation.isoformat() if last_validation else None,
                'time_since_refresh': None,
                'time_since_validation': None
            }
            
            if last_refresh:
                uptime_info['time_since_refresh'] = (datetime.now() - last_refresh).total_seconds()
            
            if last_validation:
                uptime_info['time_since_validation'] = (datetime.now() - last_validation).total_seconds()
            
            # Compile health data
            health_data = {
                'status': 'healthy' if token_available and token_valid else 'unhealthy',
                'token_available': token_available,
                'token_valid': token_valid,
                'validation_status': validation_status,
                'uptime': uptime_info,
                'metrics': health_metrics,
                'recent_alerts': alerts[-5:] if alerts else [],  # Last 5 alerts
                'refresh_stats': {
                    'success_count': cache.get('ebay_token_refresh_success_count', 0),
                    'failure_count': cache.get('ebay_token_refresh_failure_count', 0),
                },
                'last_updated': datetime.now().isoformat()
            }
            
            return Response(health_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting eBay token health: {e}")
            return Response(
                {'error': 'Failed to get token health status'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class EbayTokenActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Perform actions on eBay tokens"""
        action = request.data.get('action')
        
        if action == 'refresh':
            return self._refresh_token(request)
        elif action == 'validate':
            return self._validate_token(request)
        elif action == 'emergency_refresh':
            return self._emergency_refresh(request)
        else:
            return Response(
                {'error': 'Invalid action. Use: refresh, validate, or emergency_refresh'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _refresh_token(self, request):
        """Manually trigger token refresh"""
        try:
            from .tasks import refresh_ebay_token_task
            # Trigger refresh task
            task = refresh_ebay_token_task.delay() if hasattr(refresh_ebay_token_task, "delay") and callable(refresh_ebay_token_task.delay) else None

            return Response({
                'message': 'Token refresh initiated',
                'task_id': getattr(task, "id", None),
                'status': 'queued'
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            logger.error(f"Error triggering token refresh: {e}")
            return Response(
                {'error': 'Failed to trigger token refresh'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _validate_token(self, request):
        """Manually validate token"""
        try:
            from .tasks import validate_ebay_token_task
            # Trigger validation task
            task = validate_ebay_token_task.delay() if hasattr(validate_ebay_token_task, "delay") and callable(validate_ebay_token_task.delay) else None

            return Response({
                'message': 'Token validation initiated',
                'task_id': getattr(task, "id", None),
                'status': 'queued'
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            logger.error(f"Error triggering token validation: {e}")
            return Response(
                {'error': 'Failed to trigger token validation'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _emergency_refresh(self, request):
        """Emergency token refresh"""
        try:
            from .tasks import emergency_token_refresh_task
            
            # Trigger emergency refresh task
            task = emergency_token_refresh_task.delay()
            
            return Response({
                'message': 'Emergency token refresh initiated',
                'task_id': task.id,
                'status': 'queued'
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            logger.error(f"Error triggering emergency refresh: {e}")
            return Response(
                {'error': 'Failed to trigger emergency refresh'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# --- eBay Search Views ---
class EbaySearchView(APIView):
    logger.error('[DEBUG] EbaySearchView: class loaded')
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        logger.error(f"[DEBUG] EbaySearchView: HEADERS: {dict(request.headers)}")
        logger.error(f"[DEBUG] EbaySearchView: request.user={request.user}, request.auth={request.auth}")
        # Collect all supported query params
        params = {}
        for key in [
            'q', 'category_ids', 'filter', 'limit', 'offset', 'sort', 'fieldgroups', 'aspect_filter', 'compatibility_filter'
        ]:
            value = request.query_params.get(key)
            if value:
                params[key] = value
        # Set defaults
        if 'limit' not in params:
            params['limit'] = 20
        if 'offset' not in params:
            params['offset'] = 0
        # Use EbayService for search
        try:
            ebay_service = EbayService()
            items = ebay_service.search_items(
                query=params.get('q', ''),
                category_ids=params.get('category_ids'),
                limit=int(params.get('limit', 20)),
                localization=request.query_params.get('delivery_country')
            )
            return Response(items, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"EbaySearchView error: {e}")
            return Response({'error': str(e)}, status=503)

# --- Item Views ---
class ItemListCreateView(generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user)
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Item creation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user)

# --- Analysis Views ---
class TriggerAnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        try:
            item = Item.objects.get(pk=pk, owner=request.user)
            # Create or get existing analysis
            analysis, created = MarketAnalysis.objects.get_or_create(
                item=item,
                defaults={'status': 'PENDING'}
            )
            # Trigger the market analysis task
            task = perform_market_analysis.delay(analysis.id)
            analysis.task_id = getattr(task, 'id', None)
            analysis.save()
            logger.error(f"[TRIGGER_ANALYSIS] Triggered for item {item.id}, analysis {analysis.id}, task_id {getattr(task, 'id', None)} (created={created})")
            return Response({
                'message': f'Analysis started for item {pk}',
                'analysis_id': analysis.id,
                'task_id': getattr(task, 'id', None)
            }, status=status.HTTP_200_OK)
        except Item.DoesNotExist:
            logger.error(f"[TRIGGER_ANALYSIS] Item {pk} not found for user {request.user}")
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"[TRIGGER_ANALYSIS] Failed to start analysis for item {pk}: {str(e)}")
            return Response({'error': f'Failed to start analysis: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AnalysisStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        try:
            item = Item.objects.get(pk=pk, owner=request.user)
            try:
                analysis = MarketAnalysis.objects.get(item=item)
                comps_qs = analysis.comps.all()
                
                # Add pagination support
                page = int(request.query_params.get('page', 1))
                page_size = int(request.query_params.get('page_size', 10))
                offset = (page - 1) * page_size
                
                # Get paginated comps
                paginated_comps = comps_qs[offset:offset + page_size]
                total_comps = comps_qs.count()
                has_more = (offset + page_size) < total_comps
                
                comps_count = paginated_comps.count()
                comps_titles = list(paginated_comps.values_list('title', flat=True))
                logger.error(f"[DEBUG] AnalysisStatusView: Returning analysis {analysis.id} with {comps_count} comps (page {page}): {comps_titles}")
                
                # Create response with pagination info
                serializer = MarketAnalysisSerializer(analysis)
                response_data = serializer.data
                response_data['pagination'] = {
                    'page': page,
                    'page_size': page_size,
                    'total_comps': total_comps,
                    'has_more': has_more,
                    'offset': offset
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
            except MarketAnalysis.DoesNotExist:
                logger.error(f"[DEBUG] AnalysisStatusView: No analysis found for item {item.id}")
                return Response({'error': 'No analysis found for this item'}, status=status.HTTP_404_NOT_FOUND)
        except Item.DoesNotExist:
            logger.error(f"[DEBUG] AnalysisStatusView: Item {pk} not found for user {request.user}")
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

# --- Listing Views ---
class ListingListCreateView(generics.ListCreateAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        item_pk = self.kwargs['item_pk']
        return Listing.objects.filter(item__pk=item_pk, item__owner=self.request.user)

    def perform_create(self, serializer):
        item_pk = self.kwargs.get('item_pk')
        item = Item.objects.get(pk=item_pk, owner=self.request.user)
        platform = serializer.validated_data.get('platform')
        if Listing.objects.filter(item=item, platform=platform).exists():
            raise serializers.ValidationError(f"A listing for this item on {platform} already exists.")
        listing = serializer.save(item=item)
        if listing.platform == 'EBAY':
            print(f"Dispatching task to list item {listing.id} on eBay.")
            create_ebay_listing.delay(listing.id)

class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Listing.objects.filter(item__owner=self.request.user)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint for startup scripts"""
    return Response({"status": "healthy", "message": "Backend is running"})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_status(request):
    """Get AI services status"""
    try:
        # Check if AI services are available
        ai_services = {
            'vision': True,  # Google Vision
            'rekognition': True,  # AWS Rekognition
            'gemini': True,  # Google Gemini
            'vertex': True,  # Google Vertex AI
        }
        
        # Check if credentials are available
        try:
            import os
            google_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            aws_creds = os.path.exists('/app/restyle-rekognition-user_accessKeys.csv')
            
            ai_services['vision'] = google_creds
            ai_services['rekognition'] = aws_creds
            ai_services['gemini'] = google_creds
            ai_services['vertex'] = google_creds
        except Exception as e:
            logger.error(f"Error checking AI credentials: {e}")
        
        return Response({
            'services': ai_services,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        return Response(
            {'error': 'Failed to get AI status'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def performance_metrics(request):
    """Get performance metrics for the system"""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Get cached metrics
        total_searches = cache.get('total_searches', 0)
        successful_searches = cache.get('successful_searches', 0)
        average_response_time = cache.get('average_response_time', 0)
        ai_confidence_avg = cache.get('ai_confidence_avg', 0)
        
        metrics = {
            'total_searches': total_searches,
            'successful_searches': successful_searches,
            'average_response_time': average_response_time,
            'ai_confidence_avg': ai_confidence_avg,
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'memory_total': memory.total
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return Response(metrics)
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return Response(
            {'error': 'Failed to get performance metrics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class SetEbayRefreshTokenView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        new_token = request.data.get('refresh_token')
        if not new_token:
            return Response({'error': 'Missing refresh_token in request body.'}, status=400)
        try:
            from .ebay_auth import token_manager
            token_manager._update_refresh_token(new_token)
            return Response({'message': 'Refresh token updated successfully!'}, status=200)
        except Exception as e:
            return Response({'error': f'Failed to update refresh token: {e}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class EbayOAuthCallbackView(APIView):
    permission_classes = []  # Public endpoint for OAuth redirect

    def get(self, request):
        code = request.query_params.get('code')
        if not code:
            return Response({'error': 'Missing code parameter from eBay.'}, status=400)
        try:
            # Exchange code for tokens
            from django.conf import settings
            import requests
            import base64
            import logging

            client_id = getattr(settings, 'EBAY_PRODUCTION_APP_ID', None)
            client_secret = getattr(settings, 'EBAY_PRODUCTION_CLIENT_SECRET', None)
            # Hardcoded redirect_uri to match eBay app settings
            redirect_uri = "https://ead6946c7030.ngrok-free.app/api/core/ebay-oauth-callback/"
            if not all([client_id, client_secret]):
                return Response({'error': 'Missing eBay client credentials.'}, status=500)

            token_url = 'https://api.ebay.com/identity/v1/oauth2/token'
            basic_auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Basic {basic_auth}',
            }
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri,
            }
            # Log the outgoing request for debugging
            logging.error(f"eBay OAuth token exchange request: url={token_url}, headers={headers}, data={data}")
            resp = requests.post(token_url, headers=headers, data=data, timeout=30)
            if resp.status_code == 200:
                token_data = resp.json()
                refresh_token = token_data.get('refresh_token')
                if refresh_token:
                    from .ebay_auth import token_manager
                    token_manager._update_refresh_token(refresh_token)
                    return Response({'message': 'eBay refresh token updated successfully! You may close this window.'}, status=200)
                else:
                    return Response({'error': 'No refresh token in response.'}, status=500)
            else:
                logging.error(f"eBay OAuth token exchange response: status={resp.status_code}, body={resp.text}")
                return Response({'error': f'Failed to exchange code: {resp.status_code} {resp.text}'}, status=500)
        except Exception as e:
            return Response({'error': f'Exception during token exchange: {e}'}, status=500)

class EbayOAuthDeclinedView(APIView):
    permission_classes = []  # Public endpoint

    def get(self, request):
        return Response({'message': 'eBay authorization was declined. If this was a mistake, please try again.'}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class AIImageSearchView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def __init__(self):
        super().__init__()
        # Import the new services
        from .market_analysis_service import get_market_analysis_service
        self.market_analyzer = get_market_analysis_service()
        self.ai_service = get_ai_service()
    
    def search_ebay_with_queries(self, query):
        """
        Search eBay with a query and return results.
        """
        if not query:
            return []
        try:
            ebay_service = EbayService()
            items = ebay_service.search_items(query=query, limit=20)
            logger.info(f"eBay API returned {len(items)} items for query: {query}")
            return items
        except Exception as e:
            logger.error(f"Error in eBay search: {e}")
            return []
    
    def post(self, request):
        """
        Multi-expert AI image search with optional intelligent cropping.
        Accepts 'intelligent_crop' boolean flag (default: True).
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"AIImageSearchView POST called. Method: {request.method}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"FILES: {request.FILES}")
        logger.info(f"User: {getattr(request, 'user', None)}")
        logger.info(f"Auth: {getattr(request, 'auth', None)}")
        logger.info(f"REMOTE_ADDR: {request.META.get('REMOTE_ADDR')}")
        print("--- MULTI-EXPERT AI MARKET ANALYSIS PIPELINE ---")
        print(f"[DEBUG] Request method: {request.method}")
        print(f"[DEBUG] Request content type: {request.content_type}")
        print(f"[DEBUG] Request FILES keys: {list(request.FILES.keys())}")
        print(f"[DEBUG] Request DATA keys: {list(request.data.keys())}")
        
        process = psutil.Process(os.getpid())
        mem_start = process.memory_info().rss / (1024 * 1024)
        print(f"[MEMORY] Start: {mem_start:.2f} MB")
        
        image_file = request.FILES.get('image')
        if not image_file:
            print(f"[DEBUG] No image file found in request.FILES")
            print(f"[DEBUG] Available files: {list(request.FILES.keys())}")
            return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            image_data = image_file.read()
            
            # --- Intelligent Cropping ---
            intelligent_crop = request.data.get('intelligent_crop', 'true')
            if isinstance(intelligent_crop, str):
                intelligent_crop = intelligent_crop.lower() in ['1', 'true', 'yes']
            crop_info = {'service': 'none', 'bounding_box': None}
            if intelligent_crop:
                image_data, crop_info = self.ai_service.intelligent_crop(image_data)
                logger.info(f"[CROP] Crop info: {crop_info}")
            
            # Define the marketplace API function
            def ebay_api_func(query):
                return self.search_ebay_with_queries(query)
            
            # Run the complete multi-expert analysis pipeline
            print("Running Multi-Expert AI Analysis...")
            analysis_results = self.market_analyzer.run_complete_analysis(
                image_data=image_data,
                marketplace_api_func=ebay_api_func
            )
            
            # Add price analysis if we have ranked comps
            if analysis_results.get('visually_ranked_comps'):
                price_analysis = self.market_analyzer.analyze_price_trends(
                    analysis_results['visually_ranked_comps']
                )
                analysis_results['price_analysis'] = price_analysis
            
            mem_end = process.memory_info().rss / (1024 * 1024)
            print(f"[MEMORY] End: {mem_end:.2f} MB")
            print(f"[MEMORY] Peak: {psutil.virtual_memory().used / (1024 * 1024):.2f} MB used system-wide")
            
            # Return the comprehensive analysis results
            response = Response({
                'message': 'Multi-expert AI analysis completed successfully.',
                'analysis_results': analysis_results,
                'results': analysis_results.get('visually_ranked_comps', []),
                'crop_info': crop_info,
                'system_info': {
                    'memory_usage_mb': round(mem_end - mem_start, 2),
                    'total_memory_peak_mb': round(psutil.virtual_memory().used / (1024 * 1024), 2)
                }
            }, status=status.HTTP_200_OK)
            return response
        except Exception as e:
            logger.error(f"Error in Multi-Expert AI search view: {e}")
            response = Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return response
        finally:
            logger.info(f"AIImageSearchView POST response status: {getattr(response, 'status_code', None)}")

@method_decorator(csrf_exempt, name='dispatch')
class PriceAnalysisView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        title = data.get('title')
        brand = data.get('brand')
        category = data.get('category')
        size = data.get('size')
        color = data.get('color')
        condition = data.get('condition')
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 10))
        query = f"{brand or ''} {title or ''} {size or ''} {color or ''} {condition or ''}".strip()
        try:
            ebay_service = EbayService()
            items = ebay_service.search_items(query=query, category_ids=category if category and category != 'Unknown' else None, limit=100);
            comps = [];
            prices = [];
            for idx, item in enumerate(items):
                price = item.get('price', {}).get('value');
                if price:
                    prices.append(float(price));
                comps.append({
                    'id': idx + 1,
                    'title': item.get('title', ''),
                    'sold_price': float(price) if price else 0.0,
                    'platform': 'EBAY',
                    'image_url': item.get('image', {}).get('imageUrl', ''),
                    'source_url': item.get('itemWebUrl', ''),
                });
            if prices and len(prices) >= 3:
                price_range_low = min(prices);
                price_range_high = max(prices);
                suggested_price = sum(prices) / len(prices);
                analysis_result = {
                    'price_range_low': price_range_low,
                    'price_range_high': price_range_high,
                    'suggested_price': suggested_price,
                    'status': 'COMPLETE',
                    'confidence_score': f'Medium ({len(prices)} comparable listings)',
                    'comps': comps
                }
                logger.info(f"[DEBUG] Returning {len(comps)} comps. First 3: {comps[:3]}")
            else:
                if prices:
                    price_range_low = min(prices);
                    price_range_high = max(prices);
                    suggested_price = sum(prices) / len(prices);
                else:
                    price_range_low = price_range_high = suggested_price = 0.0;
                analysis_result = {
                    'price_range_low': price_range_low,
                    'price_range_high': price_range_high,
                    'suggested_price': suggested_price,
                    'status': 'COMPLETE',
                    'confidence_score': f'Low (only {len(prices)} comparable listings found)',
                    'comps': comps
                };
            return Response(analysis_result, status=200);
        except Exception as e:
            logger.error(f"PriceAnalysisView error: {e}")
            return Response({'error': str(e)}, status=503)

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
        self.ai_service = get_ai_service()
        self.ebay_service = EbayService()
        self.market_analyzer = get_market_analysis_service()

    def calculate_confidence_score(self, analysis_results):
        """Calculate confidence scores for different AI services."""
        confidence_scores = {}
        
        # Google Vision confidence
        vision_data = analysis_results.get('vision')
        if vision_data and isinstance(vision_data, dict):
            vision_score = 0
            if vision_data.get('texts'):
                vision_score += 30  # Text detection is valuable
            if vision_data.get('labels'):
                vision_score += 20  # Label detection
            if vision_data.get('objects'):
                vision_score += 15  # Object detection
            if vision_data.get('colors'):
                vision_score += 10  # Color analysis
            confidence_scores['vision'] = min(vision_score, 100)
        
        # AWS Rekognition confidence
        rekognition_data = analysis_results.get('rekognition')
        if rekognition_data and isinstance(rekognition_data, dict):
            rekognition_score = 0
            if rekognition_data.get('labels'):
                rekognition_score += 40  # Rekognition labels are very accurate
            if rekognition_data.get('texts'):
                rekognition_score += 30  # Text detection
            if rekognition_data.get('faces', 0) > 0:
                rekognition_score += 10  # Face detection
            confidence_scores['rekognition'] = min(rekognition_score, 100)
        
        # Gemini API confidence
        if analysis_results.get('gemini_query'):
            confidence_scores['gemini'] = 95  # AI synthesis is highly valuable
        
        # Vertex AI confidence
        if analysis_results.get('vertex_analysis'):
            confidence_scores['vertex'] = 90  # Advanced analysis is valuable
        
        return confidence_scores
    
    def generate_multiple_query_variants(self, analysis_results):
        """Generate multiple query variants for better search coverage."""
        variants = []
        
        # Primary query (Gemini)
        if analysis_results.get('gemini_query'):
            variants.append({
                'query': analysis_results['gemini_query'],
                'confidence': 95,
                'source': 'Gemini AI'
            })
        
        # Brand-focused query
        brand_query = ""
        vision_data = analysis_results.get('vision')
        if vision_data and isinstance(vision_data, dict) and vision_data.get('texts'):
            for text in vision_data['texts']:
                if any(brand in text.upper() for brand in ['BURBERRY', 'NIKE', 'ADIDAS', 'LEVI', 'CALVIN', 'RALPH', 'TOMMY']):
                    brand_query = f"{text.upper()} shirt"
                    break
        
        if brand_query:
            variants.append({
                'query': brand_query,
                'confidence': 85,
                'source': 'Brand Detection'
            })
        
        # Feature-focused query
        feature_terms = []
        rekognition_data = analysis_results.get('rekognition')
        if rekognition_data and isinstance(rekognition_data, dict) and rekognition_data.get('labels'):
            for label in rekognition_data['labels']:
                if any(term in label.lower() for term in ['long sleeve', 'dress shirt', 'button down', 'polo', 't-shirt']):
                    feature_terms.append(label)
        
        if feature_terms:
            feature_query = ' '.join(feature_terms[:2])
            variants.append({
                'query': feature_query,
                'confidence': 80,
                'source': 'Feature Detection'
            })
        
        # Generic fallback
        if rekognition_data and isinstance(rekognition_data, dict) and rekognition_data.get('labels'):
            generic_terms = [label for label in rekognition_data['labels'][:3]]
            generic_query = ' '.join(generic_terms)
            variants.append({
                'query': generic_query,
                'confidence': 70,
                'source': 'Generic Detection'
            })
        
        return variants
    
    def optimize_search_query(self, query, analysis_results):
        """Optimize the search query based on analysis results."""
        optimized_query = query
        
        # Add brand name if detected but missing from query
        detected_brands = []
        vision_data = analysis_results.get('vision')
        if vision_data and isinstance(vision_data, dict) and vision_data.get('texts'):
            for text in vision_data['texts']:
                if any(brand in text.upper() for brand in ['BURBERRY', 'NIKE', 'ADIDAS', 'LEVI', 'CALVIN', 'RALPH', 'TOMMY']):
                    detected_brands.append(text.upper())
        
        if detected_brands and not any(brand in optimized_query.upper() for brand in detected_brands):
            optimized_query = f"{detected_brands[0]} {optimized_query}"
        
        # Add specific features if missing
        specific_features = []
        rekognition_data = analysis_results.get('rekognition')
        if rekognition_data and isinstance(rekognition_data, dict) and rekognition_data.get('labels'):
            for label in rekognition_data['labels']:
                if any(feature in label.lower() for feature in ['long sleeve', 'short sleeve', 'button down', 'polo', 't-shirt']):
                    specific_features.append(label)
        
        if specific_features and not any(feature.lower() in optimized_query.lower() for feature in specific_features):
            optimized_query = f"{optimized_query} {specific_features[0]}"
        
        return optimized_query
    
    def post(self, request):
        self.logger.debug("--- AdvancedMultiExpertAISearchView POST called ---")
        self.logger.debug(f"Request method: {request.method}")
        self.logger.debug(f"Headers: {dict(request.headers)}")
        self.logger.debug(f"FILES: {request.FILES}")
        self.logger.debug(f"DATA: {request.data}")
        self.logger.debug(f"User: {getattr(request, 'user', None)}")
        self.logger.debug(f"Auth: {getattr(request, 'auth', None)}")
        self.logger.debug(f"REMOTE_ADDR: {request.META.get('REMOTE_ADDR')}")
        try:
            image_file = request.FILES.get('image')
            if not image_file:
                self.logger.error("No image file found in request.FILES")
                return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
            image_data = image_file.read()
            intelligent_crop = request.data.get('intelligent_crop', 'true')
            if isinstance(intelligent_crop, str):
                intelligent_crop = intelligent_crop.lower() in ['1', 'true', 'yes']
            crop_info = {'service': 'none', 'bounding_box': None}
            if intelligent_crop:
                image_data, crop_info = self.ai_service.intelligent_crop(image_data)
                self.logger.info(f"[CROP] Crop info: {crop_info}")
            def ebay_api_func(query):
                return self.ebay_service.search_items(query=query, limit=20)
            self.logger.info("Running Multi-Expert AI Analysis...")
            analysis_results = self.market_analyzer.run_complete_analysis(
                image_data=image_data,
                marketplace_api_func=ebay_api_func
            )
            if analysis_results.get('visually_ranked_comps'):
                price_analysis = self.market_analyzer.analyze_price_trends(
                    analysis_results['visually_ranked_comps']
                )
                analysis_results['price_analysis'] = price_analysis
            response = Response({
                'message': 'Multi-expert AI analysis completed successfully.',
                'analysis_results': analysis_results,
                'results': analysis_results.get('visually_ranked_comps', []),
                'crop_info': crop_info
            }, status=status.HTTP_200_OK)
            self.logger.debug(f"Response status: {response.status_code}")
            return response
        except Exception as e:
            self.logger.error(f"Error in AdvancedMultiExpertAISearchView: {e}", exc_info=True)
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PrivacyPolicyView(APIView):
    """
    Privacy Policy endpoint required by eBay OAuth
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Return privacy policy for eBay OAuth compliance"""
        privacy_policy = {
            "app_name": "Restyle AI Reseller Assistant",
            "version": "1.0",
            "last_updated": "2025-07-12",
            "privacy_policy": {
                "data_collection": {
                    "images": "We temporarily process uploaded images for AI analysis and eBay search",
                    "usage": "Images are used solely for product identification and search query generation",
                    "retention": "Images are not stored permanently and are deleted after processing"
                },
                "ebay_integration": {
                    "oauth": "We use eBay OAuth for secure API access",
                    "data_shared": "Only search queries are sent to eBay, no personal data is shared",
                    "permissions": "We request minimal permissions needed for product search"
                },
                "ai_services": {
                    "google_vision": "Uses Google Vision API for image analysis",
                    "aws_rekognition": "Uses AWS Rekognition for object detection",
                    "google_gemini": "Uses Google Gemini for AI-powered query generation",
                    "google_vertex": "Uses Google Vertex AI for advanced analysis"
                },
                "data_protection": {
                    "encryption": "All data is transmitted over HTTPS",
                    "storage": "No personal data is stored permanently",
                    "access": "Only authorized users can access the system"
                },
                "contact": {
                    "email": "support@restyle-ai.com",
                    "website": "https://restyle-ai.com"
                }
            }
        }
        
        return Response(privacy_policy, status=status.HTTP_200_OK)


class EbayOAuthView(APIView):
    """
    eBay OAuth initiation endpoint
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Initiate eBay OAuth flow"""
        try:
            from django.conf import settings
            import urllib.parse
            
            # Get eBay credentials
            client_id = getattr(settings, 'EBAY_PRODUCTION_APP_ID', None)
            if not client_id:
                return Response({
                    'error': 'eBay App ID not configured. Please set EBAY_PRODUCTION_APP_ID in settings.'
                }, status=500)
            
            # Build OAuth URL
            redirect_uri = "https://ead6946c7030.ngrok-free.app/api/core/ebay-oauth-callback/"
            scope = "https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment"
            
            oauth_url = (
                "https://auth.ebay.com/oauth2/authorize?"
                f"client_id={client_id}&"
                f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
                f"scope={urllib.parse.quote(scope)}&"
                "response_type=code"
            )
            
            return Response({
                'message': 'eBay OAuth flow initiated',
                'oauth_url': oauth_url,
                'instructions': [
                    '1. Click the OAuth URL below',
                    '2. Sign in with your eBay account',
                    '3. Grant permissions to your app',
                    '4. You will be redirected back with a refresh token'
                ]
            }, status=200)
            
        except Exception as e:
            return Response({
                'error': f'Failed to initiate OAuth flow: {str(e)}'
            }, status=500)

ItemDoesNotExist = Item.DoesNotExist
MarketAnalysisDoesNotExist = MarketAnalysis.DoesNotExist

@method_decorator(csrf_exempt, name='dispatch')
class CropPreviewView(APIView):
    """
    Endpoint for intelligent crop preview.
    POST an image, get a cropped preview (base64), crop info, and optionally the original image (base64).
    No AI search is performed.
    """
    permission_classes = [AllowAny]

    def __init__(self):
        super().__init__()
        self.ai_service = get_ai_service()
        self.logger = logging.getLogger("core.crop_preview")

    def post(self, request, *args, **kwargs):
        self.logger.info("Received crop-preview request.")
        try:
            image_file = request.FILES.get('image')
            if not image_file:
                self.logger.error("No image file provided in request.")
                return Response({'error': 'No image file provided.'}, status=400)
            image_data = image_file.read()
            crop_result = self.ai_service.intelligent_crop(image_data)
            if crop_result['cropped_image']:
                self.logger.info(f"Cropping successful. Service: {crop_result['service']}, Box: {crop_result['bounding_box']}")
            else:
                self.logger.warning("Cropping failed or no bounding box found. Returning original image.")
            response = {
                'cropped_image_base64': crop_result['cropped_image'],
                'crop_info': {
                    'service': crop_result['service'],
                    'bounding_box': crop_result['bounding_box']
                },
                'original_image_base64': base64.b64encode(image_data).decode('utf-8'),
            }
            return Response(response)
        except Exception as e:
            self.logger.error(f"Exception in crop-preview: {e}\n{traceback.format_exc()}")
            return Response({'error': str(e)}, status=500)

@api_view(["GET"])
@permission_classes([AllowAny])
def root_view(request):
    return Response({"message": "Welcome to the Restyle API! The backend is running."})