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
    health_check
)

urlpatterns = [
    # Health check endpoint
    path('health/', health_check, name='health-check'),
    
    # Item URLs
    path('items/', ItemListCreateView.as_view(), name='item-list-create'),
    path('items/<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
    
    # Analysis URLs
    path('items/<int:pk>/analyze/', TriggerAnalysisView.as_view(), name='trigger-analysis'),
    path('items/<int:pk>/analysis/', AnalysisStatusView.as_view(), name='analysis-status'),
    
    # Listing URLs
    path('items/<int:item_pk>/listings/', ListingListCreateView.as_view(), name='listing-list-create'),
    path('listings/<int:pk>/', ListingDetailView.as_view(), name='listing-detail'),
]