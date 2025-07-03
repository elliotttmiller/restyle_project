from django.core.management.base import BaseCommand
from core.ebay_auth import token_manager
import os

class Command(BaseCommand):
    help = 'Set the eBay refresh token (writes to persistent file and reloads in memory)'

    def add_arguments(self, parser):
        parser.add_argument('refresh_token', type=str, help='The new eBay refresh token')

    def handle(self, *args, **options):
        new_token = options['refresh_token']
        try:
            # Write to the persistent file
            token_manager._update_refresh_token(new_token)
            self.stdout.write(self.style.SUCCESS('Refresh token updated successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to update refresh token: {e}')) 