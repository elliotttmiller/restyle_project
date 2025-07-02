# File: backend/core/views.py

from rest_framework import generics, permissions, serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ItemSerializer, ListingSerializer, MarketAnalysisSerializer
from .models import Item, Listing, MarketAnalysis # We need MarketAnalysis for the view
from .tasks import create_ebay_listing, perform_market_analysis # Import the analysis task
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

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

        # Auth
        auth_token = getattr(settings, 'EBAY_PRODUCTION_USER_TOKEN', None)
        if not auth_token:
            logger.warning("No eBay OAuth token available for search")
            return Response({'error': 'eBay API not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

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