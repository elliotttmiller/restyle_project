"""
Django management command for managing eBay OAuth tokens
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from core.ebay_auth import token_manager, validate_ebay_token
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Manage eBay OAuth tokens'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['refresh', 'validate', 'status', 'force-refresh'],
            help='Action to perform on eBay tokens'
        )
        parser.add_argument(
            '--token',
            type=str,
            help='Token to validate (for validate action)'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'refresh':
            self.refresh_token()
        elif action == 'validate':
            self.validate_token(options['token'])
        elif action == 'status':
            self.show_status()
        elif action == 'force-refresh':
            self.force_refresh()

    def refresh_token(self):
        """Refresh the eBay OAuth token"""
        self.stdout.write("🔄 Refreshing eBay OAuth token...")
        
        try:
            token = token_manager.get_valid_token()
            if token:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Token refreshed successfully!")
                )
                self.stdout.write(f"   Token length: {len(token)} characters")
                self.stdout.write(f"   Token starts with: {token[:20]}...")
            else:
                self.stdout.write(
                    self.style.ERROR("❌ Failed to refresh token")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error refreshing token: {e}")
            )

    def validate_token(self, token_str):
        """Validate a specific token"""
        if not token_str:
            # Use current token from manager
            token_str = token_manager.get_valid_token()
            if not token_str:
                self.stdout.write(
                    self.style.ERROR("❌ No token available to validate")
                )
                return
        
        self.stdout.write("🔍 Validating eBay OAuth token...")
        
        try:
            is_valid = validate_ebay_token(token_str)
            if is_valid:
                self.stdout.write(
                    self.style.SUCCESS("✅ Token is valid!")
                )
            else:
                self.stdout.write(
                    self.style.ERROR("❌ Token is invalid or expired")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error validating token: {e}")
            )

    def show_status(self):
        """Show current token status"""
        self.stdout.write("📊 eBay OAuth Token Status")
        self.stdout.write("=" * 40)
        
        # Check cached token
        cached_token = token_manager.get_valid_token()
        if cached_token:
            self.stdout.write("✅ Valid token available")
            self.stdout.write(f"   Length: {len(cached_token)} characters")
            self.stdout.write(f"   Starts with: {cached_token[:20]}...")
            
            # Validate the token
            is_valid = validate_ebay_token(cached_token)
            if is_valid:
                self.stdout.write("✅ Token validation: PASSED")
            else:
                self.stdout.write("❌ Token validation: FAILED")
        else:
            self.stdout.write("❌ No valid token available")
        
        # Check configuration
        self.stdout.write("\n🔧 Configuration:")
        self.stdout.write(f"   App ID: {'✅ Set' if getattr(settings, 'EBAY_PRODUCTION_APP_ID', None) else '❌ Missing'}")
        self.stdout.write(f"   Cert ID: {'✅ Set' if getattr(settings, 'EBAY_PRODUCTION_CERT_ID', None) else '❌ Missing'}")
        self.stdout.write(f"   Client Secret: {'✅ Set' if getattr(settings, 'EBAY_PRODUCTION_CLIENT_SECRET', None) else '❌ Missing'}")
        self.stdout.write(f"   Refresh Token: {'✅ Set' if getattr(settings, 'EBAY_PRODUCTION_REFRESH_TOKEN', None) else '❌ Missing'}")
        self.stdout.write(f"   Fallback Token: {'✅ Set' if getattr(settings, 'EBAY_PRODUCTION_USER_TOKEN', None) else '❌ Missing'}")

    def force_refresh(self):
        """Force a token refresh regardless of expiry"""
        self.stdout.write("🔄 Force refreshing eBay OAuth token...")
        
        try:
            token = token_manager.force_refresh()
            if token:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Token force refreshed successfully!")
                )
                self.stdout.write(f"   Token length: {len(token)} characters")
            else:
                self.stdout.write(
                    self.style.ERROR("❌ Failed to force refresh token")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error force refreshing token: {e}")
            ) 