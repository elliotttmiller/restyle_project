# backend/core/urls.py

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # The single, definitive AI analysis endpoint
    path('analyze-and-price/', views.AnalyzeAndPriceView.as_view(), name='analyze-and-price'),

    # Health and system endpoints
    path('health/', views.health_check, name='health_check'),
    path('ebay-token-health/', views.EbayTokenHealthView.as_view(), name='ebay_token_health'),

    # Internal: Dynamic URL discovery (admin only)
    path('internal/list-urls/', views.ListUrlsView.as_view(), name='list-urls'),
]