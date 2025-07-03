# File: backend/core/urls.py

from django.urls import path
# We ONLY import the views that currently exist in core/views.py
from .views import (
    ItemListCreateView, 
    ItemDetailView, 
    ListingListCreateView, 
    ListingDetailView,
    TriggerAnalysisView,
    AnalysisStatusView,
    EbaySearchView,
    health_check,
    EbayTokenHealthView,
    EbayTokenActionView,
    SetEbayRefreshTokenView,
    EbayOAuthCallbackView,
    EbayOAuthDeclinedView,
    PriceAnalysisView,
)

urlpatterns = [
    # Health check endpoint
    path('health/', health_check, name='health-check'),
    
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

    path('price-analysis/', PriceAnalysisView.as_view(), name='price-analysis'),
]