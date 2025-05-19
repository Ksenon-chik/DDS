from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('used', 'Б/У'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='items'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='items'
    )
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.owner.username})"


class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ]

    ad_sender = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='sent_proposals'
    )
    ad_receiver = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='received_proposals'
    )
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proposal from {self.ad_sender.owner.username} to {self.ad_receiver.owner.username}"
