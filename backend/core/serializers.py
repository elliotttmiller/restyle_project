# File: backend/core/serializers.py

from rest_framework import serializers
from .models import Item, Listing, MarketAnalysis, ComparableSale
import uuid

class ComparableSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComparableSale
        fields = '__all__'

class MarketAnalysisSerializer(serializers.ModelSerializer):
    comps = ComparableSaleSerializer(many=True, read_only=True)
    class Meta:
        model = MarketAnalysis
        fields = [ 'id', 'status', 'suggested_price', 'price_range_low', 
                   'price_range_high', 'confidence_score', 'updated_at', 'comps' ]

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = [ 'id', 'platform', 'list_price', 'is_active', 'listing_type', 'duration',
                   'listing_url', 'platform_item_id', 'created_at', 'updated_at' ]

class ItemSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    analysis = MarketAnalysisSerializer(read_only=True)
    listings = ListingSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = [ 'id', 'owner', 'owner_username', 'title', 'description', 'brand', 
                   'category', 'size', 'color', 'cost_of_goods', 'sku', 
                   'condition', 'is_sold', 'created_at', 'updated_at',
                   'ebay_category_id',
                   'analysis', 'listings' ]
        read_only_fields = ['owner']