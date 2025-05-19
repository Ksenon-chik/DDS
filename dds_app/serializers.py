from rest_framework import serializers
from .models import Item, ExchangeProposal


class ItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'title', 'description', 'category', 'condition', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        return Item.objects.create(owner=user, **validated_data)


class ExchangeProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeProposal
        fields = ['id', 'ad_sender', 'ad_receiver', 'comment', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']
