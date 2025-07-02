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
        """Search eBay for items using the Browse API"""
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get eBay OAuth token
            oauth_token = getattr(settings, 'EBAY_PRODUCTION_USER_TOKEN', None)
            if not oauth_token:
                logger.warning("No eBay OAuth token available for search")
                return Response({'error': 'eBay API not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # Call eBay Browse API
            api_url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
            params = {
                "q": query,
                "limit": 20,  # Get more results for better selection
                "filter": "conditions:{NEW|USED_EXCELLENT|USED_VERY_GOOD|USED_GOOD}"  # Filter by condition
            }
            
            headers = {
                "Authorization": f"Bearer {oauth_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            logger.info(f"Searching eBay for: {query}")
            response = requests.get(api_url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('itemSummaries', [])
                
                # Transform eBay data to match frontend expectations
                transformed_items = []
                for item in items:
                    transformed_item = {
                        'itemId': item.get('itemId', ''),
                        'title': item.get('title', ''),
                        'price': {
                            'value': item.get('price', {}).get('value', '0'),
                            'currency': item.get('price', {}).get('currency', 'USD')
                        },
                        'condition': [{
                            'conditionDisplayName': item.get('condition', 'Unknown')
                        }],
                        'image': {
                            'imageUrl': item.get('image', {}).get('imageUrl', '')
                        },
                        'itemWebUrl': item.get('itemWebUrl', ''),
                        'shippingCost': item.get('shippingOptions', [{}])[0].get('shippingCost', {})
                    }
                    transformed_items.append(transformed_item)
                
                logger.info(f"Found {len(transformed_items)} items for query: {query}")
                return Response(transformed_items, status=status.HTTP_200_OK)
                
            else:
                logger.warning(f"eBay API error: {response.status_code} - {response.text}")
                return Response({'error': 'Failed to search eBay'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except requests.exceptions.Timeout:
            logger.error("eBay API timeout")
            return Response({'error': 'eBay search timed out'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.exceptions.RequestException as e:
            logger.error(f"eBay API request error: {e}")
            return Response({'error': 'Failed to connect to eBay'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            logger.error(f"Unexpected error in eBay search: {e}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- Item Views ---
class ItemListCreateView(generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user)
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

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