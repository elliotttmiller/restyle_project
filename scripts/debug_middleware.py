import logging
import time
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request details
        start_time = time.time()
        logger.info(f"Request: {request.method} {request.path} from {request.META.get('REMOTE_ADDR', 'unknown')}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        try:
            response = self.get_response(request)
            duration = time.time() - start_time
            logger.info(f"Response: {response.status_code} in {duration:.3f}s")
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Request failed after {duration:.3f}s: {e}")
            return JsonResponse({
                "error": "Internal server error",
                "details": str(e)
            }, status=500) 