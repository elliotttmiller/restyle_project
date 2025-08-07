# File: backend/core/admin.py

from django.contrib import admin
from .models import Item, Listing, MarketAnalysis, ComparableSale

class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'owner', 'condition', 'is_sold')
    search_fields = ('title', 'brand', 'sku')

class ListingAdmin(admin.ModelAdmin):
    list_display = ('item', 'platform', 'list_price', 'is_active')
    list_filter = ('platform', 'is_active')

class MarketAnalysisAdmin(admin.ModelAdmin):
    list_display = ('item', 'status', 'suggested_price')
    list_filter = ('status',)

class ComparableSaleAdmin(admin.ModelAdmin):
    list_display = ('title', 'sold_price', 'platform')
    list_filter = ('platform',)

admin.site.register(Item, ItemAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(MarketAnalysis, MarketAnalysisAdmin)
admin.site.register(ComparableSale, ComparableSaleAdmin)