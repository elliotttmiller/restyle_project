import logging
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


BASE_URL = "/api/core/"

ENDPOINTS = [
    ("health/", False),
    ("health-check/", True),  # requires authentication
    ("env-debug/", False),
    ("ebay-token/health/", False),
    ("ebay-token/action/", False),
    ("ebay-search/", False),
    ("admin/set-ebay-refresh-token/", False),
    ("ebay-oauth-callback/", False),
    ("ebay-oauth-declined/", False),
    ("ebay-oauth/", False),
    ("ai/status/", False),
    ("metrics/", False),
    ("items/", False),
    ("price-analysis/", False),
    ("ai/image-search/", False),
    ("ai/advanced-search/", False),
    ("privacy-policy/", False),
    ("accepted/", False),
    ("declined/", False),
    ("ai/crop-preview/", False),
]

class AllEndpointsTest(APITestCase):
    def setUp(self):
        # Optionally create a user and authenticate for endpoints that require it
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username="apitestuser", password="apitestpass")
        self.client.login(username="apitestuser", password="apitestpass")



    def test_health_endpoint(self):
        self.client.logout()
        response = self.client.get(f"{BASE_URL}health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_health_check_endpoint(self):
        self.client.login(username="apitestuser", password="apitestpass")
        response = self.client.get(f"{BASE_URL}health-check/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_public_endpoints_batch(self):
        self.client.logout()
        public_endpoints = [ep for ep, auth in ENDPOINTS if not auth and ep != "health/"]
        # Test endpoints without explicit loop
        responses = {ep: self.client.get(f"{BASE_URL}{ep}") for ep in public_endpoints}
        failed_endpoints = [ep for ep, resp in responses.items() if resp.status_code != status.HTTP_200_OK]
        self.assertEqual(len(failed_endpoints), 0, f"Failed endpoints: {failed_endpoints}")

    def test_items_detail_endpoints(self):
        try:
            from backend.core.models import Item
            item = Item.objects.create(name="Test Item")
            pk = item.pk
        except Exception as e:
            self.skipTest(f"Could not create Item instance: {e}")
        
        endpoints = [f"items/{pk}/", f"items/{pk}/analyze/", f"items/{pk}/analysis/", f"items/{pk}/listings/"]
        
        # Test all endpoints without explicit loop
        responses = {ep: self.client.get(f"{BASE_URL}{ep}") for ep in endpoints}
        failed_endpoints = [ep for ep, resp in responses.items() if resp.status_code != status.HTTP_200_OK]
        self.assertEqual(len(failed_endpoints), 0, f"Failed item endpoints: {failed_endpoints}")
