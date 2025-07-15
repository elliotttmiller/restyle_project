# File: backend/core/models.py

from django.db import models
from django.conf import settings
from django.db.models import Q
from django.db.models.constraints import UniqueConstraint
import uuid
from django.contrib.postgres.fields import ArrayField

class Item(models.Model):
    class ConditionChoices(models.TextChoices):
        NEW_WITH_TAGS = 'NWT', 'New with tags'
        NEW_WITHOUT_TAGS = 'NWOT', 'New without tags'
        EXCELLENT = 'EUC', 'Excellent used condition'
        GOOD = 'GUC', 'Good used condition'
        FAIR = 'Fair', 'Fair condition'
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    cost_of_goods = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sku = models.CharField(max_length=100, blank=True, null=True)
    condition = models.CharField(max_length=4, choices=ConditionChoices.choices, default=ConditionChoices.GOOD)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ebay_category_id = models.CharField(max_length=32, blank=True, null=True)
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['owner', 'sku'], 
                condition=Q(sku__isnull=False), 
                name='unique_sku_for_owner'
            )
        ]
    
    def __str__(self):
        return f"{self.brand} {self.title}"

    def save(self, *args, **kwargs):
        # Auto-generate a unique SKU if not provided
        if not self.sku:
            base_sku = f"SKU-{uuid.uuid4().hex[:8]}"
            unique_sku = base_sku
            suffix = 1
            while Item.objects.filter(owner=self.owner, sku=unique_sku).exclude(pk=self.pk).exists():
                unique_sku = f"{base_sku}-{suffix}"
                suffix += 1
            self.sku = unique_sku
        super().save(*args, **kwargs)

class MarketAnalysis(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name='analysis')
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_range_low = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_range_high = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    confidence_score = models.CharField(max_length=50, blank=True, null=True)
    task_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analysis for {self.item.title}"

class ComparableSale(models.Model):
    analysis = models.ForeignKey(MarketAnalysis, on_delete=models.CASCADE, related_name='comps')
    title = models.CharField(max_length=255)
    sold_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(null=True, blank=True)
    platform = models.CharField(max_length=50)
    source_url = models.URLField(max_length=1024)
    image_url = models.URLField(max_length=1024, blank=True, null=True)
    
    def __str__(self):
        return f"Comp for {self.analysis.item.title} - ${self.sold_price}"

class Listing(models.Model):
    class PlatformChoices(models.TextChoices):
        EBAY = 'EBAY', 'eBay'
    
    class EbayListingType(models.TextChoices):
        AUCTION = 'AUCTION', 'Auction'
        FIXED_PRICE = 'FIXED', 'Fixed Price'
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='listings')
    platform = models.CharField(max_length=10, choices=PlatformChoices.choices)
    list_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=False)
    platform_item_id = models.CharField(max_length=255, blank=True, null=True)
    listing_url = models.URLField(max_length=1024, blank=True, null=True)
    listing_type = models.CharField(max_length=10, choices=EbayListingType.choices, default=EbayListingType.FIXED_PRICE)
    duration = models.CharField(max_length=20, default='GTC')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('item', 'platform')
    
    def __str__(self):
        return f"{self.item.title} on {self.get_platform_display()}"

class ItemEmbedding(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name='embedding')
    embedding = ArrayField(models.FloatField(), size=512)  # 512 for CLIP ViT-B/32, adjust as needed
    model_name = models.CharField(max_length=100, default='clip-vit-b32')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Embedding for {self.item.title} ({self.model_name})"

class SearchFeedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='feedbacks')
    query = models.CharField(max_length=255)
    relevant = models.BooleanField()
    matched_on = models.CharField(max_length=255, blank=True, null=True)  # e.g., 'color,brand,label'
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Feedback: {self.item.title} - {'Relevant' if self.relevant else 'Irrelevant'}"