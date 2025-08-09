

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
    path('price-analysis/', views.PriceAnalysisView.as_view(), name='price-analysis'),

    # Legal and policy endpoints
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('accepted/', views.AcceptedView.as_view(), name='accepted'),
    path('declined/', views.DeclinedView.as_view(), name='declined'),

    # Misc/test endpoints
    path('test-ebay-login/', views.TestEbayLoginView.as_view(), name='test-ebay-login'),
    path('', views.root_view, name='root'),
]

# Import or define authenticated_health_check before using it