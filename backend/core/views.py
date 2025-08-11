# backend/core/views.py
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import JsonResponse, HttpResponse
from django.urls import get_resolver, URLPattern, URLResolver
from django.views.decorators.csrf import csrf_exempt

# Import the REAL service, not the stub
from .market_analysis_service import get_market_analysis_service

logger = logging.getLogger(__name__)

# --- The Primary AI Endpoint ---

class AnalyzeAndPriceView(APIView):
    """
    The single, primary endpoint for performing a full AI-driven
    image analysis and price evaluation. It is secured and requires authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logger.info(f"AnalyzeAndPriceView received a request from user: {request.user.username}")
        
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({"error": "No image file provided in the 'image' field."}, status=status.HTTP_400_BAD_REQUEST)
        
        image_data = image_file.read()

        try:
            market_service = get_market_analysis_service()
            analysis_results = market_service.run_ai_statistical_analysis(image_data)
            
            if "error" in analysis_results:
                status_code = status.HTTP_404_NOT_FOUND if "No recently sold" in analysis_results.get("error", "") else status.HTTP_500_INTERNAL_SERVER_ERROR
                return Response(analysis_results, status=status_code)
                
            return Response(analysis_results, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Critical error in AnalyzeAndPriceView: {e}", exc_info=True)
            return Response({"error": "An unexpected server error occurred during analysis."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- Health, System, and Test Endpoints ---

class ListUrlsView(APIView):
    """
    An endpoint for testing that lists all available URL patterns.
    This version correctly cleans and joins regex patterns to form valid paths.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        resolver = get_resolver(None)
        url_list = self._get_urls(resolver.url_patterns)
        # Final filtering for safety
        url_list = [u for u in url_list if u['path'].startswith('api/') and not u['path'].startswith('admin/')]
        return Response(url_list)

    def _get_urls(self, patterns: list, prefix: str = ''):
        """A robust recursive function to extract and clean URL patterns."""
        results = []
        for pattern in patterns:
            if isinstance(pattern, URLResolver):
                # This is an include(), so recurse into its patterns
                new_prefix = prefix + pattern.pattern.regex.pattern.replace('^', '').rstrip('/') + '/'
                results.extend(self._get_urls(pattern.url_patterns, new_prefix))
            elif isinstance(pattern, URLPattern):
                # This is a regular URL, clean its pattern
                path = prefix + pattern.pattern.regex.pattern.replace('^', '').replace('$', '')
                
                # Replace dynamic parts with static values for testing
                if '<int:pk>' in path: path = path.replace('<int:pk>', '1')
                if '<item_pk>' in path: path = path.replace('<item_pk>', '1')
                
                # We only want to test the main API endpoints
                if path.startswith('api/'):
                    results.append({"path": path, "name": pattern.name})
        return results

def health_check(request):
    """A simple, public health check endpoint."""
    return JsonResponse({"status": "healthy", "service": "core"})

class EbayTokenHealthView(APIView):
    """Provides a status report for the eBay OAuth token."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # This can be fully implemented later using your ebay_auth_service
        return Response({"status": "ok", "token_status": "not_implemented"})