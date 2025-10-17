"""
Custom error handling middleware for improved error responses and logging
"""
import logging
import traceback
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import DatabaseError
from rest_framework.exceptions import APIException
from rest_framework import status

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware:
    """
    Middleware to handle exceptions and return consistent JSON error responses
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """
        Process exceptions and return appropriate JSON responses
        """
        # Log the exception
        logger.error(
            f"Exception occurred: {exception.__class__.__name__}",
            exc_info=True,
            extra={
                'request_path': request.path,
                'request_method': request.method,
                'user': getattr(request.user, 'username', 'anonymous'),
            }
        )
        
        # Handle different exception types
        if isinstance(exception, PermissionDenied):
            return self._error_response(
                message="You don't have permission to perform this action",
                status_code=status.HTTP_403_FORBIDDEN,
                error_type='permission_denied'
            )
        
        elif isinstance(exception, ValidationError):
            return self._error_response(
                message=str(exception),
                status_code=status.HTTP_400_BAD_REQUEST,
                error_type='validation_error'
            )
        
        elif isinstance(exception, DatabaseError):
            return self._error_response(
                message="A database error occurred. Please try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_type='database_error'
            )
        
        elif isinstance(exception, APIException):
            return self._error_response(
                message=str(exception.detail),
                status_code=exception.status_code,
                error_type='api_error'
            )
        
        # Generic server error
        return self._error_response(
            message="An unexpected error occurred. Please try again later.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type='server_error',
            details=str(exception) if logger.level == logging.DEBUG else None
        )
    
    def _error_response(self, message, status_code, error_type, details=None):
        """
        Create a consistent error response
        """
        error_data = {
            'error': {
                'type': error_type,
                'message': message,
                'status_code': status_code,
            }
        }
        
        if details:
            error_data['error']['details'] = details
        
        return JsonResponse(error_data, status=status_code)


class RequestLoggingMiddleware:
    """
    Middleware to log all API requests for monitoring and debugging
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log request
        logger.info(
            f"API Request: {request.method} {request.path}",
            extra={
                'method': request.method,
                'path': request.path,
                'user': getattr(request.user, 'username', 'anonymous'),
                'ip': self._get_client_ip(request),
            }
        )
        
        response = self.get_response(request)
        
        # Log response
        logger.info(
            f"API Response: {request.method} {request.path} - {response.status_code}",
            extra={
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'user': getattr(request.user, 'username', 'anonymous'),
            }
        )
        
        return response
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
