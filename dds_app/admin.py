from django.contrib import admin
from .models import Category, Item, ExchangeProposal


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'category', 'condition', 'created_at', 'is_active')
    list_filter = ('category', 'condition', 'is_active')
    search_fields = ('title', 'description', 'owner__username')


@admin.register(ExchangeProposal)
class ExchangeProposalAdmin(admin.ModelAdmin):
    list_display = ('id', 'ad_sender', 'ad_receiver', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('ad_sender__title', 'ad_receiver__title', 'comment')
