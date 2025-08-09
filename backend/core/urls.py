

# backend/core/urls.py

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Health and system endpoints
    path('health/', views.health_check, name='health_check'),
    path('ai/status/', views.ai_status, name='ai_status'),
    path('metrics/', views.performance_metrics, name='performance_metrics'),
    path('env-debug/', views.EnvVarDebugView.as_view(), name='env-debug'),

    # eBay OAuth and token endpoints
    path('ebay-token/health/', views.EbayTokenHealthView.as_view(), name='ebay_token_health'),
    path('ebay-token/action/', views.EbayTokenActionView.as_view(), name='ebay_token_action'),
    path('admin/set-ebay-refresh-token/', views.SetEbayRefreshTokenView.as_view(), name='set-ebay-refresh-token'),
    path('ebay-oauth-callback/', views.EbayOAuthCallbackView.as_view(), name='ebay-oauth-callback'),
    path('ebay-oauth-declined/', views.EbayOAuthDeclinedView.as_view(), name='ebay-oauth-declined'),
    path('ebay-oauth/', views.EbayOAuthView.as_view(), name='ebay-oauth'),

    # eBay and item endpoints
    path('ebay-search/', views.EbaySearchView.as_view(), name='ebay-search'),
    path('items/', views.ItemListCreateView.as_view(), name='item-list-create'),
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='item-detail'),
    path('items/<int:pk>/analyze/', views.TriggerAnalysisView.as_view(), name='trigger-analysis'),
    path('items/<int:pk>/analysis/', views.AnalysisStatusView.as_view(), name='analysis-status'),
    path('items/<int:item_pk>/listings/', views.ListingListCreateView.as_view(), name='listing-list-create'),
    path('listings/<int:pk>/', views.ListingDetailView.as_view(), name='listing-detail'),

    # AI endpoints
    path('analyze-and-price/', views.AnalyzeAndPriceView.as_view(), name='analyze-and-price'),
    path('ai/image-search/', views.AIImageSearchView.as_view(), name='ai-image-search'),
    path('ai/advanced-search/', views.AdvancedMultiExpertAISearchView.as_view(), name='advanced-ai-search'),
    path('ai/crop-preview/', views.CropPreviewView.as_view(), name='ai-crop-preview'),

    # Price analysis
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

urlpatterns += [
]