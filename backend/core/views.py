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

logger = logging.getLogger(__name__)

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
            redirect_uri = "https://4022a978ecf9.ngrok-free.app/api/core/ebay-oauth-callback/"
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
    
    def search_ebay_with_queries(self, search_terms):
        """
        Search eBay with a list of search terms and return results.
        """
        if not search_terms:
            return []
        query = search_terms[0] if isinstance(search_terms, list) else str(search_terms)
        try:
            ebay_service = EbayService()
            items = ebay_service.search_items(query=query, limit=20)
            logger.info(f"eBay API returned {len(items)} items for query: {query}")
            return items
        except Exception as e:
            logger.error(f"Error in eBay search: {e}")
            return []
    
    def post(self, request):
        print("--- ENHANCED AI SEARCH VIEW ---")
        process = psutil.Process(os.getpid())
        mem_start = process.memory_info().rss / (1024 * 1024)
        print(f"[MEMORY] Start: {mem_start:.2f} MB")
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            image_data = image_file.read()
            ai_service = get_ai_service()
            
            # Step 1: Try Google Vision Product Search (Primary Method)
            print("Running Comprehensive Visual Search...")
            visual_search_results = ai_service.comprehensive_visual_search(image_data)
            
            # Step 2: Also run Ensemble Search for enhanced query building demonstration
            print("Running Ensemble Search with Enhanced Query Building...")
            def ebay_search_func(queries):
                print(f"[DEBUG] Search terms sent to eBay: {queries}")
                results = self.search_ebay_with_queries(queries)
                print(f"[DEBUG] eBay API returned {len(results)} items for queries: {queries}")
                if results:
                    print(f"[DEBUG] First eBay item: {results[0]}")
                return results
            hybrid_results = ai_service.ensemble_search(image_data, text_query=None, top_k=10)
            
            mem_end = process.memory_info().rss / (1024 * 1024)
            print(f"[MEMORY] End: {mem_end:.2f} MB")
            print(f"[MEMORY] Peak: {psutil.virtual_memory().used / (1024 * 1024):.2f} MB used system-wide")
            
            # Get search terms from AI analysis
            analysis_results = ai_service.analyze_image(image_data)
            search_terms, best_guess, suggested_queries = ai_service._nlp_enhanced_search_terms(analysis_results)
            
            # Return structured response with search terms
            return Response({
                'message': 'AI search successful.',
                'search_terms': search_terms,
                'suggested_queries': suggested_queries,
                'best_guess': best_guess,
                'visual_search_results': visual_search_results,
                'hybrid_results': hybrid_results
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in Enhanced AI search view: {e}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            items = ebay_service.search_items(query=query, category_ids=category if category and category != 'Unknown' else None, limit=20)
            comps = []
            prices = []
            offset = (page - 1) * page_size
            paginated_items = items[offset:offset + page_size]
            total_items = len(items)
            has_more = (offset + page_size) < total_items
            for idx, item in enumerate(paginated_items):
                price = item.get('price', {}).get('value')
                if price:
                    prices.append(float(price))
                comps.append({
                    'id': offset + idx + 1,
                    'title': item.get('title', ''),
                    'sold_price': float(price) if price else 0.0,
                    'platform': 'EBAY',
                    'image_url': item.get('image', {}).get('imageUrl', ''),
                    'source_url': item.get('itemWebUrl', ''),
                })
            if prices and len(prices) >= 3:
                price_range_low = min(prices)
                price_range_high = max(prices)
                suggested_price = sum(prices) / len(prices)
                analysis_result = {
                    'price_range_low': price_range_low,
                    'price_range_high': price_range_high,
                    'suggested_price': suggested_price,
                    'status': 'COMPLETE',
                    'confidence_score': f'Medium ({len(prices)} comparable listings)',
                    'comps': comps,
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total_items': total_items,
                        'has_more': has_more,
                        'offset': offset
                    }
                }
            else:
                if prices:
                    price_range_low = min(prices)
                    price_range_high = max(prices)
                    suggested_price = sum(prices) / len(prices)
                else:
                    price_range_low = price_range_high = suggested_price = 0.0
                analysis_result = {
                    'price_range_low': price_range_low,
                    'price_range_high': price_range_high,
                    'suggested_price': suggested_price,
                    'status': 'COMPLETE',
                    'confidence_score': f'Low (only {len(prices)} comparable listings found)',
                    'comps': comps,
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total_items': total_items,
                        'has_more': has_more,
                        'offset': offset
                    }
                }
            return Response(analysis_result, status=200)
        except Exception as e:
            logger.error(f"PriceAnalysisView error: {e}")
            return Response({'error': str(e)}, status=503)

ItemDoesNotExist = Item.DoesNotExist
MarketAnalysisDoesNotExist = MarketAnalysis.DoesNotExist