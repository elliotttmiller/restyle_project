# File: backend/core/urls.py

from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .views import (
    ItemListCreateView,
    ItemDetailView,
    ListingListCreateView,
    ListingDetailView,
    TriggerAnalysisView,
    AnalysisStatusView,
    EbaySearchView,
    health_check,
    ai_status,
    performance_metrics,
    EbayTokenHealthView,
    EbayTokenActionView,
    SetEbayRefreshTokenView,
    EbayOAuthCallbackView,
    EbayOAuthDeclinedView,
    EbayOAuthView,
    PriceAnalysisView,
    AIImageSearchView,
    AdvancedMultiExpertAISearchView,
    PrivacyPolicyView,
    CropPreviewView,
    root_view,
    AcceptedView,
    DeclinedView,
)

# We ONLY import the views that currently exist in core/views.py
urlpatterns = [
    # Health check endpoint
    path('health/', health_check, name='health-check'),
    
    # AI Dashboard endpoints
    path('ai/status/', ai_status, name='ai-status'),
    path('metrics/', performance_metrics, name='performance-metrics'),
    
    # eBay Token Monitoring
    path('ebay-token/health/', EbayTokenHealthView.as_view(), name='ebay_token_health'),
    path('ebay-token/action/', EbayTokenActionView.as_view(), name='ebay_token_action'),
    
    # eBay Search endpoint
    path('ebay-search/', EbaySearchView.as_view(), name='ebay-search'),
    
    # Item URLs
    path('items/', ItemListCreateView.as_view(), name='item-list-create'),
    path('items/<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
    
    # Analysis URLs
    path('items/<int:pk>/analyze/', TriggerAnalysisView.as_view(), name='trigger-analysis'),
    path('items/<int:pk>/analysis/', AnalysisStatusView.as_view(), name='analysis-status'),
    
    # Listing URLs
    path('items/<int:item_pk>/listings/', ListingListCreateView.as_view(), name='listing-list-create'),
    path('listings/<int:pk>/', ListingDetailView.as_view(), name='listing-detail'),

    path('admin/set-ebay-refresh-token/', SetEbayRefreshTokenView.as_view(), name='set-ebay-refresh-token'),

    path('ebay-oauth-callback/', EbayOAuthCallbackView.as_view(), name='ebay-oauth-callback'),

    path('ebay-oauth-declined/', EbayOAuthDeclinedView.as_view(), name='ebay-oauth-declined'),

    path('ebay-oauth/', EbayOAuthView.as_view(), name='ebay-oauth'),

    path('price-analysis/', PriceAnalysisView.as_view(), name='price-analysis'),
    
    # AI Image Search
    path('ai/image-search/', AIImageSearchView.as_view(), name='ai-image-search'),
    
    # Advanced Multi-Expert AI Search
    path('ai/advanced-search/', AdvancedMultiExpertAISearchView.as_view(), name='advanced-ai-search'),

    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),

    path('accepted/', AcceptedView.as_view(), name='accepted'),
    path('declined/', DeclinedView.as_view(), name='declined'),

    path('ai/crop-preview/', CropPreviewView.as_view(), name='ai-crop-preview'),
]

# Authenticated health check endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def authenticated_health_check(request):
    return Response({"status": "ok", "user": str(request.user)})

urlpatterns += [
    path('health-check/', authenticated_health_check, name='authenticated-health-check'),
]