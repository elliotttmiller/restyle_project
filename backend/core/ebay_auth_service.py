"""
Supercharged eBay Authentication Service
This service provides a robust, proactive, and centralized system for managing
eBay OAuth tokens, ensuring high availability and performance.
"""
import logging
from datetime import datetime, timedelta, timezone
from django.core.cache import cache
from django.conf import settings
import requests
import base64

# Import the Celery app and the specific task
from backend.celery_app import app as celery_app
from core.tasks import refresh_ebay_token_task

logger = logging.getLogger(__name__)

class EbayAuthService:
    """
    A stateful service to manage eBay OAuth tokens with proactive refreshing.
    """
    _instance = None

    # Cache keys for storing token state
    TOKEN_CACHE_KEY = "ebay_access_token"
    EXPIRY_CACHE_KEY = "ebay_token_expiry"
    LAST_REFRESH_CACHE_KEY = "ebay_last_successful_refresh"
    REFRESH_LOCK_KEY = "ebay_token_refresh_lock"

    # Proactive refresh threshold: if token expires within this window, refresh it.
    PROACTIVE_REFRESH_WINDOW = timedelta(hours=1)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EbayAuthService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.app_id = getattr(settings, 'EBAY_PRODUCTION_APP_ID', None)
        self.client_secret = getattr(settings, 'EBAY_PRODUCTION_CLIENT_SECRET', None)
        self.refresh_token = getattr(settings, 'EBAY_PRODUCTION_REFRESH_TOKEN', None)
        
        self._log_credential_status()
        self._initialized = True

    def _log_credential_status(self):
        logger.info("EbayAuthService Initialized.")
        logger.info(f"  - App ID: {'SET' if self.app_id else 'MISSING'}")
        logger.info(f"  - Client Secret: {'SET' if self.client_secret else 'MISSING'}")
        logger.info(f"  - Refresh Token: {'SET' if self.refresh_token else 'MISSING'}")

    def ensure_valid_token(self) -> str | None:
        """
        The primary method to get a valid token.
        It checks the current token and triggers a proactive or immediate refresh if needed.
        """
        token = cache.get(self.TOKEN_CACHE_KEY)
        expiry = cache.get(self.EXPIRY_CACHE_KEY)

        if not token or not expiry:
            logger.info("No cached token found. Forcing an immediate refresh.")
            return self.force_refresh()

        now = datetime.now(timezone.utc)
        time_to_expiry = expiry - now

        if time_to_expiry <= timedelta(seconds=0):
            logger.warning("Token has expired. Forcing an immediate synchronous refresh.")
            return self.force_refresh()

        if time_to_expiry <= self.PROACTIVE_REFRESH_WINDOW:
            logger.info("Token is nearing expiration. Triggering proactive background refresh.")
            self._proactive_refresh()

        return token

    def force_refresh(self) -> str | None:
        """
        Performs an immediate, synchronous token refresh.
        This should be used when a token is known to be expired or invalid.
        """
        lock = cache.add(self.REFRESH_LOCK_KEY, "locked", timeout=60)
        if not lock:
            logger.warning("Token refresh is already in progress. Waiting briefly.")
            time.sleep(5)
            return cache.get(self.TOKEN_CACHE_KEY)

        try:
            logger.info("Performing synchronous token refresh.")
            if not all([self.app_id, self.client_secret, self.refresh_token]):
                logger.error("Cannot refresh token, missing essential credentials.")
                return None

            headers = self._get_auth_headers()
            data = self._get_refresh_payload()

            response = requests.post(
                "https://api.ebay.com/identity/v1/oauth2/token",
                headers=headers,
                data=data,
                timeout=20
            )
            response.raise_for_status()  # Will raise an exception for 4xx/5xx status

            token_data = response.json()
            return self._cache_new_token(token_data)

        except requests.exceptions.RequestException as e:
            logger.critical(f"eBay token refresh HTTP request failed: {e}", exc_info=True)
            return None
        finally:
            cache.delete(self.REFRESH_LOCK_KEY)

    def _proactive_refresh(self):
        """
        Triggers the Celery task to refresh the token in the background.
        This avoids blocking the current request.
        """
        lock = cache.add(self.REFRESH_LOCK_KEY, "locked", timeout=60)
        if lock:
            logger.info("Dispatching background task to refresh eBay token.")
            refresh_ebay_token_task.delay()
        else:
            logger.info("Background refresh already dispatched recently. Skipping.")

    def _cache_new_token(self, token_data: dict) -> str | None:
        """Caches the newly received token data."""
        access_token = token_data.get("access_token")
        if not access_token:
            logger.error("Refresh response did not contain an access_token.")
            return None

        expires_in = token_data.get("expires_in", 7200)  # Default to 2 hours
        expiry_time = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        cache.set(self.TOKEN_CACHE_KEY, access_token, timeout=expires_in)
        cache.set(self.EXPIRY_CACHE_KEY, expiry_time, timeout=expires_in)
        cache.set(self.LAST_REFRESH_CACHE_KEY, datetime.now(timezone.utc), timeout=None) # Persist forever

        logger.info(f"Successfully refreshed and cached new eBay token. Expires at {expiry_time.isoformat()}")
        return access_token

    def _get_auth_headers(self) -> dict:
        """Constructs the necessary headers for the token refresh request."""
        creds = f"{self.app_id}:{self.client_secret}"
        encoded_creds = base64.b64encode(creds.encode()).decode()
        return {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_creds}",
        }

    def _get_refresh_payload(self) -> dict:
        """Constructs the payload for the token refresh request."""
        return {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "scope": "https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.inventory",
        }

    def get_status(self) -> dict:
        """Provides a detailed status report of the current token."""
        expiry = cache.get(self.EXPIRY_CACHE_KEY)
        last_refresh = cache.get(self.LAST_REFRESH_CACHE_KEY)
        status = {}

        if expiry and isinstance(expiry, datetime):
            now = datetime.now(timezone.utc)
            ttl = expiry - now
            status['status'] = 'active' if ttl > timedelta(0) else 'expired'
            status['expires_at'] = expiry.isoformat()
            status['time_remaining'] = str(ttl)
        else:
            status['status'] = 'unknown'
            status['expires_at'] = None
            status['time_remaining'] = None

        if last_refresh and isinstance(last_refresh, datetime):
            status['last_successful_refresh'] = last_refresh.isoformat()
        else:
            status['last_successful_refresh'] = None
            
        return status

# Singleton instance for easy access across the application
ebay_auth_service = EbayAuthService()
