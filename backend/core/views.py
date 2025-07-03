# File: backend/core/views.py

from rest_framework import generics, permissions, serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ItemSerializer, ListingSerializer, MarketAnalysisSerializer
from .models import Item, Listing, MarketAnalysis # We need MarketAnalysis for the view
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
            task = refresh_ebay_token_task.delay()
            
            return Response({
                'message': 'Token refresh initiated',
                'task_id': task.id,
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
            task = validate_ebay_token_task.delay()
            
            return Response({
                'message': 'Token validation initiated',
                'task_id': task.id,
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
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Proxy eBay Browse API with all supported filters and headers"""
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

        # Auth - Use token manager with automatic refresh
        try:
            from .ebay_auth import get_ebay_oauth_token
            auth_token = get_ebay_oauth_token()
        except Exception as e:
            logger.error(f"Error getting eBay token: {e}")
            auth_token = None
        
        # Always log the access token being used (mask for security)
        if auth_token:
            masked_token = auth_token[:6] + '...' + auth_token[-4:]
            logger.error(f"Using eBay access token for API call: {masked_token}")
        else:
            logger.warning("No valid eBay OAuth token available for search (no fallback).")
            return Response({'error': 'No valid eBay OAuth token available. Please re-authorize the app.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Headers
        headers = {
            'Authorization': f'Bearer {auth_token}',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Content-Language': 'en-US',
        }
        # Optionally support localization
        if 'delivery_country' in request.query_params:
            headers['X-EBAY-C-ENDUSERCTX'] = f"contextualLocation=country={request.query_params['delivery_country']}"

        api_url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        logger.info(f"Proxying eBay search: {params}")
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                items = data.get('itemSummaries', [])
                # Return all relevant fields, including affiliate link if present
                for item in items:
                    if 'itemAffiliateWebUrl' not in item and 'itemWebUrl' in item:
                        item['itemAffiliateWebUrl'] = item['itemWebUrl']
                return Response(items, status=status.HTTP_200_OK)
            elif response.status_code == 429:
                logger.warning(f"eBay API rate limit hit: {response.text}")
                return Response({'error': 'eBay rate limit reached. Please try again later.'}, status=429)
            elif response.status_code == 401:
                logger.error(f"eBay API authentication failed: {response.status_code} - {response.text}")
                return Response({'error': 'eBay authentication failed. OAuth token may have expired. Please refresh the token.'}, status=503)
            elif response.status_code == 403:
                logger.error(f"eBay API access denied: {response.status_code} - {response.text}")
                return Response({'error': 'eBay access denied. Check API permissions.'}, status=503)
            else:
                logger.warning(f"eBay API error: {response.status_code} - {response.text}")
                return Response({'error': 'Failed to search eBay'}, status=503)
        except requests.exceptions.Timeout:
            logger.error("eBay API timeout")
            return Response({'error': 'eBay search timed out'}, status=504)
        except requests.exceptions.RequestException as e:
            logger.error(f"eBay API request error: {e}")
            return Response({'error': 'Failed to connect to eBay'}, status=503)
        except Exception as e:
            logger.error(f"Unexpected error in eBay search: {e}")
            return Response({'error': 'An unexpected error occurred'}, status=500)

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
            analysis.task_id = task.id
            analysis.save()
            
            return Response({
                'message': f'Analysis started for item {pk}',
                'analysis_id': analysis.id,
                'task_id': task.id
            }, status=status.HTTP_200_OK)
            
        except Item.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Failed to start analysis: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AnalysisStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        try:
            item = Item.objects.get(pk=pk, owner=request.user)
            try:
                analysis = MarketAnalysis.objects.get(item=item)
                serializer = MarketAnalysisSerializer(analysis)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except MarketAnalysis.DoesNotExist:
                return Response({'error': 'No analysis found for this item'}, status=status.HTTP_404_NOT_FOUND)
        except Item.DoesNotExist:
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
            redirect_uri = "https://f8e6-2601-444-882-b090-394b-9d47-4958-eca9.ngrok-free.app/api/core/ebay-oauth-callback/"
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