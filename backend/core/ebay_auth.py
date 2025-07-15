"""
eBay Authentication Service
Handles OAuth token management, refresh, and automatic renewal
"""

import requests
import json
import logging
import time
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.db import models
from typing import Optional, Dict, Any
import os
from django.core.mail import mail_admins

logger = logging.getLogger(__name__)

class EbayTokenManager:
    """Manages eBay OAuth tokens with automatic refresh capabilities"""
    
    # Cache keys
    TOKEN_CACHE_KEY = "ebay_oauth_token"
    TOKEN_EXPIRY_CACHE_KEY = "ebay_token_expiry"
    REFRESH_LOCK_KEY = "ebay_token_refresh_lock"
    
    # Token expiry buffer (refresh 1 hour before expiry)
    EXPIRY_BUFFER = timedelta(hours=1)
    
    REFRESH_TOKEN_FILE = os.path.join(os.path.dirname(__file__), '..', 'ebay_refresh_token.txt')
    
    def __init__(self):
        self.app_id = getattr(settings, 'EBAY_PRODUCTION_APP_ID', None)
        self.cert_id = getattr(settings, 'EBAY_PRODUCTION_CERT_ID', None)
        self.***REMOVED*** = getattr(settings, 'EBAY_PRODUCTION_CLIENT_SECRET', None)
        self.***REMOVED***= self._load_refresh_token()
        
    def _load_refresh_token(self):
        """Load refresh token from file if it exists, else from settings."""
        try:
            token_file = os.path.abspath(self.REFRESH_TOKEN_FILE)
            if os.path.exists(token_file):
                with open(token_file, 'r') as f:
                    token = f.read().strip()
                    if token:
                        logger.info("Loaded eBay refresh token from file.")
                        return token
            logger.info("Loading eBay refresh token from settings.")
            return getattr(settings, 'EBAY_PRODUCTION_REFRESH_TOKEN', None)
        except Exception as e:
            logger.error(f"Failed to load refresh token: {e}")
            return getattr(settings, 'EBAY_PRODUCTION_REFRESH_TOKEN', None)
    
    def get_valid_token(self) -> Optional[str]:
        """
        Get a valid OAuth token, refreshing if necessary
        Returns None if no valid token can be obtained
        """
        try:
            # Check if we have a cached token
            cached_token = cache.get(self.TOKEN_CACHE_KEY)
            token_expiry = cache.get(self.TOKEN_EXPIRY_CACHE_KEY)
            
            if cached_token and token_expiry:
                # Check if token is still valid (with buffer)
                if datetime.now() < token_expiry - self.EXPIRY_BUFFER:
                    logger.debug("Using cached eBay OAuth token")
                    return cached_token
                else:
                    logger.info("eBay OAuth token expired or expiring soon, refreshing...")
            
            # Try to refresh the token
            return self._refresh_token()
            
        except Exception as e:
            logger.error(f"Error getting valid eBay token: {e}")
            return self._get_fallback_token()
    
    def _refresh_token(self) -> Optional[str]:
        """
        Refresh the OAuth token using the refresh token
        Returns the new access token or None if failed
        """
        # Prevent multiple simultaneous refresh attempts
        if cache.get(self.REFRESH_LOCK_KEY):
            logger.warning("Token refresh already in progress, waiting...")
            time.sleep(2)
            return cache.get(self.TOKEN_CACHE_KEY)
        
        try:
            # Set refresh lock
            cache.set(self.REFRESH_LOCK_KEY, True, timeout=30)
            
            if not all([self.app_id, self.cert_id, self.***REMOVED***, self.refresh_token]):
                logger.warning("Missing eBay credentials for token refresh")
                return self._get_fallback_token()
            
            # eBay OAuth token refresh endpoint
            refresh_url = "https://api.ebay.com/identity/v1/oauth2/token"
            
            # Prepare the request
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Basic {self._get_basic_auth()}'
            }
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'scope': 'https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment'
            }
            
            logger.info("Refreshing eBay OAuth token...")
            response = requests.post(refresh_url, headers=headers, data=data, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 7200)  # Default 2 hours
                new_***REMOVED***= token_data.get('refresh_token')
                
                if access_token:
                    # Calculate expiry time
                    expiry_time = datetime.now() + timedelta(seconds=expires_in)
                    
                    # Cache the new token
                    cache.set(self.TOKEN_CACHE_KEY, access_token, timeout=expires_in)
                    cache.set(self.TOKEN_EXPIRY_CACHE_KEY, expiry_time, timeout=expires_in)
                    
                    # Update refresh token if provided
                    if new_refresh_token:
                        self._update_refresh_token(new_refresh_token)
                    
                    logger.info(f"Successfully refreshed eBay OAuth token, expires at {expiry_time}")
                    return access_token
                else:
                    logger.error("No access token in refresh response")
                    return self._get_fallback_token()
            else:
                logger.error(f"Failed to refresh eBay token: {response.status_code} - {response.text}")
                # Alert admins if refresh token is invalid or expired
                if response.status_code == 400 and 'invalid_grant' in response.text:
                    mail_admins(
                        subject="eBay OAuth Re-Authorization Required",
                        message="The eBay refresh token is invalid, expired, or revoked. Manual re-authorization is required. Please visit the eBay developer site, complete the OAuth flow, and update the refresh token in the system."
                    )
                return self._get_fallback_token()
                
        except Exception as e:
            logger.error(f"Exception during token refresh: {e}")
            return self._get_fallback_token()
        finally:
            # Release refresh lock
            cache.delete(self.REFRESH_LOCK_KEY)
    
    def _get_fallback_token(self) -> Optional[str]:
        """
        Get fallback token from settings (manual token)
        This is used when automatic refresh fails
        """
        fallback_token = getattr(settings, 'EBAY_PRODUCTION_USER_TOKEN', None)
        if fallback_token:
            logger.warning("Using fallback eBay OAuth token from settings")
            return fallback_token
        else:
            logger.error("No fallback eBay OAuth token available")
            return None
    
    def _get_basic_auth(self) -> str:
        """Generate Basic Auth header for eBay API"""
        import base64
        credentials = f"{self.app_id}:{self.cert_id}"
        return base64.b64encode(credentials.encode()).decode()
    
    def _update_refresh_token(self, new_refresh_token: str):
        """
        Update the refresh token in persistent storage (file)
        """
        try:
            token_file = os.path.abspath(self.REFRESH_TOKEN_FILE)
            with open(token_file, 'w') as f:
                f.write(new_refresh_token)
            self.***REMOVED***= new_refresh_token
            logger.info("New refresh token saved to file and updated in memory.")
        except Exception as e:
            logger.error(f"Failed to update refresh token: {e}")
    
    def validate_token(self, token: str) -> bool:
        """
        Validate if a token is still valid by making a test API call
        """
        try:
            test_url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'X-EBAY-C-MARKETPLACE-ID': 'EBAY-US'
            }
            params = {'q': 'test', 'limit': 1}
            
            response = requests.get(test_url, headers=headers, params=params, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return False
    
    def force_refresh(self) -> Optional[str]:
        """
        Force a token refresh regardless of expiry
        Useful for manual token updates
        """
        logger.info("Forcing eBay OAuth token refresh...")
        cache.delete(self.TOKEN_CACHE_KEY)
        cache.delete(self.TOKEN_EXPIRY_CACHE_KEY)
        return self._refresh_token()

# Global token manager instance
token_manager = EbayTokenManager()

def get_ebay_oauth_token() -> Optional[str]:
    """
    Get a valid eBay OAuth token with automatic refresh
    This is the main function to use throughout the application
    """
    return token_manager.get_valid_token()

def refresh_ebay_token() -> Optional[str]:
    """
    Manually refresh the eBay OAuth token
    Useful for admin operations or when tokens are known to be expired
    """
    return token_manager.force_refresh()

def validate_ebay_token(token: str) -> bool:
    """
    Validate if an eBay OAuth token is still valid
    """
    return token_manager.validate_token(token) 